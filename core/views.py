from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.db.models import Q
from datetime import date, timedelta
import os

from .models import (
    UserProfile, CardamomPrice, GalleryImage, AIReport,
    DiseaseRecommendation, SoilTestRequest, Announcement, TeamMember, District
)
from .forms import (
    CustomLoginForm, FarmerRegisterForm, AIReportForm,
    SoilTestRequestForm, GalleryUploadForm, AdminSoilUpdateForm,
    DistrictForm
)
from .gemini_service import analyze_cardamom_image
from .scraper import scrape_cardamom_prices, get_latest_prices_fallback


# ─── Helpers ────────────────────────────────────────────────────────────────

def get_user_profile(user):
    profile, _ = UserProfile.objects.get_or_create(user=user)
    return profile


def require_farmer(view_func):
    """Decorator: user must be logged in and have farmer role."""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        profile = get_user_profile(request.user)
        if profile.role != 'farmer':
            messages.error(request, 'Access denied. This area is for farmers only.')
            return redirect('home')
        return view_func(request, *args, **kwargs)
    wrapper.__name__ = view_func.__name__
    return wrapper


def require_admin(view_func):
    """Decorator: user must be logged in and have admin role."""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        profile = get_user_profile(request.user)
        if profile.role != 'admin':
            messages.error(request, 'Access denied. This area is for admins only.')
            return redirect('home')
        return view_func(request, *args, **kwargs)
    wrapper.__name__ = view_func.__name__
    return wrapper


# ─── Public Views ────────────────────────────────────────────────────────────

def home(request):
    today = date.today()
    
    # Get latest 8 unique dates for prices (Today + past 7 days)
    latest_dates = CardamomPrice.objects.values_list('date', flat=True).distinct().order_by('-date')[:8]
    prices = CardamomPrice.objects.filter(date__in=latest_dates).order_by('-date', 'market')

    # Auto-scrape if no prices today
    if not CardamomPrice.objects.filter(date=today).exists():
        try:
            from .management.commands.scrape_prices import Command
            cmd = Command()
            cmd.handle(force=False, use_fallback=False)
            prices = CardamomPrice.objects.filter(date=today)
            if not prices.exists():
                # Use fallback
                prices_data = get_latest_prices_fallback()
                for pd in prices_data:
                    CardamomPrice.objects.get_or_create(
                        market=pd['market'], date=today,
                        defaults=pd
                    )
                prices = CardamomPrice.objects.filter(date=today)
        except Exception:
            pass

    # Gallery featured images
    gallery_images = GalleryImage.objects.filter(is_featured=True)[:6]
    if gallery_images.count() < 3:
        gallery_images = GalleryImage.objects.all()[:6]

    # Latest announcements
    announcements = Announcement.objects.filter(is_active=True)[:3]

    # Stats
    farmer_count = UserProfile.objects.filter(role='farmer').count()
    report_count = AIReport.objects.count()

    # Get today's prices for the main section
    today_prices = prices.filter(date=today)
    if not today_prices.exists() and prices.exists():
        today_prices = prices.filter(date=latest_dates[0])[:4]

    context = {
        'prices': today_prices,
        'ticker_prices': prices,
        'price_date': today,
        'gallery_images': gallery_images,
        'announcements': announcements,
        'farmer_count': farmer_count,
        'report_count': report_count,
    }
    return render(request, 'home.html', context)


def about(request):
    team_members = TeamMember.objects.all()
    farmer_count = UserProfile.objects.filter(role='farmer').count()
    report_count = AIReport.objects.count()
    context = {
        'team_members': team_members,
        'farmer_count': farmer_count,
        'report_count': report_count,
    }
    return render(request, 'about.html', context)


def gallery(request):
    category = request.GET.get('category', '')
    if category:
        images = GalleryImage.objects.filter(category=category)
    else:
        images = GalleryImage.objects.all()

    categories = GalleryImage.objects.values_list('category', flat=True).distinct()

    context = {
        'images': images,
        'categories': categories,
        'selected_category': category,
    }
    return render(request, 'gallery.html', context)


def get_prices_api(request):
    """API endpoint to get latest prices as JSON."""
    today = date.today()
    prices = CardamomPrice.objects.filter(date=today)
    if not prices.exists():
        prices = CardamomPrice.objects.all()[:10]

    data = [{
        'market': p.market,
        'grade': p.grade,
        'min_price': str(p.min_price) if p.min_price else None,
        'max_price': str(p.max_price) if p.max_price else None,
        'modal_price': str(p.modal_price) if p.modal_price else None,
        'unit': p.unit,
        'date': str(p.date),
    } for p in prices]

    return JsonResponse({'prices': data, 'count': len(data)})


# ─── Auth Views ──────────────────────────────────────────────────────────────

def login_view(request):
    if request.user.is_authenticated:
        profile = get_user_profile(request.user)
        if profile.role == 'admin':
            return redirect('admin_dashboard')
        return redirect('farmer_dashboard')

    if request.method == 'POST':
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            # Specify the backend since we have multiples configured
            login(request, user, backend='core.backends.EmailOrPhoneBackend' if '@' in request.POST.get('username', '') or request.POST.get('username', '').isdigit() else 'django.contrib.auth.backends.ModelBackend')
            profile = get_user_profile(user)
            messages.success(request, f'Welcome back, {user.first_name or user.email}!')
            if profile.role == 'admin':
                return redirect('admin_dashboard')
            return redirect('farmer_dashboard')
        else:
            messages.error(request, 'Invalid Email/Phone or password.')
    else:
        form = CustomLoginForm(request)

    return render(request, 'auth/login.html', {'form': form})


def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = FarmerRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Specify the backend since we have multiples configured in settings
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            messages.success(request, f'Welcome to FarmCare, {user.first_name}! Your account has been created.')
            return redirect('farmer_dashboard')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = FarmerRegisterForm()

    return render(request, 'auth/register.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home')


# ─── Farmer Views ──────────────────────────────────────────────────────────

@require_farmer
def farmer_dashboard(request):
    profile = get_user_profile(request.user)
    recent_reports = AIReport.objects.filter(farmer=request.user)[:5]
    soil_requests = SoilTestRequest.objects.filter(farmer=request.user)[:3]
    today = date.today()
    # Get latest 5 unique dates for prices
    latest_dates = CardamomPrice.objects.values_list('date', flat=True).distinct().order_by('-date')[:5]
    prices = CardamomPrice.objects.filter(date__in=latest_dates).order_by('-date', 'market')
    
    total_reports = AIReport.objects.filter(farmer=request.user).count()
    pending_soil = SoilTestRequest.objects.filter(farmer=request.user, status='pending').count()

    context = {
        'profile': profile,
        'recent_reports': recent_reports,
        'soil_requests': soil_requests,
        'prices': prices,
        'total_reports': total_reports,
        'pending_soil': pending_soil,
    }
    return render(request, 'farmer/dashboard.html', context)


@require_farmer
def ai_detect(request):
    profile = get_user_profile(request.user)
    report = None

    if request.method == 'POST':
        form = AIReportForm(request.POST, request.FILES)
        if form.is_valid():
            image = form.cleaned_data['image']

            # 1. History Context Calculation
            # Provide context if the farmer has recent successful reports
            last_report = AIReport.objects.filter(farmer=request.user, status='completed').first()
            history_context = "None"
            if last_report:
                history_context = f"Previous Disease: {last_report.disease_detected}. Symptoms were: {last_report.symptoms[:200]}"

            # Create report record
            ai_report = AIReport.objects.create(
                farmer=request.user,
                image=image,
                status='processing',
            )

            # Analyze with Gemini
            image_full_path = ai_report.image.path
            result = analyze_cardamom_image(image_full_path, history_context=history_context)

            if not result.get('is_cardamom', True):
                ai_report.status = 'failed'
                ai_report.disease_detected = 'Invalid Image'
                ai_report.is_cardamom = False
                ai_report.gemini_response = result.get('gemini_response', 'Species mismatch.')
                ai_report.save()
                messages.warning(request, result.get('gemini_response', 'The uploaded image is not a cardamom plant.'))
                return redirect('ai_detect')

            ai_report.disease_detected = result.get('disease_detected', 'Unknown')
            ai_report.confidence_level = result.get('confidence_level', 'Unknown')
            ai_report.severity = result.get('severity', 'Unknown')
            ai_report.symptoms = result.get('symptoms', '')
            ai_report.diagnosis = result.get('diagnosis', '')
            ai_report.medicines = result.get('medicines', '')
            ai_report.dosage = result.get('dosage', '')
            ai_report.precautions = result.get('precautions', '')
            ai_report.expert_deep_dive = result.get('expert_deep_dive', '')
            ai_report.gemini_response = result.get('gemini_response', '')
            ai_report.status = 'completed' if result.get('success') else 'failed'

            # Try to match with recommendation
            disease_name = ai_report.disease_detected.lower()
            for rec in DiseaseRecommendation.objects.all():
                if rec.disease_name.lower() in disease_name or disease_name in rec.disease_name.lower():
                    ai_report.recommendation = rec
                    break

            ai_report.save()
            report = ai_report

            if result.get('success'):
                messages.success(request, 'Analysis complete! Check the results below.')
            else:
                messages.warning(request, 'Analysis completed with some issues. Please check the results.')

            return redirect('report_detail', report_id=ai_report.id)
        else:
            messages.error(request, 'Please upload a valid image.')
    else:
        form = AIReportForm()

    return render(request, 'farmer/ai_detect.html', {'form': form, 'profile': profile})


@require_farmer
def download_report(request, report_id):
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
    from io import BytesIO

    report = get_object_or_404(AIReport, id=report_id, farmer=request.user)
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    styles = getSampleStyleSheet()
    
    # Custom Styles
    title_style = ParagraphStyle('Title', parent=styles['Heading1'], fontSize=24, textColor=colors.HexColor("#1e3a2f"), spaceAfter=20)
    h2_style = ParagraphStyle('Header2', parent=styles['Heading2'], fontSize=16, textColor=colors.HexColor("#2d5a45"), spaceBefore=15, spaceAfter=10)
    body_style = ParagraphStyle('Body', parent=styles['Normal'], fontSize=10, leading=14, spaceAfter=8)
    label_style = ParagraphStyle('Label', parent=styles['Normal'], fontSize=10, fontName='Helvetica-Bold', textColor=colors.grey)

    elements = []

    # Title
    elements.append(Paragraph("🌿 FarmCare Analysis Report", title_style))
    elements.append(Paragraph(f"Date: {report.created_at.strftime('%d %B %Y')}", label_style))
    elements.append(Paragraph(f"Farmer: {report.farmer.first_name or report.farmer.email}", label_style))
    elements.append(Spacer(1, 20))

    # Plant Image
    if report.image:
        img_path = report.image.path
        img = Image(img_path, width=400, height=300)
        elements.append(img)
        elements.append(Spacer(1, 20))

    # Disease Summary Table
    data = [
        ["Disease Detected", report.disease_detected],
        ["Confidence Level", report.confidence_level],
        ["Intensity", report.severity or "N/A"],
        ["Status", report.status.upper()]
    ]
    t = Table(data, colWidths=[150, 300])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor("#f0f7f4")),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor("#1e3a2f")),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.white),
    ]))
    elements.append(t)
    elements.append(Spacer(1, 20))

    # Detailed Sections
    def add_section(header, content):
        if content:
            elements.append(Paragraph(header, h2_style))
            elements.append(Paragraph(content.replace('\n', '<br/>'), body_style))

    add_section("🔍 Diagnosis", report.diagnosis)
    add_section("🦠 Symptoms Observed", report.symptoms)
    add_section("💊 Recommended Medicines", report.medicines)
    add_section("📏 Dosage & Application", report.dosage)
    add_section("⚠️ Precautions", report.precautions)

    # Footer
    elements.append(Spacer(1, 40))
    elements.append(Paragraph("--- End of Report ---", ParagraphStyle('Footer', parent=styles['Normal'], alignment=1, textColor=colors.grey)))
    elements.append(Paragraph("Generated by FarmCare AI Diagnostics", ParagraphStyle('FooterSmall', parent=styles['Normal'], alignment=1, fontSize=8, textColor=colors.grey)))

    doc.build(elements)
    buffer.seek(0)
    
    filename = f"FarmCare_Report_{report.id}_{report.created_at.strftime('%Y%m%d')}.pdf"
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


@login_required
def report_detail(request, report_id):
    report = get_object_or_404(AIReport, id=report_id)
    # Farmer can only view their own reports; admin can view all
    profile = get_user_profile(request.user)
    if profile.role == 'farmer' and report.farmer != request.user:
        messages.error(request, 'Access denied.')
        return redirect('farmer_dashboard')

    return render(request, 'farmer/report_detail.html', {'report': report, 'profile': profile})


@require_farmer
def history(request):
    profile = get_user_profile(request.user)
    reports = AIReport.objects.filter(farmer=request.user)
    soil_requests = SoilTestRequest.objects.filter(farmer=request.user)

    tab = request.GET.get('tab', 'reports')

    context = {
        'reports': reports,
        'soil_requests': soil_requests,
        'profile': profile,
        'tab': tab,
    }
    return render(request, 'farmer/history.html', context)


@require_farmer
def soil_request(request):
    profile = get_user_profile(request.user)
    existing_requests = SoilTestRequest.objects.filter(farmer=request.user)

    if request.method == 'POST':
        form = SoilTestRequestForm(request.POST)
        if form.is_valid():
            soil_req = form.save(commit=False)
            soil_req.farmer = request.user
            soil_req.save()
            messages.success(request, 'Your soil test request has been submitted! The admin will contact you soon.')
            return redirect('history')
        else:
            messages.error(request, 'Please fill in all required fields.')
    else:
        form = SoilTestRequestForm()
        # Pre-fill farm details from profile
        if profile.location:
            form.fields['farm_location'].initial = profile.location
        if profile.farm_size:
            form.fields['farm_size'].initial = profile.farm_size

    context = {
        'form': form,
        'existing_requests': existing_requests,
        'profile': profile,
    }
    return render(request, 'farmer/soil_request.html', context)


# ─── Admin Views ──────────────────────────────────────────────────────────

@require_admin
def admin_dashboard(request):
    total_farmers = UserProfile.objects.filter(role='farmer').count()
    total_reports = AIReport.objects.count()
    pending_soil = SoilTestRequest.objects.filter(status='pending').count()
    recent_reports = AIReport.objects.select_related('farmer')[:8]
    recent_soil = SoilTestRequest.objects.select_related('farmer')[:5]

    # Disease stats
    disease_stats = {}
    for report in AIReport.objects.filter(status='completed'):
        d = report.disease_detected or 'Unknown'
        disease_stats[d] = disease_stats.get(d, 0) + 1

    top_diseases = sorted(disease_stats.items(), key=lambda x: x[1], reverse=True)[:5]

    context = {
        'total_farmers': total_farmers,
        'total_reports': total_reports,
        'pending_soil': pending_soil,
        'recent_reports': recent_reports,
        'recent_soil': recent_soil,
        'top_diseases': top_diseases,
    }
    return render(request, 'admin_panel/dashboard.html', context)


@require_admin
def admin_farmers(request):
    search = request.GET.get('search', '')
    farmers = UserProfile.objects.filter(role='farmer').select_related('user')
    if search:
        farmers = farmers.filter(
            Q(user__username__icontains=search) |
            Q(user__first_name__icontains=search) |
            Q(user__last_name__icontains=search) |
            Q(location__icontains=search)
        )

    farmer_data = []
    for fp in farmers:
        farmer_data.append({
            'profile': fp,
            'report_count': AIReport.objects.filter(farmer=fp.user).count(),
            'soil_requests': SoilTestRequest.objects.filter(farmer=fp.user).count(),
        })

    return render(request, 'admin_panel/farmer_list.html', {
        'farmer_data': farmer_data,
        'search': search,
    })


@require_admin
def admin_disease_reports(request):
    farmer_id = request.GET.get('farmer_id', '')
    disease_filter = request.GET.get('disease', '')

    reports = AIReport.objects.select_related('farmer', 'recommendation').all()

    if farmer_id:
        reports = reports.filter(farmer__id=farmer_id)
    if disease_filter:
        reports = reports.filter(disease_detected__icontains=disease_filter)

    farmers = User.objects.filter(
        profile__role='farmer',
        ai_reports__isnull=False
    ).distinct()

    context = {
        'reports': reports,
        'farmers': farmers,
        'selected_farmer': farmer_id,
        'disease_filter': disease_filter,
    }
    return render(request, 'admin_panel/disease_reports.html', context)


@require_admin
def admin_soil_requests(request):
    status_filter = request.GET.get('status', '')
    soil_requests = SoilTestRequest.objects.select_related('farmer').all()

    if status_filter:
        soil_requests = soil_requests.filter(status=status_filter)

    context = {
        'soil_requests': soil_requests,
        'status_filter': status_filter,
        'statuses': SoilTestRequest.STATUS_CHOICES,
    }
    return render(request, 'admin_panel/soil_requests.html', context)


@require_admin
def admin_update_soil_request(request, request_id):
    soil_req = get_object_or_404(SoilTestRequest, id=request_id)

    if request.method == 'POST':
        form = AdminSoilUpdateForm(request.POST, instance=soil_req)
        if form.is_valid():
            form.save()
            messages.success(request, f'Soil test request for {soil_req.farmer.get_full_name() or soil_req.farmer.username} has been updated.')
            return redirect('admin_soil_requests')
    else:
        form = AdminSoilUpdateForm(instance=soil_req)

    return render(request, 'admin_panel/update_soil_request.html', {
        'form': form,
        'soil_req': soil_req,
    })


@require_admin
def admin_gallery_upload(request):
    if request.method == 'POST':
        form = GalleryUploadForm(request.POST, request.FILES)
        if form.is_valid():
            img = form.save(commit=False)
            img.uploaded_by = request.user
            img.save()
            messages.success(request, 'Gallery image uploaded successfully.')
            return redirect('gallery')
    else:
        form = GalleryUploadForm()
    return render(request, 'admin_panel/gallery_upload.html', {'form': form})


# ─── Trigger Scrape (Admin) ──────────────────────────────────────────────

@require_admin
def trigger_scrape(request):
    """Manually trigger price scraping."""
    try:
        from .scraper import scrape_cardamom_prices, get_latest_prices_fallback
        today = date.today()
        prices_data = scrape_cardamom_prices()
        if not prices_data:
            prices_data = get_latest_prices_fallback()

        CardamomPrice.objects.filter(date=today).delete()
        count = 0
        for pd in prices_data:
            CardamomPrice.objects.create(
                market=pd.get('market', 'Unknown'),
                grade=pd.get('grade', 'other'),
                min_price=pd.get('min_price'),
                max_price=pd.get('max_price'),
                modal_price=pd.get('modal_price'),
                unit=pd.get('unit', 'per kg'),
                date=pd.get('date', today),
                raw_data=pd.get('raw_data', ''),
            )
            count += 1
        messages.success(request, f'Prices updated! {count} entries saved for {today}.')
    except Exception as e:
        messages.error(request, f'Scrape failed: {str(e)}')

    return redirect('admin_dashboard')


@require_admin
def admin_districts(request):
    districts = District.objects.all()
    if request.method == 'POST':
        form = DistrictForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'District added successfully.')
            return redirect('admin_districts')
    else:
        form = DistrictForm()
    
    return render(request, 'admin_panel/dashboard_districts.html', {
        'districts': districts,
        'form': form
    })


@require_admin
def delete_district(request, district_id):
    district = get_object_or_404(District, id=district_id)
    district.delete()
    messages.success(request, 'District deleted.')
    return redirect('admin_districts')

