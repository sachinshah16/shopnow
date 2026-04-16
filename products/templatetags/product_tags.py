from django import template

register = template.Library()


@register.filter
def currency(value):
    """Format a number as Indian Rupees."""
    try:
        return f"₹ {float(value):,.0f}"
    except (ValueError, TypeError):
        return value


@register.filter
def star_rating(value):
    """Convert a decimal rating to star characters."""
    try:
        rating = float(value)
        full_stars = int(rating)
        half_star = 1 if rating - full_stars >= 0.5 else 0
        empty_stars = 5 - full_stars - half_star
        return '★' * full_stars + ('½' if half_star else '') + '☆' * empty_stars
    except (ValueError, TypeError):
        return '☆☆☆☆☆'


@register.filter
def multiply(value, arg):
    """Multiply two values."""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0
