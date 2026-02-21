// Prompt para solicitar permisos de notificaciones

document.addEventListener('DOMContentLoaded', () => {
    // Esperar 3 segundos después de cargar la página
    setTimeout(() => {
        checkAndPromptNotifications();
    }, 3000);
});

function checkAndPromptNotifications() {
    // Verificar si el navegador soporta notificaciones
    if (!('Notification' in window)) {
        return;
    }

    // Si ya tenemos permiso o ya fue denegado, no mostrar
    if (Notification.permission !== 'default') {
        return;
    }

    // Verificar si ya se mostró el prompt alguna vez
    const promptShown = localStorage.getItem('notificationPromptShown');

    if (promptShown === 'true') {
        return;
    }

    // Mostrar banner de notificaciones
    showNotificationBanner();
}

function showNotificationBanner() {
    // Verificar que notificationManager esté disponible
    if (!window.notificationManager) {
        console.log('NotificationManager no disponible aún');
        return;
    }

    const banner = document.createElement('div');
    banner.className = 'notification-banner';
    banner.innerHTML = `
        <div class="notification-banner-content">
            <div class="notification-banner-icon">
                <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"></path>
                    <path d="M13.73 21a2 2 0 0 1-3.46 0"></path>
                </svg>
            </div>
            <div class="notification-banner-text">
                <strong>Activa las notificaciones</strong>
                <p>Recibe alertas de nuevas tareas y recordatorios de vencimientos</p>
            </div>
            <div class="notification-banner-actions">
                <button class="btn-banner btn-primary" id="enableNotifications">Activar</button>
                <button class="btn-banner btn-secondary" id="dismissNotifications">Ahora no</button>
            </div>
        </div>
    `;

    document.body.appendChild(banner);

    // Mostrar con animación
    setTimeout(() => banner.classList.add('show'), 100);

    // Event listeners
    document.getElementById('enableNotifications').addEventListener('click', async () => {
        try {
            const granted = await window.notificationManager.requestPermission();
            if (granted) {
                localStorage.setItem('notificationPromptShown', 'true');
                hideBanner(banner);
            }
        } catch (error) {
            console.error('Error al activar notificaciones:', error);
        }
    });

    document.getElementById('dismissNotifications').addEventListener('click', () => {
        localStorage.setItem('notificationPromptShown', 'true');
        hideBanner(banner);
    });
}

function hideBanner(banner) {
    banner.classList.remove('show');
    setTimeout(() => banner.remove(), 300);
}

// Estilos para el banner
if (!document.getElementById('notification-banner-styles')) {
    const style = document.createElement('style');
    style.id = 'notification-banner-styles';
    style.textContent = `
    .notification-banner {
        position: fixed;
        top: 20px;
        right: 20px;
        max-width: 400px;
        background: white;
        border-radius: 15px;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
        z-index: 10000;
        transform: translateX(500px);
        transition: transform 0.3s ease;
    }

    .notification-banner.show {
        transform: translateX(0);
    }

    .notification-banner-content {
        padding: 20px;
        display: flex;
        flex-direction: column;
        gap: 15px;
    }

    .notification-banner-icon {
        text-align: center;
    }

    .notification-banner-icon svg {
        width: 48px;
        height: 48px;
        color: var(--azul-principal);
    }

    .notification-banner-text {
        text-align: center;
    }

    .notification-banner-text strong {
        font-size: 1.2rem;
        color: var(--azul-principal);
        display: block;
        margin-bottom: 5px;
    }

    .notification-banner-text p {
        color: #666;
        font-size: 0.9rem;
        margin: 0;
    }

    .notification-banner-actions {
        display: flex;
        gap: 10px;
    }

    .btn-banner {
        flex: 1;
        padding: 10px 20px;
        border: none;
        border-radius: 25px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
        font-family: 'Montserrat', sans-serif;
    }

    .btn-banner.btn-primary {
        background: linear-gradient(135deg, var(--azul-pastel), var(--azul-secundario));
        color: white;
    }

    .btn-banner.btn-primary:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 109, 185, 0.3);
    }

    .btn-banner.btn-secondary {
        background: #f5f5f5;
        color: #666;
    }

    .btn-banner.btn-secondary:hover {
        background: #e0e0e0;
    }

    @media (max-width: 768px) {
        .notification-banner {
            top: 10px;
            right: 10px;
            left: 10px;
            max-width: none;
        }

        .notification-banner-content {
            padding: 15px;
        }

        .notification-banner-icon svg {
            width: 36px;
            height: 36px;
        }

        .notification-banner-text strong {
            font-size: 1rem;
        }

        .notification-banner-text p {
            font-size: 0.85rem;
        }

        .notification-banner-actions {
            flex-direction: column;
        }
    }
`;
    document.head.appendChild(style);
}
