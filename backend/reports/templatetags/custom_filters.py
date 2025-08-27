from django import template

register = template.Library()

@register.filter
def pluck(lst, key):
    return [item.get(key) for item in lst]
