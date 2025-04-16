from django import template

register = template.Library()

@register.filter
def average(queryset, field_name):
    """Calculate the average of a field in a queryset."""
    values = [getattr(obj, field_name, 0) for obj in queryset if getattr(obj, field_name, None) is not None]
    return sum(values) / len(values) if values else 0

@register.filter
def get_item(dictionary, key):
    """Get a value from a dictionary by key."""
    return dictionary.get(key)
