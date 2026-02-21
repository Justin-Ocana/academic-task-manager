from .models import Notification


def create_notification(recipient, notification_type, title, message, sender=None, action_url='', content_object=None):
    """
    Función helper para crear notificaciones
    
    Args:
        recipient: Usuario que recibe la notificación
        notification_type: Tipo de notificación
        title: Título de la notificación
        message: Mensaje de la notificación
        sender: Usuario que genera la notificación (opcional)
        action_url: URL de acción (opcional)
        content_object: Objeto relacionado (opcional)
    """
    notification = Notification.objects.create(
        recipient=recipient,
        sender=sender,
        notification_type=notification_type,
        title=title,
        message=message,
        action_url=action_url,
        content_object=content_object
    )
    return notification


def notify_group_leaders(group, notification_type, title, message, sender=None, action_url=''):
    """Notificar a todos los líderes de un grupo"""
    from apps.groups.models import GroupMember
    
    leaders = GroupMember.objects.filter(
        group=group,
        role='leader'
    ).select_related('user')
    
    notifications = []
    for leader in leaders:
        notification = create_notification(
            recipient=leader.user,
            notification_type=notification_type,
            title=title,
            message=message,
            sender=sender,
            action_url=action_url,
            content_object=group
        )
        notifications.append(notification)
    
    return notifications
