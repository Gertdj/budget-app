from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import EmailValidator

class User(AbstractUser):
    """Custom User model with email as username"""
    username = models.CharField(
        max_length=150,
        unique=True,
        null=True,
        blank=True,
        help_text='Optional. Not used for login.'
    )
    email = models.EmailField(
        unique=True,
        validators=[EmailValidator()],
        help_text='Required. Used as username for login.'
    )
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []  # Email is already required as USERNAME_FIELD
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        # Remove username from unique_together since it can be null
        constraints = [
            models.UniqueConstraint(fields=['email'], name='unique_email')
        ]
    
    def __str__(self):
        return self.email

class Household(models.Model):
    """Represents a household/budget group that can have multiple members"""
    name = models.CharField(max_length=100, help_text="Household name (e.g., 'Smith Family')")
    members = models.ManyToManyField(User, related_name='households', help_text="Users who have access to this household's budget")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Household'
        verbose_name_plural = 'Households'
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def get_primary_member(self):
        """Get the first member (typically the creator)"""
        return self.members.first()

class Category(models.Model):
    TYPE_CHOICES = [
        ('INCOME', 'Income'),
        ('EXPENSE', 'Expense'),
        ('SAVINGS', 'Savings & Investments'),
    ]
    PAYMENT_TYPE_CHOICES = [
        ('AUTO', 'Automatic - No tracking needed'),
        ('MANUAL', 'Manual - Track payment'),
        ('INCOME', 'Income - No tracking needed'),
    ]
    household = models.ForeignKey(Household, on_delete=models.CASCADE, related_name='categories', help_text="Household this category belongs to")
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=7, choices=TYPE_CHOICES, default='EXPENSE')
    is_persistent = models.BooleanField(default=False, help_text="If checked, the budget amount will be carried over to the next month.")
    payment_type = models.CharField(max_length=10, choices=PAYMENT_TYPE_CHOICES, default='MANUAL', help_text="How this category is paid/received.")
    is_essential = models.BooleanField(default=True, help_text="For Barebones template: True = essential (keep amount), False = non-essential (zero out). Default is Essential for safety.")
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')

    class Meta:
        verbose_name_plural = 'Categories'

    def __str__(self):
        return f"{self.name} ({self.get_type_display()})"

class Transaction(models.Model):
    TYPE_CHOICES = [
        ('INCOME', 'Income'),
        ('EXPENSE', 'Expense'),
    ]
    household = models.ForeignKey(Household, on_delete=models.CASCADE, related_name='transactions', help_text="Household this transaction belongs to")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    description = models.TextField(blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    type = models.CharField(max_length=7, choices=TYPE_CHOICES, default='EXPENSE')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.date} - {self.description} - {self.amount}"

class Budget(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    start_date = models.DateField()
    end_date = models.DateField()
    is_paid = models.BooleanField(default=False, help_text="Whether this budget item has been paid/received.")

    def __str__(self):
        return f"{self.category.name}: {self.amount}"

class CategoryNote(models.Model):
    """Notes attached to categories - not tied to specific months, just general category notes"""
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='notes', help_text="Category this note belongs to")
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, help_text="User who created this note")
    note = models.TextField(help_text="Note content")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Category Note'
        verbose_name_plural = 'Category Notes'
    
    def __str__(self):
        return f"Note for {self.category.name} by {self.author.email if self.author else 'Unknown'}"

class BudgetTemplate(models.Model):
    """Template for creating default category structures for new households"""
    name = models.CharField(max_length=100, unique=True, help_text="Template name (e.g., 'Basic Starter', 'Minimal Budget')")
    description = models.TextField(blank=True, help_text="Description of what this template includes")
    is_default = models.BooleanField(default=False, help_text="If True, this template will be used for new households by default")
    is_active = models.BooleanField(default=True, help_text="Only active templates can be used")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_templates', help_text="User who created this template")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-is_default', 'name']
        verbose_name = 'Budget Template'
        verbose_name_plural = 'Budget Templates'
    
    def __str__(self):
        default_marker = " (Default)" if self.is_default else ""
        return f"{self.name}{default_marker}"
    
    def save(self, *args, **kwargs):
        # Ensure only one template is default
        if self.is_default:
            BudgetTemplate.objects.filter(is_default=True).exclude(pk=self.pk).update(is_default=False)
        super().save(*args, **kwargs)
    
    def get_category_count(self):
        """Get total number of categories in this template"""
        return self.categories.count()

class TemplateCategory(models.Model):
    """Category definition within a budget template"""
    TYPE_CHOICES = [
        ('INCOME', 'Income'),
        ('EXPENSE', 'Expense'),
        ('SAVINGS', 'Savings & Investments'),
    ]
    PAYMENT_TYPE_CHOICES = [
        ('AUTO', 'Automatic - No tracking needed'),
        ('MANUAL', 'Manual - Track payment'),
        ('INCOME', 'Income - No tracking needed'),
    ]
    
    template = models.ForeignKey(BudgetTemplate, on_delete=models.CASCADE, related_name='categories', help_text="Template this category belongs to")
    name = models.CharField(max_length=100, help_text="Category name")
    type = models.CharField(max_length=7, choices=TYPE_CHOICES, default='EXPENSE')
    is_persistent = models.BooleanField(default=False, help_text="If checked, the budget amount will be carried over to the next month.")
    payment_type = models.CharField(max_length=10, choices=PAYMENT_TYPE_CHOICES, default='MANUAL', help_text="How this category is paid/received.")
    is_essential = models.BooleanField(default=True, help_text="For Barebones template: True = essential (keep amount), False = non-essential (zero out).")
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children', help_text="Parent category (for sub-categories)")
    display_order = models.IntegerField(default=0, help_text="Order in which categories should be displayed")
    
    class Meta:
        ordering = ['display_order', 'name']
        verbose_name = 'Template Category'
        verbose_name_plural = 'Template Categories'
        unique_together = [['template', 'name', 'parent']]  # Prevent duplicates within same template
    
    def __str__(self):
        parent_str = f" ({self.parent.name})" if self.parent else ""
        return f"{self.name}{parent_str} - {self.template.name}"
