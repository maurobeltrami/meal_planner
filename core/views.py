from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum, Count, F 
from .models import WeeklyPlan, RecipeIngredient, Ingredient, Recipe 
from .forms import WeeklyPlanForm, RecipeForm, IngredientForm, RecipeIngredientFormSet

# --- VISTA 1: Lista della Spesa ---
def shopping_list_view(request):
    
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


# --- VISTA 2: Homepage (weekly_plan_view) ---
def weekly_plan_view(request):
    
    if request.method == 'POST':
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
    else:
        form = WeeklyPlanForm()
    
    all_plans = WeeklyPlan.objects.all()
    
    meal_grid = {}
    for day_code, day_name in WeeklyPlan.DAY_CHOICES:
        meal_grid[day_code] = {
            'name': day_name,
            'meals': {meal_code: None for meal_code, _ in WeeklyPlan.MEAL_CHOICES} 
        }

    for plan in all_plans:
        if plan.day_of_week in meal_grid:
            meal_grid[plan.day_of_week]['meals'][plan.meal_type] = {
                'name': plan.recipe.name,
                'pk': plan.recipe.pk 
            }

    context = {
        'meal_grid': meal_grid,
        'form': form,
        'meal_types': WeeklyPlan.MEAL_CHOICES, 
        'day_choices': WeeklyPlan.DAY_CHOICES,
    }
    return render(request, 'core/weekly_plan.html', context)


# --- VISTA 3: Dettaglio Ricetta (recipe_detail_view) ---
def recipe_detail_view(request, pk=None):
    
    if pk:
        recipe_instance = get_object_or_404(Recipe, pk=pk)
        title = f"Modifica Ricetta: {recipe_instance.name}"
    else:
        recipe_instance = None
        title = "Crea Nuova Ricetta"

    if request.method == 'POST':
        action = request.POST.get('action')
        
        # Caso A: Aggiunta rapida di un Ingrediente (usato dal form in fondo alla pagina)
        if action == 'add_ingredient':
            ingredient_form = IngredientForm(request.POST)
            if ingredient_form.is_valid():
                ingredient_form.save()
                # Reindirizza alla pagina corrente (per aggiornare il selettore)
                return redirect('recipe_update', pk=pk) if pk else redirect('recipe_create')
        
        # Caso B: Salvataggio Ricetta e Formset
        else:
            recipe_form = RecipeForm(request.POST, instance=recipe_instance)
            
            if recipe_form.is_valid():
                recipe = recipe_form.save() 
                formset = RecipeIngredientFormSet(request.POST, instance=recipe)
                
                if formset.is_valid():
                    formset.save()
                    # Dopo il salvataggio, reindirizza alla versione 'update'
                    return redirect('recipe_update', pk=recipe.pk) 
                
                # Se il formset non è valido, non reindirizza, e i form in basso vengono inizializzati
                # correttamente per mostrare gli errori
    
    # Inizializzazione GET/Fallimento POST
    recipe_form = RecipeForm(instance=recipe_instance)
    # L'istanza Recipe() vuota viene usata se recipe_instance è None (creazione)
    formset = RecipeIngredientFormSet(instance=recipe_instance or Recipe()) 
    ingredient_form = IngredientForm() 

    context = {
        'recipe_form': recipe_form,
        'formset': formset,
        'ingredient_form': ingredient_form,
        'title': title,
        'is_new': pk is None # Passiamo questa variabile per la logica del template
    }
    
    return render(request, 'core/recipe_detail.html', context)


# --- VISTA 4: Lista delle Ricette ---
def recipe_list_view(request):
    recipes = Recipe.objects.all().order_by('name')
    context = {
        'recipes': recipes,
        'title': "Seleziona Ricetta da Modificare"
    }
    return render(request, 'core/recipe_list.html', context)