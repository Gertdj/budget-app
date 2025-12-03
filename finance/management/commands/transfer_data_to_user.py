"""
Management command to transfer data from Default Household to a user's household.
Usage: python manage.py transfer_data_to_user <username>
"""
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from finance.models import Household, Category, Budget, Transaction

class Command(BaseCommand):
    help = 'Transfers all data from Default Household to a user\'s household'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Username to transfer data to')
        parser.add_argument(
            '--delete-default',
            action='store_true',
            help='Delete the Default Household after transfer (use with caution)',
        )

    def handle(self, *args, **options):
        username = options['username']
        delete_default = options['delete_default']
        
        # Get the user
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise CommandError(f'User "{username}" does not exist. Please create the user first.')
        
        # Get or create user's household
        user_household = user.households.first()
        if not user_household:
            user_household = Household.objects.create(name=f"{user.username}'s Household")
            user_household.members.add(user)
            self.stdout.write(self.style.SUCCESS(f'Created household for {username}: {user_household.name}'))
        else:
            self.stdout.write(f'Using existing household: {user_household.name}')
        
        # Get Default Household
        default_household = Household.objects.filter(name='Default Household').first()
        if not default_household:
            self.stdout.write(self.style.WARNING('No Default Household found. Nothing to transfer.'))
            return
        
        # Count items to transfer
        categories_count = Category.objects.filter(household=default_household).count()
        budgets_count = Budget.objects.filter(category__household=default_household).count()
        transactions_count = Transaction.objects.filter(household=default_household).count()
        
        self.stdout.write(f'\nTransferring data from "{default_household.name}" to "{user_household.name}":')
        self.stdout.write(f'  - Categories: {categories_count}')
        self.stdout.write(f'  - Budgets: {budgets_count}')
        self.stdout.write(f'  - Transactions: {transactions_count}')
        
        if categories_count == 0:
            self.stdout.write(self.style.WARNING('No data to transfer.'))
            return
        
        # Confirm transfer
        self.stdout.write(self.style.WARNING('\nThis will move all categories, budgets, and transactions.'))
        response = input('Continue? (yes/no): ')
        if response.lower() not in ['yes', 'y']:
            self.stdout.write('Transfer cancelled.')
            return
        
        # Transfer categories (this will cascade to budgets through the foreign key)
        categories = Category.objects.filter(household=default_household)
        transferred = 0
        for category in categories:
            category.household = user_household
            category.save()
            transferred += 1
        
        # Transfer transactions
        transactions = Transaction.objects.filter(household=default_household)
        transactions.update(household=user_household)
        
        self.stdout.write(self.style.SUCCESS(f'\n✓ Transferred {transferred} categories'))
        self.stdout.write(self.style.SUCCESS(f'✓ Transferred {transactions_count} transactions'))
        self.stdout.write(self.style.SUCCESS(f'✓ Budgets automatically transferred (linked through categories)'))
        
        # Optionally delete default household
        if delete_default:
            # Check if default household has any remaining data
            remaining_cats = Category.objects.filter(household=default_household).count()
            if remaining_cats == 0:
                default_household.delete()
                self.stdout.write(self.style.SUCCESS('✓ Deleted Default Household'))
            else:
                self.stdout.write(self.style.WARNING(f'Default Household still has {remaining_cats} categories. Not deleted.'))
        
        self.stdout.write(self.style.SUCCESS(f'\n✓ Transfer complete!'))
        self.stdout.write(f'\nYou can now login as "{username}" to access your data.')

