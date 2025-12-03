import os
import django
import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'budget_app.settings')
django.setup()

from finance.models import Category, Budget
from finance.utils import open_budget_month

def test_rollover():
    print("Setting up test data...")
    # Clean up
    Category.objects.all().delete()
    Budget.objects.all().delete()

    # Create categories
    cat_persistent = Category.objects.create(name="Persistent Cat", is_persistent=True)
    cat_cleared = Category.objects.create(name="Cleared Cat", is_persistent=False)

    # Set budget for Jan 2024
    jan_start = datetime.date(2024, 1, 1)
    jan_end = datetime.date(2024, 1, 31)
    
    Budget.objects.create(category=cat_persistent, amount=100, start_date=jan_start, end_date=jan_end)
    Budget.objects.create(category=cat_cleared, amount=200, start_date=jan_start, end_date=jan_end)

    print("Opening Feb 2024...")
    open_budget_month(2024, 2)

    # Verify Feb budgets
    feb_start = datetime.date(2024, 2, 1)
    
    feb_persistent = Budget.objects.get(category=cat_persistent, start_date=feb_start)
    feb_cleared = Budget.objects.get(category=cat_cleared, start_date=feb_start)

    print(f"Persistent Category Feb Amount: {feb_persistent.amount} (Expected: 100)")
    print(f"Cleared Category Feb Amount: {feb_cleared.amount} (Expected: 0)")

    assert feb_persistent.amount == 100, "Persistent category failed to rollover"
    assert feb_cleared.amount == 0, "Cleared category failed to clear"
    
    print("SUCCESS: Rollover logic verified!")

if __name__ == "__main__":
    test_rollover()
