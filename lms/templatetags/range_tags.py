from django import template

register = template.Library()

@register.simple_tag
def star_range(n):
    try:
        return range(1, int(n) + 1)
    except:
        return []
