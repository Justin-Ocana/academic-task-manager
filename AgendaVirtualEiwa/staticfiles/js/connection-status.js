// Indicador de estado de conexión
class ConnectionStatus {
    constructor() {
        this.isOnline = navigator.onLine;
        this.createIndicator();
        this.attachListeners();
    }

    createIndicator() {
        const indicatorHTML = `
            <div id="connectionStatus" class="connection-status">
                <div class="connection-status-content">
                    <svg class="connection-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M1 9l2 2c4.97-4.97 13.03-4.97 18 0l2-2C16.93 2.93 7.08 2.93 1 9z"></path>
                        <path d="M5 13l2 2c3.31-3.31 8.69-3.31 12 0l2-2c-4.1-4.1-10.9-4.1-15 0z"></path>
                        <path d="M9 17l3 3 3-3c-1.66-1.66-4.34-1.66-6 0z"></path>
                    </svg>
                    <span class="connection-message">Sin conexión</span>
                </div>
            </div>
        `;
        document.body.insertAdjacentHTML('beforeend', indicatorHTML);
        this.indicator = document.getElementById('connectionStatus');
    }

    attachListeners() {
        window.addEventListener('online', () => {
            this.isOnline = true;
            this.hideIndicator();
            showToast('Conexión restaurada', 'success');
        });

        window.addEventListener('offline', () => {
            this.isOnline = false;
            this.showIndicator();
        });

        // Detectar conexión lenta
        this.monitorSlowConnection();
    }

    showIndicator() {
        this.indicator.classList.add('show');
    }

    hideIndicator() {
        this.indicator.classList.remove('show');
    }

    monitorSlowConnection() {
        // Interceptar fetch para detectar respuestas lentas
        const originalFetch = window.fetch;
        window.fetch = async (...args) => {
            const startTime = Date.now();

            try {
                const response = await originalFetch(...args);
                const duration = Date.now() - startTime;

                // Si tarda más de 5 segundos, mostrar advertencia
                if (duration > 5000) {
                    this.showSlowConnectionWarning();
                }

                return response;
            } catch (error) {
                // Error de red
                this.showIndicator();
                throw error;
            }
        };
    }

    showSlowConnectionWarning() {
        const warning = document.createElement('div');
        warning.className = 'slow-connection-warning';
        warning.innerHTML = `
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path>
            </svg>
            <span>Conexión lenta detectada</span>
        `;
        document.body.appendChild(warning);

        setTimeout(() => {
            warning.classList.add('show');
        }, 10);

        setTimeout(() => {
            warning.classList.remove('show');
            setTimeout(() => warning.remove(), 300);
        }, 3000);
    }
}

// CSS para el indicador
const style = document.createElement('style');
style.textContent = `
    .connection-status {
        position: fixed;
        top: -60px;
        left: 50%;
        transform: translateX(-50%);
        background: linear-gradient(135deg, #dc3545, #c82333);
        color: white;
        padding: 12px 24px;
        border-radius: 0 0 12px 12px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
        z-index: 9999;
        transition: top 0.3s ease;
    }

    .connection-status.show {
        top: 0;
    }

    .connection-status-content {
        display: flex;
        align-items: center;
        gap: 10px;
    }

    .connection-icon {
        width: 20px;
        height: 20px;
    }

    .connection-message {
        font-weight: 600;
        font-size: 0.9rem;
    }

    .slow-connection-warning {
        position: fixed;
        bottom: -60px;
        right: 20px;
        background: linear-gradient(135deg, #ffc107, #ff9800);
        color: #333;
        padding: 12px 20px;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
        z-index: 9999;
        display: flex;
        align-items: center;
        gap: 10px;
        transition: bottom 0.3s ease;
    }

    .slow-connection-warning.show {
        bottom: 20px;
    }

    .slow-connection-warning svg {
        width: 20px;
        height: 20px;
    }

    @media (max-width: 768px) {
        .connection-status {
            width: 90%;
            left: 5%;
            transform: none;
        }

        .slow-connection-warning {
            right: 10px;
            left: 10px;
        }
    }
`;
document.head.appendChild(style);

// Inicializar
new ConnectionStatus();
