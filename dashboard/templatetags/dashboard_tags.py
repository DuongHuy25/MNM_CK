from django import template

register = template.Library()

@register.filter
def multiply(value, arg):
    """Nhân hai số với nhau"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0
