"""
Seed script to populate FarmCare with initial demo data.
Run: python seed_data.py
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'farmcare.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.contrib.auth.models import User
from core.models import UserProfile, DiseaseRecommendation, CardamomPrice, Announcement, TeamMember
from core.scraper import get_latest_prices_fallback
from datetime import date

print("🌱 Seeding FarmCare database...")

# ── Admin user ──────────────────────────────────────────────
if not User.objects.filter(username='admin').exists():
    admin = User.objects.create_superuser('admin', 'admin@gmail.com', 'admin123')
    admin.first_name = 'Admin'
    admin.last_name = 'FarmCare'
    admin.save()
    UserProfile.objects.create(user=admin, role='admin', phone='9778238064', location='Kerala')
    print("✅ Admin user created (username: admin, password: admin123)")
else:
    print("ℹ️  Admin user already exists")

# ── Sample farmer ───────────────────────────────────────────
if not User.objects.filter(username='farmer1').exists():
    farmer = User.objects.create_user('farmer1', 'mailforadithyan@gmail.com', 'farmer123')
    farmer.first_name = 'Rajan'
    farmer.last_name = 'Pillai'
    farmer.save()
    UserProfile.objects.create(
        user=farmer, role='farmer',
        phone='9778238064', location='Idukki, Kerala',
        farm_size=3.5, bio='Third-generation cardamom farmer from Idukki.'
    )
    print("✅ Sample farmer created (username: farmer1, password: farmer123)")

# ── Disease Recommendations ─────────────────────────────────
diseases = [
    {
        'disease_name': 'Katte Disease (Mosaic Virus)',
        'description': 'A viral disease caused by Cardamom Mosaic Virus (CdMV) transmitted by aphids. It is the most devastating disease of cardamom.',
        'symptoms': 'Yellow streaks and mosaic patterns on leaves. Distorted and wrinkled leaves. Stunted plant growth. Reduced yield significantly.',
        'medicine': 'Imidacloprid 17.8% SL (for aphid control), Mineral Oil spray, Dimethoate 30% EC',
        'dosage': 'Imidacloprid: 0.5 ml per liter of water. Mineral Oil: 2% solution. Apply every 21 days during aphid season.',
        'precautions': 'Remove and destroy infected plants immediately. Control aphid vectors with systemic insecticides. Use certified virus-free planting material. Avoid monocropping.',
        'severity': 'critical',
    },
    {
        'disease_name': 'Capsule Rot (Phytophthora)',
        'description': 'Fungal disease caused by Phytophthora meadii. Primarily affects capsules during humid conditions.',
        'symptoms': 'Dark brown to black lesions on capsules and stems. Water-soaked appearance. Rotting of capsules with foul smell. Collar rot at base of plant.',
        'medicine': 'Metalaxyl 8% + Mancozeb 64% WP, Copper Oxychloride 50% WP, Phosphonic Acid (Fosetyl-Al)',
        'dosage': 'Metalaxyl+Mancozeb: 2g per liter. Copper Oxychloride: 3g per liter. Drench the soil and spray capsules.',
        'precautions': 'Improve drainage in the farm. Avoid waterlogging. Remove affected capsules and burn them. Maintain proper plant spacing for aeration.',
        'severity': 'high',
    },
    {
        'disease_name': 'Rhizome Rot (Pythium)',
        'description': 'Soil-borne disease caused by Pythium vexans. Attacks the rhizome and root system.',
        'symptoms': 'Yellowing of lower leaves. Wilting of entire plant. Brown discoloration of rhizome. Foul smell from rotting rhizome.',
        'medicine': 'Metalaxyl 35% WS, Mancozeb 75% WP, Trichoderma viride (Biological control)',
        'dosage': 'Metalaxyl: 1g per liter for soil drench. Trichoderma: 10g per plant mixed with compost.',
        'precautions': 'Use healthy planting materials. Treat planting material with Mancozeb before planting. Improve soil drainage. Avoid excessive irrigation.',
        'severity': 'high',
    },
    {
        'disease_name': 'Leaf Blight (Colletotrichum)',
        'description': 'Fungal disease caused by Colletotrichum gloeosporioides during high humidity.',
        'symptoms': 'Brown or tan spots with yellow margins on leaves. Spots may coalesce to form large blighted areas. Premature defoliation.',
        'medicine': 'Carbendazim 50% WP, Chlorothalonil 75% WP, Mancozeb 75% WP',
        'dosage': 'Carbendazim: 1g per liter. Chlorothalonil: 2g per liter. Spray at 15-day intervals.',
        'precautions': 'Remove and destroy infected leaves. Avoid overhead irrigation. Ensure good air circulation. Apply protective fungicide spray before monsoon.',
        'severity': 'medium',
    },
    {
        'disease_name': 'Thrips Infestation',
        'description': 'Thrips tabaci and Scirtothrips cardamomi are the primary pests. They feed on plant sap causing silvery streaks.',
        'symptoms': 'Silvery streaks on leaves and capsules. Curling and distortion of leaves. Bronzing of leaves. Reduced capsule quality.',
        'medicine': 'Dimethoate 30% EC, Fipronil 5% SC, Spinosad 45% SC, Imidacloprid 17.8% SL',
        'dosage': 'Dimethoate: 2ml per liter. Fipronil: 1.5ml per liter. Spray during early morning or evening.',
        'precautions': 'Monitor regularly during dry season. Avoid pesticide resistance by rotation. Remove plant debris. Use yellow sticky traps for monitoring.',
        'severity': 'medium',
    },
    {
        'disease_name': 'Stem Borer',
        'description': 'Conogethes punctiferalis bores into stems and panicles. Major pest in cardamom plantations.',
        'symptoms': 'Entry holes in stems and panicles. Presence of frass near entry holes. Dead heart in tillers. Wilting of affected shoots.',
        'medicine': 'Chlorpyrifos 20% EC, Quinalphos 25% EC, Malathion 50% EC',
        'dosage': 'Chlorpyrifos: 2.5ml per liter. Apply to stem and panicle region at first sign of attack.',
        'precautions': 'Remove and destroy affected stems immediately. Do not allow dead matter to remain in field. Use pheromone traps for monitoring adult moths.',
        'severity': 'high',
    },
    {
        'disease_name': 'Healthy Plant',
        'description': 'No disease detected. The plant appears to be in good health.',
        'symptoms': 'No visible symptoms of disease or pest infestation.',
        'medicine': 'No treatment required. Continue regular preventive care.',
        'dosage': 'N/A',
        'precautions': 'Continue regular monitoring. Apply preventive fungicide spray before monsoon onset. Maintain proper irrigation and nutrition schedule.',
        'severity': 'low',
    },
]

created_count = 0
for d in diseases:
    obj, created = DiseaseRecommendation.objects.get_or_create(
        disease_name=d['disease_name'],
        defaults=d
    )
    if created:
        created_count += 1

print(f"✅ {created_count} disease recommendations added")

# ── Cardamom Prices ─────────────────────────────────────────
if not CardamomPrice.objects.filter(date=date.today()).exists():
    prices = get_latest_prices_fallback()
    for p in prices:
        CardamomPrice.objects.create(**p)
    print(f"✅ {len(prices)} sample prices added for today")

# ── Announcements ──────────────────────────────────────────
if not Announcement.objects.exists():
    admin_user = User.objects.filter(username='admin').first()
    Announcement.objects.create(
        title='Welcome to FarmCare!',
        content='FarmCare is now live. Farmers can register, upload plant images for AI disease detection, and request soil tests. Welcome to smart farming!',
        posted_by=admin_user,
    )
    Announcement.objects.create(
        title='Cardamom Price Season Update',
        content='Current cardamom prices are strong due to high export demand. Monitor daily prices on our home page. Contact admin for more market insights.',
        posted_by=admin_user,
    )
    print("✅ Announcements created")

# ── Team Members ───────────────────────────────────────────
if not TeamMember.objects.exists():
    TeamMember.objects.bulk_create([
        TeamMember(name='Dr. Suresh Nair', role='Agricultural Scientist', bio='15+ years in spice crop research', order=1),
        TeamMember(name='Priya Menon', role='Technology Lead', bio='AI and AgriTech specialist', order=2),
        TeamMember(name='Rajan Krishnan', role='Field Officer', bio='Cardamom farming expert with hands-on field experience', order=3),
    ])
    print("✅ Team members created")

print("\n🎉 Seed data complete!")
print("\n📋 Login credentials:")
print("   Admin — username: admin, password: admin123")
print("   Farmer — username: farmer1, password: farmer123")
print("\n🚀 Run the server: python manage.py runserver")
