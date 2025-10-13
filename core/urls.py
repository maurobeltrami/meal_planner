# File: core/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Mappa l'URL radice ('/') al piano settimanale (è la pagina principale)
    path('', views.weekly_plan_view, name='weekly_plan'),
    # Mappa un URL separato alla lista della spesa
    path('shopping-list/', views.shopping_list_view, name='shopping_list'), 
]