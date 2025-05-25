from django.db import models
import firebase_admin
from firebase_admin import credentials, firestore, auth

# Verifica se o app já foi inicializado
if not firebase_admin._apps:
    # Carregamento das credenciais do Firebase
    cred = credentials.Certificate(r'C:\Users\Marcelo\Documents\GitHub\Sistema_mapeamento_laboratorio_e_materiais\sistemamapeamentolaboratorio-firebase-adminsdk-dmdt8-f79abd9e82.json')
    firebase_admin.initialize_app(cred)

# Obtendo a referência ao Firestore
db = firestore.client()

class Usuario(models.Model):
    nome = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    senha = models.CharField(max_length=255)

    def __str__(self) -> str:
        return self.nome

    def save(self, *args, **kwargs):
        # Salva no banco local para manter compatibilidade
        super(Usuario, self).save(*args, **kwargs)

        # Salva no Firestore
        user_ref = db.collection('usuarios').document(str(self.id))
        user_ref.set({
            'id': str(self.id),
            'nome': self.nome,
            'email': self.email
        })

    @classmethod
    def create_user(cls, nome, email, senha):
        """
        Cria um usuário no banco local e no Firebase
        """
        # Cria o usuário no banco local
        usuario = cls(nome=nome, email=email, senha=senha)
        usuario.save()

        # Adiciona ao Firestore
        user_ref = db.collection('usuarios').document(str(usuario.id))
        user_ref.set({
            'id': str(usuario.id),
            'nome': nome,
            'email': email
        })

        return usuario

    @classmethod
    def get_by_email(cls, email):
        """
        Busca um usuário pelo email
        """
        try:
            return cls.objects.get(email=email)
        except cls.DoesNotExist:
            # Tenta buscar no Firestore
            users_ref = db.collection('usuarios')
            query = users_ref.where('email', '==', email).limit(1).get()

            if len(query) > 0:
                user_data = query[0].to_dict()
                # Cria o usuário no banco local se não existir
                usuario = cls(
                    id=int(user_data.get('id')),
                    nome=user_data.get('nome'),
                    email=user_data.get('email')
                )
                usuario.save()
                return usuario

            return None

    @classmethod
    def get_by_id(cls, id):
        """
        Busca um usuário pelo ID
        """
        try:
            return cls.objects.get(id=id)
        except cls.DoesNotExist:
            # Tenta buscar no Firestore
            user_ref = db.collection('usuarios').document(str(id))
            user_doc = user_ref.get()

            if user_doc.exists:
                user_data = user_doc.to_dict()
                # Cria o usuário no banco local se não existir
                usuario = cls(
                    id=int(user_data.get('id')),
                    nome=user_data.get('nome'),
                    email=user_data.get('email')
                )
                usuario.save()
                return usuario

            return None
