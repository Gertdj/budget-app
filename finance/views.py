from django.shortcuts import render, redirect
from django.db.models import Sum
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from decimal import Decimal
from .models import Transaction, Category, Budget, Household, CategoryNote, BudgetTemplate, TemplateCategory
from .forms import TransactionForm, CategoryForm, BulkCategoryForm
from .utils import open_budget_month
from .templates import create_base_starter_template, apply_barebones_template
from .excel_reports import export_yearly_budget, export_monthly_detail, export_category_summary, export_transactions, export_category_setup
import datetime
import calendar

def get_user_household(user):
    """Get the user's primary household (first household they belong to)"""
    if not user.is_authenticated:
        return None
    household = user.households.first()
    if not household:
        # Create a default household if user doesn't have one
        household = Household.objects.create(name=f"{user.username}'s Household")
        household.members.add(user)
    return household

def check_and_apply_base_template(household):
    """Check if household needs base template and apply it if needed
    
    Note: This function is now only used for backward compatibility.
    New registrations handle template application during registration.
    """
    if not household:
        return False
    
    # Check if household already has categories
    if Category.objects.filter(household=household).exists():
        return False  # Already has categories, don't apply template
    
    # Only apply template if household is truly empty (for backward compatibility)
    # This prevents applying template to users who explicitly chose blank registration
    # We check if this is a new household by checking if it was just created
    # For now, we'll skip auto-application and let users choose during registration
    return False

@login_required
def dashboard(request):
    """Show budget summary for active month"""
    # Get active month from session or URL
    year = request.GET.get('year')
    month = request.GET.get('month')

    if year and month:
        try:
            active_date = datetime.date(int(year), int(month), 1)
            request.session['active_date'] = active_date.isoformat()
        except ValueError:
            active_date = datetime.date.today()
    else:
        active_date_str = request.session.get('active_date')
        if active_date_str:
            active_date = datetime.date.fromisoformat(active_date_str)
        else:
            active_date = datetime.date.today()
            request.session['active_date'] = active_date.isoformat()

    year, month = active_date.year, active_date.month
    start_date = active_date.replace(day=1)
    _, last_day = calendar.monthrange(year, month)
    end_date = active_date.replace(day=last_day)

    # Get user's household
    household = get_user_household(request.user)
    if not household:
        return redirect('register')
    
    # Note: Template application is now handled during registration
    # This check is kept for backward compatibility but won't auto-apply
    check_and_apply_base_template(household)

    # Get parent categories only for this household
    income_categories = Category.objects.filter(household=household, type='INCOME', parent__isnull=True).prefetch_related('children').order_by('name')
    expense_categories = Category.objects.filter(household=household, type='EXPENSE', parent__isnull=True).prefetch_related('children').order_by('name')
    savings_categories = Category.objects.filter(household=household, type='SAVINGS', parent__isnull=True).prefetch_related('children').order_by('name')

    # Build income summary (main categories only)
    income_summary = []
    for category in income_categories:
        children = list(category.children.all())
        if children:
            # Sum child budgets
            total = sum(
                Budget.objects.filter(category=child, start_date=start_date).first().amount 
                if Budget.objects.filter(category=child, start_date=start_date).first() else 0
                for child in children
            )
        else:
            # Use own budget
            budget = Budget.objects.filter(category=category, start_date=start_date).first()
            total = budget.amount if budget else 0
        
        income_summary.append({'category': category, 'amount': total})

    # Build expense summary (main categories only)
    expense_summary = []
    for category in expense_categories:
        children = list(category.children.all())
        if children:
            # Sum child budgets
            total = sum(
                Budget.objects.filter(category=child, start_date=start_date).first().amount 
                if Budget.objects.filter(category=child, start_date=start_date).first() else 0
                for child in children
            )
        else:
            # Use own budget
            budget = Budget.objects.filter(category=category, start_date=start_date).first()
            total = budget.amount if budget else 0
        
        expense_summary.append({'category': category, 'amount': total})

    # Build savings summary (main categories only)
    savings_summary = []
    for category in savings_categories:
        children = list(category.children.all())
        if children:
            # Sum child budgets
            total = sum(
                Budget.objects.filter(category=child, start_date=start_date).first().amount 
                if Budget.objects.filter(category=child, start_date=start_date).first() else 0
                for child in children
            )
        else:
            # Use own budget
            budget = Budget.objects.filter(category=category, start_date=start_date).first()
            total = budget.amount if budget else 0
        
        savings_summary.append({'category': category, 'amount': total})

    # Calculate totals
    total_income = sum(item['amount'] for item in income_summary)
    total_expenses = sum(item['amount'] for item in expense_summary)
    total_savings = sum(item['amount'] for item in savings_summary)
    balance = total_income - total_expenses - total_savings

    # Outstanding payments count (manual expenses only, excluding parents with children)
    # Only count sub-categories and standalone parent categories
    unpaid_budgets = Budget.objects.filter(
        category__household=household,
        start_date=start_date,
        is_paid=False,
        category__payment_type='MANUAL',
        category__type='EXPENSE'
    ).select_related('category')
    
    # Filter out parent categories that have children
    unpaid_count = sum(1 for budget in unpaid_budgets if budget.category.parent or not budget.category.children.exists())

    # Calculate previous and next month for navigation
    prev_month_date = start_date - datetime.timedelta(days=1)
    next_month_date = end_date + datetime.timedelta(days=1)

    context = {
        'active_date': active_date,
        'income_budgets': income_summary,
        'expense_budgets': expense_summary,
        'savings_budgets': savings_summary,
        'total_income': total_income,
        'total_expenses': total_expenses,
        'total_savings': total_savings,
        'balance': balance,
        'unpaid_count': unpaid_count,
        'prev_month_year': prev_month_date.year,
        'prev_month_month': prev_month_date.month,
        'next_month_year': next_month_date.year,
        'next_month_month': next_month_date.month,
    }
    return render(request, 'finance/dashboard.html', context)

@login_required
def category_list(request):
    household = get_user_household(request.user)
    if not household:
        return redirect('register')
    
    from django.db.models import Prefetch
    income_categories = Category.objects.filter(household=household, type='INCOME', parent__isnull=True).prefetch_related(
        Prefetch('children', queryset=Category.objects.prefetch_related('notes')),
        'notes'
    ).order_by('name')
    expense_categories = Category.objects.filter(household=household, type='EXPENSE', parent__isnull=True).prefetch_related(
        Prefetch('children', queryset=Category.objects.prefetch_related('notes')),
        'notes'
    ).order_by('name')
    savings_categories = Category.objects.filter(household=household, type='SAVINGS', parent__isnull=True).prefetch_related(
        Prefetch('children', queryset=Category.objects.prefetch_related('notes')),
        'notes'
    ).order_by('name')
    
    context = {
        'income_categories': income_categories,
        'expense_categories': expense_categories,
        'savings_categories': savings_categories,
    }
    return render(request, 'finance/category_list.html', context)

@login_required
def add_category(request):
    household = get_user_household(request.user)
    if not household:
        return redirect('register')
    
    if request.method == 'POST':
        form = CategoryForm(request.POST, household=household)
        if form.is_valid():
            category = form.save(commit=False)
            category.household = household
            category.save()
            return redirect('category_list')
    else:
        form = CategoryForm(household=household)
    return render(request, 'finance/form.html', {'form': form, 'title': 'Add Category'})

@login_required
def bulk_add_categories(request):
    household = get_user_household(request.user)
    if not household:
        return redirect('register')
    
    if request.method == 'POST':
        form = BulkCategoryForm(request.POST, household=household)
        if form.is_valid():
            parent = form.cleaned_data['parent']
            is_persistent = form.cleaned_data['is_persistent']
            payment_type = form.cleaned_data['payment_type']
            names = form.cleaned_data['names'].splitlines()
            for name in names:
                name = name.strip()
                if name:
                    Category.objects.create(
                        household=household,
                        name=name,
                        type=parent.type,
                        parent=parent,
                        is_persistent=is_persistent,
                        payment_type=payment_type
                    )
            return redirect('category_list')
    else:
        form = BulkCategoryForm(household=household)
    return render(request, 'finance/bulk_category_form.html', {'form': form, 'title': 'Bulk Add Sub-categories'})

@login_required
def edit_category(request, category_id):
    """Edit an existing category"""
    household = get_user_household(request.user)
    if not household:
        return redirect('register')
    
    try:
        category = Category.objects.get(id=category_id, household=household)
    except Category.DoesNotExist:
        messages.error(request, 'Category not found.')
        return redirect('category_list')
    
    # Check if category has budgets (can't delete if it does)
    has_budgets = Budget.objects.filter(category=category).exists()
    
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category, household=household)
        if form.is_valid():
            form.save()
            messages.success(request, f'Category "{category.name}" updated successfully.')
            return redirect('category_list')
    else:
        form = CategoryForm(instance=category, household=household)
    
    context = {
        'form': form,
        'title': f'Edit Category: {category.name}',
        'category': category,
        'has_budgets': has_budgets,
        'is_edit': True
    }
    return render(request, 'finance/form.html', context)

@login_required
def delete_category(request, category_id):
    """Delete a category (only if no budgets exist)"""
    household = get_user_household(request.user)
    if not household:
        return redirect('register')
    
    try:
        category = Category.objects.get(id=category_id, household=household)
    except Category.DoesNotExist:
        messages.error(request, 'Category not found.')
        return redirect('category_list')
    
    # Check if category has any budgets
    has_budgets = Budget.objects.filter(category=category).exists()
    
    if request.method == 'POST':
        if has_budgets:
            # Prevent deletion
            context = {
                'category': category,
                'error': 'Cannot delete this category because it has existing budgets.'
            }
            return render(request, 'finance/category_confirm_delete.html', context)
        else:
            category.delete()
            return redirect('category_list')
    
    context = {
        'category': category,
        'has_budgets': has_budgets
    }
    return render(request, 'finance/category_confirm_delete.html', context)

@login_required
def clear_all_categories(request):
    """Delete all categories for the user's household"""
    household = get_user_household(request.user)
    if not household:
        return redirect('register')
    
    if request.method == 'POST':
        # Get count before deletion for message
        category_count = Category.objects.filter(household=household).count()
        
        # Delete all categories (this will cascade delete budgets and notes)
        Category.objects.filter(household=household).delete()
        
        messages.success(request, f'All {category_count} categories have been deleted. You can now create your own categories.')
        return redirect('category_list')
    
    # GET request - show confirmation
    category_count = Category.objects.filter(household=household).count()
    budget_count = Budget.objects.filter(category__household=household).count()
    
    context = {
        'category_count': category_count,
        'budget_count': budget_count,
    }
    return render(request, 'finance/clear_all_categories_confirm.html', context)

@login_required
@require_POST
def move_category(request):
    """Move a sub-category to a new parent via AJAX"""
    household = get_user_household(request.user)
    if not household:
        return JsonResponse({'success': False, 'error': 'No household found'}, status=400)
    
    try:
        sub_category_id = request.POST.get('sub_category_id')
        new_parent_id = request.POST.get('new_parent_id')
        
        sub_category = Category.objects.get(id=sub_category_id, household=household)
        new_parent = Category.objects.get(id=new_parent_id, household=household)
        
        # Validate: ensure new parent is a top-level category
        if new_parent.parent is not None:
            return JsonResponse({'success': False, 'error': 'Cannot move to a sub-category'}, status=400)
        
        # Validate: ensure sub-category is actually a sub-category
        if sub_category.parent is None:
            return JsonResponse({'success': False, 'error': 'Cannot move a parent category'}, status=400)
        
        sub_category.parent = new_parent
        sub_category.save()
        
        return JsonResponse({'success': True})
    except Category.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Category not found'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)

@login_required
def yearly_budget_view(request, year=None):
    household = get_user_household(request.user)
    if not household:
        return redirect('register')
    
    if year is None:
        # Check session for active_date first, then fall back to current year
        active_date_str = request.session.get('active_date')
        if active_date_str:
            try:
                active_date = datetime.date.fromisoformat(active_date_str)
                year = active_date.year
            except (ValueError, AttributeError):
                year = datetime.date.today().year
        else:
            year = datetime.date.today().year
    
    # Fetch all budgets for the year for this household
    start_date = datetime.date(year, 1, 1)
    end_date = datetime.date(year, 12, 31)
    
    # Get categories for this household
    household_categories = Category.objects.filter(household=household)
    budgets = Budget.objects.filter(category__household=household, start_date__gte=start_date, start_date__lte=end_date)
    
    # Fetch categories
    income_categories = Category.objects.filter(household=household, type='INCOME', parent__isnull=True).prefetch_related('children').order_by('name')
    expense_categories = Category.objects.filter(household=household, type='EXPENSE', parent__isnull=True).prefetch_related('children').order_by('name')
    savings_categories = Category.objects.filter(household=household, type='SAVINGS', parent__isnull=True).prefetch_related('children').order_by('name')
    
    # Helper to build budget data structure
    def build_budget_data(categories):
        flat_data = []
        for category in categories:
            parent_item = {
                'category': category,
                'is_parent': True,
                'has_children': category.children.exists(),
                'months': {m: {'amount': 0, 'is_paid': False, 'budget_id': None} for m in range(1, 13)},
                'children': [] # We keep a reference to children here for aggregation
            }
            flat_data.append(parent_item)
            
            for child in category.children.all().order_by('name'): # Ensure children are ordered
                child_item = {
                    'category': child,
                    'is_parent': False,
                    'has_children': False,
                    'months': {m: {'amount': 0, 'is_paid': False, 'budget_id': None} for m in range(1, 13)}
                }
                parent_item['children'].append(child_item)
                flat_data.append(child_item)
                
        return flat_data

    income_budget_data = build_budget_data(income_categories)
    expense_budget_data = build_budget_data(expense_categories)
    savings_budget_data = build_budget_data(savings_categories)
    
    # Populate budget amounts for children only
    for budget in budgets:
        month = budget.start_date.month
        budget_info = {
            'amount': budget.amount,
            'is_paid': budget.is_paid,
            'budget_id': budget.id
        }
        
        # Find the category in our data structures (including parents)
        for item in income_budget_data:
            if item['category'] == budget.category:
                item['months'][month] = budget_info
                break
        
        for item in expense_budget_data:
            # Update if it's a child OR if it's a parent with NO children (standalone)
            if (not item['is_parent'] or (item['is_parent'] and not item['has_children'])) and item['category'] == budget.category:
                item['months'][month] = budget_info
                break

        for item in savings_budget_data:
            # Update if it's a child OR if it's a parent with NO children (standalone)
            if (not item['is_parent'] or (item['is_parent'] and not item['has_children'])) and item['category'] == budget.category:
                item['months'][month] = budget_info
                break
    
    # Income parents remain editable; no automatic sum aggregation performed.
    
    for item in expense_budget_data:
        # Only aggregate totals for parents that HAVE children
        # Standalone parents (has_children=False) should keep their own budget amounts
        if item['is_parent'] and item['has_children']:
            for month in range(1, 13):
                total = sum(child['months'][month]['amount'] for child in item['children'])
                all_paid = all(child['months'][month]['is_paid'] for child in item['children']) if item['children'] else True
                item['months'][month] = {
                    'amount': total,
                    'is_paid': all_paid,
                    'budget_id': None  # Parent has no budget entry
                }

    for item in savings_budget_data:
        # Only aggregate totals for parents that HAVE children
        if item['is_parent'] and item['has_children']:
            for month in range(1, 13):
                total = sum(child['months'][month]['amount'] for child in item['children'])
                all_paid = all(child['months'][month]['is_paid'] for child in item['children']) if item['children'] else True
                item['months'][month] = {
                    'amount': total,
                    'is_paid': all_paid,
                    'budget_id': None  # Parent has no budget entry
                }

    months = range(1, 13)
    month_names = [calendar.month_name[m] for m in months]

    active_month = None
    
    # Check GET parameter first
    month_param = request.GET.get('month')
    if month_param:
        try:
            active_month = int(month_param)
        except ValueError:
            pass
            
    # Fallback to session
    if not active_month:
        active_date_str = request.session.get('active_date')
        if active_date_str:
            active_date = datetime.date.fromisoformat(active_date_str)
            if active_date.year == year:
                active_month = active_date.month
                
    # Fallback to current month if year is current year
    if not active_month and year == datetime.date.today().year:
        active_month = datetime.date.today().month

    context = {
        'year': year,
        'income_budget_data': income_budget_data,
        'expense_budget_data': expense_budget_data,
        'savings_budget_data': savings_budget_data,
        'months': months,
        'month_names': month_names,
        'prev_year': year - 1,
        'next_year': year + 1,
        'active_month': active_month,
    }
    return render(request, 'finance/yearly_budget.html', context)

@login_required
def open_month_view(request, year, month):
    household = get_user_household(request.user)
    if not household:
        return redirect('register')
    
    open_budget_month(year, month, household=household, force_update=True)
    messages.info(request, f'Month reset: Persistent categories imported from previous month. Non-persistent categories set to 0.')
    return redirect('yearly_budget_year', year=year)

@login_required
def apply_barebones_template_view(request, year, month):
    """Apply barebones emergency budget template to a specific month"""
    household = get_user_household(request.user)
    if not household:
        return redirect('register')
    
    # Apply the template
    changes = apply_barebones_template(household, year, month)
    
    if changes:
        changes_count = len(changes)
        total_zeroed = sum(1 for c in changes if c['action'] == 'zeroed')
        messages.success(request, f'Barebones template applied to {calendar.month_name[month]} {year}. {total_zeroed} non-essential categories set to zero. You can still edit amounts manually or use Reset to import from previous month.')
    else:
        messages.info(request, f'Barebones template applied. No changes were needed (categories already at minimum).')
    
    return redirect('yearly_budget_year', year=year)

@login_required
@require_POST
def update_budget(request):
    household = get_user_household(request.user)
    if not household:
        return JsonResponse({'success': False, 'error': 'No household found'}, status=400)
    
    try:
        category_id = request.POST.get('category_id')
        year = int(request.POST.get('year'))
        month = int(request.POST.get('month'))
        amount = Decimal(request.POST.get('amount'))
        
        # Get or create budget entry
        start_date = datetime.date(year, month, 1)
        _, last_day = calendar.monthrange(year, month)
        end_date = datetime.date(year, month, last_day)
        
        # Verify category belongs to user's household
        try:
            category = Category.objects.get(id=category_id, household=household)
        except Category.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Category not found'}, status=400)
        
        # Prepare defaults
        defaults = {
            'amount': amount,
            'end_date': end_date
        }
        
        # Check if budget exists to know if we are creating
        budget = Budget.objects.filter(category_id=category_id, start_date=start_date).first()
        
        if not budget:
            # Creating new budget
            is_paid = False
            if category.payment_type in ['AUTO', 'INCOME']:
                is_paid = True
            defaults['is_paid'] = is_paid
            
            budget = Budget.objects.create(
                category_id=category_id,
                start_date=start_date,
                **defaults
            )
        else:
            # Updating existing
            budget.amount = amount
            budget.end_date = end_date
            budget.save()
        
        return JsonResponse({'success': True, 'amount': str(amount)})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)

@login_required
@require_POST
def toggle_payment(request):
    """Toggle is_paid status for a budget entry"""
    household = get_user_household(request.user)
    if not household:
        return JsonResponse({'success': False, 'error': 'No household found'}, status=400)
    
    try:
        budget_id = request.POST.get('budget_id')
        budget = Budget.objects.get(id=budget_id, category__household=household)
        
        # Only allow toggling for MANUAL payment types
        if budget.category.payment_type == 'MANUAL':
            budget.is_paid = not budget.is_paid
            budget.save()
            return JsonResponse({'success': True, 'is_paid': budget.is_paid})
        
        return JsonResponse({'success': False, 'error': 'Cannot toggle auto-paid items'}, status=400)
    except Budget.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Budget not found'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)

@login_required
def outstanding_payments(request, year=None, month=None):
    """Show unpaid manual expenses for a specific month, grouped by parent category"""
    household = get_user_household(request.user)
    if not household:
        return redirect('register')
    
    if not year or not month:
        active_date_str = request.session.get('active_date')
        if active_date_str:
            active_date = datetime.date.fromisoformat(active_date_str)
            year, month = active_date.year, active_date.month
        else:
            today = datetime.date.today()
            year, month = today.year, today.month
    
    start_date = datetime.date(year, month, 1)
    
    unpaid_budgets = Budget.objects.filter(
        category__household=household,
        start_date=start_date,
        is_paid=False,
        category__payment_type='MANUAL',
        category__type='EXPENSE'
    ).select_related('category', 'category__parent').order_by('category__parent__name', 'category__name')
    
    # Group by parent category
    grouped_budgets = {}
    total = 0
    
    for budget in unpaid_budgets:
        # Get parent category (or use the category itself if it's a top-level category)
        parent = budget.category.parent if budget.category.parent else budget.category
        
        if parent not in grouped_budgets:
            grouped_budgets[parent] = {
                'parent': parent,
                'items': [],
                'subtotal': 0
            }
        
        grouped_budgets[parent]['items'].append(budget)
        grouped_budgets[parent]['subtotal'] += budget.amount
        total += budget.amount
    
    context = {
        'year': year,
        'month': month,
        'month_name': calendar.month_name[month],
        'grouped_budgets': grouped_budgets.values(),
        'total': total,
    }
    return render(request, 'finance/outstanding_payments.html', context)

# Authentication Views

def register_view(request):
    """User registration view"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        apply_template = request.POST.get('apply_template', 'false') == 'true'
        
        if form.is_valid():
            user = form.save()
            # Create a default household for the new user
            household = Household.objects.create(name=f"{user.username}'s Household")
            household.members.add(user)
            
            # Apply template immediately if user chose to, otherwise leave blank
            if apply_template:
                create_base_starter_template(household)
                template_message = " We've set up a basic starter template with common categories."
            else:
                template_message = " You can start by creating your own categories."
            
            # Authenticate and login the user
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
                messages.success(request, f'Welcome, {username}! Your account has been created.{template_message}')
                return redirect('dashboard')
    else:
        form = UserCreationForm()
    
    return render(request, 'finance/register.html', {'form': form})

def login_view(request):
    """User login view"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            messages.success(request, f'Welcome back, {username}!')
            next_url = request.GET.get('next', 'dashboard')
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'finance/login.html')

def logout_view(request):
    """User logout view"""
    from django.contrib.auth import logout
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('login')

# Admin Views (Superuser Only)

@login_required
def admin_dashboard(request):
    """Admin dashboard showing system statistics"""
    if not request.user.is_superuser:
        messages.error(request, 'Access denied. Admin access required.')
        return redirect('dashboard')
    
    from django.contrib.auth.models import User
    from django.db.models import Count, Sum
    
    total_users = User.objects.count()
    total_households = Household.objects.count()
    total_categories = Category.objects.count()
    total_budgets = Budget.objects.count()
    
    # Recent users (last 7 days)
    from datetime import timedelta
    from django.utils import timezone
    seven_days_ago = timezone.now() - timedelta(days=7)
    recent_users = User.objects.filter(date_joined__gte=seven_days_ago).count()
    
    # Households with most members
    households_with_members = Household.objects.annotate(member_count=Count('members')).order_by('-member_count')[:5]
    
    context = {
        'total_users': total_users,
        'total_households': total_households,
        'total_categories': total_categories,
        'total_budgets': total_budgets,
        'recent_users': recent_users,
        'households_with_members': households_with_members,
    }
    return render(request, 'finance/admin_dashboard.html', context)

@login_required
def admin_users(request):
    """Admin view to manage users"""
    if not request.user.is_superuser:
        messages.error(request, 'Access denied. Admin access required.')
        return redirect('dashboard')
    
    from django.contrib.auth.models import User
    
    users = User.objects.all().order_by('-date_joined')
    
    # Add household info for each user
    users_with_households = []
    for user in users:
        households = user.households.all()
        users_with_households.append({
            'user': user,
            'households': households,
            'household_count': households.count(),
        })
    
    context = {
        'users_with_households': users_with_households,
    }
    return render(request, 'finance/admin_users.html', context)

@login_required
def admin_households(request):
    """Admin view to manage households"""
    if not request.user.is_superuser:
        messages.error(request, 'Access denied. Admin access required.')
        return redirect('dashboard')
    
    from django.db.models import Count, Q
    
    # Get households with counts
    households = Household.objects.annotate(
        member_count=Count('members', distinct=True),
        category_count=Count('categories', distinct=True)
    ).order_by('-created_at')
    
    # Add budget count separately (can't use double underscore through reverse relation easily)
    for household in households:
        # Count budgets through categories
        household.budget_count = Budget.objects.filter(category__household=household).count()
    
    context = {
        'households': households,
    }
    return render(request, 'finance/admin_households.html', context)

# Category Notes Views

@login_required
def category_notes(request, category_id):
    """View and manage notes for a category"""
    household = get_user_household(request.user)
    if not household:
        return JsonResponse({'success': False, 'error': 'No household found'}, status=400)
    
    try:
        category = Category.objects.get(id=category_id, household=household)
    except Category.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Category not found'}, status=400)
    
    if request.method == 'POST':
        # Add new note
        note_text = request.POST.get('note', '').strip()
        if not note_text:
            return JsonResponse({'success': False, 'error': 'Note cannot be empty'}, status=400)
        
        note = CategoryNote.objects.create(
            category=category,
            author=request.user,
            note=note_text
        )
        
        return JsonResponse({
            'success': True,
            'note': {
                'id': note.id,
                'note': note.note,
                'author': note.author.username,
                'created_at': note.created_at.strftime('%Y-%m-%d %H:%M'),
            }
        })
    
    # GET request - return all notes
    notes = CategoryNote.objects.filter(category=category).order_by('-created_at')
    notes_data = [{
        'id': note.id,
        'note': note.note,
        'author': note.author.username if note.author else 'Unknown',
        'created_at': note.created_at.strftime('%Y-%m-%d %H:%M'),
    } for note in notes]
    
    return JsonResponse({
        'success': True,
        'category_name': category.name,
        'notes': notes_data,
        'notes_count': len(notes_data)
    })

@login_required
@require_POST
def delete_category_note(request, note_id):
    """Delete a category note"""
    household = get_user_household(request.user)
    if not household:
        return JsonResponse({'success': False, 'error': 'No household found'}, status=400)
    
    try:
        note = CategoryNote.objects.get(id=note_id, category__household=household)
        # Only allow author or superuser to delete
        if note.author != request.user and not request.user.is_superuser:
            return JsonResponse({'success': False, 'error': 'Permission denied'}, status=403)
        
        note.delete()
        return JsonResponse({'success': True})
    except CategoryNote.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Note not found'}, status=400)

# Budget Template Management Views (Superuser Only)

def is_superuser(user):
    return user.is_superuser

@login_required
@user_passes_test(is_superuser, login_url='dashboard')
def admin_templates(request):
    """Admin view to manage budget templates"""
    templates = BudgetTemplate.objects.all().order_by('-is_default', 'name')
    
    context = {
        'templates': templates,
    }
    return render(request, 'finance/admin_templates.html', context)

@login_required
@user_passes_test(is_superuser, login_url='dashboard')
def admin_template_detail(request, template_id):
    """Admin view to view/edit a specific template"""
    try:
        template = BudgetTemplate.objects.prefetch_related('categories').get(id=template_id)
    except BudgetTemplate.DoesNotExist:
        messages.error(request, 'Template not found.')
        return redirect('admin_templates')
    
    # Group categories by type and parent
    categories_by_type = {
        'INCOME': [],
        'EXPENSE': [],
        'SAVINGS': []
    }
    
    for cat in template.categories.all().order_by('display_order', 'name'):
        if cat.parent is None:
            categories_by_type[cat.type].append({
                'category': cat,
                'children': []
            })
        else:
            # Find parent and add as child
            for parent_group in categories_by_type[cat.type]:
                if parent_group['category'].id == cat.parent.id:
                    parent_group['children'].append(cat)
                    break
    
    context = {
        'template': template,
        'categories_by_type': categories_by_type,
    }
    return render(request, 'finance/admin_template_detail.html', context)

@login_required
@user_passes_test(is_superuser, login_url='dashboard')
def admin_template_create(request):
    """Admin view to create a new template"""
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()
        is_default = request.POST.get('is_default') == 'on'
        is_active = request.POST.get('is_active') != 'off'  # Default to True
        
        if not name:
            messages.error(request, 'Template name is required.')
            return redirect('admin_template_create')
        
        template = BudgetTemplate.objects.create(
            name=name,
            description=description,
            is_default=is_default,
            is_active=is_active,
            created_by=request.user
        )
        
        messages.success(request, f'Template "{template.name}" created successfully. You can now add categories.')
        return redirect('admin_template_detail', template_id=template.id)
    
    return render(request, 'finance/admin_template_create.html')

@login_required
@user_passes_test(is_superuser, login_url='dashboard')
@require_POST
def admin_template_delete(request, template_id):
    """Delete a template"""
    try:
        template = BudgetTemplate.objects.get(id=template_id)
        template_name = template.name
        
        # Don't allow deleting if it's the only default template
        if template.is_default:
            default_count = BudgetTemplate.objects.filter(is_default=True).count()
            if default_count <= 1:
                messages.error(request, 'Cannot delete the only default template. Please set another template as default first.')
                return redirect('admin_templates')
        
        template.delete()
        messages.success(request, f'Template "{template_name}" deleted successfully.')
    except BudgetTemplate.DoesNotExist:
        messages.error(request, 'Template not found.')
    
    return redirect('admin_templates')

@login_required
@user_passes_test(is_superuser, login_url='dashboard')
@require_POST
def admin_template_set_default(request, template_id):
    """Set a template as default"""
    try:
        template = BudgetTemplate.objects.get(id=template_id)
        template.is_default = True
        template.save()  # This will automatically unset other defaults via model save()
        messages.success(request, f'Template "{template.name}" is now the default template.')
    except BudgetTemplate.DoesNotExist:
        messages.error(request, 'Template not found.')
    
    return redirect('admin_templates')

# Excel Export Views

@login_required
def export_yearly_budget_excel(request, year):
    """Export yearly budget to Excel"""
    household = get_user_household(request.user)
    if not household:
        messages.error(request, 'No household found')
        return redirect('dashboard')
    
    try:
        wb = export_yearly_budget(household, int(year))
        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename="budget_{year}.xlsx"'
        wb.save(response)
        return response
    except Exception as e:
        messages.error(request, f'Error generating report: {str(e)}')
        return redirect('yearly_budget_year', year=year)


@login_required
def export_monthly_detail_excel(request, year, month):
    """Export monthly budget detail to Excel"""
    household = get_user_household(request.user)
    if not household:
        messages.error(request, 'No household found')
        return redirect('dashboard')
    
    try:
        wb = export_monthly_detail(household, int(year), int(month))
        month_name = calendar.month_abbr[int(month)]
        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename="budget_{month_name}_{year}.xlsx"'
        wb.save(response)
        return response
    except Exception as e:
        messages.error(request, f'Error generating report: {str(e)}')
        return redirect('yearly_budget_year', year=year)


@login_required
def export_category_summary_excel(request, year):
    """Export category summary to Excel"""
    household = get_user_household(request.user)
    if not household:
        messages.error(request, 'No household found')
        return redirect('dashboard')
    
    try:
        wb = export_category_summary(household, int(year))
        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename="category_summary_{year}.xlsx"'
        wb.save(response)
        return response
    except Exception as e:
        messages.error(request, f'Error generating report: {str(e)}')
        return redirect('yearly_budget_year', year=year)


@login_required
def export_transactions_excel(request):
    """Export transactions to Excel"""
    household = get_user_household(request.user)
    if not household:
        messages.error(request, 'No household found')
        return redirect('dashboard')
    
    try:
        start_date = None
        end_date = None
        
        if request.GET.get('start_date'):
            start_date = datetime.datetime.strptime(request.GET.get('start_date'), '%Y-%m-%d').date()
        if request.GET.get('end_date'):
            end_date = datetime.datetime.strptime(request.GET.get('end_date'), '%Y-%m-%d').date()
        
        wb = export_transactions(household, start_date, end_date)
        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        filename = "transactions.xlsx"
        if start_date and end_date:
            filename = f"transactions_{start_date}_{end_date}.xlsx"
        elif start_date:
            filename = f"transactions_from_{start_date}.xlsx"
        elif end_date:
            filename = f"transactions_until_{end_date}.xlsx"
        
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        wb.save(response)
        return response
    except Exception as e:
        messages.error(request, f'Error generating report: {str(e)}')
        return redirect('dashboard')


@login_required
def export_category_setup_excel(request):
    """Export category setup information to Excel"""
    household = get_user_household(request.user)
    if not household:
        messages.error(request, 'No household found')
        return redirect('dashboard')
    
    try:
        wb = export_category_setup(household)
        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename="category_setup.xlsx"'
        wb.save(response)
        return response
    except Exception as e:
        messages.error(request, f'Error generating report: {str(e)}')
        return redirect('yearly_budget')
