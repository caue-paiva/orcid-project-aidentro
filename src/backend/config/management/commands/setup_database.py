"""
Django management command to set up the database with initial data
Usage: python manage.py setup_database
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from config.models import Institution, ResearchArea
import json


class Command(BaseCommand):
    help = 'Set up the database with initial data for institutions and research areas'

    def add_arguments(self, parser):
        parser.add_argument(
            '--skip-institutions',
            action='store_true',
            help='Skip institution data setup',
        )
        parser.add_argument(
            '--skip-research-areas',
            action='store_true',
            help='Skip research areas setup',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Setting up initial database data...'))

        if not options['skip_institutions']:
            self.setup_institutions()
        
        if not options['skip_research_areas']:
            self.setup_research_areas()

        self.stdout.write(self.style.SUCCESS('Database setup completed successfully!'))

    @transaction.atomic
    def setup_institutions(self):
        """Set up initial institution data"""
        self.stdout.write('Setting up institutions...')
        
        institutions_data = [
            {
                'name': 'Universidade de São Paulo',
                'short_name': 'USP',
                'country': 'Brazil',
                'city': 'São Paulo',
                'ror_id': 'https://ror.org/036rp1748',
                'institution_type': 'university',
                'website_url': 'https://www.usp.br/',
                'established_year': 1934,
            },
            {
                'name': 'Universidade Estadual de Campinas',
                'short_name': 'UNICAMP',
                'country': 'Brazil',
                'city': 'Campinas',
                'ror_id': 'https://ror.org/03yghzc09',
                'institution_type': 'university',
                'website_url': 'https://www.unicamp.br/',
                'established_year': 1966,
            },
            {
                'name': 'Massachusetts Institute of Technology',
                'short_name': 'MIT',
                'country': 'United States',
                'city': 'Cambridge',
                'ror_id': 'https://ror.org/042nb2s44',
                'institution_type': 'university',
                'website_url': 'https://www.mit.edu/',
                'established_year': 1861,
            },
            {
                'name': 'Stanford University',
                'short_name': 'Stanford',
                'country': 'United States',
                'city': 'Stanford',
                'ror_id': 'https://ror.org/00f54p054',
                'institution_type': 'university',
                'website_url': 'https://www.stanford.edu/',
                'established_year': 1885,
            },
            {
                'name': 'University of Oxford',
                'short_name': 'Oxford',
                'country': 'United Kingdom',
                'city': 'Oxford',
                'ror_id': 'https://ror.org/052gg0110',
                'institution_type': 'university',
                'website_url': 'https://www.ox.ac.uk/',
                'established_year': 1096,
            },
            {
                'name': 'University of Cambridge',
                'short_name': 'Cambridge',
                'country': 'United Kingdom',
                'city': 'Cambridge',
                'ror_id': 'https://ror.org/013meh722',
                'institution_type': 'university',
                'website_url': 'https://www.cam.ac.uk/',
                'established_year': 1209,
            },
            {
                'name': 'ETH Zurich',
                'short_name': 'ETH',
                'country': 'Switzerland',
                'city': 'Zurich',
                'ror_id': 'https://ror.org/05a28rw58',
                'institution_type': 'university',
                'website_url': 'https://ethz.ch/',
                'established_year': 1855,
            },
            {
                'name': 'CERN',
                'short_name': 'CERN',
                'country': 'Switzerland',
                'city': 'Geneva',
                'ror_id': 'https://ror.org/01ggx4157',
                'institution_type': 'research_institute',
                'website_url': 'https://home.cern/',
                'established_year': 1954,
            },
        ]

        created_count = 0
        for inst_data in institutions_data:
            institution, created = Institution.objects.get_or_create(
                name=inst_data['name'],
                defaults=inst_data
            )
            if created:
                created_count += 1
                self.stdout.write(f'  Created: {institution.name}')

        self.stdout.write(
            self.style.SUCCESS(f'Institutions setup complete. Created {created_count} new institutions.')
        )

    @transaction.atomic
    def setup_research_areas(self):
        """Set up initial research area taxonomy"""
        self.stdout.write('Setting up research areas...')
        
        # OECD Fields of Science and Technology classification
        research_areas_data = [
            # Level 1 - Major Fields
            {
                'name': 'Natural Sciences',
                'description': 'Mathematics, computer and information sciences, physical sciences, chemical sciences, earth and related environmental sciences, biological sciences',
                'subject_scheme': 'OECD FOS',
                'parent': None,
            },
            {
                'name': 'Engineering and Technology',
                'description': 'Civil engineering, electrical engineering, electronic engineering, information engineering, mechanical engineering, chemical engineering, materials engineering, medical engineering, environmental engineering, environmental biotechnology, industrial biotechnology, nano-technology',
                'subject_scheme': 'OECD FOS',
                'parent': None,
            },
            {
                'name': 'Medical and Health Sciences',
                'description': 'Basic medicine, clinical medicine, health sciences, health biotechnology',
                'subject_scheme': 'OECD FOS',
                'parent': None,
            },
            {
                'name': 'Agricultural Sciences',
                'description': 'Agriculture, forestry, and fisheries, animal and dairy science, veterinary science, agricultural biotechnology',
                'subject_scheme': 'OECD FOS',
                'parent': None,
            },
            {
                'name': 'Social Sciences',
                'description': 'Psychology, economics and business, educational sciences, sociology, law, political science, social and economic geography, media and communications',
                'subject_scheme': 'OECD FOS',
                'parent': None,
            },
            {
                'name': 'Humanities',
                'description': 'History and archaeology, languages and literature, philosophy, ethics and religion, arts',
                'subject_scheme': 'OECD FOS',
                'parent': None,
            },
        ]

        # Create major fields first
        major_fields = {}
        for area_data in research_areas_data:
            area, created = ResearchArea.objects.get_or_create(
                name=area_data['name'],
                defaults={
                    'description': area_data['description'],
                    'subject_scheme': area_data['subject_scheme'],
                    'parent': None,
                }
            )
            major_fields[area_data['name']] = area
            if created:
                self.stdout.write(f'  Created major field: {area.name}')

        # Level 2 - Subfields
        subfields_data = [
            # Natural Sciences subfields
            {
                'name': 'Computer Science',
                'description': 'Algorithms, artificial intelligence, computer systems, software engineering',
                'parent': 'Natural Sciences',
            },
            {
                'name': 'Mathematics',
                'description': 'Pure mathematics, applied mathematics, statistics and probability',
                'parent': 'Natural Sciences',
            },
            {
                'name': 'Physics',
                'description': 'Theoretical physics, applied physics, condensed matter physics',
                'parent': 'Natural Sciences',
            },
            {
                'name': 'Chemistry',
                'description': 'Organic chemistry, inorganic chemistry, physical chemistry',
                'parent': 'Natural Sciences',
            },
            {
                'name': 'Biology',
                'description': 'Molecular biology, cell biology, genetics, ecology',
                'parent': 'Natural Sciences',
            },
            
            # Engineering subfields
            {
                'name': 'Software Engineering',
                'description': 'Software development, systems analysis, programming methodologies',
                'parent': 'Engineering and Technology',
            },
            {
                'name': 'Electrical Engineering',
                'description': 'Electronics, telecommunications, power systems',
                'parent': 'Engineering and Technology',
            },
            {
                'name': 'Mechanical Engineering',
                'description': 'Thermodynamics, fluid mechanics, materials science',
                'parent': 'Engineering and Technology',
            },
            
            # Medical Sciences subfields
            {
                'name': 'Clinical Medicine',
                'description': 'Internal medicine, surgery, pediatrics, psychiatry',
                'parent': 'Medical and Health Sciences',
            },
            {
                'name': 'Biomedical Research',
                'description': 'Pharmacology, pathology, immunology',
                'parent': 'Medical and Health Sciences',
            },
            
            # Social Sciences subfields
            {
                'name': 'Psychology',
                'description': 'Cognitive psychology, social psychology, developmental psychology',
                'parent': 'Social Sciences',
            },
            {
                'name': 'Economics',
                'description': 'Microeconomics, macroeconomics, econometrics',
                'parent': 'Social Sciences',
            },
            {
                'name': 'Education',
                'description': 'Educational psychology, curriculum development, educational technology',
                'parent': 'Social Sciences',
            },
        ]

        created_subfields = 0
        for subfield_data in subfields_data:
            parent_area = major_fields.get(subfield_data['parent'])
            if parent_area:
                subfield, created = ResearchArea.objects.get_or_create(
                    name=subfield_data['name'],
                    defaults={
                        'description': subfield_data['description'],
                        'subject_scheme': 'OECD FOS',
                        'parent': parent_area,
                    }
                )
                if created:
                    created_subfields += 1
                    self.stdout.write(f'  Created subfield: {subfield.name} (under {parent_area.name})')

        total_areas = len(research_areas_data) + created_subfields
        self.stdout.write(
            self.style.SUCCESS(f'Research areas setup complete. Total areas: {total_areas}')
        ) 