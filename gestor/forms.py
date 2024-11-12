from django import forms
from .models import Salas
from .models import Materiais

class SalaForm(forms.ModelForm):
    class Meta:
        model = Salas
        fields = ['nome_da_sala', 'local']  
        
class MaterialForm(forms.ModelForm):
    class Meta:
        model = Materiais
        fields = ['nome_do_material'] 