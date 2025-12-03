# Finance Flow - Complete User Manual

## Table of Contents
1. [Getting Started](#getting-started)
2. [Application Overview](#application-overview)
3. [User Authentication](#user-authentication)
4. [Dashboard](#dashboard)
5. [Budget Planning](#budget-planning)
6. [Category Management](#category-management)
7. [Category Notes](#category-notes)
8. [Outstanding Payments](#outstanding-payments)
9. [Budget Templates](#budget-templates)
10. [Admin Features](#admin-features)
11. [Features and Functionality](#features-and-functionality)
12. [User Workflows](#user-workflows)
13. [Tips and Best Practices](#tips-and-best-practices)
14. [Troubleshooting](#troubleshooting)

---

## Getting Started

### Prerequisites
- Docker and Docker Compose installed on your system
- A web browser (Chrome, Firefox, Safari, or Edge)

### Starting the Application

**1. Navigate to the project directory:**
```bash
cd /Users/gert/projects/Budget
```

**2. Start the Docker container:**
```bash
docker-compose up --build
```

This command will:
- Build the Docker image if it doesn't exist
- Start the web server
- Make the application available at `http://localhost:8000`

**3. Run database migrations (first time only):**
If this is your first time running the application, you need to set up the database:
```bash
docker-compose exec web python manage.py migrate
```

**4. Create a superuser (optional, for admin access):**
```bash
docker-compose exec web python manage.py createsuperuser
```

**5. Access the application:**
Open your web browser and navigate to:
- **Main Application**: http://localhost:8000/
- **Login Page**: http://localhost:8000/login/
- **Admin Panel** (superuser only): http://localhost:8000/admin/

### Docker Commands Reference

**Start the application:**
```bash
docker-compose up
```

**Start in background (detached mode):**
```bash
docker-compose up -d
```

**Stop the application:**
```bash
docker-compose down
```

**View application logs:**
```bash
docker-compose logs -f web
```

**Restart after code changes:**
```bash
docker-compose restart web
```

**Access Django shell (for advanced users):**
```bash
docker-compose exec web python manage.py shell
```

**Create a superuser (for admin access):**
```bash
docker-compose exec web python manage.py createsuperuser
```

**Populate default budget template (first time only):**
```bash
docker-compose exec web python manage.py populate_default_template
```

**Complete reset (removes all data):**
```bash
docker-compose down -v  # Remove volumes
docker-compose up --build  # Rebuild and start
docker-compose exec web python manage.py migrate  # Re-run migrations
```

---

## Application Overview

**Finance Flow** is a Django-based household budget planning application focused on **planning** monthly budgets and **tracking** payment status. Unlike traditional expense trackers, this application doesn't require you to enter every transaction - it focuses on planning your budget and tracking which bills you've paid.

### Key Philosophy
- **Plan, Don't Track**: Focus on planning your budget, not recording every transaction
- **Your Bank Tracks Transactions**: Let your bank statement handle transaction history
- **Simple Payment Tracking**: Use checkboxes to mark bills as paid
- **Automatic Calculations**: Parent categories automatically sum from their children

### Main Navigation
The application has four main sections accessible from the top navigation bar:
1. **Dashboard** - Overview of your financial summary
2. **Budget** - Yearly budget planning view
3. **Outstanding** - View and track unpaid bills
4. **Categories** - Manage your income, expense, and savings categories

**Additional Features:**
- **User Authentication** - Login, Register, and Logout
- **Category Notes** - Add time-stamped notes to categories
- **Budget Templates** - Database-driven templates for new users
- **Admin Panel** - System administration (superuser only)

---

## User Authentication

Finance Flow requires user authentication to access your budget data. Each user has their own household with isolated financial data.

### Registration

**First Time Users:**
1. Navigate to http://localhost:8000/register/
2. Fill in the registration form:
   - **Username**: Choose a unique username
   - **Password**: Create a strong password
   - **Confirm Password**: Re-enter your password
3. Click **"Register"**
4. You'll be automatically logged in and redirected to the Dashboard
5. A default household is created for you
6. The **Basic Starter Template** is automatically applied, creating common categories

### Login

**Returning Users:**
1. Navigate to http://localhost:8000/login/
2. Enter your username and password
3. Click **"Login"**
4. You'll be redirected to the Dashboard

### Logout

- Click **"Logout (username)"** in the top navigation bar
- You'll be logged out and redirected to the login page

### Household System

- Each user has a **Household** - a budget group that can be shared with multiple users
- By default, each user gets their own household named "{username}'s Household"
- Households can have multiple members (for shared budgets)
- All categories, budgets, and transactions are linked to a household
- Data is isolated between households

---

## Dashboard

The Dashboard is your main overview page, showing a financial summary for the selected month.

### Accessing the Dashboard
- Click **"Finance Flow"** in the top-left corner, or
- Click **"Dashboard"** in the navigation menu

### Dashboard Features

#### 1. Month Selector
At the top of the dashboard, you'll find navigation buttons:
- **Previous** - Go to the previous month
- **Current Month Display** - Shows the active month (e.g., "January 2024")
- **Next** - Go to the next month

**Note**: The selected month/year is synchronized across the entire application. When you change the month on the dashboard, the Budget page will automatically show the same year.

#### 2. Financial Summary Cards
Four summary cards display your key financial metrics:

- **Total Income** (Green) - Sum of all income categories
- **Total Expenses** (Red) - Sum of all expense categories
- **Total Savings** (Teal/Blue) - Sum of all savings and investment categories
- **Balance** (Orange) - Calculated as: Income - Expenses - Savings
  - If balance is negative, you'll see a warning: "⚠️ Over-allocated!"

**All amounts display with thousand separators** (e.g., R 1,234.56)

#### 3. Outstanding Payments Alert
If you have unpaid manual expenses for the month, a yellow alert box appears at the top:
- Shows the count of outstanding payments
- Includes a link to view all outstanding payments
- Disappears when all payments are marked as paid

#### 4. Category Breakdown Tables
Three side-by-side tables show detailed breakdowns:

**Income Table** (Green header):
- Lists all income categories
- Shows budgeted amount for each category
- Categories are clickable and link to the Budget page

**Expenses Table** (Red header):
- Lists all expense categories
- Shows budgeted amount for each category
- Categories are clickable and link to the Budget page

**Savings & Investments Table** (Teal header):
- Lists all savings and investment categories
- Shows budgeted amount for each category
- Categories are clickable and link to the Budget page

#### 5. Visual Charts
Two charts provide visual representation of your budget:

**Budget Overview Chart** (Bar Chart):
- Compares Income, Expenses, and Savings side-by-side
- Y-axis shows amounts with thousand separators
- Tooltips display formatted amounts when hovering

**Income Allocation Chart** (Multi-layered Donut Chart):
- Shows expenses and savings in relation to total income
- Grouped legend showing:
  - **Expenses**: Total expenses with percentage of income
  - **Savings & Investments**: Total savings with percentage of income
  - **Remaining**: Unallocated income after expenses and savings
  - **Total Income**: Reference line showing total income
- Center text displays key metrics
- Color-coded: Red tones for expenses, Teal/Blue for savings
- Tooltips show detailed breakdowns with percentages
- Chart height: 400px for optimal viewing

Both charts provide visual insights into your budget allocation.

---

## Budget Planning

The Budget page is where you plan and manage your monthly budgets for the entire year.

### Accessing the Budget Page
- Click **"Budget"** in the top navigation menu
- The page automatically shows the year matching your dashboard's active date

### Budget Page Layout

#### Left Sidebar Menu
A compact sidebar on the left allows you to switch between three sections:
- **💰 Income** - View and edit income categories
- **💳 Expenses** - View and edit expense categories (default view)
- **💎 Savings & Investments** - View and edit savings categories

Click any menu item to switch sections.

#### Main Content Area
The main area displays a 12-month grid showing:
- **Category names** in the leftmost column
- **12 month columns** (January through December)
- **Active month highlighted in blue** - matches the month selected on the dashboard

### Understanding the Budget Grid

#### Category Types

**Parent Categories with Children:**
- Displayed in **bold** with a **▶ arrow icon**
- Click the category name to expand/collapse sub-categories
- **Not directly editable** - amounts are automatically calculated from children
- Show the sum of all child category amounts
- When expanded, children appear indented below

**Standalone Parent Categories:**
- Displayed in **bold** without an arrow
- **Directly editable** - you can enter amounts
- No children, so you manage the amount directly

**Sub-Categories (Children):**
- Displayed with indentation (4 spaces)
- **Always editable** - click any cell to enter/update amounts
- Hidden by default when parent is collapsed

#### Color Coding

**Blue Cells (`table-info`):**
- Indicates the **active month** (the month you're currently viewing on the dashboard)
- Applied to the entire column for that month
- Makes it easy to see which month you're working with

**Yellow Cells (`table-warning`):**
- Indicates **non-persistent categories with zero budget**
- Serves as a reminder to budget for these categories
- Only appears on editable cells (not parent totals)

**Gray Background:**
- Parent category cells have a light gray background
- Helps distinguish parent totals from editable cells

### Editing Budget Amounts

#### How to Edit
1. **Click any editable cell** (sub-categories or standalone parents)
2. A text input field appears with the current amount
3. **All text is automatically selected** - you can immediately type a new value
4. Enter the new amount (e.g., "5000" or "5000.50")
5. Press **Enter** or click outside the cell to save
6. The cell updates with a green flash to confirm the save

#### Automatic Parent Updates
- When you edit a sub-category amount, the parent category total **automatically recalculates**
- No page refresh needed - updates happen instantly
- Parent totals are always the sum of their children

#### Payment Status Indicators

**For Manual Payment Types:**
- **Checkbox** appears on the right side of the cell
- Check the box when you've paid the bill
- Uncheck if you need to mark it as unpaid
- Checkbox state is saved immediately

**For Auto Payment Types:**
- **✓ checkmark** appears (gray, small) indicating it's automatically marked as paid
- No action needed from you

**For Income Categories:**
- Automatically marked as paid (no indicator shown)

### Initiate/Reset Month Feature

Each active month column has a **"🔄 Reset"** button in the column header (right-aligned).

**What it does:**
- **Imports persistent data** from the previous month
- **Resets the month** by copying budget amounts from categories marked as "persistent"
- Only affects categories where `is_persistent = True`
- Non-persistent categories are set to 0

**When to use it:**
- At the start of a new month
- When you want to reset a month's budgets
- To quickly populate recurring expenses

**How to use:**
1. Navigate to the month you want to initiate/reset
2. Click the **"🔄 Reset"** button in that month's column header
3. A confirmation modal appears explaining what will happen
4. Click **"Yes, Reset Month"** to confirm
5. The page refreshes with persistent budgets imported

**Warning**: This action cannot be undone. All current amounts for the month will be overwritten.

### Barebones Emergency Budget Template

Each active month column also has a **"⚡ Barebones"** button next to the Reset button.

**What it does:**
- Applies an emergency budget template to the selected month
- **Essential categories** (marked as essential) keep their current amounts
- **Non-essential categories** (marked as non-essential) are set to 0
- Income categories remain unchanged

**When to use it:**
- During financial emergencies
- When you need to cut back to essential spending only
- To quickly create a minimal budget

**How to use:**
1. Navigate to the month you want to apply the template
2. Click the **"⚡ Barebones"** button in that month's column header
3. A confirmation modal appears explaining what will happen
4. Click **"Yes, Apply Barebones Template"** to confirm
5. Non-essential categories are zeroed out

**To revert**: Use the Reset button to import from the previous month, or manually edit amounts back.

### Year Navigation

At the top of the Budget page:
- **Previous Year** button - Navigate to the previous year
- **Current Year Display** - Shows the active year
- **Next Year** button - Navigate to the next year

**Synchronization**: The year automatically matches your dashboard's active date when you first open the Budget page.

---

## Category Management

The Categories page allows you to organize your income, expense, and savings categories.

### Accessing Category Management
- Click **"Categories"** in the top navigation menu

### Category Types

The page is organized into three sections:

1. **Income Categories** (💰 Green)
   - All sources of income
   - Examples: Salary, Freelance, Investments, Rental Income

2. **Expense Categories** (💳 Red)
   - All spending categories
   - Examples: Rent, Groceries, Utilities, Transportation

3. **Savings & Investments** (💎 Teal)
   - Savings goals and investment categories
   - Examples: Emergency Fund, Retirement, Stocks, Bonds

### Category Structure

Categories can be organized hierarchically:
- **Parent Categories** - Main category groups (e.g., "Living Expenses")
- **Sub-Categories** - Specific items under parents (e.g., "Rent", "Utilities" under "Living Expenses")

### Category Properties

Each category has the following properties:

**Name:**
- The display name of the category
- Examples: "Groceries", "Electricity", "Salary"

**Type:**
- **INCOME** - Money coming in
- **EXPENSE** - Money going out
- **SAVINGS** - Money being saved or invested

**Payment Type:**
- **AUTO** - Automatic payments (debit orders, subscriptions)
  - Automatically marked as paid
  - No tracking needed
- **MANUAL** - Manual payments (bills you pay yourself)
  - Requires checkbox tracking
  - Appears in Outstanding Payments
- **INCOME** - Income sources
  - Automatically marked as received
  - No tracking needed

**Is Persistent:**
- **Yes** - Budget amount carries over to next month automatically
- **No** - Budget amount resets to zero each month
- Use for recurring expenses (rent, subscriptions, etc.)

**Is Essential:**
- **Yes (Essential)** - Category is considered essential spending
  - Keeps current amount when applying Barebones template
  - Default for all new categories (for safety)
- **No (Non-Essential)** - Category is considered non-essential spending
  - Set to 0 when applying Barebones template
  - Examples: Entertainment, Eating Out, Subscriptions

### Managing Categories

#### Adding a New Category

1. Click **"Add New Category"** button
2. Fill in the form:
   - **Name**: Enter the category name
   - **Type**: Select Income, Expense, or Savings
   - **Payment Type**: Select how this category is paid/received
   - **Is Persistent**: Check if this should carry over monthly
3. Click **"Save"**

#### Adding Multiple Sub-Categories (Bulk Add)

1. Click **"Bulk Add Sub-categories"** button
2. Select the **Parent Category** (dropdown shows only top-level categories)
3. Enter category names, **one per line** in the text area
4. Set **Payment Type** for all categories being added
5. Check **"Is Persistent"** if all should be persistent
6. Click **"Save"**
7. All categories are created as sub-categories under the selected parent

#### Editing a Category

1. Find the category in the list
2. Click the **✏️ Edit** icon next to the category name
3. Modify any properties (name, type, payment type, persistence)
4. Click **"Save"**

#### Deleting a Category

1. Click the **✏️ Edit** icon next to the category
2. Scroll to the bottom and click **"Delete"**
3. Confirm the deletion

**Note**: Categories with existing budgets cannot be deleted. You must first remove all budget entries for that category.

#### Reorganizing Categories (Drag and Drop)

**Desktop Only Feature:**
1. Expand the parent category you want to move from
2. Click and hold on a sub-category name
3. Drag it to the target parent category
4. Release to drop
5. The sub-category is moved immediately

**Note**: You can only move sub-categories, not parent categories. You can only move to other parent categories, not to other sub-categories.

### Collapsible Interface

- **Click any parent category name** to expand/collapse its sub-categories
- **Expand All** button - Expands all parent categories
- **Collapse All** button - Collapses all parent categories
- **State is remembered** - Your browser remembers which categories were expanded

### Persistent Badge

Categories marked as persistent display a badge indicating they will auto-import each month.

### Category Notes

Each category (parent and sub-categories) has a **notes icon** (📝) next to its name.

**Features:**
- **Time-stamped notes** - Each note shows when it was created
- **Author tracking** - Shows who created each note
- **Not month-specific** - Notes are linked to the category, not a budget month
- **Easy access** - Click the icon to view/add notes
- **Visual indicator** - Badge shows note count when notes exist

**How to use:**
1. Click the **notes icon** (📝) next to any category name
2. A modal opens showing all notes for that category
3. **View existing notes** - See all notes with author and timestamp
4. **Add new note** - Enter text in the textarea and click "Add Note"
5. **Delete notes** - Click the trash icon (only author or superuser can delete)

**Use cases:**
- Reminders about category-specific information
- Notes about payment schedules
- Context that isn't tied to a specific month
- Important details about the category

---

## Category Notes

See [Category Management](#category-management) section above for details on using category notes.

---

## Outstanding Payments

The Outstanding Payments page shows all unpaid manual expenses for the selected month.

### Accessing Outstanding Payments
- Click **"Outstanding"** in the top navigation menu
- Or click the alert link on the Dashboard when payments are outstanding

### Page Features

#### Grouped Display
Payments are organized by parent category:
- Each parent category is a section header
- Sub-categories are listed below with their amounts
- Each group shows a **subtotal**

#### Payment Tracking
- Each unpaid item has a **checkbox**
- Check the box when you've paid the bill
- The item fades out and disappears
- The page automatically updates

#### Grand Total
At the bottom of the page:
- Shows the **total outstanding amount** for the month
- Updates as you check off payments
- Disappears when all payments are complete

#### Success Message
When all payments are marked as paid:
- A success message appears
- The page shows "All payments complete!"
- No items are displayed

### Workflow

1. **View Outstanding Payments**
   - Navigate to the Outstanding Payments page
   - Review all unpaid manual expenses

2. **Pay Bills**
   - As you pay each bill, check its checkbox
   - Items disappear as they're marked paid

3. **Monitor Progress**
   - Watch the grand total decrease
   - See subtotals update for each category group

4. **Complete All Payments**
   - When all checkboxes are checked, you're done for the month
   - The success message confirms completion

---

## Budget Templates

Budget templates define the default category structure for new households. When a new user registers, the default template is automatically applied to create their initial categories.

### Template System Overview

- **Database-driven** - Templates are stored in the database, not hardcoded
- **Multiple templates** - Create different templates for different user types
- **Default template** - One template is marked as default for new users
- **Easy management** - Superusers can create, edit, and manage templates via the admin UI

### Default Template

The **"Basic Starter"** template is automatically applied to new users and includes:
- 4 Income categories (Salary, Bonus, Freelance, Investment Income)
- ~20 Expense categories (Housing, Utilities, Transport, Healthcare, Debt, Lifestyle, etc.)
- 4 Savings categories (Emergency Fund, Retirement, Investments, Short-term Goals)

### Template Management (Superuser Only)

**Access Template Management:**
1. Login as a superuser
2. Click **"Admin"** in the top navigation
3. Select **"Manage Templates"**

**Template List Page:**
- View all available templates
- See template name, description, category count, status
- Identify which template is the default (green "Default" badge)
- Set a template as default (star icon)
- Delete templates (trash icon)
- View template details (eye icon)

**Template Detail Page:**
- View all categories in the template
- See category properties (type, persistence, payment type, essential status)
- View parent-child relationships
- Link to Django Admin for full editing

**Create New Template:**
1. Click **"Create New Template"**
2. Enter template name (required)
3. Enter description (optional)
4. Check **"Set as Default Template"** if this should be used for new users
5. Set **"Active"** status (only active templates can be used)
6. Click **"Create Template"**
7. Use Django Admin to add categories to the template

**Edit Templates:**
- Click **"Edit in Django Admin"** on the template detail page
- Use Django Admin's inline editing to:
  - Add new categories
  - Edit category properties
  - Set parent-child relationships
  - Configure display order
  - Set essential/non-essential status

**Set Default Template:**
- Click the **star icon** next to any template
- Confirm the action
- That template becomes the default for new households
- Only one template can be default at a time

**Template Properties:**
- **Name**: Unique identifier for the template
- **Description**: Helpful text explaining what the template includes
- **Is Default**: If checked, used automatically for new households
- **Is Active**: Only active templates can be used
- **Created By**: User who created the template
- **Created At**: Timestamp of creation

### Template Categories

Each template contains categories with the same properties as regular categories:
- Name, Type (Income/Expense/Savings)
- Is Persistent, Payment Type, Is Essential
- Parent-child relationships
- Display order

When a template is applied to a household, all template categories are created as actual categories for that household.

---

## Admin Features

Superusers have access to additional administrative features through the **"Admin"** dropdown menu.

### Admin Dashboard

**Access**: Admin → Admin Dashboard

**Features:**
- **System Statistics**:
  - Total Users (with count of new users in last 7 days)
  - Total Households
  - Total Categories
  - Total Budgets
- **Top Households by Members** - Shows households with most members
- **Quick Actions** - Links to user management, household management, and Django Admin

### User Management

**Access**: Admin → Manage Users

**Features:**
- View all users in the system
- See user details: username, email, date joined, superuser status
- View which households each user belongs to
- Link to Django Admin for full user editing
- Create new users via Django Admin

### Household Management

**Access**: Admin → Manage Households

**Features:**
- View all households in the system
- See household details: name, members, category count, budget count
- View member preview (first 3 members, with count if more)
- Link to Django Admin for full household editing
- Create new households via Django Admin

### Template Management

**Access**: Admin → Manage Templates

See [Budget Templates](#budget-templates) section above for details.

### Django Admin

**Access**: Admin → Django Admin (opens in new tab)

Full Django admin interface with complete control over:
- All models (Users, Households, Categories, Budgets, Transactions, Templates, Notes)
- Advanced filtering and searching
- Bulk operations
- Inline editing for related objects

---

## Features and Functionality

### Number Formatting
- **All numbers display with thousand separators**
- Format: R 1,234.56 (comma for thousands, period for decimals)
- Applied to:
  - Dashboard summary cards
  - Budget table cells
  - Chart tooltips and labels
  - Outstanding payments amounts

### Session Synchronization
- **Active month/year is stored in your session**
- Changing the month on the Dashboard updates the Budget page
- Navigating between pages maintains the same time period
- The Budget page automatically shows the year matching your dashboard selection

### Automatic Calculations
- **Parent categories automatically sum from children**
- Updates happen instantly when you edit sub-category amounts
- No manual calculation needed
- Applies to:
  - Expense parent categories
  - Savings parent categories
  - Income categories (if structured hierarchically)

### Persistent Budgets
- Categories marked as "persistent" automatically import to the next month
- Use the "Initiate/Reset" button to import persistent budgets
- Saves time on recurring expenses
- Examples: Rent, subscriptions, insurance premiums

### Payment Type Logic

**AUTO Payment Type:**
- Automatically marked as paid
- No checkbox appears
- Shows a ✓ indicator
- Examples: Debit orders, automatic subscriptions

**MANUAL Payment Type:**
- Requires manual tracking
- Checkbox appears for tracking
- Appears in Outstanding Payments when unpaid
- Examples: Utility bills, credit card payments

**INCOME Payment Type:**
- Automatically marked as received
- No tracking needed
- Examples: Salary, freelance income

### Collapsible Interface
- **Parent categories can be expanded/collapsed**
- Saves screen space
- State is remembered in your browser
- Quick expand/collapse all buttons available

### Responsive Design
- Works on desktop and tablet devices
- Drag-and-drop requires desktop (mouse/trackpad)
- All other features work on mobile devices

---

## User Workflows

### Initial Setup (First Time)

**1. Start the Application**
```bash
cd /Users/gert/projects/Budget
docker-compose up --build
docker-compose exec web python manage.py migrate
```

**2. Create Superuser (Optional)**
```bash
docker-compose exec web python manage.py createsuperuser
```

**3. Populate Default Template (First Time)**
```bash
docker-compose exec web python manage.py populate_default_template
```

**4. Register Your Account**
- Navigate to http://localhost:8000/register/
- Create your user account
- The Basic Starter template is automatically applied
- You'll have common categories ready to use

**5. Review and Customize Categories**
- Navigate to Categories
- Review the automatically created categories
- Add additional categories as needed
- Edit category properties (persistent, payment type, essential status)
- Organize into parent/child structure as needed

**6. Set Up First Month's Budget**
- Navigate to Budget page
- Select the current month
- Click cells to enter budget amounts
- Mark categories as persistent if they recur monthly

### Monthly Budget Planning Workflow

**1. Start a New Month**
- Navigate to Dashboard
- Use Previous/Next to select the new month
- Go to Budget page (year syncs automatically)

**2. Initiate the Month**
- Click "🔄 Initiate/Reset" button for the active month
- Persistent budgets are imported from previous month
- Review and adjust amounts as needed

**3. Enter New Budgets**
- Click cells to enter amounts for non-persistent categories
- Edit amounts for categories that changed
- Verify parent totals are correct

**4. Review Dashboard**
- Check the Balance card
- Ensure it's positive (not over-allocated)
- Review category breakdowns

**5. Track Payments Throughout the Month**
- Navigate to Outstanding Payments
- Check off bills as you pay them
- Monitor remaining outstanding amount

### Category Organization Workflow

**1. Create Main Categories**
- Go to Categories
- Add parent categories (e.g., "Living Expenses", "Transportation")

**2. Add Sub-Categories**
- Use "Bulk Add Sub-categories" for efficiency
- Or add individually under each parent
- Set payment types, persistence, and essential status as needed

**3. Organize Structure**
- Use drag-and-drop to move sub-categories
- Edit categories to change properties
- Delete unused categories (if no budgets exist)

**4. Add Category Notes**
- Click the notes icon (📝) next to any category
- Add notes with important information
- Notes are time-stamped and show author

### Payment Tracking Workflow

**1. View Outstanding Payments**
- Click "Outstanding" in navigation
- Or click alert on Dashboard

**2. Pay Bills**
- As you pay each bill, check its checkbox
- Item disappears when marked paid

**3. Monitor Progress**
- Watch grand total decrease
- Review by category group

**4. Complete Month**
- When all payments checked, you're done
- Success message confirms completion

---

## Tips and Best Practices

### Category Organization
1. **Use Hierarchical Structure**
   - Group related expenses under parent categories
   - Makes the budget easier to navigate
   - Example: "Living Expenses" → Rent, Utilities, Groceries

2. **Name Categories Clearly**
   - Use descriptive names
   - Be consistent with naming conventions
   - Examples: "Electricity" not "Elec" or "Power"

3. **Set Payment Types Correctly**
   - AUTO for automatic payments (debit orders)
   - MANUAL for bills you pay yourself
   - INCOME for all revenue sources

### Budget Planning
1. **Use Persistent Budgets Wisely**
   - Mark recurring expenses as persistent
   - Saves time each month
   - Examples: Rent, insurance, subscriptions

2. **Use Essential/Non-Essential Marking**
   - Mark essential categories (housing, utilities, groceries)
   - Mark non-essential categories (entertainment, eating out)
   - Makes Barebones template application more accurate

3. **Plan Ahead**
   - Use the Yearly Budget view to plan multiple months
   - Adjust amounts as needed throughout the year

4. **Review Regularly**
   - Check Dashboard weekly
   - Review Outstanding Payments regularly
   - Adjust budgets based on actual spending

5. **Use Barebones Template When Needed**
   - Apply Barebones template during financial emergencies
   - Quickly reduces non-essential spending to zero
   - Easy to revert using Reset button

### Payment Tracking
1. **Check Outstanding Weekly**
   - Don't wait until month-end
   - Pay bills as they come due
   - Mark as paid immediately

2. **Use the Dashboard Alert**
   - The alert shows count of outstanding payments
   - Click to go directly to Outstanding Payments page

### General Tips
1. **Keep It Simple**
   - Don't over-categorize
   - Group similar items together
   - Focus on major categories

2. **Use the Collapse Feature**
   - Collapse categories you're not working with
   - Expands screen space
   - State is remembered

3. **Leverage Auto-Calculations**
   - Let parent categories sum automatically
   - Only edit sub-categories
   - Verify totals are correct

4. **Sync Across Pages**
   - Use Dashboard month selector
   - Budget page follows automatically
   - Consistent time period across app

5. **Use Category Notes**
   - Add notes to categories for important reminders
   - Notes are not month-specific, so they persist
   - Helpful for payment schedules or special instructions

6. **Mark Categories Correctly**
   - Set essential/non-essential status accurately
   - Makes Barebones template more useful
   - Default is "Essential" for safety

---

## Troubleshooting

### Application Won't Start

**Problem**: Docker container won't start
**Solutions**:
```bash
# Check if port 8000 is already in use
lsof -i :8000

# Stop and restart
docker-compose down
docker-compose up --build

# Check logs for errors
docker-compose logs -f web
```

### Database Issues

**Problem**: Migration errors or database not found
**Solutions**:
```bash
# Run migrations
docker-compose exec web python manage.py migrate

# If that fails, reset database (WARNING: deletes all data)
docker-compose down -v
docker-compose up --build
docker-compose exec web python manage.py migrate
```

### Budget Amounts Not Saving

**Problem**: Changes to budget amounts don't persist
**Solutions**:
- Check browser console for JavaScript errors (F12)
- Verify you're clicking editable cells (not parent totals)
- Ensure you press Enter or click outside the cell
- Check Docker logs: `docker-compose logs -f web`
- Refresh the page and try again

### Parent Totals Not Updating

**Problem**: Parent category totals don't update when editing children
**Solutions**:
- Ensure you're editing a sub-category (indented)
- Check that the parent has children
- Refresh the page
- Check browser console for errors

### Categories Not Expanding/Collapsing

**Problem**: Clicking parent categories doesn't show/hide children
**Solutions**:
- Clear browser cache
- Check browser console for JavaScript errors
- Try a different browser
- Refresh the page

### Drag-and-Drop Not Working

**Problem**: Can't drag sub-categories to reorganize
**Solutions**:
- Ensure you're on a desktop (not mobile)
- Try a different browser
- Refresh the page
- Check that you're dragging sub-categories (not parents)

### Outstanding Count Incorrect

**Problem**: Dashboard shows wrong count of outstanding payments
**Solutions**:
- Refresh the dashboard page
- Verify categories have correct payment types (MANUAL)
- Check that budgets exist for the month
- Navigate to Outstanding Payments to see actual list

### Month/Year Not Syncing

**Problem**: Budget page shows different year than dashboard
**Solutions**:
- Navigate to Dashboard first
- Select the desired month/year
- Then navigate to Budget page
- The year should sync automatically

### Charts Not Displaying

**Problem**: Dashboard charts don't show
**Solutions**:
- Check internet connection (Chart.js loads from CDN)
- Refresh the page
- Check browser console for errors
- Try a different browser

### Numbers Not Formatted

**Problem**: Numbers don't show thousand separators
**Solutions**:
- Refresh the page
- Clear browser cache
- Check that you're viewing the latest version

---

## Technical Details

### Application Architecture
- **Backend**: Django 5.x with Python 3.11
- **Database**: SQLite (stored in `db.sqlite3`)
- **Frontend**: Bootstrap 5, Chart.js, vanilla JavaScript
- **Deployment**: Docker Compose
- **Server**: Django development server (port 8000)

### Key Models

**Household:**
- `name`: Household name
- `members`: Many-to-many relationship with User
- `created_at`: Timestamp
- `updated_at`: Timestamp

**Category:**
- `name`: Category name
- `household`: Foreign key to Household
- `type`: INCOME, EXPENSE, or SAVINGS
- `parent`: Foreign key to parent category (nullable)
- `is_persistent`: Boolean (carries over to next month)
- `payment_type`: AUTO, MANUAL, or INCOME
- `is_essential`: Boolean (for Barebones template)

**Budget:**
- `category`: Foreign key to Category
- `amount`: Decimal (budget amount)
- `start_date`: Date (first day of month)
- `end_date`: Date (last day of month)
- `is_paid`: Boolean (payment status)

**CategoryNote:**
- `category`: Foreign key to Category
- `author`: Foreign key to User
- `note`: Text content
- `created_at`: Timestamp
- `updated_at`: Timestamp

**BudgetTemplate:**
- `name`: Template name (unique)
- `description`: Template description
- `is_default`: Boolean (default template for new users)
- `is_active`: Boolean (only active templates can be used)
- `created_by`: Foreign key to User
- `created_at`: Timestamp
- `updated_at`: Timestamp

**TemplateCategory:**
- `template`: Foreign key to BudgetTemplate
- `name`: Category name
- `type`: INCOME, EXPENSE, or SAVINGS
- `is_persistent`: Boolean
- `payment_type`: AUTO, MANUAL, or INCOME
- `is_essential`: Boolean
- `parent`: Foreign key to parent TemplateCategory (nullable)
- `display_order`: Integer (for ordering)

### Key URLs

**Public:**
- `/login/` - User login
- `/register/` - User registration
- `/logout/` - User logout

**Main Application (requires login):**
- `/` - Dashboard
- `/budget/yearly/` - Yearly Budget View
- `/budget/yearly/<year>/` - Specific year budget
- `/budget/open/<year>/<month>/` - Initiate/Reset month
- `/budget/barebones/<year>/<month>/` - Apply Barebones template
- `/budget/outstanding/` - Outstanding Payments
- `/categories/` - Category Management
- `/categories/<id>/notes/` - Category notes (AJAX)
- `/budget/update/` - AJAX endpoint for budget updates
- `/budget/toggle-payment/` - AJAX endpoint for payment checkboxes

**Admin (superuser only):**
- `/admin/dashboard/` - Admin dashboard
- `/admin/users/` - User management
- `/admin/households/` - Household management
- `/admin/templates/` - Template management
- `/admin/templates/create/` - Create new template
- `/admin/templates/<id>/` - Template detail
- `/admin/` - Django Admin (full access)

### Browser Compatibility
- Chrome (recommended)
- Firefox
- Safari
- Edge
- Mobile browsers (limited drag-and-drop support)

---

## Support and Maintenance

### Regular Maintenance
- **Backup Database**: Copy `db.sqlite3` regularly
- **Update Dependencies**: Check `requirements.txt` for updates
- **Monitor Logs**: Review Docker logs periodically

### Getting Help
1. Check this manual first
2. Review Docker logs for errors
3. Check browser console for JavaScript errors
4. Verify database migrations are current

### Data Backup
To backup your data:
```bash
# Copy the database file
cp db.sqlite3 db.sqlite3.backup
```

To restore:
```bash
# Replace the database file
cp db.sqlite3.backup db.sqlite3
```

---

## Conclusion

Finance Flow is designed to make budget planning simple and payment tracking effortless. By focusing on planning rather than transaction entry, you can manage your finances efficiently without spending hours on data entry.

### Key Features Summary

- **User Authentication** - Secure login and registration
- **Multi-User Support** - Household system for shared budgets
- **Dashboard Overview** - Visual summary with charts
- **Yearly Budget Planning** - Plan 12 months ahead
- **Category Management** - Organize income, expenses, and savings
- **Category Notes** - Time-stamped notes for important information
- **Payment Tracking** - Checkbox-based tracking for manual payments
- **Persistent Budgets** - Auto-import recurring expenses
- **Barebones Template** - Emergency budget feature
- **Budget Templates** - Database-driven templates for new users
- **Admin Features** - Comprehensive administration tools

### Remember:
- **Plan your budget** at the start of each month
- **Track payments** as you pay bills
- **Use persistent budgets** for recurring expenses
- **Mark essential/non-essential** categories correctly
- **Add notes** to categories for important reminders
- **Review regularly** to stay on track
- **Use Barebones template** during financial emergencies

Happy budgeting! 💰
