// Sistema de notificaciones en tiempo real
// Verifica nuevas notificaciones cada minuto y las muestra como push

class RealtimeNotifications {
    constructor() {
        this.lastCheck = Date.now();
        this.checkInterval = 60 * 1000; // 1 minuto
        this.notifiedIds = new Set();
        this.init();
    }

    init() {
        // Cargar IDs ya notificados del localStorage
        this.loadNotifiedIds();

        // Verificar inmediatamente
        setTimeout(() => this.checkNewNotifications(), 3000);

        // Verificar cada minuto
        setInterval(() => this.checkNewNotifications(), this.checkInterval);
    }

    loadNotifiedIds() {
        try {
            const stored = localStorage.getItem('notifiedNotificationIds');
            if (stored) {
                const ids = JSON.parse(stored);
                this.notifiedIds = new Set(ids);
            }
        } catch (error) {
            console.error('Error cargando IDs notificados:', error);
        }
    }

    saveNotifiedIds() {
        try {
            const ids = Array.from(this.notifiedIds);
            localStorage.setItem('notifiedNotificationIds', JSON.stringify(ids));
        } catch (error) {
            console.error('Error guardando IDs notificados:', error);
        }
    }

    async checkNewNotifications() {
        try {
            const response = await fetch('/notifications/api/get/');
            const data = await response.json();

            if (data.notifications && data.notifications.length > 0) {
                // Filtrar solo notificaciones nuevas (no leídas y no notificadas)
                const newNotifications = data.notifications.filter(notif =>
                    !notif.is_read &&
                    !this.notifiedIds.has(notif.id) &&
                    this.isRecent(notif.created_at)
                );

                // Mostrar notificaciones push
                newNotifications.forEach(notif => {
                    this.showPushNotification(notif);
                    this.notifiedIds.add(notif.id);
                });

                if (newNotifications.length > 0) {
                    this.saveNotifiedIds();
                }
            }
        } catch (error) {
            console.error('Error verificando notificaciones:', error);
        }
    }

    isRecent(createdAt) {
        // Considerar reciente si fue creada en los últimos 5 minutos
        const notifTime = new Date(createdAt).getTime();
        const now = Date.now();
        const fiveMinutes = 5 * 60 * 1000;
        return (now - notifTime) < fiveMinutes;
    }

    showPushNotification(notification) {
        // Verificar que tengamos permiso y el manager esté disponible
        if (!window.notificationManager || window.notificationManager.permission !== 'granted') {
            return;
        }

        // Título siempre es "Agenda Virtual Eiwa"
        const title = 'Agenda Virtual Eiwa';
        let body = '';

        // Personalizar el cuerpo según el tipo de notificación
        if (notification.type === 'task_created' || notification.title.includes('Nueva tarea')) {
            // Nueva tarea: "Usuario agregó tarea de Materia"
            const match = notification.message.match(/(.+) agregó tarea de (.+)/);
            if (match) {
                const user = match[1];
                const subject = match[2];
                body = `Nueva tarea de ${subject}\n${user} la agregó al grupo`;
            } else {
                body = `${notification.title}\n${notification.message}`;
            }
        } else if (notification.type === 'task_request' || notification.title.includes('solicitud')) {
            // Solicitud de tarea
            body = `${notification.title}\n${notification.message}`;
        } else if (notification.type === 'task_approved' || notification.title.includes('aprobad')) {
            // Tarea aprobada
            body = `${notification.title}\n${notification.message}`;
        } else if (notification.type === 'task_rejected' || notification.title.includes('rechazad')) {
            // Tarea rechazada
            body = `${notification.title}\n${notification.message}`;
        } else if (notification.type === 'group_invite' || notification.title.includes('invitación')) {
            // Invitación a grupo
            body = `${notification.title}\n${notification.message}`;
        } else {
            // Cualquier otra notificación
            body = `${notification.title}\n${notification.message}`;
        }

        const options = {
            body: body,
            icon: '/static/img/logoeiwa.png',
            tag: `notification-${notification.id}-${Date.now()}`,
            data: {
                url: notification.action_url || '/dashboard/',
                notificationId: notification.id
            }
        };

        window.notificationManager.showNotification(title, options);
    }

    // Limpiar IDs antiguos (llamar periódicamente)
    cleanOldIds() {
        // Mantener solo los últimos 100 IDs
        if (this.notifiedIds.size > 100) {
            const idsArray = Array.from(this.notifiedIds);
            this.notifiedIds = new Set(idsArray.slice(-100));
            this.saveNotifiedIds();
        }
    }
}

// Crear instancia global
let realtimeNotifications;

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    // Esperar a que notificationManager esté disponible
    setTimeout(() => {
        if (window.notificationManager) {
            realtimeNotifications = new RealtimeNotifications();
            window.realtimeNotifications = realtimeNotifications;

            // Limpiar IDs antiguos cada hora
            setInterval(() => {
                if (realtimeNotifications) {
                    realtimeNotifications.cleanOldIds();
                }
            }, 60 * 60 * 1000);
        }
    }, 2000);
});
