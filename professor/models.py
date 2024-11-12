from django.db import models
from salas.models import Salas, Reservas
from .forms import RealizarReservas
from materiais.models import Materiais, Reserva
from .forms import RealizarReserva
from usuarios.models import Usuario
from .validators import validate_date_not_past 
from django.core.exceptions import ValidationError



def validate_date_not_past(date):
    if date < timezone.now().date():
        raise ValidationError("A data não pode ser no passado!")
