"""
API URL Configuration for Finance Flow
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token
from . import api_views

router = DefaultRouter()
router.register(r'households', api_views.HouseholdViewSet, basename='household')
router.register(r'categories', api_views.CategoryViewSet, basename='category')
router.register(r'budgets', api_views.BudgetViewSet, basename='budget')
router.register(r'transactions', api_views.TransactionViewSet, basename='transaction')
router.register(r'category-notes', api_views.CategoryNoteViewSet, basename='category-note')
router.register(r'templates', api_views.BudgetTemplateViewSet, basename='template')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/token/', obtain_auth_token, name='api_token_auth'),
    path('dashboard/', api_views.dashboard_data, name='api_dashboard'),
    path('yearly-budget/<int:year>/', api_views.yearly_budget_data, name='api_yearly_budget'),
    path('outstanding-payments/', api_views.outstanding_payments_data, name='api_outstanding_payments'),
    path('outstanding-payments/<int:year>/<int:month>/', api_views.outstanding_payments_data, name='api_outstanding_payments_month'),
    # Excel export endpoints
    path('export/yearly/<int:year>/', api_views.export_yearly_budget_excel_api, name='api_export_yearly_budget'),
    path('export/monthly/<int:year>/<int:month>/', api_views.export_monthly_detail_excel_api, name='api_export_monthly_detail'),
    path('export/category-summary/<int:year>/', api_views.export_category_summary_excel_api, name='api_export_category_summary'),
    path('export/category-setup/', api_views.export_category_setup_excel_api, name='api_export_category_setup'),
    path('export/transactions/', api_views.export_transactions_excel_api, name='api_export_transactions'),
]

