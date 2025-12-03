"""
API Views for Finance Flow
Provides REST API endpoints while maintaining all existing functionality
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication
from django.db.models import Sum, Q
from django.utils import timezone
from datetime import datetime, date, timedelta
import calendar

from .models import (
    Household, Category, Budget, Transaction,
    CategoryNote, BudgetTemplate, TemplateCategory
)
from .serializers import (
    HouseholdSerializer, CategorySerializer, CategoryListSerializer,
    BudgetSerializer, TransactionSerializer, CategoryNoteSerializer,
    BudgetTemplateSerializer, TemplateCategorySerializer
)
from .utils import open_budget_month
from .templates import create_base_starter_template, apply_barebones_template
from .excel_reports import export_yearly_budget, export_monthly_detail, export_category_summary, export_transactions
from django.http import HttpResponse


def get_user_household(user):
    """Get the user's primary household"""
    if not user.is_authenticated:
        return None
    household = user.households.first()
    if not household:
        household = Household.objects.create(name=f"{user.username}'s Household")
        household.members.add(user)
    return household


class HouseholdViewSet(viewsets.ModelViewSet):
    """ViewSet for Household management"""
    serializer_class = HouseholdSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [SessionAuthentication]
    
    def get_queryset(self):
        """Users can only see households they belong to"""
        return Household.objects.filter(members=self.request.user)
    
    def perform_create(self, serializer):
        """Add current user as member when creating household"""
        household = serializer.save()
        household.members.add(self.request.user)


class CategoryViewSet(viewsets.ModelViewSet):
    """ViewSet for Category management"""
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [SessionAuthentication]
    
    def get_queryset(self):
        """Filter categories by user's household"""
        household = get_user_household(self.request.user)
        if not household:
            return Category.objects.none()
        return Category.objects.filter(household=household).select_related('parent', 'household').prefetch_related('children', 'notes')
    
    def get_serializer_class(self):
        """Use list serializer for list view"""
        if self.action == 'list':
            return CategoryListSerializer
        return CategorySerializer
    
    def perform_create(self, serializer):
        """Set household when creating category"""
        household = get_user_household(self.request.user)
        if household:
            serializer.save(household=household)
    
    @action(detail=True, methods=['post'])
    def move(self, request, pk=None):
        """Move category to different parent"""
        category = self.get_object()
        new_parent_id = request.data.get('parent_id')
        
        if new_parent_id:
            try:
                new_parent = Category.objects.get(id=new_parent_id, household=category.household)
                category.parent = new_parent
                category.save()
                return Response({'success': True, 'message': 'Category moved successfully'})
            except Category.DoesNotExist:
                return Response({'success': False, 'error': 'Parent category not found'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            category.parent = None
            category.save()
            return Response({'success': True, 'message': 'Category moved to root level'})
    
    @action(detail=True, methods=['get', 'post'])
    def notes(self, request, pk=None):
        """Get or create notes for a category"""
        category = self.get_object()
        
        if request.method == 'GET':
            notes = CategoryNote.objects.filter(category=category).order_by('-created_at')
            serializer = CategoryNoteSerializer(notes, many=True)
            return Response({
                'success': True,
                'category_name': category.name,
                'notes': serializer.data,
                'notes_count': len(serializer.data)
            })
        
        elif request.method == 'POST':
            note_text = request.data.get('note', '').strip()
            if not note_text:
                return Response({'success': False, 'error': 'Note cannot be empty'}, status=status.HTTP_400_BAD_REQUEST)
            
            note = CategoryNote.objects.create(
                category=category,
                author=request.user,
                note=note_text
            )
            serializer = CategoryNoteSerializer(note)
            return Response({
                'success': True,
                'note': serializer.data
            })


class BudgetViewSet(viewsets.ModelViewSet):
    """ViewSet for Budget management"""
    serializer_class = BudgetSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [SessionAuthentication]
    
    def get_queryset(self):
        """Filter budgets by user's household"""
        household = get_user_household(self.request.user)
        if not household:
            return Budget.objects.none()
        
        queryset = Budget.objects.filter(category__household=household).select_related('category')
        
        # Filter by year/month if provided
        year = self.request.query_params.get('year')
        month = self.request.query_params.get('month')
        if year:
            queryset = queryset.filter(start_date__year=year)
        if month:
            queryset = queryset.filter(start_date__month=month)
        
        return queryset
    
    def perform_create(self, serializer):
        """Ensure category belongs to user's household"""
        household = get_user_household(self.request.user)
        category = serializer.validated_data['category']
        if category.household != household:
            raise serializers.ValidationError("Category does not belong to your household")
        serializer.save()
    
    @action(detail=False, methods=['post'])
    def update_amount(self, request):
        """Update budget amount (maintains existing functionality)"""
        category_id = request.data.get('category_id')
        month = request.data.get('month')
        year = request.data.get('year')
        amount = request.data.get('amount')
        
        if not all([category_id, month, year, amount is not None]):
            return Response({'success': False, 'error': 'Missing required fields'}, status=status.HTTP_400_BAD_REQUEST)
        
        household = get_user_household(request.user)
        if not household:
            return Response({'success': False, 'error': 'No household found'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            category = Category.objects.get(id=category_id, household=household)
            start_date = date(int(year), int(month), 1)
            _, last_day = calendar.monthrange(int(year), int(month))
            end_date = date(int(year), int(month), last_day)
            
            budget, created = Budget.objects.update_or_create(
                category=category,
                start_date=start_date,
                defaults={'amount': amount, 'end_date': end_date}
            )
            
            serializer = BudgetSerializer(budget)
            return Response({'success': True, 'budget': serializer.data})
        except Category.DoesNotExist:
            return Response({'success': False, 'error': 'Category not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'success': False, 'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def toggle_payment(self, request, pk=None):
        """Toggle payment status (maintains existing functionality)"""
        budget = self.get_object()
        budget.is_paid = not budget.is_paid
        budget.save()
        return Response({
            'success': True,
            'is_paid': budget.is_paid
        })
    
    @action(detail=False, methods=['post'])
    def open_month(self, request):
        """Open/initiate a budget month (maintains existing functionality)"""
        year = request.data.get('year')
        month = request.data.get('month')
        
        if not year or not month:
            return Response({'success': False, 'error': 'Year and month required'}, status=status.HTTP_400_BAD_REQUEST)
        
        household = get_user_household(request.user)
        if not household:
            return Response({'success': False, 'error': 'No household found'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            open_budget_month(household, int(year), int(month))
            return Response({'success': True, 'message': f'Budget month {year}-{month:02d} opened successfully'})
        except Exception as e:
            return Response({'success': False, 'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def apply_barebones(self, request):
        """Apply barebones template to a month (maintains existing functionality)"""
        year = request.data.get('year')
        month = request.data.get('month')
        
        if not year or not month:
            return Response({'success': False, 'error': 'Year and month required'}, status=status.HTTP_400_BAD_REQUEST)
        
        household = get_user_household(request.user)
        if not household:
            return Response({'success': False, 'error': 'No household found'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            apply_barebones_template(household, int(year), int(month))
            return Response({'success': True, 'message': f'Barebones template applied to {year}-{month:02d}'})
        except Exception as e:
            return Response({'success': False, 'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class TransactionViewSet(viewsets.ModelViewSet):
    """ViewSet for Transaction management"""
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [SessionAuthentication]
    
    def get_queryset(self):
        """Filter transactions by user's household"""
        household = get_user_household(self.request.user)
        if not household:
            return Transaction.objects.none()
        return Transaction.objects.filter(household=household).select_related('category', 'household')


class CategoryNoteViewSet(viewsets.ModelViewSet):
    """ViewSet for CategoryNote management"""
    serializer_class = CategoryNoteSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [SessionAuthentication]
    
    def get_queryset(self):
        """Filter notes by user's household"""
        household = get_user_household(self.request.user)
        if not household:
            return CategoryNote.objects.none()
        return CategoryNote.objects.filter(category__household=household).select_related('category', 'author')
    
    def perform_create(self, serializer):
        """Set author when creating note"""
        serializer.save(author=self.request.user)

    def destroy(self, request, *args, **kwargs):
        """Delete a note and return JSON success for frontend compatibility"""
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({'success': True})


class BudgetTemplateViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for BudgetTemplate (read-only for regular users)"""
    serializer_class = BudgetTemplateSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [SessionAuthentication]
    
    def get_queryset(self):
        """Show active templates"""
        return BudgetTemplate.objects.filter(is_active=True).prefetch_related('categories')


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_data(request):
    """Get dashboard data (maintains existing functionality)"""
    household = get_user_household(request.user)
    if not household:
        return Response({'error': 'No household found'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Get active month from query params or session
    year = request.GET.get('year')
    month = request.GET.get('month')
    
    if year and month:
        try:
            active_date = date(int(year), int(month), 1)
        except ValueError:
            active_date = date.today()
    else:
        active_date_str = request.session.get('active_date')
        if active_date_str:
            active_date = date.fromisoformat(active_date_str)
        else:
            active_date = date.today()
    
    year, month = active_date.year, active_date.month
    start_date = active_date.replace(day=1)
    _, last_day = calendar.monthrange(year, month)
    end_date = active_date.replace(day=last_day)
    
    # Get categories
    income_categories = Category.objects.filter(household=household, type='INCOME', parent__isnull=True).prefetch_related('children')
    expense_categories = Category.objects.filter(household=household, type='EXPENSE', parent__isnull=True).prefetch_related('children')
    savings_categories = Category.objects.filter(household=household, type='SAVINGS', parent__isnull=True).prefetch_related('children')
    
    # Calculate totals
    income_budgets = Budget.objects.filter(
        category__household=household,
        category__type='INCOME',
        start_date=start_date
    )
    expense_budgets = Budget.objects.filter(
        category__household=household,
        category__type='EXPENSE',
        start_date=start_date
    )
    savings_budgets = Budget.objects.filter(
        category__household=household,
        category__type='SAVINGS',
        start_date=start_date
    )
    
    total_income = income_budgets.aggregate(Sum('amount'))['amount__sum'] or 0
    total_expenses = expense_budgets.aggregate(Sum('amount'))['amount__sum'] or 0
    total_savings = savings_budgets.aggregate(Sum('amount'))['amount__sum'] or 0
    balance = total_income - total_expenses - total_savings
    
    # Count unpaid items
    unpaid_count = Budget.objects.filter(
        category__household=household,
        category__type='EXPENSE',
        category__payment_type='MANUAL',
        start_date=start_date,
        is_paid=False,
        amount__gt=0
    ).count()
    
    # Build budget lists
    income_budget_list = []
    for category in income_categories:
        children = list(category.children.all())
        if children:
            total = sum(
                Budget.objects.filter(category=child, start_date=start_date).first().amount 
                if Budget.objects.filter(category=child, start_date=start_date).first() else 0
                for child in children
            )
        else:
            budget = Budget.objects.filter(category=category, start_date=start_date).first()
            total = budget.amount if budget else 0
        income_budget_list.append({
            'category': CategoryListSerializer(category).data,
            'amount': float(total)
        })
    
    expense_budget_list = []
    for category in expense_categories:
        children = list(category.children.all())
        if children:
            total = sum(
                Budget.objects.filter(category=child, start_date=start_date).first().amount 
                if Budget.objects.filter(category=child, start_date=start_date).first() else 0
                for child in children
            )
        else:
            budget = Budget.objects.filter(category=category, start_date=start_date).first()
            total = budget.amount if budget else 0
        expense_budget_list.append({
            'category': CategoryListSerializer(category).data,
            'amount': float(total)
        })
    
    savings_budget_list = []
    for category in savings_categories:
        children = list(category.children.all())
        if children:
            total = sum(
                Budget.objects.filter(category=child, start_date=start_date).first().amount 
                if Budget.objects.filter(category=child, start_date=start_date).first() else 0
                for child in children
            )
        else:
            budget = Budget.objects.filter(category=category, start_date=start_date).first()
            total = budget.amount if budget else 0
        savings_budget_list.append({
            'category': CategoryListSerializer(category).data,
            'amount': float(total)
        })
    
    return Response({
        'active_date': active_date.isoformat(),
        'year': year,
        'month': month,
        'total_income': float(total_income),
        'total_expenses': float(total_expenses),
        'total_savings': float(total_savings),
        'balance': float(balance),
        'unpaid_count': unpaid_count,
        'income_budgets': income_budget_list,
        'expense_budgets': expense_budget_list,
        'savings_budgets': savings_budget_list,
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def yearly_budget_data(request, year):
    """Get yearly budget data (maintains existing functionality)"""
    household = get_user_household(request.user)
    if not household:
        return Response({'error': 'No household found'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Get active month from query params
    active_month = int(request.GET.get('month', date.today().month))
    
    # Get all months
    months = list(range(1, 13))
    month_names = [calendar.month_abbr[i] for i in months]
    
    # Get all categories
    income_categories = Category.objects.filter(household=household, type='INCOME').order_by('name')
    expense_categories = Category.objects.filter(household=household, type='EXPENSE').order_by('name')
    savings_categories = Category.objects.filter(household=household, type='SAVINGS').order_by('name')
    
    # Build budget data structure
    def build_budget_data(categories):
        result = []
        for category in categories:
            months_data = {}
            for month in months:
                month_date = date(int(year), month, 1)
                budget = Budget.objects.filter(
                    category=category,
                    start_date__year=year,
                    start_date__month=month
                ).first()
                months_data[month] = {
                    'amount': float(budget.amount) if budget else 0.0,
                    'budget_id': budget.id if budget else None,
                    'is_paid': budget.is_paid if budget else False
                }
            
            result.append({
                'category': CategoryListSerializer(category).data,
                'months': months_data,
                'is_parent': category.parent is None,
                'has_children': category.children.exists()
            })
        return result
    
    income_budget_data = build_budget_data(income_categories)
    expense_budget_data = build_budget_data(expense_categories)
    savings_budget_data = build_budget_data(savings_categories)
    
    return Response({
        'year': year,
        'active_month': active_month,
        'months': months,
        'month_names': month_names,
        'income_budget_data': income_budget_data,
        'expense_budget_data': expense_budget_data,
        'savings_budget_data': savings_budget_data,
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def outstanding_payments_data(request, year=None, month=None):
    """Get outstanding payments data (maintains existing functionality)"""
    household = get_user_household(request.user)
    if not household:
        return Response({'error': 'No household found'}, status=status.HTTP_400_BAD_REQUEST)
    
    if not year or not month:
        today = date.today()
        year = year or today.year
        month = month or today.month
    
    month_date = date(int(year), int(month), 1)
    month_name = calendar.month_name[int(month)]
    
    # Get parent categories with manual payment tracking
    parent_categories = Category.objects.filter(
        household=household,
        type='EXPENSE',
        payment_type='MANUAL',
        parent__isnull=True
    ).prefetch_related('children')
    
    grouped_budgets = []
    total = 0
    
    for parent in parent_categories:
        items = []
        subtotal = 0
        
        for child in parent.children.all():
            budget = Budget.objects.filter(
                category=child,
                start_date__year=year,
                start_date__month=month
            ).first()
            
            if budget and budget.amount > 0 and not budget.is_paid:
                items.append({
                    'id': budget.id,
                    'category': CategoryListSerializer(child).data,
                    'amount': float(budget.amount),
                    'is_paid': budget.is_paid
                })
                subtotal += float(budget.amount)
        
        if items:
            grouped_budgets.append({
                'parent': CategoryListSerializer(parent).data,
                'items': items,
                'subtotal': float(subtotal)
            })
            total += subtotal
    
    return Response({
        'year': year,
        'month': month,
        'month_name': month_name,
        'grouped_budgets': grouped_budgets,
        'total': float(total)
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def export_yearly_budget_excel_api(request, year):
    """Export yearly budget to Excel (maintains existing functionality)"""
    household = get_user_household(request.user)
    if not household:
        return Response({'error': 'No household found'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        from .excel_reports import export_yearly_budget
        from io import BytesIO
        wb = export_yearly_budget(household, year)
        output = BytesIO()
        wb.save(output)
        output.seek(0)
        response = HttpResponse(
            output.read(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename="yearly_budget_{year}.xlsx"'
        return response
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def export_monthly_detail_excel_api(request, year, month):
    """Export monthly detail to Excel (maintains existing functionality)"""
    household = get_user_household(request.user)
    if not household:
        return Response({'error': 'No household found'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        from .excel_reports import export_monthly_detail
        from io import BytesIO
        wb = export_monthly_detail(household, year, month)
        output = BytesIO()
        wb.save(output)
        output.seek(0)
        response = HttpResponse(
            output.read(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename="monthly_detail_{year}_{month:02d}.xlsx"'
        return response
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def export_category_summary_excel_api(request, year):
    """Export category summary to Excel (maintains existing functionality)"""
    household = get_user_household(request.user)
    if not household:
        return Response({'error': 'No household found'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        from .excel_reports import export_category_summary
        from io import BytesIO
        wb = export_category_summary(household, year)
        output = BytesIO()
        wb.save(output)
        output.seek(0)
        response = HttpResponse(
            output.read(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename="category_summary_{year}.xlsx"'
        return response
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def export_category_setup_excel_api(request):
    """Export category setup information to Excel (maintains existing functionality)"""
    household = get_user_household(request.user)
    if not household:
        return Response({'error': 'No household found'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        from .excel_reports import export_category_setup
        from io import BytesIO
        wb = export_category_setup(household)
        output = BytesIO()
        wb.save(output)
        output.seek(0)
        response = HttpResponse(
            output.read(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename="category_setup.xlsx"'
        return response
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def export_transactions_excel_api(request):
    """Export all transactions to Excel (maintains existing functionality)"""
    household = get_user_household(request.user)
    if not household:
        return Response({'error': 'No household found'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Get date range from query params (optional)
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    try:
        from .excel_reports import export_transactions
        from io import BytesIO
        
        if start_date:
            start_date = date.fromisoformat(start_date)
        else:
            start_date = date(2000, 1, 1)  # Default to very early date
        
        if end_date:
            end_date = date.fromisoformat(end_date)
        else:
            end_date = date.today()
        
        wb = export_transactions(household, start_date, end_date)
        output = BytesIO()
        wb.save(output)
        output.seek(0)
        response = HttpResponse(
            output.read(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename="transactions_{start_date}_{end_date}.xlsx"'
        return response
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

