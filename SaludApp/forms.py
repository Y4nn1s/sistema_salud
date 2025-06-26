from django import forms
from .models import Empleado, Visita, Diagnostico, CustomUser
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
import re
#============================================================================

# User = get_user_model()

#============================================================================
# FORMULARIO PARA INICIO DE SESIÓN (AUTENTICACIÓN)
class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control'})
        self.fields['password'].widget.attrs.update({'class': 'form-control'})

#============================================================================
# FORMULARIO PARA REGISTRO DE USUARIO (AUTENTICACIÓN)
class RegisterForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Nombre de usuario'
        self.fields['password1'].label = 'Contraseña'
        self.fields['password2'].label = 'Confirmar contraseña'
#============================================================================
# FORMULARIO PARA EL REGISTRO DE EMPLEADOS
class EmpleadoForm(forms.ModelForm):
    class Meta:
        model = Empleado
        fields = ['cedula', 'p00', 'nombre', 'apellido']
        widgets = {
            'cedula': forms.TextInput(attrs={
                'pattern': r'\d{7,9}',
                'title': 'Debe ingresar entre 7 y 9 dígitos numéricos'
            }),
            'p00': forms.TextInput(attrs={
                'pattern': '\d{8}',
                'title': 'Debe ingresar exactamente 8 dígitos numéricos'
            }),
            'nombre': forms.TextInput(attrs={
                'pattern': '[A-Za-zÁÉÍÓÚáéíóúñÑ\s]+',
                'title': 'Solo letras y espacios'
            }),
            'apellido': forms.TextInput(attrs={
                'pattern': '[A-Za-zÁÉÍÓÚáéíóúñÑ\s]+',
                'title': 'Solo letras y espacios'
            }),
        }

    def clean_cedula(self):
        cedula = self.cleaned_data['cedula']

        # Validar formato (7 a 9 dígitos)
        if not re.fullmatch(r'^\d{7,9}$', cedula):
            raise forms.ValidationError("La cédula debe tener entre 7 y 9 dígitos.")

        # Validar unicidad (excluyendo el registro actual)
        if Empleado.objects.filter(cedula=cedula).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("Esta cédula ya está registrada.")
        return cedula

    def clean_p00(self):
        p00 = self.cleaned_data['p00']

        # Validar formato (8 dígitos)
        if not re.fullmatch(r'\d{8}', p00):
            raise forms.ValidationError("El P00 debe tener exactamente 8 dígitos numéricos.")

        # Validar unicidad (excluyendo el registro actual)
        if Empleado.objects.filter(p00=p00).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("Este P00 ya está registrado.")
        return p00
#============================================================================



#============================================================================
# FORMULARIO PARA EL REGISTRO DE VISITAS
class VisitaForm(forms.ModelForm):
    class Meta:
        model = Visita
        fields = ['empleado', 'motivo', 'estado']
        widgets = {
            'empleado': forms.Select(attrs={'class': 'form-control select2'}),
            'motivo': forms.Select(attrs={'class': 'form-control'}),
            'estado': forms.Select(attrs={'class': 'form-control'})
        }
#============================================================================



#============================================================================
# FORMULARIO PARA EL REGISTRO DE DIAGNÓSTICOS
class DiagnosticoForm(forms.ModelForm):
    class Meta:
        model = Diagnostico
        fields = ['diagnostico', 'tratamiento']
        widgets = {
            'diagnostico': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descripción detallada del diagnóstico'
            }),

            'tratamiento': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descripción detallada del tratamiento a emplear'
            })
        }

    def clean_diagnostico(self):
        diagnostico = self.cleaned_data.get('diagnostico')
        if diagnostico and len(diagnostico.strip()) < 10:
            raise ValidationError("El escrito debe contener al menos 10 caracteres.")
        return diagnostico
#============================================================================