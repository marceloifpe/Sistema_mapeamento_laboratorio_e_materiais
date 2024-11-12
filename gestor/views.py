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