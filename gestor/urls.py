from django.urls import path
from . import views
from .views import calendario_reservas
from .views import calendario_reservas_materiais
from .views import reservas_materiais
from .views import reservas_salas
from .views import SalaListView, SalaCreateView, SalaUpdateView, SalaDetailView, SalaDeleteView
from .views import MaterialListView, MaterialCreateView, MaterialUpdateView, MaterialDetailView, MaterialDeleteView



app_name = 'gestor'

urlpatterns = [
    path('home/', views.home, name='home'),
    path('gestor_ver_salas/', views.gestor_ver_salas, name='gestor_ver_salas'),
    path('gestor_ver_materiais/', views.gestor_ver_materiais, name='gestor_ver_materiais'),
    path('calendario_reservas/', calendario_reservas, name='calendario_reservas'),
    path('calendario_reservas_materiais/', calendario_reservas_materiais, name='calendario_reservas_materiais'),
    path('reservas_materiais/', reservas_materiais, name='reservas_materiais'),
    path('reservas_salas/', reservas_salas, name='reservas_salas'),
    path('salas/', SalaListView.as_view(), name='sala_list'),
    path('salas/nova/', SalaCreateView.as_view(), name='sala_create'),
    path('salas/<int:pk>/editar/', SalaUpdateView.as_view(), name='sala_edit'),
    path('salas/<int:pk>/detail/', SalaDetailView.as_view(), name='sala_detail'),
    path('salas/<int:pk>/excluir/', SalaDeleteView.as_view(), name='sala_delete'),
     path('materiais/', MaterialListView.as_view(), name='material_list'),
    path('materiais/novo/', MaterialCreateView.as_view(), name='material_create'),
    path('materiais/<int:pk>/editar/', MaterialUpdateView.as_view(), name='material_edit'),
    path('materiais/<int:pk>/detalhes/', MaterialDetailView.as_view(), name='material_detail'),
    path('materiais/<int:pk>/excluir/', MaterialDeleteView.as_view(), name='material_delete')
]