"""
Management command to migrate existing data to Household model.
This assigns all existing categories, budgets, and transactions to a default household.
Run this after adding the Household model to your database.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from finance.models import Household, Category, Budget, Transaction

class Command(BaseCommand):
    help = 'Migrates existing data to Household model by creating a default household and assigning all data to it'

    def handle(self, *args, **options):
        self.stdout.write('Starting data migration to Household model...')
        
        # Create a default household for existing data
        default_household, created = Household.objects.get_or_create(
            name='Default Household',
            defaults={}
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created default household: {default_household.name}'))
        else:
            self.stdout.write(f'Using existing household: {default_household.name}')
        
        # Get or create a default user if none exists
        default_user, user_created = User.objects.get_or_create(
            username='default_user',
            defaults={
                'email': 'default@example.com',
                'first_name': 'Default',
                'last_name': 'User'
            }
        )
        
        if user_created:
            default_user.set_password('changeme')  # User should change this
            default_user.save()
            self.stdout.write(self.style.WARNING(f'Created default user: {default_user.username} (password: changeme - PLEASE CHANGE)'))
        
        # Add default user to household if not already a member
        if default_user not in default_household.members.all():
            default_household.members.add(default_user)
            self.stdout.write(f'Added {default_user.username} to default household')
        
        # Migrate categories without household
        categories_without_household = Category.objects.filter(household__isnull=True)
        count = categories_without_household.count()
        if count > 0:
            categories_without_household.update(household=default_household)
            self.stdout.write(self.style.SUCCESS(f'Migrated {count} categories to default household'))
        else:
            self.stdout.write('No categories to migrate')
        
        # Migrate transactions without household
        transactions_without_household = Transaction.objects.filter(household__isnull=True)
        count = transactions_without_household.count()
        if count > 0:
            transactions_without_household.update(household=default_household)
            self.stdout.write(self.style.SUCCESS(f'Migrated {count} transactions to default household'))
        else:
            self.stdout.write('No transactions to migrate')
        
        # Note: Budgets don't need migration as they're linked through Category
        
        self.stdout.write(self.style.SUCCESS('\nMigration completed successfully!'))
        self.stdout.write(f'\nDefault household: {default_household.name}')
        self.stdout.write(f'Default user: {default_user.username}')
        self.stdout.write(self.style.WARNING('\nIMPORTANT: If you have existing users, you should:'))
        self.stdout.write('1. Create households for each user')
        self.stdout.write('2. Assign their categories/budgets to their household')
        self.stdout.write('3. Add users to their respective households')

