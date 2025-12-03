# Barebones Emergency Budget Template - Design

## Overview

The Barebones Emergency Budget template is an **amount-only template** that adjusts budget amounts for a specific month to reflect essential-only spending. It does NOT create new categories - it works with your existing category structure.

## Design Approach

### ✅ Recommended: Apply to Specific Month from Budget Page

**How it works:**
1. User is on the Budget page (yearly view)
2. User selects a month (e.g., January 2026)
3. User clicks "Apply Barebones Template" button (in month header or dropdown)
4. System identifies essential vs non-essential categories
5. System adjusts budget amounts for that month only:
   - **Essential categories**: Keep current amounts (or set to minimum if needed)
   - **Non-essential categories**: Reduce to 0 or minimal amounts
6. User can still manually edit after applying

### Key Design Decisions

#### 1. **Based on User's Current Categories** (Not Base Template)
- ✅ Works with whatever categories the user has
- ✅ Respects user's custom category structure
- ✅ No assumptions about category names

#### 2. **Month-Specific Application**
- ✅ Applies to ONE month at a time
- ✅ Doesn't affect other months
- ✅ User can apply to multiple months if needed (one at a time)

#### 3. **Essential vs Non-Essential Logic**

**Essential Categories** (Keep/Reduce minimally):
- Housing (Rent/Bond, Rates & Taxes, Home Insurance)
- Utilities (Electricity, Water, Internet, Mobile)
- Groceries
- Healthcare (Medical Aid, Medication)
- Debt (Minimum payments only)
- Transport (Fuel/Public Transport - minimal)
- Car Insurance

**Non-Essential Categories** (Zero out):
- Eating Out
- Entertainment
- Subscriptions (Netflix, Spotify, etc.)
- Lifestyle expenses
- Non-essential savings (keep Emergency Fund, reduce others)
- Short-term Goals savings
- Investments (optional - user choice)

**Income Categories**:
- Keep all income as-is (don't reduce income)

#### 4. **Smart Reduction Logic**

For essential categories, we can:
- **Option A**: Keep current amounts (if already minimal)
- **Option B**: Reduce by percentage (e.g., 20% reduction)
- **Option C**: Set to user-defined minimums

For non-essential:
- Set to 0 (or very minimal like R100 buffer)

## User Interface

### Option 1: Button in Month Header
```
[January] [🔄 Initiate/Reset] [⚡ Barebones]
```

### Option 2: Dropdown Menu
```
[January] [🔄 Initiate/Reset] [📋 Templates ▼]
  - Apply Barebones Template
  - (Future: Holiday Template, etc.)
```

### Option 3: Modal Dialog
- Click button → Modal opens
- Shows what will be changed
- Preview of essential vs non-essential
- Confirm button

## Implementation Details

### Category Classification

We can identify essential categories by:
1. **Category name matching** (keywords: "Rent", "Bond", "Electricity", "Groceries", etc.)
2. **Category type** (all INCOME kept, EXPENSE/SAVINGS evaluated)
3. **Payment type** (AUTO payment types are usually essential)
4. **User tags** (future: let users mark categories as essential/non-essential)

### Template Application Function

```python
def apply_barebones_template(household, year, month):
    """
    Apply barebones template to a specific month
    - Identifies essential vs non-essential categories
    - Adjusts budget amounts accordingly
    - Only affects the specified month
    """
    # Get all categories for household
    # Classify as essential/non-essential
    # Get/create budgets for that month
    # Update amounts
    # Return summary of changes
```

## Example Workflow

1. User has a normal January budget:
   - Rent: R5000
   - Groceries: R2000
   - Eating Out: R800
   - Entertainment: R500
   - Subscriptions: R300

2. User applies Barebones template to January:
   - Rent: R5000 (kept - essential)
   - Groceries: R1500 (reduced 25% - essential but minimized)
   - Eating Out: R0 (zeroed - non-essential)
   - Entertainment: R0 (zeroed - non-essential)
   - Subscriptions: R0 (zeroed - non-essential)

3. User can still manually adjust after applying

## Questions to Decide

1. **Reduction Strategy**: 
   - Keep current amounts for essential?
   - Reduce by percentage?
   - Set to fixed minimums?

2. **Savings Categories**:
   - Zero out all savings?
   - Keep Emergency Fund only?
   - Reduce by percentage?

3. **Debt Payments**:
   - Keep minimum payments only?
   - Keep full payment amounts?

4. **Confirmation**:
   - Show preview before applying?
   - Require confirmation?
   - Allow undo?

5. **Multiple Months**:
   - Apply to one month at a time?
   - Or allow range selection (e.g., Jan-Mar)?

## Recommended Defaults

- **Essential categories**: Keep current amounts (user already set them)
- **Non-essential categories**: Zero out
- **Savings**: Keep Emergency Fund, zero others
- **Debt**: Keep minimum payments (full amount if already set)
- **Show preview**: Yes, with confirmation
- **One month at a time**: Yes (simpler, less error-prone)

