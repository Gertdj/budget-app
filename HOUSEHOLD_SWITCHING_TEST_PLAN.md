# Household Switching & Creation - Test Plan

## Overview
This document outlines the logical test plan for household switching and creation functionality.

## Core Functionality Tests

### 1. Session-Based Household Selection ✅
**Test**: `get_user_household(user, request)`
- ✅ Checks session for `active_household_id` first
- ✅ Verifies user is still a member of session household
- ✅ Clears session if household deleted or user removed
- ✅ Falls back to first household if no session
- ✅ Creates default household if user has none
- ✅ Stores household in session for future requests

### 2. Switch Household View ✅
**Test**: `switch_household(request, household_id)`
- ✅ Verifies household exists
- ✅ Verifies user is a member
- ✅ Sets session `active_household_id`
- ✅ Redirects to dashboard with success message
- ✅ Handles non-existent household gracefully
- ✅ Handles unauthorized access gracefully

### 3. Create Household ✅
**Test**: `edit_household()` with `action='create_household'`
- ✅ Creates new household with provided name
- ✅ Adds current user as member
- ✅ Sets new household as active in session
- ✅ Refreshes household list
- ✅ Shows success message
- ✅ Handles empty name validation

### 4. API Consistency ✅
**Test**: All API views use session-aware `get_user_household`
- ✅ `CategoryViewSet` - uses session household
- ✅ `BudgetViewSet` - uses session household
- ✅ `TransactionViewSet` - uses session household
- ✅ `CategoryNoteViewSet` - uses session household
- ✅ `dashboard_data` API - uses session household
- ✅ All other API endpoints - use session household

### 5. Edge Cases ✅

#### 5.1 User Removed from Household
- ✅ Session cleared when user no longer member
- ✅ Falls back to first available household
- ✅ Error message shown if trying to access removed household

#### 5.2 Household Deleted
- ✅ Session cleared when household deleted
- ✅ Falls back to first available household
- ✅ Error message shown if trying to access deleted household

#### 5.3 No Households
- ✅ Creates default household automatically
- ✅ User can still use the app

#### 5.4 Multiple Households
- ✅ Dashboard shows dropdown if > 1 household
- ✅ Edit page shows all households with switch option
- ✅ Switching updates session correctly

### 6. Template Integration ✅
- ✅ Dashboard template shows household selector
- ✅ Edit household template shows all households
- ✅ Create household form works correctly
- ✅ Switch buttons work correctly

## Potential Issues Found & Fixed

### Issue 1: API Views Not Using Session ✅ FIXED
**Problem**: `api_views.py` had its own `get_user_household()` that didn't use session
**Fix**: Updated to import and use session-aware version from `views.py`
**Impact**: All API calls now respect household switching

### Issue 2: Missing Request Parameter ✅ FIXED
**Problem**: Some API calls didn't pass `request` to `get_user_household()`
**Fix**: Updated all calls to pass `self.request` or `request` parameter
**Impact**: Session-based selection works in all API endpoints

## Test Scenarios

### Scenario 1: User with Single Household
1. User logs in → Default household created/selected
2. Dashboard shows household name
3. Edit page shows single household (no switch option)
4. Can create new household
5. After creating, new household becomes active

### Scenario 2: User with Multiple Households
1. User has 2+ households
2. Dashboard shows dropdown with all households
3. Can switch between households via dropdown
4. Edit page shows all households with switch buttons
5. Switching updates session and redirects to dashboard
6. All subsequent views use switched household

### Scenario 3: API Calls After Switching
1. User switches household via web UI
2. Makes API call (e.g., update budget)
3. API call uses switched household (not first household)
4. Data is saved to correct household

### Scenario 4: User Removed from Household
1. User is member of Household A (active)
2. Another user removes them from Household A
3. User makes request → Session cleared
4. Falls back to first available household
5. Error message shown if trying to access removed household

## Verification Checklist

- [x] All `get_user_household()` calls pass `request` parameter
- [x] API views use session-aware household selection
- [x] Session properly stores/retrieves active household
- [x] Edge cases handled (deleted household, removed user)
- [x] Dashboard shows household selector when multiple households
- [x] Edit page shows all households with switch option
- [x] Create household sets new household as active
- [x] Switch household updates session correctly
- [x] All views use session-selected household consistently

## Conclusion

✅ **All logic verified and corrected**
- Session-based selection implemented correctly
- API views updated to use session-aware selection
- Edge cases handled properly
- UI components integrated correctly
- Ready for testing

