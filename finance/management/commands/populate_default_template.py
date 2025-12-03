"""
Management command to populate the default budget template from the hardcoded template.
This migrates the existing create_base_starter_template logic to a database template.
"""
from django.core.management.base import BaseCommand
from finance.models import BudgetTemplate, TemplateCategory
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Populates the default budget template from the hardcoded template structure'

    def handle(self, *args, **options):
        self.stdout.write('Creating default budget template...')
        
        # Get or create default template
        template, created = BudgetTemplate.objects.get_or_create(
            name='Basic Starter',
            defaults={
                'description': 'A comprehensive starter template with common income, expense, and savings categories. Perfect for most users.',
                'is_default': True,
                'is_active': True
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'✓ Created template: {template.name}'))
        else:
            self.stdout.write(f'Template "{template.name}" already exists. Clearing existing categories...')
            template.categories.all().delete()
        
        # Set as default
        template.is_default = True
        template.save()
        
        order = 0
        
        # INCOME CATEGORIES
        income_salary = TemplateCategory.objects.create(
            template=template,
            name='Salary',
            type='INCOME',
            is_persistent=True,
            payment_type='INCOME',
            parent=None,
            is_essential=True,
            display_order=order
        )
        order += 1
        
        TemplateCategory.objects.create(
            template=template,
            name='Bonus',
            type='INCOME',
            is_persistent=False,
            payment_type='INCOME',
            parent=None,
            is_essential=True,
            display_order=order
        )
        order += 1
        
        TemplateCategory.objects.create(
            template=template,
            name='Freelance / Side Hustle',
            type='INCOME',
            is_persistent=False,
            payment_type='INCOME',
            parent=None,
            is_essential=True,
            display_order=order
        )
        order += 1
        
        TemplateCategory.objects.create(
            template=template,
            name='Investment Income',
            type='INCOME',
            is_persistent=False,
            payment_type='INCOME',
            parent=None,
            is_essential=True,
            display_order=order
        )
        order += 1
        
        # EXPENSE CATEGORIES - HOUSING
        expense_housing = TemplateCategory.objects.create(
            template=template,
            name='Housing',
            type='EXPENSE',
            is_persistent=False,
            payment_type='MANUAL',
            parent=None,
            is_essential=True,
            display_order=order
        )
        order += 1
        
        TemplateCategory.objects.create(
            template=template,
            name='Rent / Bond',
            type='EXPENSE',
            is_persistent=True,
            payment_type='MANUAL',
            parent=expense_housing,
            is_essential=True,
            display_order=order
        )
        order += 1
        
        TemplateCategory.objects.create(
            template=template,
            name='Rates & Taxes',
            type='EXPENSE',
            is_persistent=True,
            payment_type='AUTO',
            parent=expense_housing,
            is_essential=True,
            display_order=order
        )
        order += 1
        
        TemplateCategory.objects.create(
            template=template,
            name='Home Insurance',
            type='EXPENSE',
            is_persistent=True,
            payment_type='AUTO',
            parent=expense_housing,
            is_essential=True,
            display_order=order
        )
        order += 1
        
        # EXPENSE CATEGORIES - UTILITIES
        expense_utilities = TemplateCategory.objects.create(
            template=template,
            name='Utilities',
            type='EXPENSE',
            is_persistent=False,
            payment_type='MANUAL',
            parent=None,
            is_essential=True,
            display_order=order
        )
        order += 1
        
        TemplateCategory.objects.create(
            template=template,
            name='Electricity',
            type='EXPENSE',
            is_persistent=True,
            payment_type='MANUAL',
            parent=expense_utilities,
            is_essential=True,
            display_order=order
        )
        order += 1
        
        TemplateCategory.objects.create(
            template=template,
            name='Water',
            type='EXPENSE',
            is_persistent=True,
            payment_type='MANUAL',
            parent=expense_utilities,
            is_essential=True,
            display_order=order
        )
        order += 1
        
        TemplateCategory.objects.create(
            template=template,
            name='Internet',
            type='EXPENSE',
            is_persistent=True,
            payment_type='AUTO',
            parent=expense_utilities,
            is_essential=True,
            display_order=order
        )
        order += 1
        
        TemplateCategory.objects.create(
            template=template,
            name='Mobile',
            type='EXPENSE',
            is_persistent=True,
            payment_type='AUTO',
            parent=expense_utilities,
            is_essential=True,
            display_order=order
        )
        order += 1
        
        # EXPENSE CATEGORIES - TRANSPORT
        expense_transport = TemplateCategory.objects.create(
            template=template,
            name='Transport',
            type='EXPENSE',
            is_persistent=False,
            payment_type='MANUAL',
            parent=None,
            is_essential=True,
            display_order=order
        )
        order += 1
        
        TemplateCategory.objects.create(
            template=template,
            name='Fuel',
            type='EXPENSE',
            is_persistent=True,
            payment_type='MANUAL',
            parent=expense_transport,
            is_essential=True,
            display_order=order
        )
        order += 1
        
        TemplateCategory.objects.create(
            template=template,
            name='Public Transport',
            type='EXPENSE',
            is_persistent=True,
            payment_type='MANUAL',
            parent=expense_transport,
            is_essential=True,
            display_order=order
        )
        order += 1
        
        TemplateCategory.objects.create(
            template=template,
            name='Car Insurance',
            type='EXPENSE',
            is_persistent=True,
            payment_type='AUTO',
            parent=expense_transport,
            is_essential=True,
            display_order=order
        )
        order += 1
        
        # EXPENSE CATEGORIES - STANDALONE
        TemplateCategory.objects.create(
            template=template,
            name='Groceries',
            type='EXPENSE',
            is_persistent=True,
            payment_type='MANUAL',
            parent=None,
            is_essential=True,
            display_order=order
        )
        order += 1
        
        TemplateCategory.objects.create(
            template=template,
            name='Eating Out',
            type='EXPENSE',
            is_persistent=False,
            payment_type='MANUAL',
            parent=None,
            is_essential=False,
            display_order=order
        )
        order += 1
        
        # EXPENSE CATEGORIES - HEALTHCARE
        expense_healthcare = TemplateCategory.objects.create(
            template=template,
            name='Healthcare',
            type='EXPENSE',
            is_persistent=False,
            payment_type='MANUAL',
            parent=None,
            is_essential=True,
            display_order=order
        )
        order += 1
        
        TemplateCategory.objects.create(
            template=template,
            name='Medical Aid',
            type='EXPENSE',
            is_persistent=True,
            payment_type='AUTO',
            parent=expense_healthcare,
            is_essential=True,
            display_order=order
        )
        order += 1
        
        TemplateCategory.objects.create(
            template=template,
            name='Medication',
            type='EXPENSE',
            is_persistent=False,
            payment_type='MANUAL',
            parent=expense_healthcare,
            is_essential=True,
            display_order=order
        )
        order += 1
        
        # EXPENSE CATEGORIES - DEBT
        expense_debt = TemplateCategory.objects.create(
            template=template,
            name='Debt',
            type='EXPENSE',
            is_persistent=False,
            payment_type='MANUAL',
            parent=None,
            is_essential=True,
            display_order=order
        )
        order += 1
        
        TemplateCategory.objects.create(
            template=template,
            name='Credit Card',
            type='EXPENSE',
            is_persistent=True,
            payment_type='AUTO',
            parent=expense_debt,
            is_essential=True,
            display_order=order
        )
        order += 1
        
        TemplateCategory.objects.create(
            template=template,
            name='Personal Loan',
            type='EXPENSE',
            is_persistent=True,
            payment_type='AUTO',
            parent=expense_debt,
            is_essential=True,
            display_order=order
        )
        order += 1
        
        # EXPENSE CATEGORIES - LIFESTYLE
        expense_lifestyle = TemplateCategory.objects.create(
            template=template,
            name='Lifestyle',
            type='EXPENSE',
            is_persistent=False,
            payment_type='MANUAL',
            parent=None,
            is_essential=False,
            display_order=order
        )
        order += 1
        
        TemplateCategory.objects.create(
            template=template,
            name='Entertainment',
            type='EXPENSE',
            is_persistent=False,
            payment_type='MANUAL',
            parent=expense_lifestyle,
            is_essential=False,
            display_order=order
        )
        order += 1
        
        TemplateCategory.objects.create(
            template=template,
            name='Subscriptions',
            type='EXPENSE',
            is_persistent=True,
            payment_type='AUTO',
            parent=expense_lifestyle,
            is_essential=False,
            display_order=order
        )
        order += 1
        
        TemplateCategory.objects.create(
            template=template,
            name='Miscellaneous',
            type='EXPENSE',
            is_persistent=False,
            payment_type='MANUAL',
            parent=None,
            is_essential=False,
            display_order=order
        )
        order += 1
        
        # SAVINGS & INVESTMENTS
        TemplateCategory.objects.create(
            template=template,
            name='Emergency Fund',
            type='SAVINGS',
            is_persistent=True,
            payment_type='MANUAL',
            parent=None,
            is_essential=True,
            display_order=order
        )
        order += 1
        
        TemplateCategory.objects.create(
            template=template,
            name='Retirement / Pension',
            type='SAVINGS',
            is_persistent=True,
            payment_type='AUTO',
            parent=None,
            is_essential=True,
            display_order=order
        )
        order += 1
        
        TemplateCategory.objects.create(
            template=template,
            name='Investments',
            type='SAVINGS',
            is_persistent=True,
            payment_type='MANUAL',
            parent=None,
            is_essential=True,
            display_order=order
        )
        order += 1
        
        TemplateCategory.objects.create(
            template=template,
            name='Short-term Goals',
            type='SAVINGS',
            is_persistent=False,
            payment_type='MANUAL',
            parent=None,
            is_essential=False,
            display_order=order
        )
        
        category_count = template.categories.count()
        self.stdout.write(self.style.SUCCESS(f'\n✓ Successfully populated template with {category_count} categories'))
        self.stdout.write(self.style.SUCCESS(f'✓ Template "{template.name}" is now set as default'))

