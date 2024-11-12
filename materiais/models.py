from django.db import models
from datetime import date

from django.forms import ValidationError
from usuarios.models import Usuario

class Materiais(models.Model):
    nome_do_material = models.CharField(max_length=30)
    reservado = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = 'Material'

    def __str__(self):
        return self.nome_do_material

class Reserva(models.Model):
    usuarios = models.ForeignKey(Usuario, on_delete=models.DO_NOTHING)
    data_reserva = models.DateTimeField()
    data_devolucao = models.DateTimeField()
    data_solicitacao = models.DateTimeField(auto_now_add=True)
    materiais = models.ForeignKey(Materiais, on_delete=models.DO_NOTHING)
    
    class Meta:
        verbose_name = 'Reserva'
    
    def __str__(self) -> str:
        return f"{self.usuarios} | {self.materiais}"

    def clean(self):
         # Certifique-se de que materiais, data_reserva e data_devolucao não são None
        if self.materiais is None or self.data_reserva is None or self.data_devolucao is None:
           raise ValidationError('Materiais, data de reserva e data de devolução devem ser fornecidos.')

        # Verifica se já existe uma reserva para o mesmo material no mesmo horário
        conflito = Reserva.objects.filter(
            materiais=self.materiais,
            data_reserva__lt=self.data_devolucao,
            data_devolucao__gt=self.data_reserva
        ).exists()

        if conflito:
            raise ValidationError('Já existe uma reserva para este material no horário selecionado.')

    def save(self, *args, **kwargs):
        self.clean()
        return super(Reserva, self).save(*args, **kwargs)

