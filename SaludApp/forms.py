from django import forms
from .models import Empleado, Visita, Diagnostico, CustomUser
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
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
            'cedula': forms.TextInput(attrs={'class': 'form-control'}),
            'p00': forms.TextInput(attrs={'class': 'form-control'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'apellido': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean_cedula(self):
        cedula = self.cleaned_data['cedula']
        if Empleado.objects.filter(cedula=cedula).exclude(id=self.instance.id).exists():
            raise ValidationError("Esta cédula ya está registrada.")
        return cedula
    
    def clean_p00(self):
        p00 = self.cleaned_data['p00']
        if Empleado.objects.filter(p00=p00).exclude(id=self.instance.id).exists():
            raise ValidationError("Este P00 ya está registrado.")
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