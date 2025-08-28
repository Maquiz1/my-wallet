from django import template

register = template.Library()

@register.filter
def dict_get(d, key):
    """Get a value from a dictionary by key."""
    return d.get(key)

@register.filter
def non_empty(value, default="No description provided"):
    """Return value if not empty/whitespace, else return default."""
    if value and value.strip():
        return value
    return default

@register.filter
def trim(value):
    if value:
        return value.strip()
    return ""

