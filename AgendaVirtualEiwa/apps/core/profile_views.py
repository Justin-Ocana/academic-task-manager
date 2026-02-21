# Vistas para configuración de perfil
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST


@login_required
def profile_settings(request):
    """Vista principal de configuración de perfil"""
    from apps.groups.models import GroupMember
    
    # Obtener grupos del usuario
    user_groups = GroupMember.objects.filter(user=request.user).select_related('group')
    
    context = {
        'user_groups': user_groups,
    }
    
    return render(request, 'settings/profile_settings.html', context)


@login_required
@require_POST
def update_profile(request):
    """Actualizar información del perfil"""
    try:
        user = request.user
        
        # Obtener datos del formulario
        nombre = request.POST.get('nombre', '').strip()
        apellido = request.POST.get('apellido', '').strip()
        email = request.POST.get('email', '').strip()
        
        # Validaciones
        if not nombre or not apellido or not email:
            messages.error(request, 'Todos los campos son obligatorios')
            return redirect('profile_settings')
        
        if len(nombre) < 2 or len(apellido) < 2:
            messages.error(request, 'El nombre y apellido deben tener al menos 2 caracteres')
            return redirect('profile_settings')
        
        # Verificar si el email ya existe (excepto el del usuario actual)
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        if User.objects.filter(email=email).exclude(id=user.id).exists():
            messages.error(request, 'Este email ya está en uso')
            return redirect('profile_settings')
        
        # Actualizar usuario
        user.nombre = nombre
        user.apellido = apellido
        user.email = email
        user.save()
        
        messages.success(request, 'Perfil actualizado exitosamente')
        return redirect('profile_settings')
        
    except Exception as e:
        messages.error(request, f'Error al actualizar perfil: {str(e)}')
        return redirect('profile_settings')


@login_required
@require_POST
def change_password(request):
    """Cambiar contraseña del usuario"""
    try:
        user = request.user
        
        # Obtener datos del formulario
        current_password = request.POST.get('current_password', '')
        new_password = request.POST.get('new_password', '')
        confirm_password = request.POST.get('confirm_password', '')
        
        # Validaciones
        if not current_password or not new_password or not confirm_password:
            messages.error(request, 'Todos los campos son obligatorios')
            return redirect('profile_settings')
        
        # Verificar contraseña actual
        if not user.check_password(current_password):
            messages.error(request, 'La contraseña actual es incorrecta')
            return redirect('profile_settings')
        
        # Verificar que las nuevas contraseñas coincidan
        if new_password != confirm_password:
            messages.error(request, 'Las nuevas contraseñas no coinciden')
            return redirect('profile_settings')
        
        # Verificar longitud mínima
        if len(new_password) < 8:
            messages.error(request, 'La contraseña debe tener al menos 8 caracteres')
            return redirect('profile_settings')
        
        # Cambiar contraseña
        user.set_password(new_password)
        user.save()
        
        # Mantener la sesión activa
        update_session_auth_hash(request, user)
        
        messages.success(request, 'Contraseña cambiada exitosamente')
        return redirect('profile_settings')
        
    except Exception as e:
        messages.error(request, f'Error al cambiar contraseña: {str(e)}')
        return redirect('profile_settings')


@login_required
@require_POST
def update_preferences(request):
    """Actualizar preferencias del usuario"""
    try:
        user = request.user
        form_type = request.POST.get('form_type', '')
        
        # Manejar grupos del dashboard
        if form_type == 'dashboard_groups':
            from apps.groups.models import Group, GroupMember
            dashboard_group_ids = request.POST.getlist('dashboard_groups')
            
            # Limpiar grupos actuales
            user.dashboard_groups.clear()
            
            # Agregar grupos seleccionados
            if dashboard_group_ids:
                for group_id in dashboard_group_ids:
                    try:
                        group = Group.objects.get(id=group_id)
                        # Verificar que el usuario sea miembro del grupo
                        if GroupMember.objects.filter(group=group, user=user).exists():
                            user.dashboard_groups.add(group)
                    except Group.DoesNotExist:
                        pass
                    except Exception as e:
                        print(f"Error adding group {group_id}: {str(e)}")
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': 'Grupos del dashboard actualizados exitosamente'
                })
            
            messages.success(request, 'Grupos del dashboard actualizados exitosamente')
            return redirect('profile_settings')
        
        # Obtener preferencias de resumen de actividades
        pending_range = request.POST.get('pending_range', 'week')
        completed_range = request.POST.get('completed_range', 'week')
        overdue_range = request.POST.get('overdue_range', '7days')
        
        # Obtener preferencia de modo multigrupo
        multigroup_mode = request.POST.get('multigroup_mode', 'separated')
        
        # Validar valores
        valid_ranges = ['today', 'week', 'month', 'all']
        valid_overdue_ranges = ['today', '7days', '30days', 'all']
        valid_multigroup_modes = ['separated', 'unified']
        
        if pending_range in valid_ranges:
            user.pending_range = pending_range
        if completed_range in valid_ranges:
            user.completed_range = completed_range
        if overdue_range in valid_overdue_ranges:
            user.overdue_range = overdue_range
        if multigroup_mode in valid_multigroup_modes:
            user.multigroup_mode = multigroup_mode
        
        user.save()
        
        # Si es petición AJAX, devolver JSON (sin agregar mensaje de Django)
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': 'Preferencias actualizadas exitosamente'
            })
        
        # Solo agregar mensaje si NO es AJAX
        messages.success(request, 'Preferencias actualizadas exitosamente')
        # Redirigir a la sección de preferencias
        from django.shortcuts import redirect
        from django.urls import reverse
        return redirect(reverse('profile_settings') + '#preferences')
        
    except Exception as e:
        # Si es petición AJAX, devolver error JSON
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
        
        messages.error(request, f'Error al actualizar preferencias: {str(e)}')
        from django.urls import reverse
        return redirect(reverse('profile_settings') + '#preferences')


@login_required
def delete_account(request):
    """Eliminar cuenta del usuario"""
    if request.method == 'POST':
        try:
            from django.contrib.auth import logout
            import json
            
            user = request.user
            user_id = user.id
            
            # Eliminar el usuario (Django maneja las eliminaciones en cascada automáticamente)
            user.delete()
            
            # Cerrar sesión
            logout(request)
            
            return JsonResponse({
                'success': True,
                'message': 'Cuenta eliminada exitosamente'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'Error al eliminar cuenta: {str(e)}'
            }, status=500)
    
    return JsonResponse({
        'success': False,
        'error': 'Método no permitido'
    }, status=405)


@login_required
def notifications_settings(request):
    """Vista de configuración de notificaciones"""
    return render(request, 'settings/notifications_settings.html')


@login_required
def avatar_settings(request):
    """Vista de selección de categorías de avatar"""
    return render(request, 'settings/avatar_categories.html')


@login_required
def avatar_settings_category(request, category):
    """Vista de configuración de avatar por categoría"""
    # Validar categoría
    valid_categories = ['eiwa', 'animals', 'disney']
    if category not in valid_categories:
        messages.error(request, 'Categoría no válida')
        return redirect('avatar_settings')
    
    if request.method == 'POST':
        try:
            user = request.user
            
            # Obtener datos del formulario
            avatar_style = request.POST.get('avatar_style')
            bg_color = request.POST.get('bg_color')
            svg_color = request.POST.get('svg_color', '#FFFFFF')  # Usar blanco por defecto
            avatar_category = request.POST.get('avatar_category', category)
            
            # Debug: imprimir lo que se recibe
            print(f"DEBUG - Datos recibidos:")
            print(f"  avatar_style: {avatar_style}")
            print(f"  bg_color: {bg_color}")
            print(f"  svg_color: {svg_color}")
            print(f"  avatar_category: {avatar_category}")
            print(f"  POST data: {request.POST}")
            
            # Validar que los datos mínimos existan
            if avatar_style and bg_color:
                # Guardar configuración
                user.avatar_style = avatar_style
                user.avatar_bg_color = bg_color
                user.avatar_svg_color = svg_color if svg_color and len(svg_color) <= 7 else '#FFFFFF'
                user.avatar_category = avatar_category
                user.save()
                
                print(f"DEBUG - Avatar guardado exitosamente para usuario {user.email}")
                messages.success(request, 'Avatar actualizado exitosamente')
            else:
                print(f"DEBUG - Validación fallida: avatar_style={avatar_style}, bg_color={bg_color}")
                messages.error(request, 'Por favor completa todos los campos')
                
        except Exception as e:
            print(f"DEBUG - Error al guardar: {str(e)}")
            import traceback
            traceback.print_exc()
            messages.error(request, f'Error al actualizar avatar: {str(e)}')
        
        return redirect('avatar_settings_category', category=category)
    
    # Determinar qué template usar según la categoría
    template_map = {
        'eiwa': 'settings/avatar_settings_eiwa.html',
        'animals': 'settings/avatar_settings_animals.html',
        'disney': 'settings/avatar_settings_disney.html',
    }
    
    context = {
        'category': category,
        'category_name': {
            'eiwa': 'Agenda Virtual Eiwa',
            'animals': 'Animales',
            'disney': 'Disney'
        }[category]
    }
    
    return render(request, template_map[category], context)
