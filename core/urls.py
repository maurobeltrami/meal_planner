from django.urls import path
from . import views

urlpatterns = [
    # ===============================================
    # VISTE PRINCIPALI E PIANIFICAZIONE
    # ===============================================
    
    # 1. Homepage (Piano Settimanale)
    path('', views.weekly_plan, name='weekly_plan'),
    
    # 2. Lista della Spesa
    path('shopping-list/', views.shopping_list, name='shopping_list'),
    
    # 3. Creazione/Inizializzazione di un nuovo slot pasto
    path('meal-slot/create/<str:day>/<str:meal_type>/', 
         views.meal_slot_create, 
         name='meal_slot_create'),
    
    # 4. Modifica di uno slot pasto esistente
    path('meal-slot/update/<int:pk>/', 
         views.meal_slot_update, 
         name='meal_slot_update'),
    
    # 5. Reset Settimana (usa POST)
    path('reset/', views.reset_weekly_plan, name='reset_weekly_plan'),
    
    # ===============================================
    # VISTE GESTIONE RICETTE
    # ===============================================
    
    # 6. Lista di tutte le ricette (per la modifica centralizzata)
    path('recipes/', views.recipe_list, name='recipe_list'),
    
    # 7. Creazione Nuova Ricetta
    path('recipe/new/', views.recipe_create, name='recipe_create'),
    
    # 8. Modifica Ricetta Esistente (Dettaglio/Update)
    path('recipe/<int:pk>/', views.recipe_detail, name='recipe_detail'),
    
    # 9. Rotta per la creazione di un nuovo ingrediente (aggiunto)
    path('ingredient/new/', views.ingredient_create, name='ingredient_create'),
]