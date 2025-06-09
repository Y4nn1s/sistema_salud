from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Empleado, Visita, Diagnostico, CustomUser
#============================================================================



#============================================================================
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'rol', 'is_staff')
    list_filter = ('rol', 'is_staff')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Información Personal', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permisos', {'fields': ('rol', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Fechas importantes', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'rol'),
        }),
    )

#============================================================================

admin.site.register(CustomUser, CustomUserAdmin)

#============================================================================
# Registro de los demás modelos con admin por defecto
admin.site.register(Empleado),
admin.site.register(Diagnostico),
admin.site.register(Visita),
