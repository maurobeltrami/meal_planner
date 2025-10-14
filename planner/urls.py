from django.contrib import admin
from django.urls import path, include # Importa 'include'

urlpatterns = [
    path('admin/', admin.site.urls),
    # DEVE ESSERE PRESENTE: Inoltra le richieste all'app core
    path('', include('core.urls')), 
]