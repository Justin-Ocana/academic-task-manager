// Sistema de Notificaciones Push - Agenda Virtual Eiwa

class NotificationManager {
    constructor() {
        this.permission = 'default';
        this.init();
    }

    init() {
        // Verificar si el navegador soporta notificaciones
        if (!('Notification' in window)) {
            console.log('Este navegador no soporta notificaciones');
            return;
        }

        this.permission = Notification.permission;
        console.log('NotificationManager inicializado. Permiso:', this.permission);
    }

    async requestPermission() {
        if (!('Notification' in window)) {
            return false;
        }

        try {
            const permission = await Notification.requestPermission();
            this.permission = permission;

            if (permission === 'granted') {
                this.showToast('Notificaciones activadas correctamente', 'success');
                console.log('Permiso de notificaciones concedido');
                return true;
            } else {
                this.showToast('Notificaciones desactivadas', 'error');
                console.log('Permiso de notificaciones denegado');
                return false;
            }
        } catch (error) {
            console.error('Error al solicitar permiso:', error);
            return false;
        }
    }

    showNotification(title, options = {}) {
        // Si no tenemos permiso, no hacer nada
        if (this.permission !== 'granted') {
            console.log('No hay permiso para mostrar notificaciones');
            return;
        }

        // URL completa del icono (importante para Android)
        const iconUrl = window.location.origin + '/static/img/logoeiwa.png';

        const defaultOptions = {
            icon: iconUrl,
            badge: iconUrl,
            vibrate: [200, 100, 200],
            requireInteraction: false,
            silent: false,
            ...options
        };

        console.log('Mostrando notificación:', title);
        console.log('Opciones:', defaultOptions);

        try {
            // Crear notificación
            const notification = new Notification(title, defaultOptions);

            // Eventos de debugging
            notification.onshow = () => console.log('Notificación mostrada');
            notification.onerror = (e) => console.error('Error en notificación:', e);

            // Manejar click
            notification.onclick = function (event) {
                event.preventDefault();
                console.log('Click en notificación');

                if (window.focus) window.focus();

                // Navegar si hay URL
                if (defaultOptions.data && defaultOptions.data.url) {
                    window.location.href = defaultOptions.data.url;
                }

                notification.close();
            };

        } catch (error) {
            console.error('Error al crear notificación:', error);
        }
    }

    // Notificación de nueva tarea
    notifyNewTask(task) {
        const title = `Agenda Virtual Eiwa`;
        const options = {
            body: `Nueva tarea de ${task.subject}: ${task.title}`,
            icon: '/static/img/logoeiwa.png',
            tag: `task-${task.id}-${Date.now()}`,
            data: {
                url: `/tasks/${task.id}/`,
                taskId: task.id
            }
        };

        this.showNotification(title, options);
    }

    // Notificación de tarea próxima a vencer
    notifyTaskDueSoon(task, hoursLeft) {
        const title = `Agenda Virtual Eiwa`;
        const options = {
            body: `Tarea próxima a vencer\n${task.subject}: ${task.title}\nVence en ${hoursLeft} horas`,
            icon: '/static/img/logoeiwa.png',
            tag: `due-${task.id}-${Date.now()}`,
            data: {
                url: `/tasks/${task.id}/`,
                taskId: task.id
            }
        };

        this.showNotification(title, options);
    }

    // Notificación de tarea vencida
    notifyTaskOverdue(task) {
        const title = `Agenda Virtual Eiwa`;
        const options = {
            body: `Tarea vencida\n${task.subject}: ${task.title}`,
            icon: '/static/img/logoeiwa.png',
            tag: `overdue-${task.id}-${Date.now()}`,
            vibrate: [300, 100, 300, 100, 300],
            data: {
                url: `/tasks/${task.id}/`,
                taskId: task.id
            }
        };

        this.showNotification(title, options);
    }

    // Notificación de tarea completada
    notifyTaskCompleted(task) {
        const title = `Agenda Virtual Eiwa`;
        const options = {
            body: `Tarea completada\n${task.subject}: ${task.title}`,
            icon: '/static/img/logoeiwa.png',
            tag: `completed-${task.id}-${Date.now()}`,
            vibrate: [200],
        };

        this.showNotification(title, options);
    }

    showToast(message, type = 'success') {
        // Crear toast simple si no existe la función global
        if (typeof window.showToast === 'function') {
            window.showToast(message, type);
        } else {
            console.log(`[${type}] ${message}`);
        }
    }

    // Verificar tareas y enviar notificaciones
    async checkTasksAndNotify() {
        try {
            const response = await fetch('/notifications/api/pending/');
            const data = await response.json();

            // Obtener tareas ya notificadas hoy
            const notifiedToday = this.getNotifiedToday();
            const today = new Date().toDateString();

            // Notificar tareas de hoy (solo una vez al día)
            if (data.today && data.today.length > 0) {
                const todayKey = `today-${today}`;
                if (!notifiedToday.includes(todayKey)) {
                    this.notifyTodayTasks(data.today);
                    this.markAsNotified(todayKey);
                }
            }

            // Notificar tareas de mañana (solo una vez al día)
            if (data.tomorrow && data.tomorrow.length > 0) {
                const tomorrowKey = `tomorrow-${today}`;
                if (!notifiedToday.includes(tomorrowKey)) {
                    this.notifyTomorrowTasks(data.tomorrow);
                    this.markAsNotified(tomorrowKey);
                }
            }

            // Notificar tareas próximas a vencer (cada una solo una vez)
            if (data.due_soon && data.due_soon.length > 0) {
                data.due_soon.forEach(task => {
                    const dueKey = `due-${task.id}-${today}`;
                    if (!notifiedToday.includes(dueKey)) {
                        this.notifyTaskDueSoon(task, task.hours_left);
                        this.markAsNotified(dueKey);
                    }
                });
            }

            // Notificar tareas vencidas (cada una solo una vez al día)
            if (data.overdue && data.overdue.length > 0) {
                data.overdue.forEach(task => {
                    const overdueKey = `overdue-${task.id}-${today}`;
                    if (!notifiedToday.includes(overdueKey)) {
                        this.notifyTaskOverdue(task);
                        this.markAsNotified(overdueKey);
                    }
                });
            }
        } catch (error) {
            console.error('Error al verificar tareas:', error);
        }
    }

    // Obtener lista de notificaciones enviadas hoy
    getNotifiedToday() {
        const today = new Date().toDateString();
        const stored = localStorage.getItem('notifiedTasks');

        if (!stored) return [];

        try {
            const data = JSON.parse(stored);
            // Limpiar notificaciones de días anteriores
            if (data.date !== today) {
                localStorage.removeItem('notifiedTasks');
                return [];
            }
            return data.tasks || [];
        } catch {
            return [];
        }
    }

    // Marcar tarea como notificada
    markAsNotified(key) {
        const today = new Date().toDateString();
        const notified = this.getNotifiedToday();
        notified.push(key);

        localStorage.setItem('notifiedTasks', JSON.stringify({
            date: today,
            tasks: notified
        }));
    }

    // Notificación de tareas de hoy
    notifyTodayTasks(tasks) {
        const count = tasks.length;
        const title = `Agenda Virtual Eiwa`;
        const options = {
            body: `Tareas de hoy\nTienes ${count} tarea${count > 1 ? 's' : ''} para completar hoy`,
            icon: '/static/img/logoeiwa.png',
            tag: `today-tasks-${Date.now()}`,
            data: {
                url: '/calendar/',
            }
        };

        this.showNotification(title, options);
    }

    // Notificación de tareas de mañana
    notifyTomorrowTasks(tasks) {
        const count = tasks.length;
        const title = `Agenda Virtual Eiwa`;
        const options = {
            body: `Tareas de mañana\nTienes ${count} tarea${count > 1 ? 's' : ''} programada${count > 1 ? 's' : ''} para mañana`,
            icon: '/static/img/logoeiwa.png',
            tag: `tomorrow-tasks-${Date.now()}`,
            data: {
                url: '/calendar/',
            }
        };

        this.showNotification(title, options);
    }
}

// Crear instancia global
const notificationManager = new NotificationManager();

// Exponer funciones globales
window.notificationManager = notificationManager;
window.requestNotificationPermission = () => notificationManager.requestPermission();

// Función para verificar si es hora de enviar notificaciones
function shouldCheckNow() {
    const now = new Date();
    const hour = now.getHours();
    const minute = now.getMinutes();

    // Horarios clave para verificar:
    // 8:00 AM - Recordatorio de tareas del día
    // 12:00 PM - Recordatorio de medio día
    // 6:00 PM - Recordatorio de tareas pendientes
    // 8:00 PM - Recordatorio de tareas de mañana

    const keyHours = [8, 12, 18, 20];

    // Verificar si estamos en una hora clave (con margen de 5 minutos)
    return keyHours.some(keyHour => hour === keyHour && minute < 5);
}

// Verificar tareas cada 5 minutos
setInterval(() => {
    if (notificationManager.permission === 'granted') {
        // Solo verificar en horarios clave o cada hora
        const now = new Date();
        if (shouldCheckNow() || now.getMinutes() === 0) {
            notificationManager.checkTasksAndNotify();
        }
    }
}, 5 * 60 * 1000);

// Verificar al cargar la página
document.addEventListener('DOMContentLoaded', () => {
    // Esperar 5 segundos antes de la primera verificación
    setTimeout(() => {
        if (notificationManager.permission === 'granted') {
            notificationManager.checkTasksAndNotify();
        }
    }, 5000);
});
