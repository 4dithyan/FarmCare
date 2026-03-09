from django.contrib import admin
from .models import (
    UserProfile, CardamomPrice, GalleryImage, DiseaseRecommendation,
    AIReport, SoilTestRequest, Announcement, TeamMember
)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'phone', 'location', 'farm_size', 'created_at']
    list_filter = ['role']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'location']


@admin.register(CardamomPrice)
class CardamomPriceAdmin(admin.ModelAdmin):
    list_display = ['market', 'grade', 'min_price', 'max_price', 'modal_price', 'unit', 'date']
    list_filter = ['date', 'grade']
    search_fields = ['market']
    date_hierarchy = 'date'


@admin.register(GalleryImage)
class GalleryImageAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'is_featured', 'uploaded_by', 'created_at']
    list_filter = ['category', 'is_featured']
    search_fields = ['title', 'caption']


@admin.register(DiseaseRecommendation)
class DiseaseRecommendationAdmin(admin.ModelAdmin):
    list_display = ['disease_name', 'severity', 'updated_at']
    list_filter = ['severity']
    search_fields = ['disease_name']


@admin.register(AIReport)
class AIReportAdmin(admin.ModelAdmin):
    list_display = ['farmer', 'disease_detected', 'confidence_level', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['farmer__username', 'disease_detected']
    date_hierarchy = 'created_at'
    readonly_fields = ['gemini_response', 'created_at', 'updated_at']


@admin.register(SoilTestRequest)
class SoilTestRequestAdmin(admin.ModelAdmin):
    list_display = ['farmer', 'farm_location', 'farm_size', 'status', 'requested_at', 'scheduled_date']
    list_filter = ['status', 'requested_at']
    search_fields = ['farmer__username', 'farm_location']


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ['title', 'posted_by', 'is_active', 'created_at']
    list_filter = ['is_active']


@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ['name', 'role', 'order']
    ordering = ['order']
