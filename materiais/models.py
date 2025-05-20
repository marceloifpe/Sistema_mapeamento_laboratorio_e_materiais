from django.db import models
from datetime import datetime, timezone
import firebase_admin
from firebase_admin import credentials, firestore
from django.forms import ValidationError
from usuarios.models import Usuario

# Inicializa o Firebase se ainda não estiver inicializado
if not firebase_admin._apps:
    cred = credentials.Certificate(
        r'C:\Users\Marcelo\Documents\GitHub\Sistema_mapeamento_laboratorio_e_materiais\sistemamapeamentolaboratorio-firebase-adminsdk-dmdt8-f79abd9e82.json'
    )
    firebase_admin.initialize_app(cred)

# Obtendo a referência do Firestore
db = firestore.client()

class Materiais(models.Model):
    nome_do_material = models.CharField(max_length=30)
    reservado = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Material'

    def __str__(self):
        return self.nome_do_material

    def save(self, *args, **kwargs):
        super(Materiais, self).save(*args, **kwargs)
        # Adiciona o material à coleção 'materiais' no Firestore
        material_ref = db.collection('materiais').document(str(self.id))
        material_ref.set({
            'nome_do_material': self.nome_do_material,
            'reservado': self.reservado
        })

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

        # Obtém a data e hora atual com fuso horário UTC
        agora = datetime.now(timezone.utc)

        # Verifica se a data de reserva é no passado
        if self.data_reserva and self.data_reserva < agora:
            raise ValidationError("A data de reserva não pode ser no passado.")

        # Verifica se já existe uma reserva para o mesmo material no mesmo horário
        conflito = Reserva.objects.filter(
            materiais=self.materiais,
            data_reserva__lt=self.data_devolucao,
            data_devolucao__gt=self.data_reserva
        ).exists()

        if conflito:
            raise ValidationError('Já existe uma reserva para este material no horário selecionado.')

    def save(self, *args, **kwargs):
        # Valida os dados antes de salvar
        self.clean()

        # Salva o objeto no banco de dados do Django
        super(Reserva, self).save(*args, **kwargs)

        # Adiciona a reserva à coleção 'reservas' no Firestore
        reserva_ref = db.collection('reserva').document(str(self.id))
        reserva_ref.set({
            'usuarios_id': self.usuarios.id,
            'data_reserva': self.data_reserva.isoformat(),  # Formato de string ISO para Firestore
            'data_devolucao': self.data_devolucao.isoformat(),
            'data_solicitacao': self.data_solicitacao.isoformat(),
            'materiais_id': self.materiais.id,
            'materiais_nome': self.materiais.nome_do_material,
        })

        # Atualiza o campo 'reservado' na coleção 'materiais' no Firestore
        material_ref = db.collection('materiais').document(str(self.materiais.id))
        material_ref.update({'reservado': True})
