from django.shortcuts import render, redirect, get_object_or_404
from django.forms import inlineformset_factory
from django.urls import reverse
from django.db.models import Sum, F, Count
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
# VISTE GESTIONE RICETTE E INGREDIENTI (CENTRALIZZATE)
# ======================================================================

def recipe_management(request):
    """
    Pagina centrale per la gestione (lista e link al CRUD) delle ricette 
    e per il form di creazione rapida degli ingredienti.
    """
    
    # 1. Gestione Lista Ricette
    recipes = Recipe.objects.all().order_by('name')
    
    # 2. Gestione Form Ingrediente
    ingredient_form = IngredientForm()
    
    context = {
        'recipes': recipes, 
        'title': 'Gestione Ricette e Ingredienti',
        'ingredient_form': ingredient_form,
    }
    return render(request, 'core/recipe_management.html', context)


def ingredient_create(request):
    """
    Crea un nuovo ingrediente e reindirizza in base alla pagina precedente (recipe_create/detail 
    o recipe_management).
    """
    if request.method == 'POST':
        form = IngredientForm(request.POST)
        if form.is_valid():
            form.save()
            
            # Logica di reindirizzamento
            next_url = request.POST.get('next_url')
            recipe_pk = request.POST.get('recipe_pk')
            
            if next_url == 'recipe_create':
                return redirect('recipe_create') 
            elif next_url == 'recipe_detail' and recipe_pk:
                return redirect('recipe_detail', pk=recipe_pk)
            
            # Default: Reindirizza alla pagina di gestione centralizzata
            return redirect('recipe_management') 
    
    # Se la richiesta non è POST o fallisce la validazione, torna alla pagina di gestione
    return redirect('recipe_management') 


# ======================================================================
# VISTE RICETTE (Creazione, Dettaglio, Eliminazione)
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
        # Passiamo un'istanza vuota (Recipe()) per l'inizializzazione del formset
        formset = RecipeIngredientFormSet(request.POST, instance=Recipe()) 
        
        if form.is_valid() and formset.is_valid():
            recipe = form.save()
            # Salviamo il formset legandolo all'istanza appena creata
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
        'is_new': True,
        'ingredient_form': IngredientForm(), # Form ingrediente rapido
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
        'is_new': False,
        'ingredient_form': IngredientForm(), # Form ingrediente rapido
    }
    return render(request, 'core/recipe_detail.html', context)


def recipe_delete(request, pk):
    """Elimina una ricetta esistente."""
    recipe = get_object_or_404(Recipe, pk=pk)
    
    if request.method == 'POST':
        recipe.delete()
        # Reindirizza alla pagina di gestione centralizzata dopo l'eliminazione
        return redirect('recipe_management') 
        
    # Se non è POST, reindirizza alla pagina di modifica
    return redirect('recipe_detail', pk=pk) 


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
    Genera la lista della spesa aggregando gli ingredienti, moltiplicando 
    le dosi per il numero di volte che la ricetta è pianificata.
    """
    
    # Dizionario finale che conterrà { (pk_ingrediente, unità): {dati} }
    final_shopping_list = {}
    
    # 1. Trova quante volte ogni ricetta è stata pianificata nella settimana
    recipe_counts = MealRecipe.objects.values('recipe__pk').annotate(count=Count('recipe__pk'))
    
    # 2. Cicla su ogni ricetta pianificata e il suo conteggio totale
    for item in recipe_counts:
        recipe_pk = item['recipe__pk']
        count = item['count'] # Numero di volte in cui la ricetta è stata pianificata

        # Ottieni tutti gli ingredienti (RecipeIngredient) per questa ricetta specifica
        ingredients = RecipeIngredient.objects.filter(recipe__pk=recipe_pk).select_related('ingredient')
        
        for ri in ingredients:
            name = ri.ingredient.name
            # Normalizza l'unità di misura per l'aggregazione
            unit = ri.ingredient.unit.lower().strip()
            # Chiave univoca per l'aggregazione: PK dell'Ingrediente e unità normalizzata
            key = (ri.ingredient.pk, unit)
            
            # Calcola la quantità totale moltiplicando la dose base per il conteggio
            total_quantity = ri.quantity * count 
            
            # Aggiorna il dizionario finale
            if key not in final_shopping_list:
                final_shopping_list[key] = {
                    'name': name,
                    'quantity': total_quantity,
                    'unit': unit
                }
            else:
                final_shopping_list[key]['quantity'] += total_quantity


    # 3. Preparazione dei dati per il template e ordinamento
    shopping_list = list(final_shopping_list.values())
    shopping_list.sort(key=lambda x: x['name'])


    context = {
        'title': 'Lista della Spesa Aggregata',
        'shopping_list': shopping_list,
    }
    return render(request, 'core/shopping_list.html', context)