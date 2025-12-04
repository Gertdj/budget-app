"""
Management command to migrate existing users to email-based authentication.
This command should be run after the database migrations are complete.

Usage: python manage.py migrate_users_to_email
"""
from django.core.management.base import BaseCommand
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from finance.models import User


class Command(BaseCommand):
    help = 'Migrates existing users to use email as username. Creates email from username if needed.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be changed without actually making changes',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        self.stdout.write('Starting user migration to email-based authentication...')
        
        users_updated = 0
        users_skipped = 0
        errors = []
        
        for user in User.objects.all():
            try:
                # Check if user already has a valid email
                if user.email and user.email != '':
                    try:
                        validate_email(user.email)
                        # User has valid email, skip
                        users_skipped += 1
                        if not dry_run:
                            self.stdout.write(f'✓ User {user.id}: Already has valid email ({user.email})')
                        continue
                    except ValidationError:
                        # Email exists but is invalid, need to fix it
                        pass
                
                # User doesn't have email or has invalid email
                if user.username:
                    # Try to use username as email if it's valid
                    try:
                        validate_email(user.username)
                        # Username is a valid email
                        new_email = user.username
                    except ValidationError:
                        # Username is not an email, create placeholder
                        new_email = f"{user.username}@migrated.local"
                else:
                    # No username either, create generic email
                    new_email = f"user_{user.id}@migrated.local"
                
                # Check if email already exists
                if User.objects.filter(email=new_email).exclude(id=user.id).exists():
                    # Email conflict, add user ID to make it unique
                    new_email = f"user_{user.id}@migrated.local"
                
                if dry_run:
                    self.stdout.write(f'[DRY RUN] Would update user {user.id}: email = {new_email}')
                else:
                    user.email = new_email
                    user.save()
                    self.stdout.write(self.style.SUCCESS(f'✓ Updated user {user.id}: email = {new_email}'))
                
                users_updated += 1
                
            except Exception as e:
                error_msg = f'Error updating user {user.id}: {str(e)}'
                errors.append(error_msg)
                self.stdout.write(self.style.ERROR(f'✗ {error_msg}'))
        
        # Summary
        self.stdout.write('')
        self.stdout.write('=' * 60)
        self.stdout.write('Migration Summary:')
        self.stdout.write(f'  Users updated: {users_updated}')
        self.stdout.write(f'  Users skipped (already have email): {users_skipped}')
        self.stdout.write(f'  Errors: {len(errors)}')
        
        if errors:
            self.stdout.write('')
            self.stdout.write(self.style.ERROR('Errors encountered:'))
            for error in errors:
                self.stdout.write(self.style.ERROR(f'  - {error}'))
        
        if dry_run:
            self.stdout.write('')
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No changes were made.'))
            self.stdout.write('Run without --dry-run to apply changes.')
        else:
            self.stdout.write('')
            self.stdout.write(self.style.SUCCESS('Migration completed!'))
            self.stdout.write('')
            self.stdout.write('Important: Users with @migrated.local emails should update their email addresses.')
            self.stdout.write('They can do this by editing their profile or contacting an administrator.')

