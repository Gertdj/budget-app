"""
Template system for creating default category structures for new users
"""
from .models import Category, Household, BudgetTemplate, TemplateCategory

def create_base_starter_template(household, template=None):
    """
    Creates categories for a household from a budget template.
    If no template is provided, uses the default template.
    
    Args:
        household: Household instance to create categories for
        template: BudgetTemplate instance (optional, defaults to default template)
    
    Returns:
        int: Number of categories created
    """
    # Get template - use provided template, or default, or fallback to hardcoded
    if template is None:
        template = BudgetTemplate.objects.filter(is_default=True, is_active=True).first()
    
    if template:
        # Use database template
        return apply_template_to_household(household, template)
    else:
        # Fallback to hardcoded template (for backwards compatibility)
        return create_hardcoded_template(household)

def apply_template_to_household(household, template):
    """
    Apply a BudgetTemplate to a household, creating all categories.
    
    Args:
        household: Household instance
        template: BudgetTemplate instance
    
    Returns:
        int: Number of categories created
    """
    # Get all template categories ordered by display_order
    template_categories = template.categories.all().order_by('display_order', 'name')
    
    # Create a mapping of template category IDs to actual category IDs for parent relationships
    category_map = {}  # {template_category_id: actual_category}
    
    # First pass: Create all parent categories
    for template_cat in template_categories:
        if template_cat.parent is None:
            category = Category.objects.create(
                household=household,
                name=template_cat.name,
                type=template_cat.type,
                is_persistent=template_cat.is_persistent,
                payment_type=template_cat.payment_type,
                is_essential=template_cat.is_essential,
                parent=None
            )
            category_map[template_cat.id] = category
    
    # Second pass: Create all child categories
    for template_cat in template_categories:
        if template_cat.parent is not None:
            parent_category = category_map.get(template_cat.parent.id)
            if parent_category:
                category = Category.objects.create(
                    household=household,
                    name=template_cat.name,
                    type=template_cat.type,
                    is_persistent=template_cat.is_persistent,
                    payment_type=template_cat.payment_type,
                    is_essential=template_cat.is_essential,
                    parent=parent_category
                )
                category_map[template_cat.id] = category
    
    return len(category_map)

def create_hardcoded_template(household):
    """
    Fallback: Creates the hardcoded base starter template with standard categories.
    This is kept for backwards compatibility if no templates exist in the database.
    """
    # INCOME CATEGORIES
    income_salary = Category.objects.create(
        household=household,
        name='Salary',
        type='INCOME',
        is_persistent=True,
        payment_type='INCOME',
        parent=None
    )
    
    income_bonus = Category.objects.create(
        household=household,
        name='Bonus',
        type='INCOME',
        is_persistent=False,
        payment_type='INCOME',
        parent=None
    )
    
    income_freelance = Category.objects.create(
        household=household,
        name='Freelance / Side Hustle',
        type='INCOME',
        is_persistent=False,
        payment_type='INCOME',
        parent=None
    )
    
    income_investment = Category.objects.create(
        household=household,
        name='Investment Income',
        type='INCOME',
        is_persistent=False,
        payment_type='INCOME',
        parent=None
    )
    
    # EXPENSE CATEGORIES - HOUSING
    expense_housing = Category.objects.create(
        household=household,
        name='Housing',
        type='EXPENSE',
        is_persistent=False,
        payment_type='MANUAL',
        parent=None
    )
    
    Category.objects.create(
        household=household,
        name='Rent / Bond',
        type='EXPENSE',
        is_persistent=True,
        payment_type='MANUAL',
        parent=expense_housing
    )
    
    Category.objects.create(
        household=household,
        name='Rates & Taxes',
        type='EXPENSE',
        is_persistent=True,
        payment_type='AUTO',
        parent=expense_housing
    )
    
    Category.objects.create(
        household=household,
        name='Home Insurance',
        type='EXPENSE',
        is_persistent=True,
        payment_type='AUTO',
        parent=expense_housing
    )
    
    # EXPENSE CATEGORIES - UTILITIES
    expense_utilities = Category.objects.create(
        household=household,
        name='Utilities',
        type='EXPENSE',
        is_persistent=False,
        payment_type='MANUAL',
        parent=None
    )
    
    Category.objects.create(
        household=household,
        name='Electricity',
        type='EXPENSE',
        is_persistent=True,
        payment_type='MANUAL',
        parent=expense_utilities
    )
    
    Category.objects.create(
        household=household,
        name='Water',
        type='EXPENSE',
        is_persistent=True,
        payment_type='MANUAL',
        parent=expense_utilities
    )
    
    Category.objects.create(
        household=household,
        name='Internet',
        type='EXPENSE',
        is_persistent=True,
        payment_type='AUTO',
        parent=expense_utilities
    )
    
    Category.objects.create(
        household=household,
        name='Mobile',
        type='EXPENSE',
        is_persistent=True,
        payment_type='AUTO',
        parent=expense_utilities
    )
    
    # EXPENSE CATEGORIES - TRANSPORT
    expense_transport = Category.objects.create(
        household=household,
        name='Transport',
        type='EXPENSE',
        is_persistent=False,
        payment_type='MANUAL',
        parent=None
    )
    
    Category.objects.create(
        household=household,
        name='Fuel',
        type='EXPENSE',
        is_persistent=True,
        payment_type='MANUAL',
        parent=expense_transport
    )
    
    Category.objects.create(
        household=household,
        name='Public Transport',
        type='EXPENSE',
        is_persistent=True,
        payment_type='MANUAL',
        parent=expense_transport
    )
    
    Category.objects.create(
        household=household,
        name='Car Insurance',
        type='EXPENSE',
        is_persistent=True,
        payment_type='AUTO',
        parent=expense_transport
    )
    
    # EXPENSE CATEGORIES - STANDALONE
    Category.objects.create(
        household=household,
        name='Groceries',
        type='EXPENSE',
        is_persistent=True,
        payment_type='MANUAL',
        parent=None
    )
    
    Category.objects.create(
        household=household,
        name='Eating Out',
        type='EXPENSE',
        is_persistent=False,
        payment_type='MANUAL',
        parent=None
    )
    
    # EXPENSE CATEGORIES - HEALTHCARE
    expense_healthcare = Category.objects.create(
        household=household,
        name='Healthcare',
        type='EXPENSE',
        is_persistent=False,
        payment_type='MANUAL',
        parent=None
    )
    
    Category.objects.create(
        household=household,
        name='Medical Aid',
        type='EXPENSE',
        is_persistent=True,
        payment_type='AUTO',
        parent=expense_healthcare
    )
    
    Category.objects.create(
        household=household,
        name='Medication',
        type='EXPENSE',
        is_persistent=False,
        payment_type='MANUAL',
        parent=expense_healthcare
    )
    
    # EXPENSE CATEGORIES - DEBT
    expense_debt = Category.objects.create(
        household=household,
        name='Debt',
        type='EXPENSE',
        is_persistent=False,
        payment_type='MANUAL',
        parent=None
    )
    
    Category.objects.create(
        household=household,
        name='Credit Card',
        type='EXPENSE',
        is_persistent=True,
        payment_type='AUTO',
        parent=expense_debt
    )
    
    Category.objects.create(
        household=household,
        name='Personal Loan',
        type='EXPENSE',
        is_persistent=True,
        payment_type='AUTO',
        parent=expense_debt
    )
    
    # EXPENSE CATEGORIES - LIFESTYLE
    expense_lifestyle = Category.objects.create(
        household=household,
        name='Lifestyle',
        type='EXPENSE',
        is_persistent=False,
        payment_type='MANUAL',
        parent=None
    )
    
    Category.objects.create(
        household=household,
        name='Entertainment',
        type='EXPENSE',
        is_persistent=False,
        payment_type='MANUAL',
        parent=expense_lifestyle
    )
    
    Category.objects.create(
        household=household,
        name='Subscriptions',
        type='EXPENSE',
        is_persistent=True,
        payment_type='AUTO',
        parent=expense_lifestyle
    )
    
    Category.objects.create(
        household=household,
        name='Miscellaneous',
        type='EXPENSE',
        is_persistent=False,
        payment_type='MANUAL',
        parent=None
    )
    
    # SAVINGS & INVESTMENTS
    Category.objects.create(
        household=household,
        name='Emergency Fund',
        type='SAVINGS',
        is_persistent=True,
        payment_type='MANUAL',
        parent=None
    )
    
    Category.objects.create(
        household=household,
        name='Retirement / Pension',
        type='SAVINGS',
        is_persistent=True,
        payment_type='AUTO',
        parent=None
    )
    
    Category.objects.create(
        household=household,
        name='Investments',
        type='SAVINGS',
        is_persistent=True,
        payment_type='MANUAL',
        parent=None
    )
    
    Category.objects.create(
        household=household,
        name='Short-term Goals',
        type='SAVINGS',
        is_persistent=False,
        payment_type='MANUAL',
        parent=None
    )
    
    return 33  # Return count of categories created

def apply_barebones_template(household, year, month):
    """
    Apply barebones emergency budget template to a specific month.
    This reduces non-essential categories to zero and keeps essential categories at current amounts.
    
    Essential categories (kept at current amounts):
    - Housing (Rent/Bond, Rates, Insurance)
    - Utilities (Electricity, Water, Internet, Mobile)
    - Groceries
    - Healthcare (Medical Aid)
    - Debt (minimum payments)
    - Transport (minimal)
    - Emergency Fund savings
    
    Non-essential categories (set to 0):
    - Eating Out
    - Entertainment
    - Subscriptions
    - Lifestyle expenses
    - Non-essential savings (except Emergency Fund)
    """
    from .models import Budget, Category
    from decimal import Decimal
    import datetime
    import calendar
    
    start_date = datetime.date(year, month, 1)
    _, last_day = calendar.monthrange(year, month)
    end_date = datetime.date(year, month, last_day)
    
    categories = Category.objects.filter(household=household)
    changes_made = []
    
    for category in categories:
        # Skip income categories - don't modify income
        if category.type == 'INCOME':
            continue
        
        # Use the is_essential field directly (defaults to True if not set)
        # True = essential (keep amount), False = non-essential (zero out)
        is_essential = category.is_essential
        is_non_essential = not category.is_essential
        
        # Get or create budget for this month
        budget, created = Budget.objects.get_or_create(
            category=category,
            start_date=start_date,
            defaults={
                'amount': Decimal('0'),
                'end_date': end_date
            }
        )
        
        old_amount = budget.amount
        
        if is_non_essential:
            # Zero out non-essential categories
            budget.amount = Decimal('0')
            budget.save()
            if old_amount > 0:
                changes_made.append({
                    'category': category.name,
                    'old_amount': old_amount,
                    'new_amount': Decimal('0'),
                    'action': 'zeroed'
                })
        # Essential categories keep their current amounts (no change needed)
        # If budget doesn't exist yet, it stays at 0 (user can set it manually)
    
    return changes_made
