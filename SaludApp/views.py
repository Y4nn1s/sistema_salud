from django.views.generic import View, ListView, CreateView, UpdateView, DeleteView, RedirectView, TemplateView
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from .forms import EmpleadoForm, VisitaForm, DiagnosticoForm, LoginForm, RegisterForm
from .models import Empleado, Visita, Diagnostico, CustomUser
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect
from django.contrib import messages

#============================================================================



#============================================================================
#========================= VISTAS DE AUTENTICACIÓN ==========================
class CustomLoginView(LoginView):
    form_class = LoginForm
    template_name = 'registration/login.html'
    
    def get_success_url(self):
        user = self.request.user
        if user.is_medico:
            return reverse('lista_citasmedicas')
        elif user.is_admin:
            return reverse('lista_usuarios')
        elif user.is_recepcion:
            return reverse('lista_visitas')
        return super().get_success_url()

class CustomLogoutView(LogoutView):
    template_name = 'registration/logout.html'

class RegisterView(CreateView):

    form_class = RegisterForm
    template_name = 'registration/register.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        # Por defecto todos los nuevos usuarios son Recepción
        user = form.save(commit=False)
        user.rol = 'recepcion' #Rol por defecto
        user.save()
        return super().form_valid(form)

class AccesoDenegadoView(TemplateView):
    template_name = 'access_denied.html'

#============================================================================
#============================== EMPLEADOS =================================== 

class ListaEmpleadosView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Empleado
    template_name = 'empleados/lista_empleados.html'
    context_object_name = 'empleados'
    paginate_by = 10

    # Permiso a la Vista para Recepcionistas y Administradores
    def test_func(self):
        return self.request.user.is_recepcion or self.request.user.is_admin

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            return redirect('acceso_denegado')
        else:
            return super().handle_no_permission()
    
class CrearEmpleadoView(LoginRequiredMixin, CreateView):
    model = Empleado
    form_class = EmpleadoForm
    template_name = 'empleados/registrar_empleados.html'
    success_url = reverse_lazy('lista_empleados')

    def form_valid(self, form):
        # Mostrar mensaje de éxito
        messages.success(self.request, 'Empleado creado exitosamente.')
        return super().form_valid(form)

    def form_invalid(self, form):
        # Agrupar todos los errores en una lista
        error_list = []
        for field, errors in form.errors.items():
            for error in errors:
                # Eliminamos el nombre del campo del mensaje
                error_list.append(error)
        
        # Crear un solo mensaje con todos los errores
        error_message = "Por favor corrija el(los) siguiente(s) error(es):<br>" + "<br>".join(error_list)
        messages.error(self.request, error_message, extra_tags='safe')
        
        return redirect('lista_empleados')

class EditarEmpleadoView(LoginRequiredMixin, UpdateView):
    model = Empleado
    form_class = EmpleadoForm
    template_name='empleados/lista_empleados.html'
    success_url = reverse_lazy('lista_empleados')

    def form_valid(self, form):
        # Mostrar mensaje de éxito
        messages.success(self.request, 'Empleado actualizado exitosamente.')
        return super().form_valid(form)

    def form_invalid(self, form):
        # Agrupar todos los errores en una lista
        error_list = []
        for field, errors in form.errors.items():
            for error in errors:
                # Eliminamos el nombre del campo del mensaje
                error_list.append(error)
        
        # Crear un solo mensaje con todos los errores
        error_message = "Por favor corrija el(los) siguiente(s) error(es):<br>" + "<br>".join(error_list)
        messages.error(self.request, error_message, extra_tags='safe')
        
        return redirect('lista_empleados')

class EliminarEmpleadoView(LoginRequiredMixin, DeleteView):
    model = Empleado
    success_url = reverse_lazy('lista_empleados')

    # Deshabilitar el template de confirmación
    """ def get(self, request, *args, **kwargs):
        return HttpResponseRedirect(self.success_url) """

    def post(self, request, *args, **kwargs):
        messages.success(request, 'Empleado eliminado correctamente.')
        return super().post(request, *args, **kwargs)

#============================================================================
#=============================== VISITAS ====================================

class ListaVisitasView(LoginRequiredMixin, ListView):
    model = Visita
    template_name = 'visitas/lista_visitas.html'
    context_object_name = 'visitas'
    paginate_by = 10

    # Permiso a la Vista para Médicos, Recepcionistas y Administradores
    def test_func(self):
        user = self.request.user
        return user.is_recepcion or user.is_medico or user.is_admin

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            return redirect('acceso_denegado')
        else:
            return super().handle_no_permission()

    def get_queryset(self):
        user = self.request.user
        if user.is_medico or user.is_recepcion or user.is_admin:
            return Visita.objects.all().order_by('-fecha')
        return Visita.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = VisitaForm()
        context['empleados'] = Empleado.objects.all()
        return context

class CrearVisitaView(LoginRequiredMixin, CreateView):
    model = Visita
    form_class = VisitaForm
    template_name = 'visitas/registrar_visitas.html'
    success_url = reverse_lazy('lista_visitas')

class EditarVisitaView(LoginRequiredMixin, UpdateView):
    model = Visita
    form_class = VisitaForm
    template_name = 'visitas/editar_visita.html'
    success_url = reverse_lazy('lista_visitas')

class EliminarVisitaView(LoginRequiredMixin, DeleteView):
    model = Visita
    template_name = 'visitas/eliminar_visita.html'
    success_url = reverse_lazy('lista_visitas')
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Visita eliminada correctamente')
        return super().delete(request, *args, **kwargs)

#============================================================================
#============================= CITAS MÉDICAS =================================

class ListaCitasMedicasView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Visita
    template_name = 'citas_medicas/lista_citasmedicas.html'
    context_object_name = 'visitas_pendientes'
    paginate_by = 10

    # Permiso a la Vista para Médicos y Administradores
    def test_func(self):
        user = self.request.user
        return user.is_medico or user.is_admin
    
    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            return redirect('acceso_denegado')
        else:
            return super().handle_no_permission()

    # Filtra visitas sin diagnóstico asociado
    def get_queryset(self):
        user = self.request.user
        if user.is_medico or user.is_admin:
            # Médicos y Admins pueden ver solo Citas pendientes
            return Visita.objects.filter(estado='pendiente').order_by('-fecha')
        return Visita.objects.none()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['visitas_pendientes'] = Visita.objects.filter(estado='pendiente')
        context['form_diagnostico'] = DiagnosticoForm()
        return context

class CrearDiagnosticoView(LoginRequiredMixin, CreateView):
    model = Diagnostico
    form_class = DiagnosticoForm
    template_name = 'citas_medicas/registrar_diagnosticos.html'

    def get_success_url(self):
        return reverse('lista_citasmedicas') #Regresa a la vista Citas Médicas

    def test_func(self):
        return self.request.user.is_medico
    
    def form_valid(self, form):
        visita_id = self.kwargs['visita_id']
        visita = get_object_or_404(Visita, id=visita_id)
        # Asignación de la visita al diagnóstico
        form.instance.visita = visita
        form.instance.medico = self.request.user
        form.save()
        messages.success(self.request, 'Diagnóstico guardado exitosamente.')
        return super().form_valid(form)

class EditarDiagnosticoView(LoginRequiredMixin, UpdateView):
    model = Diagnostico
    form_class = DiagnosticoForm
    template_name = 'citas_medicas/editar_diagnostico.html'
    success_url = reverse_lazy('lista_citasmedicas')

class EliminarDiagnosticoView(LoginRequiredMixin, DeleteView):
    model = Diagnostico
    template_name = 'citas_medicas/eliminar_diagnostico.html'
    success_url = reverse_lazy('lista_citasmedicas')

#============================================================================
#=================== GESTIÓN DE USUARIOS (SOLO ADMIN) =======================

class ListaUsuariosView(LoginRequiredMixin, ListView):
    model = CustomUser
    template_name = 'usuarios/lista_usuarios.html'
    context_object_name = 'usuarios'
    paginate_by = 10
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_admin:
            return redirect('lista_visitas')  # Redirige si no es admin
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return CustomUser.objects.order_by('-date_joined')

#==================================================================================
#============================ REDIRECCION POR ROLES ===============================

class RedireccionPorRolView(LoginRequiredMixin, RedirectView):
    pattern_name = 'redireccion_por_rol' #La vista por defecto a redirigir despues del login

    def get_redirect_url(self, *args, **kwargs):
        if self.request.user.is_medico:
            return reverse('lista_citasmedicas')
        elif self.request.user.is_admin:
            return reverse('lista_usuarios')
        elif self.request.user.is_recepcion:
            return reverse('lista_visitas')
        return super().get_redirect_url(*args, **kwargs)

#==================================================================================
#=================== BOTÓN PARA MARCAR COMO COMPLETADA UNA CITA ===================

class MarcarCompletadaView(View):
    def get(self, request, *args, **kwargs):
        visita = get_object_or_404(Visita, id=kwargs['pk'])

        # Verificar permisos: Solo Médicos o Admins pueden marcar como completada
        if not  (request.user.is_medico or request.user.is_admin):
            messages.warning(request, "No tienes permiso para realizar esta acción.")
            return redirect('lista_citasmedicas')
        
        # Actualizar estado
        visita.estado = 'completada'
        visita.save()

        messages.success(request, f"La visita de {visita.empleado} ha sido marcada como completada.")

        return redirect('lista_citasmedicas')
    
#==================================================================================