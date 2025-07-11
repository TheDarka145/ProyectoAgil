from django import forms 
from django.forms import ModelForm
from django.forms import widgets
from django.forms.widgets import Widget
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm,UserChangeForm
from django.core.validators import RegexValidator
from .models import Categoria, Planta

class PlantaForm(forms.ModelForm):
    class Meta: 
        model=Planta
        fields=['idPlanta', 'nombre', 'imagen', 'descripcion', 'categoria', 'precio', 'stock']
        labels={
            'idPlanta': 'ID del producto',
            'nombre': 'Nombre',
            'imagen': 'Imagen',
            'descripcion': 'Descripcion',
            'categoria': 'Categoria',
            'precio': 'Precio',
            'stock': 'Stock',
        }
        widgets={
            'idPlanta': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder':'Ingrese el ID del producto',
                    'id':'idPlanta'
                }
            ),
            'nombre': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder':'Ingrese nombre del producto',
                    'id':'nombre'
                }
            ),
            'imagen': forms.FileInput(
                attrs={
                    'class': 'form-control',
                    'id':'imagen'
                }
            ),
            'descripcion': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder':'Ingrese la descripcion del producto',
                    'id':'descripcion'
                }
            ),
            'categoria': forms.Select(
                attrs={
                    'class': 'form-control',
                    'id':'categoria'
                }
            ),
            'precio': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'placeholder':'Ingrese el precio del producto',
                    'id':'precio'
                }
            ),
            'stock': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'placeholder':'Ingrese el stock del producto',
                    'id':'stock'
                }
            )
        }

class RegistroUserForm(UserCreationForm):

    
    username = forms.CharField(min_length=5, max_length=15)
    first_name = forms.CharField(validators=[RegexValidator(regex=r'^[a-zA-Z]+$', message='Este campo debe contener solo letras.')])
    last_name = forms.CharField(validators=[RegexValidator(regex=r'^[a-zA-Z]+$', message='Este campo debe contener solo letras.')])
    password1 = forms.CharField(min_length=5, widget=forms.PasswordInput)
    password2 = forms.CharField(min_length=5, widget=forms.PasswordInput)

    
    class Meta:
        model = User
        fields = [ 'username', 'first_name', 'last_name', 'email', 'password1', 'password2']


class EditProfileForm(UserChangeForm):
    password = None  
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')