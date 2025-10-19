# File: core/templatetags/core_tags.py

from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Permette di accedere agli elementi di un dizionario nel template Django."""
    if isinstance(dictionary, dict):
        return dictionary.get(key)
    return None