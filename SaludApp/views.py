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
from django.db.models import Q

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
    ordering = ['-fecha_registro']

    def get_queryset(self):
        queryset = super().get_queryset()  # Usa el ordering

        # Búsqueda por texto
        q = self.request.GET.get('q')
        if q:
            queryset = queryset.filter(
                Q(nombre__icontains=q) |
                Q(apellido__icontains=q) |
                Q(cedula__icontains=q)
            )
        return queryset

    # Permiso a la Vista para Recepcionistas y Administradores
    def test_func(self):
        return self.request.user.is_recepcion or self.request.user.is_admin

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            return redirect('acceso_denegado')
        else:
            return super().handle_no_permission()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Agrega cédula con formato
        empleados = list(context['empleados'])  # Convierte a lista para poder modificar
        for emp in empleados:
            cedula = emp.cedula
            if len(cedula) == 7:
                emp.cedula_formateada = f"V-{cedula[0]}.{cedula[1:4]}.{cedula[4:]}"
            elif len(cedula) == 8:
                emp.cedula_formateada = f"V-{cedula[:2]}.{cedula[2:5]}.{cedula[5:]}"
            elif len(cedula) == 9:
                emp.cedula_formateada = f"V-{cedula[:3]}.{cedula[3:6]}.{cedula[6:]}"
            else:
                emp.cedula_formateada = f"V-{cedula}"

        context['empleados'] = empleados
        return context
    
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
        # Agrupa todos los errores en una lista
        error_list = []
        for field, errors in form.errors.items():
            for error in errors:
                # Elimina el nombre del campo del mensaje
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

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()  # Aplica el ordenamiento definido (si lo tienes)

        # Filtra según rol
        if user.is_medico:
            queryset = Visita.objects.filter(estado='completada').order_by('-fecha')
        elif user.is_recepcion or user.is_admin:
            queryset = Visita.objects.all().order_by('-fecha')
        else:
            queryset = Visita.objects.none()

        # Búsqueda por texto
        q = self.request.GET.get('q')
        if q:
            queryset = queryset.filter(
                Q(empleado__nombre__icontains=q) |
                Q(empleado__apellido__icontains=q) |
                Q(motivo__icontains=q) |
                Q(estado__icontains=q)
            )
        return queryset

    # Permiso a la Vista para Médicos, Recepcionistas y Administradores
    def test_func(self):
        user = self.request.user
        return user.is_recepcion or user.is_medico or user.is_admin

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            return redirect('acceso_denegado')
        else:
            return super().handle_no_permission()

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

    def form_valid(self, form):
        # Mostrar mensaje de éxito
        messages.success(self.request, 'Visita creada exitosamente.')
        return super().form_valid(form)

    def form_invalid(self, form):
        # Agrupar todos los errores en una lista
        error_list = []
        for field, errors in form.errors.items():
            for error in errors:
                error_list.append(error) 

        # Crear un solo mensaje con todos los errores
        if error_list:
            error_message = "Por favor corrija el(los) siguiente(s) error(es):<br>" + "<br>".join(error_list)
            messages.error(self.request, error_message, extra_tags='safe')
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['empleados'] = Empleado.objects.all()
        return context

class EditarVisitaView(LoginRequiredMixin, UpdateView):
    model = Visita
    form_class = VisitaForm
    template_name = 'visitas/editar_visita.html'
    success_url = reverse_lazy('lista_visitas')

    def form_valid(self, form):
        messages.success(self.request, 'Visita actualizada correctamente.')
        return super().form_valid(form)

    def form_invalid(self, form):
        # Agrupa todos los errores
        error_list = []
        for field, errors in form.errors.items():
            for error in errors:
                error_list.append(error)

        # Muestra mensaje de error formateado
        if error_list:
            error_message = "Por favor corrija el(los) siguiente(s) error(es):<br>" + "<br>".join(error_list)
            messages.error(self.request, error_message, extra_tags='safe')

        return super().form_invalid(form)

class EliminarVisitaView(LoginRequiredMixin, DeleteView):
    model = Visita
    template_name = 'visitas/eliminar_visita.html'
    success_url = reverse_lazy('lista_visitas')
    
    def post(self, request, *args, **kwargs):
        messages.success(request, 'Visita eliminada correctamente.')
        return super().post(request, *args, **kwargs)

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

        # Asignar visita y médico automáticamente
        form.instance.visita = visita
        form.instance.medico = self.request.user  # <-- Aquí asignamos al médico

        messages.success(self.request, 'Diagnóstico guardado exitosamente.')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        # Agrupa todos los errores del formulario
        error_list = []
        for field, errors in form.errors.items():
            for error in errors:
                error_list.append(error)

        if error_list:
            error_message = "Por favor corrija el(los) siguiente(s) error(es):<br>" + "<br>".join(error_list)
            messages.error(self.request, error_message, extra_tags='safe')

        return redirect('lista_citasmedicas')

class EditarDiagnosticoView(LoginRequiredMixin, UpdateView):
    model = Diagnostico
    form_class = DiagnosticoForm
    template_name = 'citas_medicas/editar_diagnostico.html'
    success_url = reverse_lazy('lista_citasmedicas')

    def form_valid(self, form):
        if not self.request.user.is_medico:
            # Añadir mensaje de error con formato consistente
            error_message = "Por favor corrija el(los) siguiente(s) error(es):<br>" + "<br> Solo los médicos pueden crear diagnósticos."
            messages.error(self.request, error_message, extra_tags='safe')
            return redirect('lista_citasmedicas')

        form.instance.medico = self.request.user
        messages.success(self.request, 'Diagnóstico actualizado correctamente.')
        return super().form_valid(form)

    def form_invalid(self, form):
        error_list = []
        for field, errors in form.errors.items():
            for error in errors:
                error_list.append(error)

        if error_list:
            error_message = "Por favor corrija el(los) siguiente(s) error(es):<br>" + "<br>".join(error_list)
            messages.error(self.request, error_message, extra_tags='safe')

        return redirect('lista_citasmedicas')

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
            return redirect('acceso_denegado')  # Redirige si no es admin
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