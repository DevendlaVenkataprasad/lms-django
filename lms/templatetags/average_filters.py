from django import template

register = template.Library()

@register.filter
def average(reviews, field):
    values = [getattr(r, field, 0) for r in reviews if getattr(r, field, None) is not None]
    if values:
        return sum(values) / len(values)
    return None

@register.filter
def star_rating(value):
    """
    Converts a numeric rating into a list of 5 elements: 'full', 'half', or 'empty'
    """
    try:
        value = float(value)
    except (ValueError, TypeError):
        return ['empty'] * 5

    stars = []
    for i in range(1, 6):
        if value >= i:
            stars.append('full')
        elif value + 0.5 >= i:
            stars.append('half')
        else:
            stars.append('empty')
    return stars
