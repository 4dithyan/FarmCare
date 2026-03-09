from django.urls import path
from . import views

urlpatterns = [
    # Public
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('gallery/', views.gallery, name='gallery'),
    path('api/prices/', views.get_prices_api, name='prices_api'),

    # Auth
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),

    # Farmer
    path('farmer/dashboard/', views.farmer_dashboard, name='farmer_dashboard'),
    path('farmer/ai-detect/', views.ai_detect, name='ai_detect'),
    path('farmer/report/<int:report_id>/', views.report_detail, name='report_detail'),
    path('farmer/report/<int:report_id>/download/', views.download_report, name='download_report'),
    path('farmer/history/', views.history, name='history'),
    path('farmer/soil-request/', views.soil_request, name='soil_request'),

    # Admin Panel
    path('admin-panel/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-panel/farmers/', views.admin_farmers, name='admin_farmers'),
    path('admin-panel/disease-reports/', views.admin_disease_reports, name='admin_disease_reports'),
    path('admin-panel/soil-requests/', views.admin_soil_requests, name='admin_soil_requests'),
    path('admin-panel/soil-requests/<int:request_id>/update/', views.admin_update_soil_request, name='admin_update_soil'),
    path('admin-panel/gallery/upload/', views.admin_gallery_upload, name='admin_gallery_upload'),
    path('admin-panel/districts/', views.admin_districts, name='admin_districts'),
    path('admin-panel/districts/<int:district_id>/delete/', views.delete_district, name='delete_district'),
    path('admin-panel/trigger-scrape/', views.trigger_scrape, name='trigger_scrape'),
]
