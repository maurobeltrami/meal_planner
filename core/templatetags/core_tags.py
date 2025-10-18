from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Permette di accedere a un elemento di un dizionario con una chiave."""
    # Se il dizionario è None (o se la chiave non esiste, restituirà None)
    if dictionary is None:
        return None
    return dictionary.get(key)