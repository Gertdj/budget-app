"""
Management command to check household membership and identify orphaned households
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from finance.models import Household

User = get_user_model()


class Command(BaseCommand):
    help = 'Check household membership and identify any orphaned households'

    def add_arguments(self, parser):
        parser.add_argument(
            '--user-email',
            type=str,
            help='Check households for a specific user email'
        )

    def handle(self, *args, **options):
        user_email = options.get('user_email')
        
        if user_email:
            try:
                user = User.objects.get(email=user_email)
                self.stdout.write(f'\n=== Households for {user.email} ===')
                households = user.households.all()
                self.stdout.write(f'Total households: {households.count()}')
                for h in households:
                    self.stdout.write(f'  - {h.name} (ID: {h.id}) - {h.members.count()} member(s)')
                    for member in h.members.all():
                        self.stdout.write(f'    Member: {member.email}')
            except User.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'User {user_email} not found'))
        else:
            self.stdout.write('\n=== All Households ===')
            all_households = Household.objects.all()
            self.stdout.write(f'Total households: {all_households.count()}')
            
            for h in all_households:
                member_count = h.members.count()
                self.stdout.write(f'\n  {h.name} (ID: {h.id})')
                self.stdout.write(f'    Members: {member_count}')
                if member_count == 0:
                    self.stdout.write(self.style.WARNING('    ⚠ ORPHANED - No members!'))
                else:
                    for member in h.members.all():
                        self.stdout.write(f'      - {member.email}')
            
            # Check for orphaned households
            orphaned = Household.objects.filter(members__isnull=True)
            self.stdout.write(self.style.WARNING(f'\n⚠ Orphaned households (no members): {orphaned.count()}'))

