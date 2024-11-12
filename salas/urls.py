from django.urls import path
from . import views

app_name = 'salas'

urlpatterns = [
    path('home/', views.home, name = 'home')
]
