# File: core/admin.py

from django.contrib import admin
from .models import Ingredient, Recipe, RecipeIngredient, WeeklyPlan

# --- 1. Definizione dell'Inline per RecipeIngredient ---
# Permette di inserire/modificare gli ingredienti direttamente dalla pagina della Ricetta.
class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1  # Numero di righe vuote da mostrare per l'aggiunta rapida
    # Campi visualizzati nell'inline (opzionale)
    fields = ('ingredient', 'quantity',) 

# --- 2. Definizione dell'Admin per la Ricetta ---
# Questa classe specifica come deve essere visualizzato il modello Recipe nell'Admin.
class RecipeAdmin(admin.ModelAdmin):
    # Usa l'Inline definito sopra
    inlines = [RecipeIngredientInline]
    # Colonne visualizzate nella lista principale delle ricette
    list_display = ('name',) 
    # Permette la ricerca per nome
    search_fields = ('name',)

# --- 3. Registrazione dei Modelli ---

# Modelli semplici (registrazione standard)
admin.site.register(Ingredient)
admin.site.register(WeeklyPlan)

# Registra la Ricetta usando la classe Admin modificata (con Inlines)
admin.site.register(Recipe, RecipeAdmin) 

# NON è necessario registrare RecipeIngredient separatamente, 
# poiché è gestito come Inline di Recipe.