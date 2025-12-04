from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Transaction, Category, Budget, User

class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['date', 'amount', 'type', 'category', 'description']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'type': forms.Select(attrs={'class': 'form-select'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'type', 'parent', 'is_persistent', 'payment_type', 'is_essential']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'type': forms.Select(attrs={'class': 'form-select'}),
            'parent': forms.Select(attrs={'class': 'form-select'}),
            'payment_type': forms.Select(attrs={'class': 'form-select'}),
        }
    
    def __init__(self, *args, **kwargs):
        household = kwargs.pop('household', None)
        super().__init__(*args, **kwargs)
        if household:
            # Filter parent choices to only show categories from this household
            self.fields['parent'].queryset = Category.objects.filter(
                household=household, 
                parent__isnull=True
            ).order_by('name')
        
        # Customize is_essential field - use checkbox for simple True/False
        self.fields['is_essential'].widget = forms.CheckboxInput(attrs={'class': 'form-check-input'})
        self.fields['is_essential'].label = 'Essential (keep in Barebones template)'
        self.fields['is_essential'].help_text = 'Uncheck to mark as Non-essential (will be zeroed in Barebones template)'
    
    def __init__(self, *args, **kwargs):
        household = kwargs.pop('household', None)
        super().__init__(*args, **kwargs)
        if household:
            # Filter parent choices to only show categories from this household
            self.fields['parent'].queryset = Category.objects.filter(
                household=household, 
                parent__isnull=True
            ).order_by('name')

class BulkCategoryForm(forms.Form):
    def __init__(self, *args, **kwargs):
        household = kwargs.pop('household', None)
        super().__init__(*args, **kwargs)
        if household:
            self.fields['parent'].queryset = Category.objects.filter(
                household=household,
                parent__isnull=True
            ).order_by('name')
    
    parent = forms.ModelChoiceField(
        queryset=Category.objects.none(),  # Will be set in __init__
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Parent Category"
    )
    is_persistent = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label="Persistent",
        help_text="Check if these categories should have persistent budgets (auto-import from previous month)"
    )
    payment_type = forms.ChoiceField(
        choices=Category.PAYMENT_TYPE_CHOICES,
        initial='MANUAL',
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Payment Type",
        help_text="Select how these categories should be tracked"
    )
    names = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Enter one category per line'}),
        help_text="Enter one sub-category per line.",
        label="Sub-categories"
    )

class BulkMainCategoryForm(forms.Form):
    """Form for bulk adding main/parent categories"""
    type = forms.ChoiceField(
        choices=Category.TYPE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Category Type",
        help_text="Select whether these are Income, Expense, or Savings categories"
    )
    is_persistent = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label="Persistent",
        help_text="Check if these categories should have persistent budgets (auto-import from previous month)"
    )
    payment_type = forms.ChoiceField(
        choices=Category.PAYMENT_TYPE_CHOICES,
        initial='MANUAL',
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Payment Type",
        help_text="Select how these categories should be tracked"
    )
    is_essential = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label="Essential",
        help_text="Check if these categories are essential (will be kept in Barebones template)"
    )
    names = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Enter one category per line'}),
        help_text="Enter one main category per line. These will be created as parent categories (not sub-categories).",
        label="Categories"
    )

class CustomUserCreationForm(UserCreationForm):
    """Custom user creation form that uses email as username"""
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'autocomplete': 'email'}),
        label="Email Address",
        help_text="Your email address will be used as your username for login."
    )
    
    class Meta:
        model = User
        fields = ("email", "password1", "password2")
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remove username field
        if 'username' in self.fields:
            del self.fields['username']
        # Make email required and set as username field
        self.fields['email'].required = True
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user
