from django.shortcuts import render, redirect, get_object_or_404 # Aggiunta get_object_or_404
from django.db.models import Sum, Count, F 
from .models import WeeklyPlan, RecipeIngredient, Ingredient, Recipe 
from .forms import WeeklyPlanForm, RecipeForm, IngredientForm, RecipeIngredientFormSet # Importazione Formset

# --- VISTA 1: Generazione della Lista della Spesa Aggregata ---
def shopping_list_view(request):
    """
    Genera la lista della spesa aggregando le quantità degli ingredienti 
    tenendo conto di quante volte ogni ricetta è stata pianificata.
    """
    
    planned_recipe_counts = (
        WeeklyPlan.objects
        .values('recipe_id') 
        .annotate(times_planned=Count('recipe_id'))
    )

    recipe_counts = {item['recipe_id']: item['times_planned'] for item in planned_recipe_counts}
    planned_recipe_ids = list(recipe_counts.keys())
    
    
    base_ingredients = RecipeIngredient.objects.filter(recipe_id__in=planned_recipe_ids)
    
    aggregated_totals = {}

    for item in base_ingredients:
        recipe_id = item.recipe_id
        count = recipe_counts.get(recipe_id, 0) 
        
        if count > 0:
            total_needed = item.quantity * count
            key = (item.ingredient.name, item.ingredient.unit)
            aggregated_totals[key] = aggregated_totals.get(key, 0) + total_needed

    shopping_list = []
    for (name, unit), quantity in aggregated_totals.items():
        shopping_list.append({
            'ingredient__name': name,
            'ingredient__unit': unit,
            'total_quantity': quantity
        })

    shopping_list.sort(key=lambda x: x['ingredient__name'])


    context = {
        'shopping_list': shopping_list,
        'title': "Lista della Spesa Aggregata"
    }

    return render(request, 'core/shopping_list.html', context)


# --- VISTA 2: Visualizzazione e Gestione del Piano Settimanale (e Forms di Creazione) ---
def weekly_plan_view(request):
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'add_plan':
            form = WeeklyPlanForm(request.POST)
            if form.is_valid():
                try:
                    plan_instance = WeeklyPlan.objects.get(
                        day_of_week=form.cleaned_data['day_of_week'],
                        meal_type=form.cleaned_data['meal_type']
                    )
                    plan_instance.recipe = form.cleaned_data['recipe']
                    plan_instance.save()
                except WeeklyPlan.DoesNotExist:
                    form.save()
                return redirect('weekly_plan')
        
        elif action == 'add_recipe':
            recipe_form = RecipeForm(request.POST)
            if recipe_form.is_valid():
                recipe_form.save()
                return redirect('weekly_plan')
                
        elif action == 'add_ingredient':
            ingredient_form = IngredientForm(request.POST)
            if ingredient_form.is_valid():
                ingredient_form.save()
                return redirect('weekly_plan')
    
    else:
        form = WeeklyPlanForm()
        recipe_form = RecipeForm()
        ingredient_form = IngredientForm()

    # --- Logica di Visualizzazione della Griglia (MODIFICATA per passare l'ID) ---
    all_plans = WeeklyPlan.objects.all()
    
    meal_grid = {}
    for day_code, day_name in WeeklyPlan.DAY_CHOICES:
        meal_grid[day_code] = {
            'name': day_name,
            'meals': {meal_code: None for meal_code, _ in WeeklyPlan.MEAL_CHOICES} 
        }

    for plan in all_plans:
        if plan.day_of_week in meal_grid:
            # Salviamo un dizionario con nome E ID (pk) per creare il link nel template
            meal_grid[plan.day_of_week]['meals'][plan.meal_type] = {
                'name': plan.recipe.name,
                'pk': plan.recipe.pk 
            }

    context = {
        'meal_grid': meal_grid,
        'form': form,
        'recipe_form': recipe_form,
        'ingredient_form': ingredient_form,
        'meal_types': WeeklyPlan.MEAL_CHOICES, 
        'day_choices': WeeklyPlan.DAY_CHOICES,
    }
    return render(request, 'core/weekly_plan.html', context)


# --- VISTA 3: Gestione Dettagli Ricetta e Ingredienti (Formset) ---
def recipe_detail_view(request, pk):
    """
    Gestisce la visualizzazione del nome della ricetta e il formset per aggiungere/modificare 
    i suoi ingredienti e le quantità.
    """
    recipe = get_object_or_404(Recipe, pk=pk)
    
    if request.method == 'POST':
        # Passiamo i dati POST e l'istanza della ricetta al formset
        formset = RecipeIngredientFormSet(request.POST, instance=recipe)
        
        if formset.is_valid():
            formset.save()
            return redirect('recipe_detail', pk=recipe.pk) 
    else:
        # Crea il formset popolato con i dati esistenti (o vuoto se è una nuova ricetta)
        formset = RecipeIngredientFormSet(instance=recipe)
    
    context = {
        'recipe': recipe,
        'formset': formset,
        'title': f"Dettagli Ingredienti: {recipe.name}"
    }
    
    return render(request, 'core/recipe_detail.html', context)