"""
Management command to fix household membership - add user to a household
"""
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from finance.models import Household

User = get_user_model()


class Command(BaseCommand):
    help = 'Add a user to a household (fix orphaned households)'

    def add_arguments(self, parser):
        parser.add_argument(
            'user_email',
            type=str,
            help='Email of the user to add'
        )
        parser.add_argument(
            'household_id',
            type=int,
            help='ID of the household to add the user to'
        )

    def handle(self, *args, **options):
        user_email = options['user_email']
        household_id = options['household_id']
        
        try:
            user = User.objects.get(email=user_email)
        except User.DoesNotExist:
            raise CommandError(f'User {user_email} not found')
        
        try:
            household = Household.objects.get(id=household_id)
        except Household.DoesNotExist:
            raise CommandError(f'Household {household_id} not found')
        
        # Check if user is already a member
        if user in household.members.all():
            self.stdout.write(self.style.WARNING(f'User {user_email} is already a member of {household.name}'))
            return
        
        # Add user to household
        household.members.add(user)
        self.stdout.write(self.style.SUCCESS(f'✓ Added {user_email} to household "{household.name}" (ID: {household_id})'))
        self.stdout.write(f'  Household now has {household.members.count()} member(s)')

