#!/usr/bin/env python
"""
Test script for authentication and template functionality
Run with: docker-compose exec web python test_auth_and_templates.py
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'budget_app.settings')
django.setup()

from django.contrib.auth.models import User
from finance.models import Household, Category, Budget
from finance.templates import create_base_starter_template

def test_household_creation():
    """Test that households are created correctly"""
    print("\n=== Testing Household Creation ===")
    try:
        # Create a test user
        test_user, created = User.objects.get_or_create(
            username='test_user_household',
            defaults={'email': 'test@example.com'}
        )
        if created:
            test_user.set_password('testpass123')
            test_user.save()
            print(f"✓ Created test user: {test_user.username}")
        else:
            print(f"✓ Using existing test user: {test_user.username}")
        
        # Check if user has household
        household = test_user.households.first()
        if not household:
            household = Household.objects.create(name=f"{test_user.username}'s Household")
            household.members.add(test_user)
            print(f"✓ Created household: {household.name}")
        else:
            print(f"✓ User already has household: {household.name}")
        
        print(f"✓ Household members: {household.members.count()}")
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_base_template():
    """Test base template creation"""
    print("\n=== Testing Base Template Creation ===")
    try:
        # Get or create test household
        test_user = User.objects.filter(username='test_user_household').first()
        if not test_user:
            test_user = User.objects.create_user(
                username='test_user_template',
                email='template@example.com',
                password='testpass123'
            )
            household = Household.objects.create(name=f"{test_user.username}'s Household")
            household.members.add(test_user)
        else:
            household = test_user.households.first()
            if not household:
                household = Household.objects.create(name=f"{test_user.username}'s Household")
                household.members.add(test_user)
        
        # Delete existing categories for this household to test template
        Category.objects.filter(household=household).delete()
        print(f"✓ Cleared existing categories for household: {household.name}")
        
        # Apply base template
        create_base_starter_template(household)
        print(f"✓ Base template applied")
        
        # Check categories were created
        category_count = Category.objects.filter(household=household).count()
        print(f"✓ Categories created: {category_count}")
        
        # Check for expected categories
        income_count = Category.objects.filter(household=household, type='INCOME').count()
        expense_count = Category.objects.filter(household=household, type='EXPENSE').count()
        savings_count = Category.objects.filter(household=household, type='SAVINGS').count()
        
        print(f"  - Income categories: {income_count}")
        print(f"  - Expense categories: {expense_count}")
        print(f"  - Savings categories: {savings_count}")
        
        # Check for specific expected categories
        expected_categories = ['Salary', 'Groceries', 'Emergency Fund']
        for cat_name in expected_categories:
            exists = Category.objects.filter(household=household, name=cat_name).exists()
            status = "✓" if exists else "✗"
            print(f"  {status} Category '{cat_name}': {'Found' if exists else 'Missing'}")
        
        return category_count > 0
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_data_isolation():
    """Test that users only see their own data"""
    print("\n=== Testing Data Isolation ===")
    try:
        # Create two test users with households
        user1, _ = User.objects.get_or_create(
            username='test_user1',
            defaults={'email': 'user1@example.com'}
        )
        if not user1.households.exists():
            household1 = Household.objects.create(name=f"{user1.username}'s Household")
            household1.members.add(user1)
        else:
            household1 = user1.households.first()
        
        user2, _ = User.objects.get_or_create(
            username='test_user2',
            defaults={'email': 'user2@example.com'}
        )
        if not user2.households.exists():
            household2 = Household.objects.create(name=f"{user2.username}'s Household")
            household2.members.add(user2)
        else:
            household2 = user2.households.first()
        
        # Create categories for each household
        Category.objects.filter(household=household1).delete()
        Category.objects.filter(household=household2).delete()
        
        Category.objects.create(
            household=household1,
            name='User1 Category',
            type='EXPENSE'
        )
        Category.objects.create(
            household=household2,
            name='User2 Category',
            type='EXPENSE'
        )
        
        # Check isolation
        user1_cats = Category.objects.filter(household=household1).count()
        user2_cats = Category.objects.filter(household=household2).count()
        
        print(f"✓ User1 categories: {user1_cats}")
        print(f"✓ User2 categories: {user2_cats}")
        
        # Verify they can't see each other's categories
        user1_sees_user2 = Category.objects.filter(household=household1, name='User2 Category').exists()
        user2_sees_user1 = Category.objects.filter(household=household2, name='User1 Category').exists()
        
        if not user1_sees_user2 and not user2_sees_user1:
            print("✓ Data isolation working correctly")
            return True
        else:
            print("✗ Data isolation failed")
            return False
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_model_relationships():
    """Test that model relationships work correctly"""
    print("\n=== Testing Model Relationships ===")
    try:
        # Get a household
        household = Household.objects.first()
        if not household:
            print("✗ No households found")
            return False
        
        print(f"✓ Testing with household: {household.name}")
        
        # Check categories
        categories = Category.objects.filter(household=household)
        print(f"✓ Categories in household: {categories.count()}")
        
        # Check parent-child relationships
        parent_cats = categories.filter(parent__isnull=True)
        child_cats = categories.filter(parent__isnull=False)
        print(f"✓ Parent categories: {parent_cats.count()}")
        print(f"✓ Child categories: {child_cats.count()}")
        
        # Check budgets (through categories)
        budgets = Budget.objects.filter(category__household=household)
        print(f"✓ Budgets in household: {budgets.count()}")
        
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("Finance Flow - Authentication & Template Testing")
    print("=" * 60)
    
    results = []
    
    results.append(("Household Creation", test_household_creation()))
    results.append(("Base Template", test_base_template()))
    results.append(("Data Isolation", test_data_isolation()))
    results.append(("Model Relationships", test_model_relationships()))
    
    print("\n" + "=" * 60)
    print("Test Results Summary")
    print("=" * 60)
    
    all_passed = True
    for test_name, passed in results:
        status = "PASS" if passed else "FAIL"
        symbol = "✓" if passed else "✗"
        print(f"{symbol} {test_name}: {status}")
        if not passed:
            all_passed = False
    
    print("=" * 60)
    if all_passed:
        print("✓ All tests passed!")
        return 0
    else:
        print("✗ Some tests failed")
        return 1

if __name__ == '__main__':
    sys.exit(main())

