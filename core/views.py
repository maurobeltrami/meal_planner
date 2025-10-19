from django.shortcuts import render, redirect, get_object_or_404
from django.forms import inlineformset_factory
from django.urls import reverse
from .models import (
    Recipe, Ingredient, RecipeIngredient, 
    MealSlot, MealRecipe, 
    DAY_CHOICES, MEAL_TYPE_CHOICES
)
# Devi assicurarti che IngredientForm e RecipeForm esistano e siano importabili da .forms
from .forms import RecipeForm, IngredientForm 


# ----------------------------------------------------------------------
# VISTA PRINCIPALE: PIANIFICATORE SETTIMANALE
# ----------------------------------------------------------------------

def weekly_plan(request):
    """
    Mostra la griglia settimanale, recuperando tutti gli slot pasto e le ricette associate.
    """
    
    # Prepara la query per recuperare Slot Pasto e tutte le Ricette collegate
    # L'uso di prefetch_related riduce le query al database.
    all_meal_slots = MealSlot.objects.prefetch_related('recipes__recipe').all()
    
    # Inizializzazione della griglia completa (necessaria per garantire l'ordine)
    meal_grid = {}

    # 1. Inizializza tutte le celle della griglia come None
    for day_code, day_name in DAY_CHOICES:
        meal_grid[day_code] = {'meals': {}}
        for meal_code, meal_name in MEAL_TYPE_CHOICES:
            meal_grid[day_code]['meals'][meal_code] = None 
    
    # 2. Popola la griglia con i dati reali
    for slot in all_meal_slots:
        day_code = slot.day
        meal_code = slot.meal_type
        
        # Lista delle ricette collegate a questo slot
        recipes_for_slot = [mr.recipe for mr in slot.recipes.all()] 
        
        meal_grid[day_code]['meals'][meal_code] = {
            'slot_obj': slot,
            'recipes': recipes_for_slot, # Contiene N ricette per questo pasto
        }

    context = {
        'day_choices': DAY_CHOICES,
        'meal_types': MEAL_TYPE_CHOICES,
        'meal_grid': meal_grid,
    }
    
    # Nota: Stai utilizzando il filtro get_item nel template.
    # Assicurati di aver corretto il Template Tag come da suggerimenti precedenti.
    return render(request, 'core/weekly_plan.html', context)


# ----------------------------------------------------------------------
# VISTE GESTIONE SLOT PASTO (MULTI-RICETTA)
# ----------------------------------------------------------------------

# Definisce il Formset per gestire le ricette all'interno di un MealSlot
MealRecipeFormSet = inlineformset_factory(
    MealSlot, 
    MealRecipe, 
    fields=('recipe',), # Campo 'recipe' per selezionare la ricetta
    extra=2, # Inizia con 2 righe vuote per facilitare l'aggiunta
    can_delete=True
)


def meal_slot_update(request, pk):
    """
    Permette di aggiungere/rimuovere ricette (MealRecipe) in uno slot pasto esistente (MealSlot).
    """
    meal_slot = get_object_or_404(MealSlot, pk=pk)
    
    if request.method == 'POST':
        formset = MealRecipeFormSet(request.POST, instance=meal_slot)
        if formset.is_valid():
            formset.save()
            return redirect('weekly_plan')
    else:
        formset = MealRecipeFormSet(instance=meal_slot)
        
    context = {
        'meal_slot': meal_slot,
        'formset': formset,
        'title': f"Modifica Pasto: {meal_slot}",
    }
    # Devi creare il template: core/templates/core/meal_slot_form.html
    return render(request, 'core/meal_slot_form.html', context)


def meal_slot_create(request, day, meal_type):
    """
    Crea un nuovo MealSlot se non esiste (o lo recupera), poi reindirizza alla modifica.
    """
    
    # 1. Tenta di trovare lo slot
    try:
        meal_slot = MealSlot.objects.get(day=day, meal_type=meal_type)
        
    # 2. Se non esiste, lo crea
    except MealSlot.DoesNotExist:
        meal_slot = MealSlot.objects.create(day=day, meal_type=meal_type)
        
    # 3. Reindirizza alla vista di aggiornamento per aggiungere le ricette
    return redirect('meal_slot_update', pk=meal_slot.pk)


# ----------------------------------------------------------------------
# VISTA RICETTA (Placeholder)
# ----------------------------------------------------------------------

def recipe_detail(request, pk=None):
    """
    Placeholder per la vista di dettaglio/creazione/modifica ricetta (RecipeForm e RecipeIngredient Formset).
    Questa vista richiede IngredientForm per la creazione al volo.
    """
    # Esempio per evitare errori, assumendo che i form siano disponibili
    
    recipe_instance = None
    if pk:
        recipe_instance = get_object_or_404(Recipe, pk=pk)
        
    RecipeIngredientFormSet = inlineformset_factory(
        Recipe, RecipeIngredient, fields=('ingredient', 'quantity'), extra=1, can_delete=True
    )

    if request.method == 'POST':
        # Gestione form Aggiungi Ingrediente al volo
        if request.POST.get('action') == 'add_ingredient':
            ingredient_form = IngredientForm(request.POST)
            if ingredient_form.is_valid():
                ingredient_form.save()
                # Reindirizza alla pagina corrente per aggiornare i dropdown
                return redirect(request.path_info) 
        
        # Gestione Form Ricetta e Formset Ingredienti
        recipe_form = RecipeForm(request.POST, instance=recipe_instance)
        formset = RecipeIngredientFormSet(request.POST, instance=recipe_instance)

        if recipe_form.is_valid() and formset.is_valid():
            new_recipe = recipe_form.save()
            formset.instance = new_recipe
            formset.save()
            return redirect('weekly_plan')

    else:
        recipe_form = RecipeForm(instance=recipe_instance)
        formset = RecipeIngredientFormSet(instance=recipe_instance)
        ingredient_form = IngredientForm()

    context = {
        'recipe_form': recipe_form,
        'formset': formset,
        'ingredient_form': ingredient_form,
        'title': f"Modifica Ricetta: {recipe_instance.name}" if recipe_instance else "Crea Nuova Ricetta",
        'is_new': pk is None,
    }
    return render(request, 'core/recipe_detail.html', context)


# ----------------------------------------------------------------------
# VISTA LISTA SPESA (Placeholder)
# ----------------------------------------------------------------------

def shopping_list(request):
    """
    Vista per generare la lista della spesa aggregando gli ingredienti.
    """
    # Logica della lista della spesa non inclusa per brevità, ma la vista è definita.
    context = {'title': 'Lista della Spesa Aggregata'}
    return render(request, 'core/shopping_list.html', context)