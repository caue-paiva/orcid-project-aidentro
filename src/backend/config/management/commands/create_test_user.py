"""
Django management command to create a test superuser
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import IntegrityError

User = get_user_model()


class Command(BaseCommand):
    help = 'Create a test superuser for development'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            default='admin',
            help='Username for the superuser (default: admin)'
        )
        parser.add_argument(
            '--email',
            type=str,
            default='admin@example.com',
            help='Email for the superuser (default: admin@example.com)'
        )
        parser.add_argument(
            '--password',
            type=str,
            default='admin123',
            help='Password for the superuser (default: admin123)'
        )
        parser.add_argument(
            '--orcid-id',
            type=str,
            help='ORCID ID for the test user (optional)'
        )

    def handle(self, *args, **options):
        username = options['username']
        email = options['email']
        password = options['password']
        orcid_id = options.get('orcid_id')

        try:
            # Check if user already exists
            if User.objects.filter(username=username).exists():
                self.stdout.write(
                    self.style.WARNING(f'User "{username}" already exists!')
                )
                user = User.objects.get(username=username)
                self.stdout.write(f'Existing user ID: {user.id}')
                self.stdout.write(f'Is superuser: {user.is_superuser}')
                self.stdout.write(f'Is staff: {user.is_staff}')
                return

            # Create superuser
            user = User.objects.create_superuser(
                username=username,
                email=email,
                password=password
            )

            # Add ORCID ID if provided
            if orcid_id:
                user.orcid_id = orcid_id
                user.save()

            self.stdout.write(
                self.style.SUCCESS(f'Successfully created superuser "{username}"')
            )
            self.stdout.write(f'User ID: {user.id}')
            self.stdout.write(f'Email: {user.email}')
            self.stdout.write(f'ORCID ID: {user.orcid_id or "Not set"}')
            self.stdout.write(f'Is superuser: {user.is_superuser}')
            self.stdout.write(f'Is staff: {user.is_staff}')

        except IntegrityError as e:
            self.stdout.write(
                self.style.ERROR(f'Error creating user: {e}')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Unexpected error: {e}')
            ) 