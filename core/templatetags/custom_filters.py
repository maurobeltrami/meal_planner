from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Filtro personalizzato per accedere agli elementi del dizionario."""
    return dictionary.get(key)