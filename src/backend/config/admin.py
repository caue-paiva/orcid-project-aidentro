"""
Django admin configuration for ORCID Research Platform models
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import (
    User, Institution, Affiliation, Work, WorkAuthor, Funding,
    ResearchArea, UserResearchArea, Citation, UserMetrics,
    CollaborationNetwork, CitationTimeSeries, APIUsageLog
)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin configuration for User model"""
    
    list_display = [
        'username', 'orcid_id', 'display_name', 'email', 
        'profile_public', 'last_orcid_sync', 'date_joined'
    ]
    list_filter = [
        'profile_public', 'show_publications', 'show_affiliations',
        'is_staff', 'is_active', 'date_joined'
    ]
    search_fields = ['username', 'email', 'orcid_id', 'display_name']
    readonly_fields = ['id', 'date_joined', 'last_login', 'last_orcid_sync']
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('ORCID Information', {
            'fields': ('orcid_id', 'orcid_access_token', 'orcid_refresh_token', 'orcid_token_expires_at')
        }),
        ('Profile Information', {
            'fields': ('display_name', 'biography', 'profile_picture_url', 'website_url', 'social_media_accounts')
        }),
        ('Privacy Settings', {
            'fields': ('profile_public', 'show_publications', 'show_affiliations', 'show_metrics')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'last_orcid_sync'),
            'classes': ('collapse',)
        }),
    )
    
    def get_readonly_fields(self, request, obj=None):
        readonly_fields = list(self.readonly_fields)
        if obj:  # editing an existing object
            readonly_fields.extend(['created_at', 'updated_at'])
        return readonly_fields


@admin.register(Institution)
class InstitutionAdmin(admin.ModelAdmin):
    """Admin configuration for Institution model"""
    
    list_display = ['name', 'short_name', 'country', 'city', 'institution_type', 'ror_id']
    list_filter = ['country', 'institution_type', 'established_year']
    search_fields = ['name', 'short_name', 'country', 'city', 'ror_id', 'grid_id']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'short_name', 'country', 'city', 'institution_type')
        }),
        ('External Identifiers', {
            'fields': ('ror_id', 'grid_id', 'wikidata_id')
        }),
        ('Additional Information', {
            'fields': ('website_url', 'logo_url', 'established_year')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Affiliation)
class AffiliationAdmin(admin.ModelAdmin):
    """Admin configuration for Affiliation model"""
    
    list_display = ['user', 'institution', 'affiliation_type', 'title', 'is_current', 'start_date']
    list_filter = ['affiliation_type', 'is_current', 'visibility', 'start_date']
    search_fields = ['user__username', 'institution__name', 'title', 'department']
    readonly_fields = ['id', 'created_at', 'updated_at']
    raw_id_fields = ['user', 'institution']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'institution', 'affiliation_type', 'title', 'department')
        }),
        ('Dates', {
            'fields': ('start_date', 'end_date', 'is_current')
        }),
        ('ORCID Settings', {
            'fields': ('orcid_put_code', 'visibility')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Work)
class WorkAdmin(admin.ModelAdmin):
    """Admin configuration for Work model"""
    
    list_display = ['title_short', 'work_type', 'publication_year', 'citation_count', 'doi']
    list_filter = ['work_type', 'publication_year', 'visibility', 'language']
    search_fields = ['title', 'doi', 'pmid', 'journal_title']
    readonly_fields = ['id', 'created_at', 'updated_at', 'last_citation_update']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'work_type', 'journal_title')
        }),
        ('Publication Details', {
            'fields': ('publication_date', 'publication_year', 'language')
        }),
        ('External Identifiers', {
            'fields': ('doi', 'pmid', 'isbn', 'issn', 'arxiv_id')
        }),
        ('Content', {
            'fields': ('abstract', 'keywords'),
            'classes': ('collapse',)
        }),
        ('URLs', {
            'fields': ('url', 'pdf_url')
        }),
        ('ORCID Settings', {
            'fields': ('orcid_put_code', 'visibility')
        }),
        ('Metrics', {
            'fields': ('citation_count', 'last_citation_update')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def title_short(self, obj):
        return obj.title[:100] + '...' if len(obj.title) > 100 else obj.title
    title_short.short_description = 'Title'


class WorkAuthorInline(admin.TabularInline):
    """Inline admin for WorkAuthor"""
    model = WorkAuthor
    extra = 1
    readonly_fields = ['created_at']
    raw_id_fields = ['user']


@admin.register(WorkAuthor)
class WorkAuthorAdmin(admin.ModelAdmin):
    """Admin configuration for WorkAuthor model"""
    
    list_display = ['name', 'work_title_short', 'author_order', 'is_corresponding', 'orcid_id']
    list_filter = ['is_corresponding', 'author_order']
    search_fields = ['name', 'orcid_id', 'email', 'work__title']
    readonly_fields = ['id', 'created_at']
    raw_id_fields = ['work', 'user']
    
    def work_title_short(self, obj):
        return obj.work.title[:50] + '...' if len(obj.work.title) > 50 else obj.work.title
    work_title_short.short_description = 'Work'


@admin.register(Funding)
class FundingAdmin(admin.ModelAdmin):
    """Admin configuration for Funding model"""
    
    list_display = ['title', 'user', 'funding_type', 'organization_name', 'amount', 'start_date']
    list_filter = ['funding_type', 'organization_country', 'currency', 'visibility']
    search_fields = ['title', 'organization_name', 'grant_number', 'user__username']
    readonly_fields = ['id', 'created_at', 'updated_at']
    raw_id_fields = ['user']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'title', 'funding_type')
        }),
        ('Organization', {
            'fields': ('organization_name', 'organization_country')
        }),
        ('Grant Details', {
            'fields': ('grant_number', 'amount', 'currency')
        }),
        ('Dates', {
            'fields': ('start_date', 'end_date')
        }),
        ('Additional Information', {
            'fields': ('description', 'url')
        }),
        ('ORCID Settings', {
            'fields': ('orcid_put_code', 'visibility')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ResearchArea)
class ResearchAreaAdmin(admin.ModelAdmin):
    """Admin configuration for ResearchArea model"""
    
    list_display = ['name', 'parent', 'subject_scheme', 'created_at']
    list_filter = ['subject_scheme', 'parent']
    search_fields = ['name', 'description', 'subject_scheme']
    readonly_fields = ['id', 'created_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'parent')
        }),
        ('External Classification', {
            'fields': ('subject_scheme', 'subject_scheme_uri')
        }),
        ('Timestamp', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


@admin.register(UserResearchArea)
class UserResearchAreaAdmin(admin.ModelAdmin):
    """Admin configuration for UserResearchArea model"""
    
    list_display = ['user', 'research_area', 'is_primary', 'created_at']
    list_filter = ['is_primary', 'research_area__parent']
    search_fields = ['user__username', 'research_area__name']
    readonly_fields = ['id', 'created_at']
    raw_id_fields = ['user', 'research_area']


@admin.register(Citation)
class CitationAdmin(admin.ModelAdmin):
    """Admin configuration for Citation model"""
    
    list_display = ['citing_work_short', 'cited_work_short', 'source', 'discovered_at']
    list_filter = ['source', 'discovered_at']
    search_fields = ['citing_work__title', 'cited_work__title']
    readonly_fields = ['id', 'discovered_at']
    raw_id_fields = ['citing_work', 'cited_work']
    
    def citing_work_short(self, obj):
        return obj.citing_work.title[:50] + '...' if len(obj.citing_work.title) > 50 else obj.citing_work.title
    citing_work_short.short_description = 'Citing Work'
    
    def cited_work_short(self, obj):
        return obj.cited_work.title[:50] + '...' if len(obj.cited_work.title) > 50 else obj.cited_work.title
    cited_work_short.short_description = 'Cited Work'


@admin.register(UserMetrics)
class UserMetricsAdmin(admin.ModelAdmin):
    """Admin configuration for UserMetrics model"""
    
    list_display = [
        'user', 'total_publications', 'total_citations', 'h_index',
        'i10_index', 'last_calculated'
    ]
    list_filter = ['calculation_version', 'last_calculated']
    search_fields = ['user__username', 'user__orcid_id']
    readonly_fields = ['id', 'last_calculated']
    raw_id_fields = ['user']
    
    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Publication Metrics', {
            'fields': ('total_publications', 'total_citations', 'h_index', 'i10_index')
        }),
        ('Career Metrics', {
            'fields': ('years_active', 'first_publication_year', 'last_publication_year')
        }),
        ('Impact Metrics', {
            'fields': ('avg_citations_per_paper', 'max_citations_single_paper')
        }),
        ('Collaboration Metrics', {
            'fields': ('total_collaborators', 'total_institutions', 'total_countries')
        }),
        ('System Information', {
            'fields': ('last_calculated', 'calculation_version'),
            'classes': ('collapse',)
        }),
    )


@admin.register(CollaborationNetwork)
class CollaborationNetworkAdmin(admin.ModelAdmin):
    """Admin configuration for CollaborationNetwork model"""
    
    list_display = ['user1', 'user2', 'total_collaborations', 'first_collaboration_date', 'last_collaboration_date']
    list_filter = ['total_collaborations', 'first_collaboration_date']
    search_fields = ['user1__username', 'user2__username']
    readonly_fields = ['id', 'created_at', 'updated_at']
    raw_id_fields = ['user1', 'user2']
    filter_horizontal = ['shared_works']


@admin.register(CitationTimeSeries)
class CitationTimeSeriesAdmin(admin.ModelAdmin):
    """Admin configuration for CitationTimeSeries model"""
    
    list_display = ['user', 'year', 'citations_count', 'created_at']
    list_filter = ['year', 'created_at']
    search_fields = ['user__username', 'user__orcid_id']
    readonly_fields = ['id', 'created_at', 'updated_at']
    raw_id_fields = ['user']
    
    fieldsets = (
        ('Citation Data', {
            'fields': ('user', 'year', 'citations_count')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


@admin.register(APIUsageLog)
class APIUsageLogAdmin(admin.ModelAdmin):
    """Admin configuration for APIUsageLog model"""
    
    list_display = ['endpoint', 'method', 'user', 'ip_address', 'status_code', 'response_time_ms', 'timestamp']
    list_filter = ['method', 'status_code', 'endpoint', 'timestamp']
    search_fields = ['endpoint', 'user__username', 'ip_address', 'user_agent']
    readonly_fields = ['id', 'timestamp']
    raw_id_fields = ['user']
    
    date_hierarchy = 'timestamp'
    
    fieldsets = (
        ('Request Information', {
            'fields': ('user', 'ip_address', 'endpoint', 'method', 'user_agent')
        }),
        ('Response Information', {
            'fields': ('status_code', 'response_time_ms')
        }),
        ('Rate Limiting', {
            'fields': ('rate_limit_key', 'requests_in_window')
        }),
        ('Timestamp', {
            'fields': ('timestamp',)
        }),
    )


# Enhance Work admin with author inline
WorkAdmin.inlines = [WorkAuthorInline] 