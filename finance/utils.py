from .models import Category, Budget, Household
import datetime
import calendar

def open_budget_month(year, month, household, force_update=False):
    """
    Ensures budget entries exist for all categories for the given month.
    If entries don't exist, they are created.
    Rollover logic:
    - If persistent: copy amount from previous month.
    - If not persistent: set amount to 0.
    """
    start_date = datetime.date(year, month, 1)
    _, last_day = calendar.monthrange(year, month)
    end_date = datetime.date(year, month, last_day)

    # Calculate previous month
    if month == 1:
        prev_month_year = year - 1
        prev_month_month = 12
    else:
        prev_month_year = year
        prev_month_month = month - 1
    
    prev_month_start = datetime.date(prev_month_year, prev_month_month, 1)

    categories = Category.objects.filter(household=household)
    
    for category in categories:
        # Check if budget already exists for this month
        budget, created = Budget.objects.get_or_create(
            category=category,
            start_date=start_date,
            defaults={
                'amount': 0,
                'end_date': end_date
            }
        )
        
        if created or force_update:
            # Set is_paid based on payment_type (only if created, to avoid resetting paid status on update?)
            # User said "populate... figures", implying amounts. 
            # Resetting is_paid might be annoying if they already paid some.
            # Let's only set is_paid if created.
            if created:
                if category.payment_type in ['AUTO', 'INCOME']:
                    budget.is_paid = True
                else:
                    budget.is_paid = False
            
            # Rollover logic
            if category.is_persistent:
                # Try to find previous month's budget
                prev_budget = Budget.objects.filter(
                    category=category,
                    start_date=prev_month_start
                ).first()
                
                if prev_budget:
                    budget.amount = prev_budget.amount
                    budget.save()
