
from django.urls import path
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LoginView as AuthLoginView
from django.contrib.auth.views import LogoutView as AuthLogoutView
from .views import (
    ListaEmpleadosView, CrearEmpleadoView, EditarEmpleadoView, EliminarEmpleadoView, 
    ListaVisitasView, CrearVisitaView, EditarVisitaView, EliminarVisitaView, 
    ListaCitasMedicasView, CrearDiagnosticoView, EditarDiagnosticoView, EliminarDiagnosticoView,
    RegisterView, CustomLogoutView, CustomLoginView, ListaUsuariosView,
    RedireccionPorRolView, AccesoDenegadoView, MarcarCompletadaView
)



# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
urlpatterns = [

    # Autenticación
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('access-denied/', AccesoDenegadoView.as_view(), name='acceso_denegado'),


    # Empleados
    path('empleados/', ListaEmpleadosView.as_view(), name='lista_empleados'),
    path('empleados/registrar/', CrearEmpleadoView.as_view(), name='registrar_empleado'),
    path('empleados/editar/<int:pk>/', EditarEmpleadoView.as_view(), name='editar_empleado'),
    path('empleados/eliminar/<int:pk>/', EliminarEmpleadoView.as_view(), name='eliminar_empleado'),


    # Visitas
    path('visitas/', ListaVisitasView.as_view(), name='lista_visitas'),
    path('visitas/registrar/', CrearVisitaView.as_view(), name='registrar_visita'),
    path('visitas/editar/<int:pk>/', EditarVisitaView.as_view(), name='editar_visita'),
    path('visitas/eliminar/<int:pk>/', EliminarVisitaView.as_view(), name='eliminar_visita'),
    path('visita/<int:pk>/completar/', MarcarCompletadaView.as_view(), name='marcar_completada'),



    # Diagnósticos
    path('diagnosticos/', ListaCitasMedicasView.as_view(), name='lista_citasmedicas'),
    path('diagnosticos/crear/<int:visita_id>/', CrearDiagnosticoView.as_view(), name='registrar_diagnostico'),
    path('diagnosticos/editar/<int:pk>/', EditarDiagnosticoView.as_view(), name='editar_diagnostico'),
    path('diagnosticos/eliminar/<int:pk>/', EliminarDiagnosticoView.as_view(), name='eliminar_diagnostico'),

    # Gestión de Usuarios (Admin)
    path('usuarios/', ListaUsuariosView.as_view(), name='lista_usuarios'),

    # Redirección por Rol
    path('redireccion/', RedireccionPorRolView.as_view(), name='redireccion_por_rol' )

]
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -





