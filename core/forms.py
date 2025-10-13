from django import forms
from django.forms.models import inlineformset_factory # Importazione chiave
from .models import WeeklyPlan, Recipe, Ingredient, RecipeIngredient

# --- 1. Form per la Pianificazione Settimanale ---
class WeeklyPlanForm(forms.ModelForm):
    recipe = forms.ModelChoiceField(
        queryset=Recipe.objects.all(), # Rimosso il filtro per il momento per semplicità di sviluppo
        empty_label="Scegli una ricetta",
        label="Ricetta"
    )

    class Meta:
        model = WeeklyPlan
        fields = ['recipe', 'day_of_week', 'meal_type'] 
        widgets = {
            'day_of_week': forms.Select(attrs={'class': 'form-control'}),
            'meal_type': forms.Select(attrs={'class': 'form-control'}),
        }

# --- 2. Form per creare una Ricetta ---
class RecipeForm(forms.ModelForm):
    class Meta:
        model = Recipe
        fields = ['name']

# --- 3. Form per creare un Ingrediente ---
class IngredientForm(forms.ModelForm):
    class Meta:
        model = Ingredient
        fields = ['name', 'unit']

# --- 4. Formset per Aggiungere/Modificare Ingredienti di una Ricetta ---
RecipeIngredientFormSet = inlineformset_factory(
    parent_model=Recipe,           # Il modello principale a cui è collegato (Ricetta)
    model=RecipeIngredient,        # Il modello che vogliamo modificare (Dettaglio Ingrediente)
    fields=('ingredient', 'quantity'), # Campi da mostrare
    extra=1,                       # Numero di righe vuote iniziali
    can_delete=True                # Permette di rimuovere righe esistenti
)