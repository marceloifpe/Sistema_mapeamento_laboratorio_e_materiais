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
from datetime import datetime
import pytz  # Para lidar com fuso horário
from usuarios.models import Usuario
import firebase_admin
from firebase_admin import credentials, firestore

# Inicializa o Firebase
if not firebase_admin._apps:
    cred = credentials.Certificate(
        r'C:\Users\Marcelo\Documents\GitHub\Sistema_mapeamento_laboratorio_e_materiais\sistemamapeamentolaboratorio-firebase-adminsdk-dmdt8-8bb2f08483.json'
    )
    firebase_admin.initialize_app(cred)

# Obtendo a referência do Firestore
db = firestore.client()

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
        return f"{self.nome_da_sala} ({self.get_local_display()})"

    def save(self, *args, **kwargs):
        super(Salas, self).save(*args, **kwargs)

        # Atualiza ou cria o documento no Firestore
        sala_ref = db.collection('salas').document(str(self.id))
        sala_ref.set({
            'nome_da_sala': self.nome_da_sala,
            'local': self.get_local_display(),
            'reservado': self.reservado,
        })

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
        if self.salas is None or self.data_reserva is None or self.data_devolucao is None:
            raise ValidationError('Salas, data de reserva e data de devolução devem ser fornecidos.')

        # Verifica se a data de reserva é no passado
        if self.data_reserva < datetime.now(pytz.utc):
            raise ValidationError("A data de reserva não pode ser no passado.")

        # Verifica se já existe uma reserva para o mesmo horário
        conflito = Reservas.objects.filter(
            salas=self.salas,
            data_reserva__lt=self.data_devolucao,
            data_devolucao__gt=self.data_reserva
        ).exists()

        if conflito:
            raise ValidationError('Já existe uma reserva para esta sala no horário selecionado.')

    def save(self, *args, **kwargs):
        # Valida os dados antes de salvar
        self.clean()

        # Salva o objeto no banco de dados do Django
        super(Reservas, self).save(*args, **kwargs)

        # Adiciona ou atualiza a reserva no Firestore
        reserva_ref = db.collection('reservas').document(str(self.id))
        reserva_ref.set({
            'usuarios_id': self.usuarios.id,
            'data_reserva': self.data_reserva.isoformat(),
            'data_devolucao': self.data_devolucao.isoformat(),
            'data_solicitacao': self.data_solicitacao.isoformat(),
            'salas_id': self.salas.id,
            'salas_nome': self.salas.nome_da_sala,
            'salas_local': self.salas.get_local_display(),
        })

        # Atualiza o campo 'reservado' na coleção de salas no Firestore
        sala_ref = db.collection('salas').document(str(self.salas.id))
        sala_ref.update({'reservado': True})

