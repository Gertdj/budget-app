import os
import django
from django.test import RequestFactory

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'budget_app.settings')
django.setup()

from finance.views import yearly_budget_view
from finance.models import Category

def test_view_context():
    factory = RequestFactory()
    request = factory.get('/budget/yearly/')
    
    # Ensure we have some categories
    if not Category.objects.exists():
        Category.objects.create(name="Income Test", type="INCOME")
        Category.objects.create(name="Expense Test", type="EXPENSE")

    response = yearly_budget_view(request)
    
    # Check context
    # Note: response.context_data is available if using TemplateResponse, 
    # but render() returns HttpResponse. 
    # However, we can inspect the content or just ensure it runs without error.
    # To properly check context, we'd need to mock render or use the test client.
    
    print("View executed successfully.")
    print(f"Status Code: {response.status_code}")
    
    # Let's use the test client to inspect context
    from django.test import Client
    client = Client()
    response = client.get('/budget/yearly/')
    
    content = response.content.decode('utf-8')
    
    assert '<h3 class="mt-4">Income</h3>' in content, "Income header missing"
    assert '<h3 class="mt-4">Expenses</h3>' in content, "Expenses header missing"
    
    # Check for highlighting
    # We expect at least one cell to be highlighted if we have non-persistent categories with 0 budget
    # In our test setup, we created categories but didn't set budgets, so they should be 0.
    # We didn't explicitly set is_persistent, so it defaults to False.
    # So we expect highlighting.
    
    assert 'table-warning' in content, "Highlighting class 'table-warning' missing"
    
    print("HTML content verified. Income/Expenses sections and highlighting present.")

if __name__ == "__main__":
    test_view_context()
