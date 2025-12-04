"""
Management command to import household data from JSON file.
This imports categories, budgets, transactions, and notes into a target household.

Usage:
    python manage.py import_household_data household_data.json gertdj@outlook.com
    python manage.py import_household_data household_data.json gertdj@outlook.com --household-name "My Budget"
"""
import json
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from finance.models import Household, Category, Budget, Transaction, CategoryNote
from decimal import Decimal
from datetime import datetime

User = get_user_model()


class Command(BaseCommand):
    help = 'Import household data (categories, budgets, transactions, notes) from JSON file'

    def add_arguments(self, parser):
        parser.add_argument(
            'json_file',
            type=str,
            help='Path to JSON file containing household data'
        )
        parser.add_argument(
            'user_email',
            type=str,
            help='Email of user to assign the household to'
        )
        parser.add_argument(
            '--household-name',
            type=str,
            help='Custom name for the household (defaults to name from JSON)'
        )
        parser.add_argument(
            '--clear-existing',
            action='store_true',
            help='Clear existing categories/budgets/transactions in the target household before importing'
        )

    def handle(self, *args, **options):
        json_file = options['json_file']
        user_email = options['user_email']
        household_name = options.get('household_name')
        clear_existing = options['clear_existing']
        
        # Load JSON data
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except FileNotFoundError:
            raise CommandError(f'File "{json_file}" not found.')
        except json.JSONDecodeError as e:
            raise CommandError(f'Invalid JSON file: {e}')
        
        # Get or create user
        try:
            user = User.objects.get(email=user_email)
        except User.DoesNotExist:
            raise CommandError(f'User with email "{user_email}" not found.')
        
        # Get or create household
        household_name = household_name or data.get('household', {}).get('name', f"{user.email}'s Household")
        household, created = Household.objects.get_or_create(name=household_name)
        household.members.add(user)
        
        if created:
            self.stdout.write(f'Created household: {household.name}')
        else:
            self.stdout.write(f'Using existing household: {household.name}')
        
        # Clear existing data if requested
        if clear_existing:
            self.stdout.write('Clearing existing data...')
            Category.objects.filter(household=household).delete()
            Transaction.objects.filter(household=household).delete()
            self.stdout.write('  ✓ Cleared existing categories and transactions')
        
        # Import categories (with parent relationships)
        self.stdout.write('\nImporting categories...')
        categories_map = {}  # name -> Category object
        
        # First pass: create all categories without parents
        for cat_data in data.get('categories', []):
            if cat_data.get('parent_name'):  # Skip sub-categories for now
                continue
            
            category = Category.objects.create(
                household=household,
                name=cat_data['name'],
                type=cat_data['type'],
                is_persistent=cat_data.get('is_persistent', False),
                payment_type=cat_data.get('payment_type', 'AUTOMATIC'),
                is_essential=cat_data.get('is_essential', True),
                parent=None
            )
            categories_map[cat_data['name']] = category
        
        # Second pass: create sub-categories with parents
        for cat_data in data.get('categories', []):
            if not cat_data.get('parent_name'):  # Already created
                continue
            
            parent = categories_map.get(cat_data['parent_name'])
            if not parent:
                self.stdout.write(self.style.WARNING(f'  ⚠ Parent "{cat_data["parent_name"]}" not found for "{cat_data["name"]}", creating as main category'))
                parent = None
            
            category = Category.objects.create(
                household=household,
                name=cat_data['name'],
                type=cat_data['type'],
                is_persistent=cat_data.get('is_persistent', False),
                payment_type=cat_data.get('payment_type', 'AUTOMATIC'),
                is_essential=cat_data.get('is_essential', True),
                parent=parent
            )
            categories_map[cat_data['name']] = category
        
        self.stdout.write(self.style.SUCCESS(f'  ✓ Imported {len(categories_map)} categories'))
        
        # Import budgets
        self.stdout.write('\nImporting budgets...')
        budget_count = 0
        for budget_data in data.get('budgets', []):
            category = categories_map.get(budget_data['category_name'])
            if not category:
                self.stdout.write(self.style.WARNING(f'  ⚠ Category "{budget_data["category_name"]}" not found, skipping budget'))
                continue
            
            Budget.objects.create(
                category=category,
                amount=Decimal(budget_data['amount']),
                start_date=datetime.fromisoformat(budget_data['start_date']).date(),
                end_date=datetime.fromisoformat(budget_data['end_date']).date(),
                is_paid=budget_data.get('is_paid', False)
            )
            budget_count += 1
        
        self.stdout.write(self.style.SUCCESS(f'  ✓ Imported {budget_count} budgets'))
        
        # Import transactions
        self.stdout.write('\nImporting transactions...')
        transaction_count = 0
        for trans_data in data.get('transactions', []):
            category = categories_map.get(trans_data.get('category_name')) if trans_data.get('category_name') else None
            
            Transaction.objects.create(
                household=household,
                amount=Decimal(trans_data['amount']),
                date=datetime.fromisoformat(trans_data['date']).date(),
                description=trans_data.get('description', ''),
                category=category,
                type=trans_data.get('type', 'EXPENSE')
            )
            transaction_count += 1
        
        self.stdout.write(self.style.SUCCESS(f'  ✓ Imported {transaction_count} transactions'))
        
        # Import notes
        self.stdout.write('\nImporting notes...')
        note_count = 0
        for note_data in data.get('notes', []):
            category = categories_map.get(note_data['category_name'])
            if not category:
                self.stdout.write(self.style.WARNING(f'  ⚠ Category "{note_data["category_name"]}" not found, skipping note'))
                continue
            
            author = None
            if note_data.get('author_email'):
                try:
                    author = User.objects.get(email=note_data['author_email'])
                except User.DoesNotExist:
                    pass  # Note will be created without author
            
            CategoryNote.objects.create(
                category=category,
                note=note_data['note'],
                author=author
            )
            note_count += 1
        
        self.stdout.write(self.style.SUCCESS(f'  ✓ Imported {note_count} notes'))
        
        # Summary
        self.stdout.write(self.style.SUCCESS(f'\n✓ Import complete!'))
        self.stdout.write(f'  Household: {household.name}')
        self.stdout.write(f'  Categories: {len(categories_map)}')
        self.stdout.write(f'  Budgets: {budget_count}')
        self.stdout.write(f'  Transactions: {transaction_count}')
        self.stdout.write(f'  Notes: {note_count}')

