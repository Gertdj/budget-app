"""
Serializers for Finance Flow API
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    Household, Category, Budget, Transaction, 
    CategoryNote, BudgetTemplate, TemplateCategory
)

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model"""
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'date_joined']
        read_only_fields = ['id', 'date_joined']


class HouseholdSerializer(serializers.ModelSerializer):
    """Serializer for Household model"""
    members = UserSerializer(many=True, read_only=True)
    member_ids = serializers.PrimaryKeyRelatedField(
        many=True, 
        queryset=User.objects.all(),
        source='members',
        write_only=True,
        required=False
    )
    
    class Meta:
        model = Household
        fields = ['id', 'name', 'members', 'member_ids', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for Category model"""
    household_name = serializers.CharField(source='household.name', read_only=True)
    parent_name = serializers.CharField(source='parent.name', read_only=True, allow_null=True)
    children_count = serializers.IntegerField(source='children.count', read_only=True)
    notes_count = serializers.IntegerField(source='notes.count', read_only=True)
    
    class Meta:
        model = Category
        fields = [
            'id', 'household', 'household_name', 'name', 'type', 
            'is_persistent', 'payment_type', 'is_essential', 
            'parent', 'parent_name', 'children_count', 'notes_count'
        ]
        read_only_fields = ['id']


class CategoryListSerializer(serializers.ModelSerializer):
    """Simplified serializer for category lists"""
    parent_name = serializers.CharField(source='parent.name', read_only=True, allow_null=True)
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'type', 'is_persistent', 'payment_type', 
                 'is_essential', 'parent', 'parent_name']


class BudgetSerializer(serializers.ModelSerializer):
    """Serializer for Budget model"""
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_type = serializers.CharField(source='category.type', read_only=True)
    
    class Meta:
        model = Budget
        fields = [
            'id', 'category', 'category_name', 'category_type',
            'amount', 'start_date', 'end_date', 'is_paid'
        ]
        read_only_fields = ['id']


class TransactionSerializer(serializers.ModelSerializer):
    """Serializer for Transaction model"""
    category_name = serializers.CharField(source='category.name', read_only=True, allow_null=True)
    household_name = serializers.CharField(source='household.name', read_only=True)
    
    class Meta:
        model = Transaction
        fields = [
            'id', 'household', 'household_name', 'amount', 'date',
            'description', 'category', 'category_name', 'type',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class CategoryNoteSerializer(serializers.ModelSerializer):
    """Serializer for CategoryNote model"""
    category_name = serializers.CharField(source='category.name', read_only=True)
    author_username = serializers.CharField(source='author.email', read_only=True, allow_null=True)
    # For backward compatibility with existing JS which expects `note.author` as a display name
    author = serializers.CharField(source='author.email', read_only=True, allow_null=True)
    
    class Meta:
        model = CategoryNote
        fields = [
            'id', 'category', 'category_name', 'author', 'author_username',
            'note', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'author', 'created_at', 'updated_at']


class TemplateCategorySerializer(serializers.ModelSerializer):
    """Serializer for TemplateCategory model"""
    parent_name = serializers.CharField(source='parent.name', read_only=True, allow_null=True)
    
    class Meta:
        model = TemplateCategory
        fields = [
            'id', 'template', 'name', 'type', 'is_persistent',
            'payment_type', 'is_essential', 'parent', 'parent_name', 'display_order'
        ]
        read_only_fields = ['id']


class BudgetTemplateSerializer(serializers.ModelSerializer):
    """Serializer for BudgetTemplate model"""
    created_by_username = serializers.CharField(source='created_by.email', read_only=True, allow_null=True)
    category_count = serializers.IntegerField(source='categories.count', read_only=True)
    categories = TemplateCategorySerializer(many=True, read_only=True)
    
    class Meta:
        model = BudgetTemplate
        fields = [
            'id', 'name', 'description', 'is_default', 'is_active',
            'created_by', 'created_by_username', 'created_at', 'updated_at',
            'category_count', 'categories'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

