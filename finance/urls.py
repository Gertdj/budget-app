from django.urls import path
from . import views

urlpatterns = [
    # Authentication
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Main app (require login)
    path('', views.dashboard, name='dashboard'),
    path('categories/', views.category_list, name='category_list'),
    path('categories/bulk-add/', views.bulk_add_categories, name='bulk_add_categories'),
    path('categories/edit/<int:category_id>/', views.edit_category, name='edit_category'),
    path('categories/delete/<int:category_id>/', views.delete_category, name='delete_category'),
    path('categories/move/', views.move_category, name='move_category'),
    path('add-category/', views.add_category, name='add_category'),
    path('budget/yearly/', views.yearly_budget_view, name='yearly_budget'),
    path('budget/yearly/<int:year>/', views.yearly_budget_view, name='yearly_budget_year'),
    path('budget/open/<int:year>/<int:month>/', views.open_month_view, name='open_budget_month'),
    path('budget/barebones/<int:year>/<int:month>/', views.apply_barebones_template_view, name='apply_barebones_template'),
    path('budget/update/', views.update_budget, name='update_budget'),
    path('budget/toggle-payment/', views.toggle_payment, name='toggle_payment'),
    path('budget/outstanding/', views.outstanding_payments, name='outstanding_payments'),
    path('budget/outstanding/<int:year>/<int:month>/', views.outstanding_payments, name='outstanding_payments_month'),
    
    # Admin views (superuser only)
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/users/', views.admin_users, name='admin_users'),
    path('admin/households/', views.admin_households, name='admin_households'),
    
    # Category Notes
    path('categories/<int:category_id>/notes/', views.category_notes, name='category_notes'),
    path('categories/notes/<int:note_id>/delete/', views.delete_category_note, name='delete_category_note'),
    
    # Template Management (superuser only)
    path('admin/templates/', views.admin_templates, name='admin_templates'),
    path('admin/templates/create/', views.admin_template_create, name='admin_template_create'),
    path('admin/templates/<int:template_id>/', views.admin_template_detail, name='admin_template_detail'),
    path('admin/templates/<int:template_id>/delete/', views.admin_template_delete, name='admin_template_delete'),
    path('admin/templates/<int:template_id>/set-default/', views.admin_template_set_default, name='admin_template_set_default'),
    
    # Excel Exports
    path('export/yearly/<int:year>/', views.export_yearly_budget_excel, name='export_yearly_budget_excel'),
    path('export/monthly/<int:year>/<int:month>/', views.export_monthly_detail_excel, name='export_monthly_detail_excel'),
    path('export/category-summary/<int:year>/', views.export_category_summary_excel, name='export_category_summary_excel'),
    path('export/category-setup/', views.export_category_setup_excel, name='export_category_setup_excel'),
    path('export/transactions/', views.export_transactions_excel, name='export_transactions_excel'),
]
