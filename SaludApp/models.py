from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
#============================================================================



#============================================================================
class CustomUserManager(BaseUserManager):
    """ Manager personalizado para el CustomUser """

    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError('El usuario debe tener un username')
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('rol', 'admin')
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser debe tener is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser debe tener is_superuser=True.')
        
        return self.create_user(username, password, **extra_fields)

#============================================================================



#============================================================================
class CustomUser(AbstractUser):
    """ Modelo de Usuario Personalizado que Extiende AbstractUser """

    ROLES = (
        ('admin', 'Administrador'),
        ('recepcion', 'Empleado de Recepción'),
        ('medico', 'Personal Médico'),
    )

    rol = models.CharField(
        max_length=10,
        choices=ROLES,
        default='recepcion',
        verbose_name='Rol del usuario'
    )

    fecha_registro = models.DateTimeField(
        default=timezone.now,
        verbose_name='Fecha de registro'
    )

    objects = CustomUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['rol']

    def __str__(self):
        return f"{self.username} ({self.get_rol_display()})"
    
    # Propiedades para verificar roles fácilmente
    @property
    def is_admin(self):
        return self.rol == 'admin'
    
    @property
    def is_recepcion(self):
        return self.rol == 'recepcion'
    
    @property
    def is_medico(self):
        return self.rol == 'medico'
    
    class Meta:
        verbose_name = 'Usuario Personalizado'
        verbose_name_plural = 'Usuarios Personalizados'
        ordering = ['-fecha_registro']

#============================================================================



#============================================================================
class Empleado(models.Model):
    cedula = models.CharField(max_length=20, unique=True, verbose_name='Cédula de Identidad')
    p00 = models.CharField(max_length=20, unique=True, verbose_name='Número P00')
    nombre = models.CharField(max_length=100, verbose_name='Nombres')
    apellido = models.CharField(max_length=100, verbose_name='Apellidos')
    fecha_registro = models.DateTimeField(default=timezone.now, verbose_name='Fecha de registro')

    def __str__(self):
        return f"{self.nombre} {self.apellido} ({self.cedula})"
    
    class Meta:
        verbose_name = 'Empleado'
        verbose_name_plural = 'Empleados'
        ordering = ['apellido', 'nombre']
#============================================================================



#============================================================================
class Visita(models.Model):
    """ Modelo Para Registrar las Visitas al Servicio Médico """

    MOTIVO_CHOICES = [
        ('consulta', 'Consulta'),
        ('emergencia', 'Emergencia'),
        ('control', 'Control'),
    ]
    
    empleado = models.ForeignKey(Empleado, on_delete=models.CASCADE, related_name='visitas', verbose_name='Empleado visitante')
    motivo = models.CharField(max_length=50, choices=MOTIVO_CHOICES, default='consulta', verbose_name='Motivo de la visita')
    estado = models.CharField(max_length=20, choices=[('pendiente', 'Pendiente'), ('completada', 'Completada')], default='pendiente')
    fecha = models.DateTimeField(default=timezone.now, verbose_name='Fecha y hora de la visita')

#============================================================================



#============================================================================
class Diagnostico(models.Model):
    """Modelo para los diagnósticos médicos"""

    MOTIVO_CHOICES = [
        ('consulta', 'Consulta'),
        ('emergencia', 'Emergencia'),
        ('seguimiento', 'Seguimiento')
    ]
    visita = models.OneToOneField(Visita, on_delete=models.CASCADE, related_name='diagnostico', verbose_name='Visita')
    motivo = models.CharField(max_length=50, choices=MOTIVO_CHOICES, null=True, blank=True, verbose_name='Motivo de la consulta')
    diagnostico = models.TextField(verbose_name='Diagnóstico médico', blank=True, null=True)
    tratamiento = models.TextField(verbose_name='Tratamiento indicado', blank=True, null=True)
    observacion = models.TextField(verbose_name='Observaciónes adicionales', blank=True, null=True)
    fecha_diagnostico = models.DateTimeField(auto_now_add=True, verbose_name='Fecha del diagnóstico')
    medico = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='diagnosticos_realizados',
        verbose_name='Médico que realizó el diagnóstico'
    )

    def __str__(self):
        return f"Cita médica para {self.visita} ({self.fecha_diagnostico.date()})"
    
    def clean(self):
        super().clean()

        # Validación 1: Por lo menos un campo presente
        if not any([self.diagnostico, self.tratamiento, self.observacion]):
            raise ValidationError("Debe completar al menos una de las dos partes del formulario: Diagnóstico con tratamiento u observación.")

        # Validación 2: Si hay diagnóstico, debe haber tratamiento
        if self.diagnostico and not self.tratamiento:
            raise ValidationError("Si registra un diagnóstico, debe incluir el tratamiento correspondiente.")
    
    class Meta:
        verbose_name = 'Cita Médica'
        verbose_name_plural = 'Citas Médicas'
        ordering = ['-fecha_diagnostico']
#============================================================================