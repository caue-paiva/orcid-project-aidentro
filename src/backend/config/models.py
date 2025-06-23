"""
Database models for ORCID Research Platform
"""

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
import uuid


class User(AbstractUser):
    """
    Extended User model with ORCID integration
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(blank=True, null=True)  # Override AbstractUser email to allow null
    orcid_id = models.CharField(
        max_length=19,
        unique=True,
        null=True,
        blank=True,
        validators=[
            RegexValidator(
                regex=r'^\d{4}-\d{4}-\d{4}-\d{3}[\dX]$',
                message='Invalid ORCID ID format. Should be: 0000-0000-0000-000X'
            )
        ],
        help_text='16-digit ORCID identifier'
    )
    orcid_access_token = models.TextField(null=True, blank=True, help_text='Encrypted ORCID access token')
    orcid_refresh_token = models.TextField(null=True, blank=True, help_text='Encrypted ORCID refresh token')
    orcid_token_expires_at = models.DateTimeField(null=True, blank=True)
    
    # Profile information
    display_name = models.CharField(max_length=255, blank=True)
    biography = models.TextField(blank=True)
    profile_picture_url = models.URLField(blank=True)
    website_url = models.URLField(blank=True)
    
    # Social media accounts
    social_media_accounts = models.JSONField(
        default=list, 
        blank=True,
        help_text='List of social media accounts: [{"platform": "twitter", "username": "johndoe", "url": "https://twitter.com/johndoe"}]'
    )
    
    # Privacy settings
    profile_public = models.BooleanField(default=True)
    show_publications = models.BooleanField(default=True)
    show_affiliations = models.BooleanField(default=True)
    show_metrics = models.BooleanField(default=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_orcid_sync = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'users'
        indexes = [
            models.Index(fields=['orcid_id']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.username} ({self.orcid_id or 'No ORCID'})"


class Institution(models.Model):
    """
    Research institutions and organizations
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=500)
    short_name = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100)
    city = models.CharField(max_length=100, blank=True)
    
    # External identifiers
    ror_id = models.CharField(max_length=200, blank=True, help_text='Research Organization Registry ID')
    grid_id = models.CharField(max_length=200, blank=True, help_text='Global Research Identifier Database ID')
    wikidata_id = models.CharField(max_length=50, blank=True)
    
    # Additional information
    website_url = models.URLField(blank=True)
    logo_url = models.URLField(blank=True)
    established_year = models.IntegerField(null=True, blank=True)
    institution_type = models.CharField(
        max_length=50,
        choices=[
            ('university', 'University'),
            ('research_institute', 'Research Institute'),
            ('government', 'Government Agency'),
            ('company', 'Company'),
            ('hospital', 'Hospital'),
            ('other', 'Other'),
        ],
        default='university'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'institutions'
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['country']),
            models.Index(fields=['ror_id']),
        ]

    def __str__(self):
        return f"{self.name} ({self.country})"


class Affiliation(models.Model):
    """
    User affiliations with institutions (employment, education, etc.)
    """
    AFFILIATION_TYPES = [
        ('employment', 'Employment'),
        ('education', 'Education'),
        ('distinction', 'Distinction'),
        ('invited_position', 'Invited Position'),
        ('membership', 'Membership'),
        ('qualification', 'Qualification'),
        ('service', 'Service'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='affiliations')
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, related_name='affiliations')
    
    affiliation_type = models.CharField(max_length=20, choices=AFFILIATION_TYPES)
    title = models.CharField(max_length=500, help_text='Job title, degree, position, etc.')
    department = models.CharField(max_length=500, blank=True)
    
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    is_current = models.BooleanField(default=False)
    
    # ORCID specific fields
    orcid_put_code = models.CharField(max_length=50, blank=True, help_text='ORCID put-code for this affiliation')
    visibility = models.CharField(
        max_length=20,
        choices=[
            ('public', 'Public'),
            ('limited', 'Limited'),
            ('private', 'Private'),
        ],
        default='public'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'affiliations'
        indexes = [
            models.Index(fields=['user', 'affiliation_type']),
            models.Index(fields=['institution']),
            models.Index(fields=['is_current']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.title} at {self.institution.name}"


class Work(models.Model):
    """
    Research works (publications, datasets, software, etc.)
    """
    WORK_TYPES = [
        ('journal-article', 'Journal Article'),
        ('book-chapter', 'Book Chapter'),
        ('book', 'Book'),
        ('conference-paper', 'Conference Paper'),
        ('dataset', 'Dataset'),
        ('software', 'Software'),
        ('report', 'Report'),
        ('preprint', 'Preprint'),
        ('thesis', 'Thesis'),
        ('patent', 'Patent'),
        ('other', 'Other'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.TextField()
    work_type = models.CharField(max_length=30, choices=WORK_TYPES)
    
    # Publication details
    journal_title = models.CharField(max_length=500, blank=True)
    publication_date = models.DateField(null=True, blank=True)
    publication_year = models.IntegerField(null=True, blank=True)
    
    # External identifiers
    doi = models.CharField(max_length=200, blank=True, unique=True, null=True)
    pmid = models.CharField(max_length=20, blank=True, help_text='PubMed ID')
    isbn = models.CharField(max_length=20, blank=True)
    issn = models.CharField(max_length=20, blank=True)
    arxiv_id = models.CharField(max_length=50, blank=True)
    
    # Content
    abstract = models.TextField(blank=True)
    keywords = models.JSONField(default=list, blank=True)
    language = models.CharField(max_length=10, default='en')
    
    # URLs
    url = models.URLField(blank=True, help_text='Primary URL for the work')
    pdf_url = models.URLField(blank=True)
    
    # ORCID specific fields
    orcid_put_code = models.CharField(max_length=50, blank=True)
    visibility = models.CharField(
        max_length=20,
        choices=[
            ('public', 'Public'),
            ('limited', 'Limited'),
            ('private', 'Private'),
        ],
        default='public'
    )
    
    # Metrics (cached from external APIs)
    citation_count = models.IntegerField(default=0)
    last_citation_update = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'works'
        indexes = [
            models.Index(fields=['doi']),
            models.Index(fields=['publication_year']),
            models.Index(fields=['work_type']),
            models.Index(fields=['citation_count']),
        ]

    def __str__(self):
        return f"{self.title[:100]}{'...' if len(self.title) > 100 else ''}"


class WorkAuthor(models.Model):
    """
    Authors associated with works (many-to-many relationship with additional data)
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    work = models.ForeignKey(Work, on_delete=models.CASCADE, related_name='authors')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='authored_works', null=True, blank=True)
    
    # Author information (for non-registered users)
    name = models.CharField(max_length=500)
    orcid_id = models.CharField(max_length=19, blank=True)
    email = models.EmailField(blank=True)
    affiliation_name = models.CharField(max_length=500, blank=True)
    
    # Authorship details
    author_order = models.IntegerField(help_text='Order of authorship (1 = first author)')
    is_corresponding = models.BooleanField(default=False)
    contribution_roles = models.JSONField(default=list, blank=True, help_text='CRediT taxonomy roles')
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'work_authors'
        unique_together = [['work', 'author_order']]
        indexes = [
            models.Index(fields=['work', 'author_order']),
            models.Index(fields=['user']),
            models.Index(fields=['orcid_id']),
        ]

    def __str__(self):
        return f"{self.name} - {self.work.title[:50]}"


class Funding(models.Model):
    """
    Research funding and grants
    """
    FUNDING_TYPES = [
        ('grant', 'Grant'),
        ('contract', 'Contract'),
        ('award', 'Award'),
        ('fellowship', 'Fellowship'),
        ('salary-award', 'Salary Award'),
        ('other', 'Other'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='funding')
    
    title = models.CharField(max_length=500)
    funding_type = models.CharField(max_length=20, choices=FUNDING_TYPES)
    
    # Funding organization
    organization_name = models.CharField(max_length=500)
    organization_country = models.CharField(max_length=100, blank=True)
    
    # Grant details
    grant_number = models.CharField(max_length=200, blank=True)
    amount = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    currency = models.CharField(max_length=3, blank=True, help_text='ISO currency code')
    
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    
    description = models.TextField(blank=True)
    url = models.URLField(blank=True)
    
    # ORCID specific fields
    orcid_put_code = models.CharField(max_length=50, blank=True)
    visibility = models.CharField(
        max_length=20,
        choices=[
            ('public', 'Public'),
            ('limited', 'Limited'),
            ('private', 'Private'),
        ],
        default='public'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'funding'
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['organization_name']),
            models.Index(fields=['start_date']),
        ]

    def __str__(self):
        return f"{self.title} - {self.organization_name}"


class ResearchArea(models.Model):
    """
    Research areas and fields of study
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    
    # External identifiers
    subject_scheme = models.CharField(max_length=100, blank=True, help_text='Classification scheme (e.g., OECD FOS)')
    subject_scheme_uri = models.URLField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'research_areas'
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['parent']),
        ]

    def __str__(self):
        return self.name


class UserResearchArea(models.Model):
    """
    Research areas associated with users
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='research_areas')
    research_area = models.ForeignKey(ResearchArea, on_delete=models.CASCADE, related_name='users')
    is_primary = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'user_research_areas'
        unique_together = [['user', 'research_area']]

    def __str__(self):
        return f"{self.user.username} - {self.research_area.name}"


class Citation(models.Model):
    """
    Citation relationships between works
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    citing_work = models.ForeignKey(Work, on_delete=models.CASCADE, related_name='citations_made')
    cited_work = models.ForeignKey(Work, on_delete=models.CASCADE, related_name='citations_received')
    
    # Citation context
    citation_context = models.TextField(blank=True, help_text='Text around the citation')
    page_number = models.CharField(max_length=20, blank=True)
    
    # Source of citation data
    source = models.CharField(
        max_length=50,
        choices=[
            ('crossref', 'CrossRef'),
            ('pubmed', 'PubMed'),
            ('semantic_scholar', 'Semantic Scholar'),
            ('google_scholar', 'Google Scholar'),
            ('manual', 'Manual Entry'),
        ],
        default='crossref'
    )
    
    discovered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'citations'
        unique_together = [['citing_work', 'cited_work']]
        indexes = [
            models.Index(fields=['cited_work']),
            models.Index(fields=['citing_work']),
            models.Index(fields=['discovered_at']),
        ]

    def __str__(self):
        return f"Citation: {self.citing_work.title[:50]} → {self.cited_work.title[:50]}"


class UserMetrics(models.Model):
    """
    Cached research metrics for users
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='metrics')
    
    # Publication metrics
    total_publications = models.IntegerField(default=0)
    total_citations = models.IntegerField(default=0)
    h_index = models.IntegerField(default=0)
    i10_index = models.IntegerField(default=0)
    
    # Career metrics
    years_active = models.IntegerField(default=0)
    first_publication_year = models.IntegerField(null=True, blank=True)
    last_publication_year = models.IntegerField(null=True, blank=True)
    
    # Impact metrics
    avg_citations_per_paper = models.FloatField(default=0.0)
    max_citations_single_paper = models.IntegerField(default=0)
    
    # Collaboration metrics
    total_collaborators = models.IntegerField(default=0)
    total_institutions = models.IntegerField(default=0)
    total_countries = models.IntegerField(default=0)
    
    # Update tracking
    last_calculated = models.DateTimeField(auto_now=True)
    calculation_version = models.CharField(max_length=20, default='1.0')

    class Meta:
        db_table = 'user_metrics'

    def __str__(self):
        return f"Metrics for {self.user.username}: {self.total_publications} pubs, {self.total_citations} cites, h={self.h_index}"


class CollaborationNetwork(models.Model):
    """
    Research collaboration networks between users
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='collaborations_as_user1')
    user2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='collaborations_as_user2')
    
    # Collaboration strength
    total_collaborations = models.IntegerField(default=1)
    first_collaboration_date = models.DateField()
    last_collaboration_date = models.DateField()
    
    # Shared works
    shared_works = models.ManyToManyField(Work, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'collaboration_networks'
        unique_together = [['user1', 'user2']]
        indexes = [
            models.Index(fields=['user1']),
            models.Index(fields=['user2']),
            models.Index(fields=['total_collaborations']),
        ]

    def __str__(self):
        return f"Collaboration: {self.user1.username} ↔ {self.user2.username} ({self.total_collaborations} works)"


class CitationTimeSeries(models.Model):
    """
    Simple temporal citation data tracking citations per year for users
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='citation_timeseries')
    year = models.IntegerField()
    citations_count = models.IntegerField(default=0, help_text='Number of citations received in this year')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'citation_timeseries'
        unique_together = [['user', 'year']]
        indexes = [
            models.Index(fields=['user', 'year']),
            models.Index(fields=['year']),
            models.Index(fields=['citations_count']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.year}: {self.citations_count} citations"


class APIUsageLog(models.Model):
    """
    API usage tracking for rate limiting and analytics
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    ip_address = models.GenericIPAddressField()
    
    # Request details
    endpoint = models.CharField(max_length=200)
    method = models.CharField(max_length=10)
    user_agent = models.TextField(blank=True)
    
    # Response details
    status_code = models.IntegerField()
    response_time_ms = models.IntegerField(help_text='Response time in milliseconds')
    
    # Rate limiting
    rate_limit_key = models.CharField(max_length=100, blank=True)
    requests_in_window = models.IntegerField(default=1)
    
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'api_usage_logs'
        indexes = [
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['ip_address', 'timestamp']),
            models.Index(fields=['endpoint']),
            models.Index(fields=['rate_limit_key', 'timestamp']),
        ]

    def __str__(self):
        return f"{self.method} {self.endpoint} - {self.status_code} ({self.timestamp})" 