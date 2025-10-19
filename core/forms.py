from django import forms
from .models import Recipe, Ingredient, RecipeIngredient, MealSlot, MealRecipe

# 1. Form per la Creazione/Modifica Ricetta
class RecipeForm(forms.ModelForm):
    """Form per il nome base della Ricetta."""
    class Meta:
        model = Recipe
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Nome del piatto (es: Lasagne alla Bolognese)'
            }),
        }
        labels = {
            'name': 'Nome della Ricetta',
        }

# 2. Form per la Creazione di Ingredienti al volo
class IngredientForm(forms.ModelForm):
    """Form per creare un nuovo Ingrediente dalla vista Recipe Detail."""
    class Meta:
        model = Ingredient
        fields = ['name', 'unit']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Es: Zucchero, Farina, Uova'
            }),
            'unit': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Es: g, ml, pezzi'
            }),
        }
        labels = {
            'name': 'Nome Ingrediente',
            'unit': 'Unità di Misura',
        }

# NOTA: I Formset (come RecipeIngredientFormSet e MealRecipeFormSet)
# NON vengono definiti qui, ma sono generati direttamente nelle viste 
# (core/views.py) utilizzando la funzione inlineformset_factory.

# Esempio:
# from django.forms import inlineformset_factory
# RecipeIngredientFormSet = inlineformset_factory(Recipe, RecipeIngredient, fields=('ingredient', 'quantity'), extra=1, can_delete=True)
# Questo è il motivo per cui non vedi qui il codice per RecipeIngredient!