# Importando as bibliotecas necessárias
from datetime import timezone
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DetailView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from gestor.forms import MaterialForm, SalaForm
from materiais.models import Materiais, Reserva
from usuarios.models import Usuario
from salas.models import Salas
from salas.models import Reservas
from itertools import groupby
from django.contrib import messages
from django.shortcuts import render
from django.db.models import F
from itertools import groupby
from .models import Reserva
from django.utils import timezone
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import cv2
import numpy as np
import re
import os
import torch
from ultralytics import YOLO



def home(request):
    # Verifica se há um usuário na sessão
    if request.session.get('usuario'):
        try:
            # Tenta obter o objeto de usuário com base no ID armazenado na sessão
            usuario = Usuario.objects.get(id=request.session['usuario'])

            # Cria um contexto para ser passado para o template
            context = {
                'usuario': usuario,          # Objeto de usuário
                'nome_usuario': usuario.nome, # Atributo 'nome' do usuário
                'salas': Salas.objects.all(),   # Obtém todas as instâncias do modelo Salas
                'usuario_logado2': usuario,
            }

            # Renderiza o template 'home.html' com o contexto
            return render(request, 'home.html', context)

        except Usuario.DoesNotExist:
            # Trata o caso em que o usuário não existe
            return render(request, 'error.html', {'message': 'Usuário não existe'})

    else:
        # Redireciona para a página de login se não houver usuário na sessão
        return redirect('/auth/login/?status=2')

# Função para o gestor visualizar as salas

def gestor_ver_salas(request):
    # Verifica se há um usuário na sessão
    if request.session.get('usuario'):
        try:
            # Tenta obter o objeto de usuário com base no ID armazenado na sessão
            usuario = Usuario.objects.get(id=request.session['usuario'])

            # Cria um contexto para ser passado para o template
            context = {
                'usuario': usuario,             # Objeto de usuário
                'nome_usuario': usuario.nome,   # Atributo 'nome' do usuário
                'salas': Salas.objects.all(),   # Obtém todas as instâncias do modelo Salas
                'usuario_logado2': usuario
            }

            return render(request, 'gestor_ver_salas.html', context)

        except Usuario.DoesNotExist:
            # Trata o caso em que o usuário não existe
            return render(request, 'error.html', {'message': 'Usuário não existe'})
    else:
        # Redireciona para a página de login se não houver usuário na sessão
        return redirect('/auth/login/?status=2')

def gestor_ver_materiais(request):
    if request.session.get('usuario'):
        try:
            usuario = Usuario.objects.get(id=request.session['usuario'])

            context = {
                'usuario': usuario,
                'nome_usuario': usuario.nome,
                'materiais': Materiais.objects.all(),
                'usuario_logado2': usuario
            }

            return render(request, 'gestor_ver_materiais.html', context)
        except Usuario.DoesNotExist:
            # Trata o caso em que o usuário não existe
            return render(request, 'error.html', {'message': 'Usuário não existe'})
    else:
        # Redireciona para a página de login se não houver usuário na sessão
        return redirect('/auth/login/?status=2')

#Função para exibir calendario salas-Tabela
def calendario_reservas(request):
    if request.session.get('usuario'):
        try:
            usuario = Usuario.objects.get(id=request.session['usuario'])
            reservas = Reservas.objects.all()
            reservas_ordenadas = sorted(reservas, key=lambda x: x.data_reserva)
            grupos_por_data = {data: list(grupo) for data, grupo in groupby(reservas_ordenadas, key=lambda x: x.data_reserva)}

            eventos = []

            for data, reservas_na_data in grupos_por_data.items():
                eventos_na_data = []
                for reserva in reservas_na_data:
                    # Converte a data de reserva e a data de devolução para o fuso horário desejado
                    data_reserva = reserva.data_reserva.astimezone(timezone.get_default_timezone())
                    data_devolucao = reserva.data_devolucao.astimezone(timezone.get_default_timezone())
                    data_solicitacao = reserva.data_solicitacao.astimezone(timezone.get_default_timezone())

                    evento = {
                        'title': f"Reserva por {reserva.usuarios.nome} - {reserva.salas.nome_da_sala}",
                        'start': data_reserva.strftime("%d/%m/%Y %H:%M" ),
                        'end': data_devolucao.strftime("%d/%m/%Y %H:%M" ),  # Formata a data de devolução corretamente
                        'url': f'/calendario_reservas.html/{reserva.id}',  # Substitue com a URL correta para detalhes da reserva
                        'data_solicitacao': data_solicitacao.strftime("%d/%m/%Y %H:%M") if reserva.data_solicitacao else None,
                    }
                    eventos_na_data.append(evento)
                eventos.append({'data': data.strftime("%d/%m/%Y"), 'eventos': eventos_na_data})

            return render(request, 'calendario_reservas.html', {'eventos': eventos, 'usuario_logado2': usuario})

        except Usuario.DoesNotExist:
            messages.error(request, 'Usuário não encontrado.')
            return render(request, 'error.html', {'message': 'Usuário não existe'})
    else:
        messages.warning(request, 'Faça login para acessar o calendário de reservas.')
        return redirect('/auth/login/?status=2')



# Função para exibir o calendário de reservas de materiais
def calendario_reservas_materiais(request):
    if request.session.get('usuario'):
        try:
            usuario = Usuario.objects.get(id=request.session['usuario'])

            # Obtenha todas as reservas de materiais do banco de dados
            reservas_materiais = Reserva.objects.filter(materiais__isnull=False)

            # Ordene as reservas por data de reserva
            reservas_ordenadas = sorted(reservas_materiais, key=lambda x: x.data_reserva)

            # Agrupe as reservas por data de reserva
            grupos_por_data = {data: list(grupo) for data, grupo in groupby(reservas_ordenadas, key=lambda x: x.data_reserva)}

            # Crie uma lista para armazenar os eventos do calendário de materiais
            eventos_materiais = []

            for data, reservas_na_data in grupos_por_data.items():
                eventos_na_data = []
                for reserva in reservas_na_data:
                    # Converte a data de reserva e a data de devolução para o fuso horário desejado
                    data_reserva = reserva.data_reserva.astimezone(timezone.get_default_timezone())
                    data_devolucao = reserva.data_devolucao.astimezone(timezone.get_default_timezone())
                    data_solicitacao = reserva.data_solicitacao.astimezone(timezone.get_default_timezone())


                    evento_material = {
                        'title': f"Reserva de Material por {reserva.usuarios.nome} - {reserva.materiais.nome_do_material}",
                        'start': data_reserva.strftime("%d/%m/%Y %H:%M"),
                        'end': data_devolucao.strftime("%d/%m/%Y %H:%M"),
                        'url': f'/calendario_reservas_materiais.html/{reserva.id}',
                        'data_solicitacao': data_solicitacao.strftime("%d/%m/%Y %H:%M" ) if reserva.data_solicitacao else None,
                        'tipo_reserva': 'Material',  # Indica que é uma reserva de material
                    }
                    eventos_na_data.append(evento_material)
                eventos_materiais.append({'data': data.strftime("%d/%m/%Y"), 'eventos': eventos_na_data})

            return render(request, 'calendario_reservas_materiais.html', {'eventos_materiais': eventos_materiais, 'usuario_logado2': usuario})

        except Usuario.DoesNotExist:
            messages.error(request, 'Usuário não encontrado.')
            return render(request, 'error.html', {'message': 'Usuário não existe'})
    else:
        messages.warning(request, 'Faça login para acessar o calendário de reservas.')
        return redirect('/auth/login/?status=2')

def reservas_materiais(request):
    if request.session.get('usuario'):
        try:
            usuario = Usuario.objects.get(id=request.session['usuario'])
            reservas = Reserva.objects.all()

            # Ordene as reservas por data de reserva
            reservas_ordenadas = reservas.order_by('data_reserva')

            # Agrupe as reservas por data de reserva
            grupos_por_data = {data: list(grupo) for data, grupo in groupby(reservas_ordenadas, key=lambda x: x.data_reserva)}

            eventos_mat = []

            for data, reservas_na_data in grupos_por_data.items():
                for reserva in reservas_na_data:
                    # Adicione o nome do usuário ao título do evento
                    evento_material = {
                        'title': f"Reserva de {reserva.usuarios.nome} - {reserva.materiais.nome_do_material}",
                        'start': reserva.data_reserva.isoformat(),
                        # 'end': reserva.data_devolucao.isoformat(),
                    }
                    eventos_mat.append(evento_material)

            return render(request, 'reservas_materiais.html', {'eventos_mat': eventos_mat, 'usuario_logado2': usuario})
        except Reserva.DoesNotExist:
            messages.error(request, 'Reservas não encontradas.')
            return render(request, 'error.html', {'message': 'Reservas não existem'})
    else:
        # Se não houver um usuário na sessão
        messages.warning(request, 'Faça login para acessar o calendário de reservas.')
        return redirect('/auth/login/?status=2')
def reservas_salas(request):
    if request.session.get('usuario'):
        try:
            usuario = Usuario.objects.get(id=request.session['usuario'])
            reservas = Reservas.objects.all()

            # Ordene as reservas por data de reserva
            reservas_ordenadas = reservas.order_by('data_reserva')

            # Agrupe as reservas por data de reserva
            grupos_por_data = {data: list(grupo) for data, grupo in groupby(reservas_ordenadas, key=lambda x: x.data_reserva)}

            eventos_sal = []

            for data, reservas_na_data in grupos_por_data.items():
                for reserva in reservas_na_data:
                    # Adicione o nome do usuário ao título do evento
                    evento_sala = {
                        'title': f"Reserva de {reserva.usuarios.nome} - {reserva.salas.nome_da_sala}",
                        'start': reserva.data_reserva.isoformat(),
                        # 'end': reserva.data_devolucao.isoformat(),
                    }
                    eventos_sal.append(evento_sala)

            return render(request, 'reservas_salas.html', {'eventos_sal': eventos_sal, 'usuario_logado2': usuario})
        except Reservas.DoesNotExist:
            messages.error(request, 'Reservas não encontradas.')
            return render(request, 'error.html', {'message': 'Reservas não existem'})
    else:
        # Se não houver um usuário na sessão
        messages.warning(request, 'Faça login para acessar o calendário de reservas.')
        return redirect('/auth/login/?status=2')


#CRUD Salas
class SalaListView(ListView):
    model = Salas
    template_name = 'sala_list.html'
    context_object_name = 'salas'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['usuario_logado2'] = self.request.user  # Adicione esta linha para passar o usuário logado para o template
        return context

class SalaCreateView(CreateView):
    model = Salas
    form_class = SalaForm
    template_name = 'sala_form.html'
    success_url = reverse_lazy('gestor:sala_list')

class SalaUpdateView(UpdateView):
    model = Salas
    form_class = SalaForm
    template_name = 'sala_form.html'
    success_url = reverse_lazy('gestor:sala_list')

class SalaDetailView(DetailView):
    model = Salas
    template_name = 'sala_detail.html'
    context_object_name = 'sala'

class SalaDeleteView(DeleteView):
    model = Salas
    template_name = 'sala_confirm_delete.html'
    success_url = reverse_lazy('gestor:sala_list')

#CRUD Materiais
class MaterialListView(ListView):
    model = Materiais
    template_name = 'material_list.html'
    context_object_name = 'materiais'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['usuario_logado2'] = self.request.user  # Adicione esta linha para passar o usuário logado para o template
        return context

class MaterialCreateView(CreateView):
    model = Materiais
    form_class = MaterialForm
    template_name = 'material_form.html'
    success_url = reverse_lazy('gestor:material_list')

class MaterialUpdateView(UpdateView):
    model = Materiais
    form_class = MaterialForm
    template_name = 'material_form.html'
    success_url = reverse_lazy('gestor:material_list')

class MaterialDetailView(DetailView):
    model = Materiais
    template_name = 'material_detail.html'
    context_object_name = 'material'

class MaterialDeleteView(DeleteView):
    model = Materiais
    template_name = 'material_confirm_delete.html'
    success_url = reverse_lazy('gestor:material_list')

# Diretório para salvar o modelo YOLO
MODEL_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'yolo_model')
os.makedirs(MODEL_DIR, exist_ok=True)

# Caminho para o modelo YOLO
MODEL_PATH = os.path.join(MODEL_DIR, 'best.pt')

# Função para carregar ou baixar o modelo YOLO
def load_yolo_model():
    """
    Carrega o modelo YOLO ou usa um modelo pré-treinado
    """
    try:
        # Verificar se o modelo personalizado existe
        if os.path.exists(MODEL_PATH):
            model = YOLO(MODEL_PATH)
        else:
            # Usar modelo pré-treinado YOLOv8n
            model = YOLO('yolov8n.pt')
        return model
    except Exception as e:
        print(f"Erro ao carregar modelo YOLO: {str(e)}")
        return None
def reconhecer_material_yolo(frame, model, debug_info=None):
    """
    Função para reconhecer o tipo de material na imagem usando YOLO
    Retorna o tipo de material detectado: 'protoboard' ou 'projetor' ou None
    """
    if model is None:
        if debug_info is not None:
            debug_info['motivo'] = "Modelo YOLO não carregado"
        return None

    # Classes que o modelo pode detectar
    # Usando modelo pré-treinado, mapeamos classes relevantes para nossos materiais
    class_mapping = {
        'keyboard': 'protoboard',  # Protoboard se parece com teclado na visão do modelo
        'remote': 'protoboard',    # Ou com controle remoto
        'mouse': 'protoboard',     # Ou com mouse
        'cell phone': 'protoboard', # Ou com celular
        'laptop': 'projetor',      # Projetor pode ser confundido com laptop
        'tv': 'projetor',          # Ou com TV
        'monitor': 'projetor'      # Ou com monitor
    }

    # Fazer predição com YOLO
    results = model(frame)

    # Criar cópia do frame para debug
    debug_frame = frame.copy()

    # Verificar se detectou algum objeto
    if len(results) == 0 or len(results[0].boxes) == 0:
        if debug_info is not None:
            debug_info['motivo'] = "Nenhum objeto detectado pelo YOLO"
        return None

    # Processar resultados
    for result in results:
        # Desenhar caixas e labels para debug
        annotated_frame = result.plot()
        cv2.imshow("Detecção YOLO", annotated_frame)

        # Extrair informações das detecções
        for box in result.boxes:
            # Obter classe e confiança
            cls_id = int(box.cls.item())
            cls_name = result.names[cls_id]
            confidence = box.conf.item()

            # Verificar se a classe detectada está no nosso mapeamento
            if cls_name in class_mapping and confidence > 0.4:  # Threshold de confiança
                material_detectado = class_mapping[cls_name]

                # Obter coordenadas da caixa
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)

                # Desenhar caixa e label no frame original
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, f"{material_detectado} ({confidence:.2f})",
                           (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

                return material_detectado

    # Se chegou aqui, não encontrou nenhum material conhecido
    if debug_info is not None:
        debug_info['motivo'] = "Objetos detectados, mas nenhum corresponde aos materiais conhecidos"

    return None

def gerar_nome_unico(tipo_material, model):
    """
    Gera um nome único para o material seguindo o padrão tipo-XX
    """
    # Buscar todos os materiais do mesmo tipo
    materiais_existentes = model.objects.filter(nome_do_material__startswith=f"{tipo_material}-")

    # Extrair os números dos nomes existentes
    numeros = []
    for material in materiais_existentes:
        match = re.search(r'-(\d+)$', material.nome_do_material)
        if match:
            numeros.append(int(match.group(1)))

    # Determinar o próximo número
    proximo_numero = 1
    if numeros:
        proximo_numero = max(numeros) + 1

    # Formatar o nome com zeros à esquerda (ex: protoboard-01)
    return f"{tipo_material}-{proximo_numero:02d}"

def cadastrar_material_camera(request):
    """
    Função para capturar imagem da webcam, reconhecer o material com YOLO
    e cadastrá-lo com nome único
    """
    # Se for um POST, significa que o usuário está confirmando o cadastro manual
    if request.method == 'POST':
        tipo_material = request.POST.get('tipo_material')
        if tipo_material:
            try:
                # Gerar nome único para o material
                nome_unico = gerar_nome_unico(tipo_material, Materiais)

                # Criar o material com o nome único
                Materiais.objects.create(nome_do_material=nome_unico)

                # Mensagem de sucesso
                messages.success(request, f'Material {nome_unico} cadastrado manualmente com sucesso!')
            except Exception as e:
                # Em caso de erro no cadastro
                messages.error(request, f'Erro ao cadastrar material: {str(e)}')

        return redirect('gestor:material_list')

    # Carregar modelo YOLO
    model = load_yolo_model()
    if model is None:
        messages.error(request, 'Erro ao carregar modelo YOLO. Verifique se as dependências estão instaladas.')
        return redirect('gestor:material_list')

    cap = cv2.VideoCapture(0)
    material_detectado = None
    tipo_material = None
    debug_info = {'motivo': "Nenhum material detectado ainda"}

    # Verificar se a câmera foi aberta corretamente
    if not cap.isOpened():
        messages.error(request, 'Erro ao acessar a câmera. Verifique se está conectada corretamente.')
        return redirect('gestor:material_list')

    # Configurar a resolução da câmera para melhor desempenho
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    # Criar janela com tamanho ajustável
    cv2.namedWindow('Camera', cv2.WINDOW_NORMAL)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Criar cópia do frame para processamento
        frame_processado = frame.copy()

        # Tentar reconhecer o material com YOLO
        tipo_material = reconhecer_material_yolo(frame_processado, model, debug_info)

        # Mostrar frame original com informações
        if tipo_material:
            cv2.putText(frame, f"Material detectado: {tipo_material}",
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(frame, "Pressione 'c' para confirmar ou 'ESC' para cancelar",
                       (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            material_detectado = tipo_material
        else:
            cv2.putText(frame, "Posicione o material na frente da camera",
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            cv2.putText(frame, f"Motivo: {debug_info['motivo']}",
                       (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
            cv2.putText(frame, "Pressione 'm' para cadastro manual ou 'ESC' para sair",
                       (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

        # Mostrar frame na tela
        cv2.imshow("Camera", frame)

        # Verificar teclas pressionadas
        key = cv2.waitKey(1) & 0xFF

        # Se detectou material e pressionou 'c' para confirmar
        if material_detectado and key == ord('c'):
            break

        # Pressione 'm' para cadastro manual
        if key == ord('m'):
            # Liberar recursos
            cap.release()
            cv2.destroyAllWindows()

            # Renderizar template para cadastro manual
            context = {
                'opcoes': ['protoboard', 'projetor'],
                'usuario_logado2': request.user
            }
            return render(request, 'material_form.html', context)

        # Pressione ESC para sair sem detectar
        if key == 27:  # ESC
            material_detectado = None
            break

    # Liberar recursos
    cap.release()
    cv2.destroyAllWindows()

    # Se detectou material, cadastrar no banco
    if material_detectado:
        try:
            # Gerar nome único para o material
            nome_unico = gerar_nome_unico(material_detectado, Materiais)

            # Criar o material com o nome único
            Materiais.objects.create(nome_do_material=nome_unico)

            # Mensagem de sucesso
            messages.success(request, f'Material {nome_unico} cadastrado com sucesso!')
        except Exception as e:
            # Em caso de erro no cadastro
            messages.error(request, f'Erro ao cadastrar material: {str(e)}')

    return redirect('gestor:material_list')


# from django.shortcuts import render
# from django.views.generic import ListView
# from .models import Usuario
import firebase_admin
from firebase_admin import auth, credentials, firestore
from django.shortcuts import get_object_or_404, redirect
from django.http import Http404
from django.views.generic import ListView


# Verifica se o app do Firebase já foi inicializado
if not firebase_admin._apps:
    cred = firebase_admin.credentials.Certificate(r'C:\Users\Marcelo\Documents\GitHub\Sistema_mapeamento_laboratorio_e_materiais\sistemamapeamentolaboratorio-firebase-adminsdk-dmdt8-f79abd9e82.json')
    firebase_admin.initialize_app(cred)

# Obtendo a referência ao Firestore
db = firestore.client()

# Função para buscar usuários do Firebase
def get_firebase_users():
    users_ref = db.collection('usuarios')
    users = users_ref.stream()
    firebase_users = []
    for user in users:
        firebase_users.append({
            'id': user.id,  # Captura o ID do documento Firebase
            'nome': user.to_dict().get('nome'),
            'email': user.to_dict().get('email')
        })
    return firebase_users

# Função para excluir o usuário
def deletar_usuario(request, usuario_id):
    print(f"Tentando excluir o usuário com ID: {usuario_id}")  # Debugging
    try:
        # Excluir do banco local (Django) se o ID for numérico
        if usuario_id.isnumeric():  # Verifica se o ID é numérico
            usuario_local = get_object_or_404(Usuario, id=int(usuario_id))  # Converte para int
            usuario_local.delete()

        # Excluir do Firebase Authentication
        try:
            auth.delete_user(usuario_id)  # Exclui o usuário do Firebase Authentication
            print(f"Usuário {usuario_id} excluído do Firebase Authentication com sucesso.")
        except auth.UserNotFoundError:
            print(f"Usuário {usuario_id} não encontrado no Firebase Authentication.")

        # Excluir do Firestore
        db = firestore.client()
        user_ref = db.collection('usuarios').document(usuario_id)  # Referência ao Firestore
        user_ref.delete()
        print(f"Usuário {usuario_id} excluído do Firestore com sucesso.")

        # Redireciona de volta para a lista de usuários
        return redirect('/gestor/usuarios/')

    except Exception as e:
        print(f"Erro ao excluir usuário: {e}")
        raise Http404("Usuário não encontrado ou não pode ser excluído.")

class UsuarioListView(ListView):
    model = Usuario
    template_name = 'usuarios_cadastrados.html'
    context_object_name = 'usuarios'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Buscar usuários do banco de dados local (Django)
        usuarios_locais = Usuario.objects.all()

        # Buscar usuários do Firebase
        usuarios_firebase = get_firebase_users()

        # Ocultar o usuário com o email 'admin@ufrpe.br' da lista de usuários locais
        usuarios_locais = usuarios_locais.exclude(email='admin@ufrpe.br')

        # Ocultar o usuário com o email 'admin@ufrpe.br' da lista de usuários do Firebase
        usuarios_firebase = [user for user in usuarios_firebase if user.get('email') != 'admin@ufrpe.br']

        # Concatenando as duas listas (filtradas)
        context['usuarios'] = list(usuarios_locais) + usuarios_firebase

        # Passa o usuário logado para o contexto
        context['usuario_logado2'] = self.request.user
        return context





# mostrar todos usuario até admin
# class UsuarioListView(ListView):
#     model = Usuario
#     template_name = 'usuarios_cadastrados.html'
#     context_object_name = 'usuarios'

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)

#         # Buscar usuários do banco de dados local (Django)
#         usuarios_locais = Usuario.objects.all()

#         # Buscar usuários do Firebase
#         usuarios_firebase = get_firebase_users()

#         # Concatenando as duas listas
#         context['usuarios'] = list(usuarios_locais) + usuarios_firebase

#         # Passa o usuário logado para o contexto
#         context['usuario_logado2'] = self.request.user
#         return context



# from django.views.generic import ListView
# from .models import Usuario funciona

# class UsuarioListView(ListView):
#     model = Usuario
#     template_name = 'usuarios_cadastrados.html'  # O template que você usa
#     context_object_name = 'usuarios'  # Corrigido para 'usuarios'

#     # Passa o usuário logado para o contexto
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['usuario_logado2'] = self.request.user
#         return context




# class UsuarioListView(ListView):
#     model = Usuario  # Ou seu modelo de usuário customizado, como Usuario
#     template_name = 'gestor/usuarios_cadastrados.html'  # O template que você está usando
#     context_object_name = 'usuarios'  # Nome que você usará no template para acessar os dados
#     # Se você quiser passar o usuário logado para o template
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['usuario_logado'] = self.request.user  # Passa o usuário logado para o template
#         return context

# def usuarios_cadastrados(request):
#     usuarios = Usuario.objects.all()  # Pega todos os usuários cadastrados
#     return render(request, 'gestor/usuarios_cadastrados.html', {'usuarios': usuarios})

# gerando gráfico de ranking materias/salas com chart.js e matplot
import matplotlib.pyplot as plt
from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic import ListView
from django.db.models import Count
from io import BytesIO
import base64
from .models import Salas, Materiais, Reservas, Reserva
from datetime import datetime

class RankingSalasView(ListView):
    model = Salas
    template_name = 'ranking_salas.html'
    context_object_name = 'salas'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Verificando se o usuário está logado
        if self.request.session.get('usuario'):
            try:
                usuario = Usuario.objects.get(id=self.request.session['usuario'])
                context['usuario_logado2'] = usuario
            except Usuario.DoesNotExist:
                context['usuario_logado2'] = None
        else:
            context['usuario_logado2'] = None

        ano = self.request.GET.get('ano')
        mes = self.request.GET.get('mes')

        if ano and mes:
            reservas_filtradas = Reservas.objects.filter(data_reserva__year=int(ano), data_reserva__month=int(mes))
        elif ano:
            reservas_filtradas = Reservas.objects.filter(data_reserva__year=int(ano))
        elif mes:
            reservas_filtradas = Reservas.objects.filter(data_reserva__month=int(mes))
        else:
            reservas_filtradas = Reservas.objects.all()

        salas = Salas.objects.filter(reservas__in=reservas_filtradas).annotate(num_reservas=Count('reservas')).order_by('-num_reservas')

        context['anos'] = [ano.year for ano in Reservas.objects.dates('data_reserva', 'year')]
        meses = [
            (1, "Janeiro"), (2, "Fevereiro"), (3, "Março"), (4, "Abril"),
            (5, "Maio"), (6, "Junho"), (7, "Julho"), (8, "Agosto"),
            (9, "Setembro"), (10, "Outubro"), (11, "Novembro"), (12, "Dezembro")
        ]
        context['meses'] = meses
        context['salas'] = salas

        sala_names = [sala.nome_da_sala for sala in salas]
        reservation_counts = [sala.num_reservas for sala in salas]

        plt.figure(figsize=(10, 5))
        plt.bar(sala_names, reservation_counts)
        plt.xlabel('Salas')
        plt.ylabel('Número de Reservas')
        plt.title('Ranking de Salas Mais Reservadas')

        buf = BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        image_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
        context['grafico_salas'] = image_base64

        return context

class RankingMateriaisView(ListView):
    model = Materiais
    template_name = 'ranking_materiais.html'
    context_object_name = 'materiais'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Verificando se o usuário está logado
        usuario_id = self.request.session.get('usuario')
        if usuario_id:
            context['usuario_logado2'] = Usuario.objects.filter(id=usuario_id).first()
        else:
            context['usuario_logado2'] = None

        ano = self.request.GET.get('ano')
        mes = self.request.GET.get('mes')

        if ano and mes:
            reservas_filtradas = Reserva.objects.filter(data_reserva__year=int(ano), data_reserva__month=int(mes))
        elif ano:
            reservas_filtradas = Reserva.objects.filter(data_reserva__year=int(ano))
        elif mes:
            reservas_filtradas = Reserva.objects.filter(data_reserva__month=int(mes))
        else:
            reservas_filtradas = Reserva.objects.all()

        materiais = Materiais.objects.filter(reserva__in=reservas_filtradas).annotate(num_reservas=Count('reserva')).order_by('-num_reservas')

        context['anos'] = [ano.year for ano in Reserva.objects.dates('data_reserva', 'year')]
        meses = [
            (1, "Janeiro"), (2, "Fevereiro"), (3, "Março"), (4, "Abril"),
            (5, "Maio"), (6, "Junho"), (7, "Julho"), (8, "Agosto"),
            (9, "Setembro"), (10, "Outubro"), (11, "Novembro"), (12, "Dezembro")
        ]
        context['meses'] = meses
        context['materiais'] = materiais

        # Dados para o gráfico de Chart.js
        material_names = [material.nome_do_material for material in materiais]
        reservation_counts = [material.num_reservas for material in materiais]

        context['grafico_materiais'] = {
            'labels': material_names,
            'data': reservation_counts
        }

        return context