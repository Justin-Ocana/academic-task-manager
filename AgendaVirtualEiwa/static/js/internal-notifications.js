// Sistema de Notificaciones Internas (Modal de campana)

class InternalNotifications {
    constructor() {
        this.dropdown = null;
        this.bell = null;
        this.badge = null;
        this.list = null;
        this.unreadCount = 0;
        this.init();
    }

    init() {
        // Esperar a que el DOM esté listo
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.setup());
        } else {
            this.setup();
        }
    }

    setup() {
        // Obtener elementos del DOM
        this.bell = document.getElementById('notificationBell');
        this.badge = document.getElementById('notificationBadge');
        this.dropdown = document.getElementById('notificationsDropdown');
        this.list = document.getElementById('notificationsList');

        if (!this.bell || !this.dropdown) {
            console.log('Elementos de notificaciones no encontrados');
            return;
        }

        // Event listeners
        this.bell.addEventListener('click', (e) => {
            e.stopPropagation();
            this.toggleDropdown();
        });

        // Cerrar dropdown al hacer click fuera
        document.addEventListener('click', (e) => {
            if (!this.dropdown.contains(e.target) && !this.bell.contains(e.target)) {
                this.closeDropdown();
            }
        });

        // Botón de marcar todas como leídas
        const markAllBtn = document.getElementById('markAllRead');
        if (markAllBtn) {
            markAllBtn.addEventListener('click', () => this.markAllAsRead());
        }

        // Cargar notificaciones inicialmente
        this.loadNotifications();

        // Actualizar cada 30 segundos
        setInterval(() => this.loadNotifications(), 30000);
    }

    toggleDropdown() {
        const isOpen = this.dropdown.classList.contains('show');
        if (isOpen) {
            this.closeDropdown();
        } else {
            this.openDropdown();
        }
    }

    openDropdown() {
        this.dropdown.classList.add('show');
        this.loadNotifications();
    }

    closeDropdown() {
        this.dropdown.classList.remove('show');
    }

    async loadNotifications() {
        try {
            const response = await fetch('/notifications/api/get/');
            const data = await response.json();

            this.unreadCount = data.unread_count || 0;
            this.updateBadge();
            this.renderNotifications(data.notifications || []);
        } catch (error) {
            console.error('Error cargando notificaciones:', error);
        }
    }

    updateBadge() {
        if (this.unreadCount > 0) {
            this.badge.textContent = this.unreadCount > 99 ? '99+' : this.unreadCount;
            this.badge.style.display = 'flex';
        } else {
            this.badge.style.display = 'none';
        }
    }

    renderNotifications(notifications) {
        if (!this.list) return;

        if (notifications.length === 0) {
            this.list.innerHTML = `
                <div class="no-notifications">
                    <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"></path>
                        <path d="M13.73 21a2 2 0 0 1-3.46 0"></path>
                    </svg>
                    <p>No tienes notificaciones</p>
                </div>
            `;
            return;
        }

        this.list.innerHTML = notifications.map(notif => `
            <div class="notification-item ${notif.is_read ? 'read' : 'unread'}" 
                 data-id="${notif.id}">
                <div class="notification-icon ${this.getNotificationIconClass(notif.type)}"
                     onclick="internalNotifications.handleNotificationClick(${notif.id}, '${notif.action_url || ''}')">
                    ${this.getNotificationIcon(notif.type)}
                </div>
                <div class="notification-content"
                     onclick="internalNotifications.handleNotificationClick(${notif.id}, '${notif.action_url || ''}')">
                    <h4>${notif.title}</h4>
                    <p>${notif.message}</p>
                    <span class="notification-time">${this.formatTime(notif.created_at)}</span>
                </div>
                <button class="notification-delete-btn" 
                        onclick="event.stopPropagation(); internalNotifications.deleteNotification(${notif.id})"
                        title="Eliminar notificación">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M6 18L18 6M6 6l12 12"></path>
                    </svg>
                </button>
            </div>
        `).join('');
    }

    getNotificationIcon(type) {
        const icons = {
            'task_created': `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4"></path>
            </svg>`,
            'task_request': `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
            </svg>`,
            'task_approved': `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
            </svg>`,
            'task_rejected': `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
            </svg>`,
            'group_invite': `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"></path>
            </svg>`,
            'general': `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
            </svg>`
        };

        return icons[type] || icons['general'];
    }

    getNotificationIconClass(type) {
        const classes = {
            'task_created': 'icon-task',
            'task_request': 'icon-request',
            'task_approved': 'icon-success',
            'task_rejected': 'icon-error',
            'group_invite': 'icon-group',
            'general': 'icon-info'
        };

        return classes[type] || 'icon-info';
    }

    async handleNotificationClick(id, url) {
        try {
            // Marcar como leída
            await fetch(`/notifications/api/${id}/read/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': this.getCookie('csrftoken'),
                }
            });

            // Actualizar contador
            this.unreadCount = Math.max(0, this.unreadCount - 1);
            this.updateBadge();

            // Cerrar dropdown
            this.closeDropdown();

            // Navegar si hay URL
            if (url) {
                window.location.href = url;
            }
        } catch (error) {
            console.error('Error al marcar notificación:', error);
        }
    }

    async markAllAsRead() {
        try {
            await fetch('/notifications/api/read-all/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': this.getCookie('csrftoken'),
                }
            });

            this.unreadCount = 0;
            this.updateBadge();
            this.loadNotifications();
        } catch (error) {
            console.error('Error al marcar todas como leídas:', error);
        }
    }

    formatTime(dateString) {
        const date = new Date(dateString);
        const now = new Date();
        const diff = now - date;
        const minutes = Math.floor(diff / 60000);
        const hours = Math.floor(minutes / 60);
        const days = Math.floor(hours / 24);

        if (minutes < 1) return 'Ahora';
        if (minutes < 60) return `Hace ${minutes}m`;
        if (hours < 24) return `Hace ${hours}h`;
        if (days < 7) return `Hace ${days}d`;
        return date.toLocaleDateString();
    }

    async deleteNotification(id) {
        try {
            const response = await fetch(`/notifications/api/${id}/delete/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': this.getCookie('csrftoken'),
                }
            });

            if (response.ok) {
                // Animar y eliminar el elemento
                const item = document.querySelector(`[data-id="${id}"]`);
                if (item) {
                    item.style.opacity = '0';
                    item.style.transform = 'translateX(100%)';
                    setTimeout(() => {
                        item.remove();
                        // Recargar notificaciones para actualizar el contador
                        this.loadNotifications();
                    }, 300);
                }
            }
        } catch (error) {
            console.error('Error al eliminar notificación:', error);
        }
    }

    getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
}

// Crear instancia global
const internalNotifications = new InternalNotifications();
window.internalNotifications = internalNotifications;
