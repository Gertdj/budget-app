#!/usr/bin/env python
"""
Test user flow: Registration -> Login -> Dashboard -> Base Template
Run with: docker-compose exec web python test_user_flow.py
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'budget_app.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from finance.models import Household, Category

def test_registration_flow():
    """Test the complete registration and first login flow"""
    print("\n=== Testing Registration Flow ===")
    client = Client()
    
    try:
        # Test 1: Access register page
        response = client.get('/register/')
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print("✓ Register page accessible")
        
        # Test 2: Register a new user
        test_username = 'flow_test_user'
        test_password = 'TestPass123!'
        
        # Delete if exists
        User.objects.filter(username=test_username).delete()
        
        response = client.post('/register/', {
            'username': test_username,
            'password1': test_password,
            'password2': test_password,
        })
        
        # Should redirect to dashboard after registration
        assert response.status_code == 302, f"Expected redirect (302), got {response.status_code}"
        assert response.url == '/', "Should redirect to dashboard"
        print("✓ User registration successful")
        
        # Test 3: Check household was created
        user = User.objects.get(username=test_username)
        household = user.households.first()
        assert household is not None, "Household should be created"
        print(f"✓ Household created: {household.name}")
        
        # Test 4: Access dashboard (should be logged in)
        response = client.get('/')
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print("✓ Dashboard accessible after registration")
        
        # Test 5: Check base template was applied
        categories = Category.objects.filter(household=household)
        assert categories.exists(), "Base template should create categories"
        print(f"✓ Base template applied: {categories.count()} categories created")
        
        # Test 6: Logout
        response = client.get('/logout/')
        assert response.status_code == 302, "Should redirect after logout"
        print("✓ Logout successful")
        
        # Test 7: Try accessing dashboard (should redirect to login)
        response = client.get('/')
        assert response.status_code == 302, "Should redirect to login"
        assert '/login' in response.url, "Should redirect to login page"
        print("✓ Dashboard protected (requires login)")
        
        return True
    except AssertionError as e:
        print(f"✗ Assertion failed: {e}")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_login_flow():
    """Test login flow"""
    print("\n=== Testing Login Flow ===")
    client = Client()
    
    try:
        # Create a test user
        test_username = 'login_test_user'
        test_password = 'TestPass123!'
        
        user, created = User.objects.get_or_create(
            username=test_username,
            defaults={'email': 'login@test.com'}
        )
        if created:
            user.set_password(test_password)
            user.save()
            # Create household
            household = Household.objects.create(name=f"{user.username}'s Household")
            household.members.add(user)
        
        # Test 1: Access login page
        response = client.get('/login/')
        assert response.status_code == 200, "Login page should be accessible"
        print("✓ Login page accessible")
        
        # Test 2: Login with correct credentials
        response = client.post('/login/', {
            'username': test_username,
            'password': test_password,
        })
        assert response.status_code == 302, "Should redirect after login"
        assert response.url == '/', "Should redirect to dashboard"
        print("✓ Login successful")
        
        # Test 3: Access dashboard while logged in
        response = client.get('/')
        assert response.status_code == 200, "Dashboard should be accessible"
        print("✓ Dashboard accessible after login")
        
        # Test 4: Login with wrong password
        client.logout()
        response = client.post('/login/', {
            'username': test_username,
            'password': 'wrongpassword',
        })
        assert response.status_code == 200, "Should stay on login page"
        print("✓ Invalid login rejected")
        
        return True
    except AssertionError as e:
        print(f"✗ Assertion failed: {e}")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_protected_views():
    """Test that protected views require authentication"""
    print("\n=== Testing Protected Views ===")
    client = Client()
    
    try:
        protected_urls = [
            '/',
            '/categories/',
            '/budget/yearly/',
            '/budget/outstanding/',
        ]
        
        for url in protected_urls:
            response = client.get(url)
            assert response.status_code == 302, f"{url} should redirect when not logged in"
            assert '/login' in response.url, f"{url} should redirect to login"
        print(f"✓ All {len(protected_urls)} protected views require authentication")
        
        return True
    except AssertionError as e:
        print(f"✗ Assertion failed: {e}")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_navigation():
    """Test navigation links"""
    print("\n=== Testing Navigation ===")
    client = Client()
    
    try:
        # Test logged out navigation
        response = client.get('/login/')
        assert response.status_code == 200
        # Check that login/register links are present
        content = response.content.decode()
        assert 'Register' in content or 'register' in content.lower()
        print("✓ Navigation shows login/register when logged out")
        
        # Test logged in navigation
        test_username = 'nav_test_user'
        test_password = 'TestPass123!'
        
        user, created = User.objects.get_or_create(
            username=test_username,
            defaults={'email': 'nav@test.com'}
        )
        if created:
            user.set_password(test_password)
            user.save()
            household = Household.objects.create(name=f"{user.username}'s Household")
            household.members.add(user)
        
        client.login(username=test_username, password=test_password)
        response = client.get('/')
        assert response.status_code == 200
        content = response.content.decode()
        assert 'Logout' in content or 'logout' in content.lower()
        print("✓ Navigation shows logout when logged in")
        
        return True
    except AssertionError as e:
        print(f"✗ Assertion failed: {e}")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all user flow tests"""
    print("=" * 60)
    print("Finance Flow - User Flow Testing")
    print("=" * 60)
    
    results = []
    
    results.append(("Registration Flow", test_registration_flow()))
    results.append(("Login Flow", test_login_flow()))
    results.append(("Protected Views", test_protected_views()))
    results.append(("Navigation", test_navigation()))
    
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
        print("✓ All user flow tests passed!")
        return 0
    else:
        print("✗ Some tests failed")
        return 1

if __name__ == '__main__':
    sys.exit(main())

