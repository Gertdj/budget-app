from django.contrib import admin
from .models import Category, Transaction, Budget, Household, CategoryNote, BudgetTemplate, TemplateCategory

@admin.register(Household)
class HouseholdAdmin(admin.ModelAdmin):
    list_display = ('name', 'get_member_count', 'created_at')
    filter_horizontal = ('members',)
    search_fields = ('name',)
    
    def get_member_count(self, obj):
        return obj.members.count()
    get_member_count.short_description = 'Members'

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'household', 'type', 'parent', 'is_persistent', 'payment_type', 'is_essential')
    list_filter = ('household', 'type', 'is_persistent', 'payment_type', 'is_essential')
    search_fields = ('name',)

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('date', 'description', 'amount', 'type', 'category', 'household')
    list_filter = ('type', 'date', 'household')
    search_fields = ('description',)

@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ('category', 'amount', 'start_date', 'is_paid', 'get_household')
    list_filter = ('start_date', 'is_paid', 'category__household')
    search_fields = ('category__name',)
    
    def get_household(self, obj):
        return obj.category.household
    get_household.short_description = 'Household'

@admin.register(CategoryNote)
class CategoryNoteAdmin(admin.ModelAdmin):
    list_display = ('category', 'author', 'note_preview', 'created_at')
    list_filter = ('created_at', 'category__household', 'category__type')
    search_fields = ('note', 'category__name')
    readonly_fields = ('created_at', 'updated_at')
    
    def note_preview(self, obj):
        return obj.note[:50] + '...' if len(obj.note) > 50 else obj.note
    note_preview.short_description = 'Note Preview'

class TemplateCategoryInline(admin.TabularInline):
    model = TemplateCategory
    extra = 1
    fields = ('name', 'type', 'parent', 'is_persistent', 'payment_type', 'is_essential', 'display_order')
    ordering = ('display_order', 'name')

@admin.register(BudgetTemplate)
class BudgetTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_default', 'is_active', 'get_category_count', 'created_by', 'created_at')
    list_filter = ('is_default', 'is_active', 'created_at')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [TemplateCategoryInline]
    fieldsets = (
        (None, {
            'fields': ('name', 'description', 'is_default', 'is_active', 'created_by')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_category_count(self, obj):
        return obj.get_category_count()
    get_category_count.short_description = 'Categories'

@admin.register(TemplateCategory)
class TemplateCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'template', 'type', 'parent', 'is_persistent', 'payment_type', 'is_essential', 'display_order')
    list_filter = ('template', 'type', 'is_persistent', 'payment_type', 'is_essential')
    search_fields = ('name', 'template__name')
    ordering = ('template', 'display_order', 'name')

