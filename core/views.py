# File: core/views.py
from django.shortcuts import render, redirect
from django.db.models import Sum, Count, F # Importa anche Count e F
from .models import WeeklyPlan, RecipeIngredient
from .forms import WeeklyPlanForm
# ... (altre importazioni)

# --- VISTA 1: Generazione della Lista della Spesa Aggregata ---
def shopping_list_view(request):
    """
    Genera la lista della spesa aggregando le quantità degli ingredienti 
    tenendo conto di quante volte ogni ricetta è stata pianificata.
    """
    
    # 1. Calcola quante volte ogni ricetta è stata pianificata in totale (anche i duplicati)
    planned_recipe_counts = (
        WeeklyPlan.objects
        # Raggruppa per ID Ricetta e conta le occorrenze
        .values('recipe_id') 
        .annotate(times_planned=Count('recipe_id'))
    )

    # Crea un dizionario {recipe_id: times_planned} per lookup
    recipe_counts = {item['recipe_id']: item['times_planned'] for item in planned_recipe_counts}
    
    # Ottieni tutti gli ID delle ricette pianificate (senza distinct, ma come lista semplice)
    planned_recipe_ids = list(recipe_counts.keys())
    
    # 2. Aggrega gli ingredienti
    # Query potente: calcola la quantità totale moltiplicando la quantità base per il conteggio
    shopping_list = []
    
    # Eseguiamo il calcolo in Python per facilitare la moltiplicazione per Count
    # Si potrebbe fare in un'unica query complessa, ma questa è più leggibile.

    # Recupera tutti i dettagli degli ingredienti per le ricette pianificate
    base_ingredients = RecipeIngredient.objects.filter(recipe_id__in=planned_recipe_ids)
    
    # Dizionario per sommare gli ingredienti: { (ingrediente_nome, unità): quantità_totale }
    aggregated_totals = {}

    for item in base_ingredients:
        recipe_id = item.recipe_id
        # Quante volte questa ricetta è stata pianificata
        count = recipe_counts.get(recipe_id, 0) 
        
        if count > 0:
            # Calcola la quantità totale necessaria
            total_needed = item.quantity * count
            
            # Chiave per l'aggregazione
            key = (item.ingredient.name, item.ingredient.unit)
            
            # Aggiungi al totale aggregato
            aggregated_totals[key] = aggregated_totals.get(key, 0) + total_needed

    # Format output per il template
    for (name, unit), quantity in aggregated_totals.items():
        shopping_list.append({
            'ingredient__name': name,
            'ingredient__unit': unit,
            'total_quantity': quantity
        })

    # Ordina la lista finale
    shopping_list.sort(key=lambda x: x['ingredient__name'])


    context = {
        'shopping_list': shopping_list,
        'title': "Lista della Spesa Aggregata"
    }

    return render(request, 'core/shopping_list.html', context)

# --- VISTA 2: Visualizzazione e Gestione del Piano Settimanale ---
def weekly_plan_view(request):
    """
    Visualizza la griglia settimanale e gestisce l'aggiunta/modifica dei pasti tramite form.
    """
    if request.method == 'POST':
        form = WeeklyPlanForm(request.POST)
        if form.is_valid():
            # Tenta di aggiornare un pasto esistente o crearne uno nuovo
            try:
                # Cerca se esiste già un piano per quel giorno e tipo di pasto
                plan_instance = WeeklyPlan.objects.get(
                    day_of_week=form.cleaned_data['day_of_week'],
                    meal_type=form.cleaned_data['meal_type']
                )
                # Se esiste, aggiorna solo la ricetta
                plan_instance.recipe = form.cleaned_data['recipe']
                plan_instance.save()
            except WeeklyPlan.DoesNotExist:
                # Se non esiste, salva la nuova istanza
                form.save()
            
            # Reindirizza alla pagina del piano per aggiornare la visualizzazione
            return redirect('weekly_plan') 
    else:
        # Se non è un POST, mostra il form vuoto
        form = WeeklyPlanForm()

    # --- Logica di Visualizzazione della Griglia ---
    all_plans = WeeklyPlan.objects.all()
    
    # Inizializza la struttura dati per la griglia [Giorno] -> [Tipo Pasto] -> Ricetta
    meal_grid = {}
    for day_code, day_name in WeeklyPlan.DAY_CHOICES:
        meal_grid[day_code] = {
            'name': day_name,
            # Inizializza tutti i pasti del giorno come None (vuoti)
            'meals': {meal_code: None for meal_code, _ in WeeklyPlan.MEAL_CHOICES} 
        }

    # Popola la griglia con i dati del database
    for plan in all_plans:
        if plan.day_of_week in meal_grid:
            meal_grid[plan.day_of_week]['meals'][plan.meal_type] = plan.recipe.name

    context = {
        'meal_grid': meal_grid,
        'form': form,
        'meal_types': WeeklyPlan.MEAL_CHOICES, # Usato per l'intestazione colonna nel template
        'day_choices': WeeklyPlan.DAY_CHOICES,   # Usato per l'intestazione riga nel template
    }
    return render(request, 'core/weekly_plan.html', context)