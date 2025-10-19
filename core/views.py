from django.shortcuts import render, redirect, get_object_or_404
from django.forms import inlineformset_factory
from django.urls import reverse
from django.db.models import Sum, F
from django.db.models.functions import Lower 
from .models import (
    Recipe, Ingredient, RecipeIngredient, 
    MealSlot, MealRecipe, 
    DAY_CHOICES, MEAL_TYPE_CHOICES
)
from .forms import RecipeForm, IngredientForm
from django.http import Http404, HttpResponse

# ======================================================================
# FUNZIONE DI UTILITÀ: Costruzione della Griglia Settimanale
# ======================================================================

def build_weekly_grid():
    """Costruisce la struttura dati per la griglia settimanale."""
    
    meal_grid = {
        day_code: {
            'name': day_name,
            'meals': {meal_code: None for meal_code, _ in MEAL_TYPE_CHOICES}
        } 
        for day_code, day_name in DAY_CHOICES
    }

    all_slots = MealSlot.objects.prefetch_related('recipes').all()

    for slot in all_slots:
        
        # Filtra MealRecipe usando 'meal_slot' (il nome del campo)
        meal_recipes = MealRecipe.objects.filter(meal_slot=slot).select_related('recipe')
        recipes_list = [mr.recipe for mr in meal_recipes]
        
        if not recipes_list and not slot:
             continue 
        
        slot_data = {
            'slot_obj': slot,
            'recipes': recipes_list
        }
        
        try:
            meal_grid[slot.day]['meals'][slot.meal_type] = slot_data
        except KeyError:
            continue

    return meal_grid


# ======================================================================
# VISTE PRINCIPALI
# ======================================================================

def weekly_plan(request):
    """Visualizza il piano settimanale e la griglia dei pasti."""
    
    context = {
        'day_choices': DAY_CHOICES,
        'meal_types': MEAL_TYPE_CHOICES,
        'meal_grid': build_weekly_grid(),
    }
    return render(request, 'core/weekly_plan.html', context)


# ======================================================================
# VISTE GESTIONE INGREDIENTI
# ======================================================================

def ingredient_create(request):
    """Crea un nuovo ingrediente e reindirizza alla pagina di creazione ricetta."""
    if request.method == 'POST':
        form = IngredientForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('recipe_create') 
    else:
        form = IngredientForm()
        
    context = {
        'form': form,
        'title': 'Crea Nuovo Ingrediente'
    }
    return render(request, 'core/ingredient_form.html', context)


# ======================================================================
# VISTE RICETTE (Creazione, Dettaglio, Lista)
# ======================================================================

RecipeIngredientFormSet = inlineformset_factory(
    Recipe, RecipeIngredient, 
    fields=('ingredient', 'quantity'), 
    extra=1, can_delete=True
)

def recipe_create(request):
    """Crea una nuova ricetta con i suoi ingredienti."""
    
    if request.method == 'POST':
        form = RecipeForm(request.POST)
        formset = RecipeIngredientFormSet(request.POST, instance=Recipe())
        
        if form.is_valid() and formset.is_valid():
            recipe = form.save()
            formset = RecipeIngredientFormSet(request.POST, instance=recipe)
            if formset.is_valid(): 
                formset.instance = recipe
                formset.save()
                return redirect('recipe_detail', pk=recipe.pk) 
    else:
        form = RecipeForm()
        formset = RecipeIngredientFormSet(instance=Recipe())
        
    context = {
        'form': form,
        'formset': formset,
        'title': 'Crea Nuova Ricetta',
        'is_new': True  
    }
    return render(request, 'core/recipe_detail.html', context)


def recipe_detail(request, pk):
    """Visualizza o modifica una ricetta esistente."""
    
    recipe = get_object_or_404(Recipe, pk=pk)
    
    if request.method == 'POST':
        form = RecipeForm(request.POST, instance=recipe)
        formset = RecipeIngredientFormSet(request.POST, instance=recipe)
        
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            return redirect('recipe_detail', pk=recipe.pk)
    else:
        form = RecipeForm(instance=recipe)
        formset = RecipeIngredientFormSet(instance=recipe)
        
    context = {
        'form': form,
        'formset': formset,
        'title': f'Modifica Ricetta: {recipe.name}',
        'recipe': recipe,
        'is_new': False 
    }
    return render(request, 'core/recipe_detail.html', context)


def recipe_list(request):
    """Visualizza l'elenco di tutte le ricette."""
    
    recipes = Recipe.objects.all().order_by('name')
    context = {'recipes': recipes, 'title': 'Elenco Ricette'}
    return render(request, 'core/recipe_list.html', context)


# ======================================================================
# VISTE SLOT PASTO (Creazione, Aggiornamento)
# ======================================================================

MealRecipeFormSet = inlineformset_factory(
    MealSlot, MealRecipe, 
    fields=('recipe',), 
    extra=1, can_delete=True
)


def meal_slot_create(request, day, meal_type):
    """Crea un nuovo MealSlot e assegna le ricette."""
    
    day_name = dict(DAY_CHOICES).get(day)
    meal_name = dict(MEAL_TYPE_CHOICES).get(meal_type)
    if not day_name or not meal_name:
        raise Http404("Giorno o tipo di pasto non valido.")

    slot, created = MealSlot.objects.get_or_create(
        day=day, 
        meal_type=meal_type
    )

    if request.method == 'POST':
        formset = MealRecipeFormSet(request.POST, instance=slot)
        if formset.is_valid():
            formset.save()
            return redirect('weekly_plan')
    else:
        formset = MealRecipeFormSet(instance=slot)

    context = {
        'slot': slot,
        'formset': formset,
        'title': f'Pianifica: {meal_name} del {day_name}',
        'created': created 
    }
    return render(request, 'core/meal_slot_form.html', context)


def meal_slot_update(request, pk):
    """Aggiorna un MealSlot esistente e le sue ricette."""
    
    slot = get_object_or_404(MealSlot, pk=pk)
    
    if request.method == 'POST':
        formset = MealRecipeFormSet(request.POST, instance=slot)
        if formset.is_valid():
            formset.save()
            return redirect('weekly_plan')
    else:
        formset = MealRecipeFormSet(instance=slot)

    day_name = dict(DAY_CHOICES).get(slot.day)
    meal_name = dict(MEAL_TYPE_CHOICES).get(slot.meal_type)
    
    context = {
        'slot': slot,
        'formset': formset,
        'title': f'Modifica: {meal_name} del {day_name}',
        'created': False 
    }
    return render(request, 'core/meal_slot_form.html', context)


# ======================================================================
# VISTE AZIONI RAPIDE
# ======================================================================

def reset_weekly_plan(request):
    """Azione rapida: Cancella tutti i MealSlot."""
    
    if request.method == 'POST':
        MealSlot.objects.all().delete()
        return redirect('weekly_plan')
    
    return redirect('weekly_plan')


def shopping_list(request):
    """
    Genera la lista della spesa aggregando gli ingredienti.
    CORREZIONE DEFINITIVA: Raggruppa per PK dell'Ingrediente e unità normalizzata.
    """
    
    # 1. Trova tutte le ricette pianificate
    planned_recipe_ids = MealRecipe.objects.values_list('recipe__id', flat=True).distinct()

    # 2. Aggrega: Raggruppa per PK, Nome e Unità normalizzata
    shopping_items = (
        RecipeIngredient.objects
        .filter(recipe__id__in=planned_recipe_ids) 
        .annotate(
            unit_lower=Lower('ingredient__unit')
        )
        .values('ingredient__pk', 'ingredient__name', 'unit_lower') 
        .annotate(total_quantity=Sum('quantity'))
        .order_by('ingredient__name', 'unit_lower') 
    )

    # 3. Preparazione dei dati per il template
    shopping_list = []
    for item in shopping_items:
        unit = item['unit_lower'] if item['unit_lower'] else ''
        
        shopping_list.append({
            'name': item['ingredient__name'],
            'quantity': item['total_quantity'],
            'unit': unit.strip()
        })

    context = {
        'title': 'Lista della Spesa Aggregata',
        'shopping_list': shopping_list,
    }
    return render(request, 'core/shopping_list.html', context)