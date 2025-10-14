# File: core/urls.py

from django.urls import path
from . import views

urlpatterns = [
    # Pianificazione e Griglia (Homepage)
    path('', views.weekly_plan_view, name='weekly_plan'),
    
    # Lista della Spesa
    path('shopping-list/', views.shopping_list_view, name='shopping_list'), 
    
    # GESTIONE RICETTE
    # 1. Pagina per la lista di tutte le ricette (per la modifica)
    path('recipes/', views.recipe_list_view, name='recipe_list'), 
    # 2. Pagina per creare una NUOVA ricetta (DEVE avere name='recipe_create')
    path('recipe/new/', views.recipe_detail_view, name='recipe_create'), 
    # 3. Pagina per modificare una ricetta esistente
    path('recipe/<int:pk>/', views.recipe_detail_view, name='recipe_update'),
]