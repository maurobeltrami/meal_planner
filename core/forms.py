from django import forms
from .models import WeeklyPlan, Recipe

class WeeklyPlanForm(forms.ModelForm):
    # Usiamo una QuerySet per mostrare solo le Ricette che hanno almeno un ingrediente
    recipe = forms.ModelChoiceField(
        queryset=Recipe.objects.filter(ingredients_list__isnull=False).distinct(),
        empty_label="Scegli una ricetta",
        label="Ricetta"
    )

    class Meta:
        model = WeeklyPlan
        # Escludiamo il campo 'date_planned' per mantenere la semplicità del piano settimanale fisso
        fields = ['recipe', 'day_of_week', 'meal_type'] 
        
        # Aggiungiamo stili CSS (opzionale, per abbellire il form)
        widgets = {
            'day_of_week': forms.Select(attrs={'class': 'form-control'}),
            'meal_type': forms.Select(attrs={'class': 'form-control'}),
        }