// Sistema de Toasts/Notificaciones mejorado

class ToastManager {
    constructor() {
        this.container = null;
        this.init();
    }

    init() {
        // Crear contenedor si no existe
        if (!document.getElementById('toastContainer')) {
            this.container = document.createElement('div');
            this.container.id = 'toastContainer';
            this.container.className = 'toast-container';
            document.body.appendChild(this.container);
        } else {
            this.container = document.getElementById('toastContainer');
        }
    }

    show(message, type = 'info', duration = 3000) {
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;

        const icon = this.getIcon(type);

        toast.innerHTML = `
            <div class="toast-icon">${icon}</div>
            <div class="toast-message">${message}</div>
            <button class="toast-close" onclick="this.parentElement.remove()">×</button>
        `;

        this.container.appendChild(toast);

        // Animar entrada
        setTimeout(() => toast.classList.add('show'), 10);

        // Auto-remover
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 300);
        }, duration);

        return toast;
    }

    success(message, duration) {
        return this.show(message, 'success', duration);
    }

    error(message, duration) {
        return this.show(message, 'error', duration);
    }

    warning(message, duration) {
        return this.show(message, 'warning', duration);
    }

    info(message, duration) {
        return this.show(message, 'info', duration);
    }

    getIcon(type) {
        const icons = {
            success: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
                <polyline points="22 4 12 14.01 9 11.01"></polyline>
            </svg>`,
            error: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10"></circle>
                <line x1="15" y1="9" x2="9" y2="15"></line>
                <line x1="9" y1="9" x2="15" y2="15"></line>
            </svg>`,
            warning: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path>
                <line x1="12" y1="9" x2="12" y2="13"></line>
                <line x1="12" y1="17" x2="12.01" y2="17"></line>
            </svg>`,
            info: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10"></circle>
                <line x1="12" y1="16" x2="12" y2="12"></line>
                <line x1="12" y1="8" x2="12.01" y2="8"></line>
            </svg>`
        };
        return icons[type] || icons.info;
    }
}

// Crear instancia global
const toast = new ToastManager();
window.toast = toast;

// Función global para compatibilidad
window.showToast = (message, type) => toast.show(message, type);

// Estilos
const style = document.createElement('style');
style.textContent = `
    .toast-container {
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 10000;
        display: flex;
        flex-direction: column;
        gap: 10px;
        max-width: 400px;
    }

    .toast {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 16px 20px;
        background: white;
        border-radius: 12px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
        transform: translateX(450px);
        transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        border-left: 4px solid;
    }

    .toast.show {
        transform: translateX(0);
    }

    .toast-icon {
        flex-shrink: 0;
        width: 24px;
        height: 24px;
    }

    .toast-icon svg {
        width: 100%;
        height: 100%;
    }

    .toast-message {
        flex: 1;
        font-family: 'Montserrat', sans-serif;
        font-weight: 500;
        font-size: 0.95rem;
        color: #333;
    }

    .toast-close {
        flex-shrink: 0;
        width: 24px;
        height: 24px;
        border: none;
        background: none;
        font-size: 24px;
        line-height: 1;
        color: #999;
        cursor: pointer;
        transition: color 0.2s;
    }

    .toast-close:hover {
        color: #333;
    }

    .toast-success {
        border-left-color: #4caf50;
    }

    .toast-success .toast-icon svg {
        color: #4caf50;
    }

    .toast-error {
        border-left-color: #f44336;
    }

    .toast-error .toast-icon svg {
        color: #f44336;
    }

    .toast-warning {
        border-left-color: #ff9800;
    }

    .toast-warning .toast-icon svg {
        color: #ff9800;
    }

    .toast-info {
        border-left-color: #2196f3;
    }

    .toast-info .toast-icon svg {
        color: #2196f3;
    }

    @media (max-width: 768px) {
        .toast-container {
            top: 10px;
            right: 10px;
            left: 10px;
            max-width: none;
        }

        .toast {
            padding: 12px 16px;
        }

        .toast-message {
            font-size: 0.9rem;
        }
    }
`;
document.head.appendChild(style);
