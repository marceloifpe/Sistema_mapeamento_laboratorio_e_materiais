from django.urls import path
from . import views

app_name = 'professor'

urlpatterns = [
    path('homee/', views.homee, name='homee'),
    path('ver_salas_professor/<int:id>', views.ver_salas_professor, name='ver_salas_professor'),
    path('realizar_reserva_salas/', views.realizar_reserva_salas, name='realizar_reserva_salas'),
    path('ver_materiais_professor/<int:id>', views.ver_materiais_professor, name='ver_materiais_professor'),
    path('realizar_reserva_materiais/', views.realizar_reserva_materiais, name='realizar_reserva_materiais'),
    path('reserva_sucesso/', views.reserva_sucesso, name='reserva_sucesso'),
    path('reserva_dados_invalidos/', views.reserva_dados_invalidos, name='reserva_dados_invalidos'),
]
