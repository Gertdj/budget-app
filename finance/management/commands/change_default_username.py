"""
Management command to change the default_user's username.
Usage: python manage.py change_default_username <new_username>
"""
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Changes the default_user username to a new username'

    def add_arguments(self, parser):
        parser.add_argument('new_username', type=str, help='New username for default_user')
        parser.add_argument(
            '--password',
            type=str,
            help='Set a new password (optional)',
        )

    def handle(self, *args, **options):
        new_username = options['new_username']
        new_password = options.get('password')
        
        # Check if new username already exists
        if User.objects.filter(username=new_username).exists():
            raise CommandError(f'Username "{new_username}" already exists. Please choose a different username.')
        
        # Get default_user
        try:
            default_user = User.objects.get(username='default_user')
        except User.DoesNotExist:
            raise CommandError('default_user does not exist.')
        
        old_username = default_user.username
        
        # Change username
        default_user.username = new_username
        default_user.save()
        
        self.stdout.write(self.style.SUCCESS(f'✓ Username changed from "{old_username}" to "{new_username}"'))
        
        # Optionally change password
        if new_password:
            default_user.set_password(new_password)
            default_user.save()
            self.stdout.write(self.style.SUCCESS(f'✓ Password updated'))
        else:
            self.stdout.write(self.style.WARNING(f'\nNote: Password is still "changeme"'))
            self.stdout.write(self.style.WARNING(f'Change it with: python manage.py changepassword {new_username}'))
        
        self.stdout.write(self.style.SUCCESS(f'\n✓ You can now login with username: {new_username}'))

