from django.urls import path
from . import views

urlpatterns = [
    # VISTE PRINCIPALI
    
    # 1. Homepage (Piano Settimanale: corretto da weekly_plan_view a weekly_plan)
    path('', views.weekly_plan, name='weekly_plan'),
    
    # 2. Lista della Spesa
    path('shopping-list/', views.shopping_list, name='shopping_list'),
    
    # VISTE GESTIONE RICETTE
    
    # 3. Creazione Nuova Ricetta (usando la vista recipe_detail senza PK)
    path('recipe/new/', views.recipe_detail, name='recipe_create'),
    
    # 4. Modifica Ricetta Esistente (usando la vista recipe_detail con PK)
    path('recipe/<int:pk>/', views.recipe_detail, name='recipe_update'),
    
    # VISTE GESTIONE SLOT PASTO (MULTI-RICETTA)
    
    # 5. Creazione/Inizializzazione di un nuovo slot pasto
    # Usa <str:day> e <str:meal_type> per identificare lo slot (es: /meal-slot/create/MON/DIN/)
    path('meal-slot/create/<str:day>/<str:meal_type>/', 
         views.meal_slot_create, 
         name='meal_slot_create'),
    
    # 6. Modifica di uno slot pasto esistente (per aggiungere/rimuovere ricette con formset)
    # Usa l'ID (PK) dello slot (es: /meal-slot/update/1/)
    path('meal-slot/update/<int:pk>/', 
         views.meal_slot_update, 
         name='meal_slot_update'),
]