from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@register.filter
def currency(value):
    """Format number with thousand separators and 2 decimal places"""
    if value is None:
        return "0.00"
    try:
        # Convert to float, format with thousand separators and 2 decimal places
        num = float(value)
        return f"{num:,.2f}"
    except (ValueError, TypeError):
        return "0.00"
