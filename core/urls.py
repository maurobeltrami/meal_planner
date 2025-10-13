# File: core/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.weekly_plan_view, name='weekly_plan'),
    path('shopping-list/', views.shopping_list_view, name='shopping_list'), 
    # NUOVO URL: Mappa l'ID (pk) della ricetta alla vista di dettaglio
    path('recipe/<int:pk>/', views.recipe_detail_view, name='recipe_detail'),
]