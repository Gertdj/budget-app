"""
Management command to migrate existing users to email-based authentication.
This should be run AFTER creating and running the database migrations for the custom User model.

IMPORTANT: This command assumes you've already:
1. Created the custom User model in models.py
2. Updated settings.py with AUTH_USER_MODEL = 'finance.User'
3. Run: python manage.py makemigrations
4. Run: python manage.py migrate

Then run this command to migrate existing user data.

Usage: 
    python manage.py migrate_to_email_auth
    python manage.py migrate_to_email_auth --dry-run  # Preview changes
"""
from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.contrib.auth import get_user_model
from django.conf import settings

User = get_user_model()


class Command(BaseCommand):
    help = 'Migrates existing users to use email as username. Creates email from username if needed.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be changed without actually making changes',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force update even if email already exists (use with caution)',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        force = options['force']
        
        self.stdout.write('=' * 60)
        self.stdout.write('User Migration to Email-Based Authentication')
        self.stdout.write('=' * 60)
        self.stdout.write('')
        
        # Check if we're using the custom User model
        # Check AUTH_USER_MODEL setting directly
        if settings.AUTH_USER_MODEL != 'finance.User':
            raise CommandError(
                f'Error: AUTH_USER_MODEL is set to {settings.AUTH_USER_MODEL}, not finance.User. '
                'Please update settings.py with: AUTH_USER_MODEL = "finance.User"'
            )
        
        users_updated = 0
        users_skipped = 0
        users_with_errors = 0
        errors = []
        
        for user in User.objects.all():
            try:
                current_email = user.email or ''
                current_username = user.username or ''
                
                # Check if user already has a valid email
                if current_email and current_email != '':
                    try:
                        validate_email(current_email)
                        # User has valid email
                        if not force:
                            users_skipped += 1
                            if not dry_run:
                                self.stdout.write(f'✓ User ID {user.id}: Already has valid email ({current_email})')
                            continue
                    except ValidationError:
                        # Email exists but is invalid
                        self.stdout.write(self.style.WARNING(f'⚠ User ID {user.id}: Has invalid email ({current_email}), will fix'))
                
                # Determine new email
                new_email = None
                
                # Strategy 1: If username is already a valid email, use it
                if current_username:
                    try:
                        validate_email(current_username)
                        new_email = current_username
                        self.stdout.write(f'  → Username "{current_username}" is already a valid email')
                    except ValidationError:
                        pass
                
                # Strategy 2: If we have a username that's not an email, create placeholder
                if not new_email and current_username:
                    # Create email from username
                    # Remove any invalid characters for email
                    safe_username = current_username.replace(' ', '_').replace('@', '_at_')
                    new_email = f"{safe_username}@migrated.local"
                    self.stdout.write(f'  → Creating email from username: {new_email}')
                
                # Strategy 3: Last resort - generic email
                if not new_email:
                    new_email = f"user_{user.id}@migrated.local"
                    self.stdout.write(f'  → Creating generic email: {new_email}')
                
                # Check for email conflicts
                existing_user = User.objects.filter(email=new_email).exclude(id=user.id).first()
                if existing_user:
                    # Conflict - make it unique
                    new_email = f"user_{user.id}@migrated.local"
                    self.stdout.write(self.style.WARNING(f'  ⚠ Email conflict, using: {new_email}'))
                
                if dry_run:
                    self.stdout.write(self.style.WARNING(f'[DRY RUN] Would update user ID {user.id}:'))
                    self.stdout.write(f'  Current email: {current_email or "(empty)"}')
                    self.stdout.write(f'  New email: {new_email}')
                else:
                    user.email = new_email
                    user.save()
                    self.stdout.write(self.style.SUCCESS(f'✓ Updated user ID {user.id}: email = {new_email}'))
                
                users_updated += 1
                
            except Exception as e:
                users_with_errors += 1
                error_msg = f'Error updating user ID {user.id}: {str(e)}'
                errors.append(error_msg)
                self.stdout.write(self.style.ERROR(f'✗ {error_msg}'))
        
        # Summary
        self.stdout.write('')
        self.stdout.write('=' * 60)
        self.stdout.write('Migration Summary:')
        self.stdout.write(f'  Total users processed: {User.objects.count()}')
        self.stdout.write(f'  Users updated: {users_updated}')
        self.stdout.write(f'  Users skipped (already have valid email): {users_skipped}')
        self.stdout.write(f'  Users with errors: {users_with_errors}')
        self.stdout.write('=' * 60)
        
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
            self.stdout.write(self.style.SUCCESS('✓ Migration completed successfully!'))
            self.stdout.write('')
            self.stdout.write('Next steps:')
            self.stdout.write('  1. Users with @migrated.local emails should update their email addresses')
            self.stdout.write('  2. They can do this by editing their profile or contacting an administrator')
            self.stdout.write('  3. Users can now log in using their email address instead of username')

