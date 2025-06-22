"""
Django management command to populate a user with ORCID data and citations
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.utils import timezone
from datetime import datetime, date
import json
import time
import random

# Import our models
from config.models import (
    User, Institution, Affiliation, Work, WorkAuthor, 
    Funding, ResearchArea, UserResearchArea, Citation, 
    UserMetrics, CitationTimeSeries
)

# Import ORCID and CrossRef API clients
from integrations.orcid_api import ORCIDAPIClient
from integrations.crossref_api import PublicationAPIClient

User = get_user_model()


class Command(BaseCommand):
    help = 'Populate a user with ORCID data and citations'

    def add_arguments(self, parser):
        parser.add_argument(
            '--orcid-id',
            type=str,
            required=True,
            help='ORCID ID to fetch data for (e.g., 0009-0007-8094-7155)'
        )
        parser.add_argument(
            '--username',
            type=str,
            help='Username for the user (will be generated from ORCID if not provided)'
        )
        parser.add_argument(
            '--email',
            type=str,
            help='Email for the user (optional)'
        )
        parser.add_argument(
            '--password',
            type=str,
            default='testuser123',
            help='Password for the user (default: testuser123)'
        )
        parser.add_argument(
            '--max-publications',
            type=int,
            default=10,
            help='Maximum number of publications to process (default: 10)'
        )
        parser.add_argument(
            '--skip-citations',
            action='store_true',
            help='Skip fetching citation data (faster but less complete)'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force update if user already exists'
        )

    def handle(self, *args, **options):
        # Support both command-line and programmatic calls
        orcid_id = options.get('orcid_id') or options.get('orcid-id')
        username = options.get('username')
        email = options.get('email')
        password = options.get('password', 'testuser123')
        max_publications = options.get('max_publications', 10)
        skip_citations = options.get('skip_citations', False)
        force = options.get('force', False)

        if not orcid_id:
            self.stdout.write(
                self.style.ERROR('❌ ORCID ID is required!')
            )
            return

        self.stdout.write(f'🔍 Fetching data for ORCID ID: {orcid_id}')

        try:
            # Initialize API clients
            orcid_client = ORCIDAPIClient(access_token='', orcid_id=orcid_id)
            crossref_client = PublicationAPIClient()

            # Get user identity and profile data
            self.stdout.write('📋 Fetching ORCID profile data...')
            user_identity = orcid_client.get_user_identity_info()
            person_info = orcid_client.get_researcher_person_info()
            works_data = orcid_client.get_researcher_works()
            employments_data = orcid_client.get_researcher_employments()
            education_data = orcid_client.get_researcher_education()
            funding_data = orcid_client.get_researcher_funding()

            # Generate username if not provided
            if not username:
                name_parts = user_identity.get('name', 'User').lower().split()
                username = f"{''.join(name_parts[:2])}_{orcid_id.replace('-', '')[-4:]}"

            # Check if user exists
            user_exists = User.objects.filter(orcid_id=orcid_id).exists()
            if user_exists and not force:
                self.stdout.write(
                    self.style.WARNING(f'User with ORCID ID {orcid_id} already exists! Use --force to update.')
                )
                return

            with transaction.atomic():
                # Create or update user
                if user_exists:
                    user = User.objects.get(orcid_id=orcid_id)
                    self.stdout.write(f'📝 Updating existing user: {user.username}')
                else:
                    user = User.objects.create_user(
                        username=username,
                        email=email or f"{username}@example.com",
                        password=password
                    )
                    self.stdout.write(f'👤 Created new user: {username}')

                # Update user profile with ORCID data
                user.orcid_id = orcid_id
                user.display_name = user_identity.get('name', '')
                user.first_name = person_info.get('name', {}).get('given-names', {}).get('value', '') if person_info.get('name') else ''
                user.last_name = person_info.get('name', {}).get('family-name', {}).get('value', '') if person_info.get('name') else ''
                user.last_orcid_sync = timezone.now()
                
                # Extract biography from person info
                if person_info.get('biography') and person_info['biography'].get('content'):
                    user.biography = person_info['biography']['content']
                
                user.save()

                # Process institutions and affiliations
                self.stdout.write('🏢 Processing affiliations...')
                self._process_affiliations(user, employments_data, 'employment')
                self._process_affiliations(user, education_data, 'education')

                # Process funding
                self.stdout.write('💰 Processing funding...')
                self._process_funding(user, funding_data)

                # Process publications
                self.stdout.write('📚 Processing publications...')
                publications_created = self._process_publications(
                    user, works_data, crossref_client, max_publications, skip_citations
                )

                # Get real citation analysis using the existing ORCID API function
                if not skip_citations and publications_created > 0:
                    self.stdout.write('📊 Fetching real citation analysis data...')
                    citation_analysis = orcid_client.get_citation_analysis(
                        years_back=10, 
                        max_publications=max_publications,
                        timeout_per_request=15
                    )
                    
                    # Store citation time series from real data
                    self._store_citation_analysis(user, citation_analysis)
                    
                    self.stdout.write(f'   📈 Citation analysis: {citation_analysis["total_citations"]} total citations')
                    self.stdout.write(f'   📚 Publications analyzed: {citation_analysis["total_publications"]}')
                    self.stdout.write(f'   ⏱️  Analysis time: {citation_analysis["analysis_time_seconds"]}s')

                # Calculate and store user metrics
                self.stdout.write('📊 Calculating user metrics...')
                self._calculate_user_metrics(user)

                self.stdout.write(
                    self.style.SUCCESS(f'✅ Successfully populated user data!')
                )
                self.stdout.write(f'   👤 User: {user.username} ({user.display_name})')
                self.stdout.write(f'   🆔 ORCID: {user.orcid_id}')
                self.stdout.write(f'   📚 Publications: {publications_created}')
                self.stdout.write(f'   🏢 Affiliations: {user.affiliations.count()}')
                self.stdout.write(f'   💰 Funding: {user.funding.count()}')

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error populating user data: {e}')
            )
            raise

    def _process_affiliations(self, user, affiliations_data, affiliation_type):
        """Process employment or education affiliations"""
        if not affiliations_data or 'affiliation-group' not in affiliations_data:
            return

        for group in affiliations_data['affiliation-group']:
            for summary in group.get('summaries', []):
                try:
                    org_name = summary.get('organization', {}).get('name', 'Unknown Organization')
                    
                    # Create or get institution
                    institution, created = Institution.objects.get_or_create(
                        name=org_name,
                        defaults={
                            'country': summary.get('organization', {}).get('address', {}).get('country', ''),
                            'city': summary.get('organization', {}).get('address', {}).get('city', ''),
                        }
                    )

                    # Parse dates
                    start_date = self._parse_orcid_date(summary.get('start-date'))
                    end_date = self._parse_orcid_date(summary.get('end-date'))

                    # Create affiliation
                    Affiliation.objects.get_or_create(
                        user=user,
                        institution=institution,
                        affiliation_type=affiliation_type,
                        defaults={
                            'title': summary.get('role-title', '') or summary.get('department-name', ''),
                            'department': summary.get('department-name', ''),
                            'start_date': start_date,
                            'end_date': end_date,
                            'is_current': end_date is None,
                            'orcid_put_code': str(summary.get('put-code', '')),
                        }
                    )

                except Exception as e:
                    self.stdout.write(f'⚠️  Warning: Could not process affiliation: {e}')
                    continue

    def _process_funding(self, user, funding_data):
        """Process funding information"""
        if not funding_data or 'group' not in funding_data:
            return

        for group in funding_data['group']:
            for summary in group.get('funding-summary', []):
                try:
                    org_name = summary.get('organization', {}).get('name', 'Unknown Funder')
                    
                    # Parse dates
                    start_date = self._parse_orcid_date(summary.get('start-date'))
                    end_date = self._parse_orcid_date(summary.get('end-date'))

                    Funding.objects.get_or_create(
                        user=user,
                        title=summary.get('title', {}).get('title', {}).get('value', 'Unknown Grant'),
                        defaults={
                            'funding_type': summary.get('type', 'grant'),
                            'organization_name': org_name,
                            'organization_country': summary.get('organization', {}).get('address', {}).get('country', ''),
                            'start_date': start_date,
                            'end_date': end_date,
                            'url': summary.get('url', {}).get('value', '') if summary.get('url') else '',
                            'orcid_put_code': str(summary.get('put-code', '')),
                        }
                    )

                except Exception as e:
                    self.stdout.write(f'⚠️  Warning: Could not process funding: {e}')
                    continue

    def _process_publications(self, user, works_data, crossref_client, max_publications, skip_citations):
        """Process publications and citations"""
        if not works_data or 'group' not in works_data:
            return 0

        publications_created = 0
        processed_count = 0

        for group in works_data['group']:
            if processed_count >= max_publications:
                break

            for work_summary in group.get('work-summary', []):
                if processed_count >= max_publications:
                    break

                try:
                    # Extract DOI
                    doi = None
                    external_ids = work_summary.get('external-ids', {}).get('external-id', [])
                    for ext_id in external_ids:
                        if ext_id.get('external-id-type') == 'doi':
                            doi = ext_id.get('external-id-value')
                            break

                    if not doi:
                        continue  # Skip works without DOI

                    # Get publication date
                    pub_date = work_summary.get('publication-date')
                    pub_year = None
                    publication_date = None
                    
                    if pub_date and pub_date.get('year'):
                        pub_year = int(pub_date['year']['value'])
                        month = int(pub_date.get('month', {}).get('value', 1)) if pub_date.get('month') else 1
                        day = int(pub_date.get('day', {}).get('value', 1)) if pub_date.get('day') else 1
                        publication_date = date(pub_year, month, day)

                    # Create work
                    work, created = Work.objects.get_or_create(
                        doi=doi,
                        defaults={
                            'title': work_summary.get('title', {}).get('title', {}).get('value', 'Unknown Title'),
                            'work_type': work_summary.get('type', 'journal-article'),
                            'journal_title': work_summary.get('journal-title', {}).get('value', '') if work_summary.get('journal-title') else '',
                            'publication_date': publication_date,
                            'publication_year': pub_year,
                            'url': work_summary.get('url', {}).get('value', '') if work_summary.get('url') else '',
                            'orcid_put_code': str(work_summary.get('put-code', '')),
                        }
                    )

                    if created:
                        publications_created += 1

                    # Create work author relationship
                    WorkAuthor.objects.get_or_create(
                        work=work,
                        user=user,
                        defaults={
                            'name': user.display_name or f"{user.first_name} {user.last_name}".strip(),
                            'orcid_id': user.orcid_id,
                            'author_order': 1,  # We don't have order info from ORCID summary
                        }
                    )

                    # Note: Citation data will be fetched in bulk using get_citation_analysis()
                    # This provides more accurate temporal citation data

                    processed_count += 1

                except Exception as e:
                    self.stdout.write(f'⚠️  Warning: Could not process publication: {e}')
                    continue

        return publications_created

    def _calculate_user_metrics(self, user):
        """Calculate and store user metrics"""
        works = Work.objects.filter(authors__user=user)
        total_publications = works.count()
        
        # Get total citations from citation time series (more accurate)
        citation_timeseries = CitationTimeSeries.objects.filter(user=user)
        total_citations = sum(cts.citations_count for cts in citation_timeseries)
        
        # If no time series data, fall back to work citation counts
        if total_citations == 0:
            total_citations = sum(work.citation_count for work in works)
            citation_counts = sorted([work.citation_count for work in works], reverse=True)
        else:
            # For h-index calculation, we need individual paper citation counts
            # This is a simplified approach - in reality we'd need per-paper citation data
            citation_counts = sorted([work.citation_count for work in works], reverse=True)
        
        # Calculate h-index approximation
        h_index = 0
        for i, citations in enumerate(citation_counts, 1):
            if citations >= i:
                h_index = i
            else:
                break

        # Calculate i10-index (papers with at least 10 citations)
        i10_index = sum(1 for count in citation_counts if count >= 10)

        # Calculate career span
        pub_years = [work.publication_year for work in works if work.publication_year]
        first_pub_year = min(pub_years) if pub_years else None
        last_pub_year = max(pub_years) if pub_years else None
        years_active = (last_pub_year - first_pub_year + 1) if first_pub_year and last_pub_year else 0

        # Update or create metrics
        metrics, created = UserMetrics.objects.get_or_create(
            user=user,
            defaults={
                'total_publications': total_publications,
                'total_citations': total_citations,
                'h_index': h_index,
                'i10_index': i10_index,
                'years_active': years_active,
                'first_publication_year': first_pub_year,
                'last_publication_year': last_pub_year,
                'avg_citations_per_paper': total_citations / total_publications if total_publications > 0 else 0,
                'max_citations_single_paper': max(citation_counts) if citation_counts else 0,
            }
        )

        if not created:
            # Update existing metrics
            metrics.total_publications = total_publications
            metrics.total_citations = total_citations
            metrics.h_index = h_index
            metrics.i10_index = i10_index
            metrics.years_active = years_active
            metrics.first_publication_year = first_pub_year
            metrics.last_publication_year = last_pub_year
            metrics.avg_citations_per_paper = total_citations / total_publications if total_publications > 0 else 0
            metrics.max_citations_single_paper = max(citation_counts) if citation_counts else 0
            metrics.save()

    def _store_citation_analysis(self, user, citation_analysis):
        """Store real citation analysis data from ORCID API"""
        # Clear existing time series data
        CitationTimeSeries.objects.filter(user=user).delete()
        
        # Store the real yearly citation data
        for yearly_data in citation_analysis.get('yearly_data', []):
            CitationTimeSeries.objects.create(
                user=user,
                year=yearly_data['year'],
                citations_count=yearly_data['citations']
            )
        
        self.stdout.write(f'   💾 Stored {len(citation_analysis.get("yearly_data", []))} years of citation data')

    def _parse_orcid_date(self, date_info):
        """Parse ORCID date format to Python date"""
        if not date_info:
            return None
        
        try:
            year = int(date_info.get('year', {}).get('value', 0))
            month = int(date_info.get('month', {}).get('value', 1))
            day = int(date_info.get('day', {}).get('value', 1))
            
            if year > 0:
                return date(year, month, day)
        except (ValueError, TypeError):
            pass
        
        return None 