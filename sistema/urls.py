from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('usuarios.urls')),
    path('professor/', include('professor.urls')),
    path('salas/', include('salas.urls')),
    path('materiais/', include('materiais.urls')),
    path('gestor/', include('gestor.urls')),
]
