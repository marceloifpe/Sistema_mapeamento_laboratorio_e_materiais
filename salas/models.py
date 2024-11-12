# from django.db import models
# from datetime import date
# from usuarios.models import Usuario

# class Salas(models.Model):
#     UABJ = 'UABJ'
#     AEB = 'AEB'
#     LOCAL_CHOICES = [
#         (UABJ, 'UABJ'),
#         (AEB, 'AEB'),
#     ]

#     nome_da_sala = models.CharField(max_length=30)
#     local = models.CharField(max_length=4, choices=LOCAL_CHOICES, default=UABJ)
#     reservado = models.BooleanField(default=False)
    
#     class Meta:
#         verbose_name = 'Sala'

#     def __str__(self):
#         return f"{self.nome_da_sala} ({self.get_local_display()})"  # Retorna nome da sala e local formatados

# class Reservas(models.Model):
#     usuarios = models.ForeignKey(Usuario, on_delete=models.DO_NOTHING)
#     data_reserva = models.DateTimeField()
#     data_devolucao = models.DateTimeField()
#     data_solicitacao = models.DateTimeField(auto_now_add=True)
#     salas = models.ForeignKey(Salas, on_delete=models.DO_NOTHING)
    
#     class Meta:
#         verbose_name = 'Reserva'
    
#     def __str__(self):
#         return f"{self.usuarios} | {self.salas}"

from django.db import models
from django.core.exceptions import ValidationError
from datetime import date
from usuarios.models import Usuario

class Salas(models.Model):
    UABJ = 'UABJ'
    AEB = 'AEB'
    LOCAL_CHOICES = [
        (UABJ, 'UABJ'),
        (AEB, 'AEB'),
    ]

    nome_da_sala = models.CharField(max_length=30)
    local = models.CharField(max_length=4, choices=LOCAL_CHOICES, default=UABJ)
    reservado = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = 'Sala'

    def __str__(self):
        return f"{self.nome_da_sala} ({self.get_local_display()})"  # Retorna nome da sala e local formatados

class Reservas(models.Model):
    usuarios = models.ForeignKey(Usuario, on_delete=models.DO_NOTHING)
    data_reserva = models.DateTimeField()
    data_devolucao = models.DateTimeField()
    data_solicitacao = models.DateTimeField(auto_now_add=True)
    salas = models.ForeignKey(Salas, on_delete=models.DO_NOTHING)
    
    class Meta:
        verbose_name = 'Reserva'
    
    def __str__(self):
        return f"{self.usuarios} | {self.salas}"

    def clean(self):
        # Certifique-se de que materiais, data_reserva e data_devolucao não são None
        if self.salas is None or self.data_reserva is None or self.data_devolucao is None:
            raise ValidationError('Salas, data de reserva e data de devolução devem ser fornecidos.')

        # Verifica se já existe uma reserva para o mesmo material no mesmo horário
        conflito = Reservas.objects.filter(
            salas=self.salas,
            data_reserva__lt=self.data_devolucao,
            data_devolucao__gt=self.data_reserva
        ).exists()

        if conflito:
            raise ValidationError('Já existe uma reserva para este material no horário selecionado.')

   

       

    def save(self, *args, **kwargs):
        self.clean()
        return super(Reservas, self).save(*args, **kwargs)
