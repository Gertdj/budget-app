"""
Management command to export household data to JSON for migration.
This exports all categories, budgets, transactions, and notes for a household.

Usage:
    python manage.py export_household_data <household_id_or_name> --output household_data.json
    python manage.py export_household_data "My Household" --output my_data.json
"""
import json
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from finance.models import Household, Category, Budget, Transaction, CategoryNote
from decimal import Decimal

User = get_user_model()


class Command(BaseCommand):
    help = 'Export household data (categories, budgets, transactions, notes) to JSON file'

    def add_arguments(self, parser):
        parser.add_argument(
            'household_identifier',
            type=str,
            help='Household ID or name to export'
        )
        parser.add_argument(
            '--output',
            type=str,
            default='household_data.json',
            help='Output JSON file path (default: household_data.json)'
        )

    def handle(self, *args, **options):
        household_id_or_name = options['household_identifier']
        output_file = options['output']
        
        # Find household
        try:
            if household_id_or_name.isdigit():
                household = Household.objects.get(id=int(household_id_or_name))
            else:
                household = Household.objects.get(name=household_id_or_name)
        except Household.DoesNotExist:
            raise CommandError(f'Household "{household_id_or_name}" not found.')
        
        self.stdout.write(f'Exporting data for household: {household.name} (ID: {household.id})')
        
        # Build export data structure
        export_data = {
            'household': {
                'name': household.name,
            },
            'members': [user.email for user in household.members.all()],
            'categories': [],
            'budgets': [],
            'transactions': [],
            'notes': []
        }
        
        # Export categories (with parent relationships)
        categories_map = {}  # id -> index in list
        
        # First pass: get all categories and build map
        all_categories = Category.objects.filter(household=household).order_by('id')
        for idx, cat in enumerate(all_categories):
            categories_map[cat.id] = idx
            export_data['categories'].append({
                'name': cat.name,
                'type': cat.type,
                'is_persistent': cat.is_persistent,
                'payment_type': cat.payment_type,
                'is_essential': cat.is_essential,
                'parent_id': cat.parent_id,  # Will resolve to name later
            })
        
        # Second pass: resolve parent names
        for cat_data in export_data['categories']:
            if cat_data['parent_id']:
                try:
                    parent_cat = Category.objects.get(id=cat_data['parent_id'])
                    cat_data['parent_name'] = parent_cat.name
                except Category.DoesNotExist:
                    cat_data['parent_name'] = None
            else:
                cat_data['parent_name'] = None
            # Remove parent_id from export (we'll use parent_name for import)
            del cat_data['parent_id']
        
        # Export budgets
        budgets = Budget.objects.filter(category__household=household).select_related('category')
        for budget in budgets:
            export_data['budgets'].append({
                'category_name': budget.category.name,
                'amount': str(budget.amount),  # Convert Decimal to string
                'start_date': budget.start_date.isoformat(),
                'end_date': budget.end_date.isoformat(),
                'is_paid': budget.is_paid,
            })
        
        # Export transactions
        transactions = Transaction.objects.filter(household=household).select_related('category')
        for trans in transactions:
            export_data['transactions'].append({
                'amount': str(trans.amount),
                'date': trans.date.isoformat(),
                'description': trans.description,
                'category_name': trans.category.name if trans.category else None,
                'type': trans.type,
            })
        
        # Export category notes
        notes = CategoryNote.objects.filter(category__household=household).select_related('category', 'author')
        for note in notes:
            export_data['notes'].append({
                'category_name': note.category.name,
                'note': note.note,
                'author_email': note.author.email if note.author else None,
            })
        
        # Write to JSON file
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        # Summary
        self.stdout.write(self.style.SUCCESS(f'\n✓ Export complete!'))
        self.stdout.write(f'  Categories: {len(export_data["categories"])}')
        self.stdout.write(f'  Budgets: {len(export_data["budgets"])}')
        self.stdout.write(f'  Transactions: {len(export_data["transactions"])}')
        self.stdout.write(f'  Notes: {len(export_data["notes"])}')
        self.stdout.write(f'\n  Saved to: {output_file}')
        self.stdout.write(f'\n  Next step: Copy this file to Render and run:')
        self.stdout.write(f'    python manage.py import_household_data {output_file} <target_user_email>')

