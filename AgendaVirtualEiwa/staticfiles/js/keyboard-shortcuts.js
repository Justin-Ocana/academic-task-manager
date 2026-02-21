// Atajos de teclado para mejorar accesibilidad
class KeyboardShortcuts {
    constructor() {
        this.shortcuts = {
            // Navegación
            'g h': () => window.location.href = '/',
            'g d': () => window.location.href = '/dashboard/',
            'g c': () => window.location.href = '/calendar/',
            'g t': () => window.location.href = '/tasks/',
            'g g': () => window.location.href = '/groups/',

            // Acciones
            'n t': () => this.openNewTaskModal(),
            'n g': () => this.openNewGroupModal(),
            '/': () => this.focusSearch(),
            'Escape': () => this.closeModals(),

            // Accesibilidad
            '?': () => this.showShortcutsHelp(),
        };

        this.sequence = '';
        this.sequenceTimer = null;
        this.init();
    }

    init() {
        document.addEventListener('keydown', (e) => {
            // Ignorar si está escribiendo en un input
            if (e.target.matches('input, textarea, select')) {
                return;
            }

            // Manejar teclas especiales
            if (e.key === 'Escape') {
                this.executeShortcut('Escape');
                return;
            }

            if (e.key === '?') {
                e.preventDefault();
                this.executeShortcut('?');
                return;
            }

            // Construir secuencia
            this.sequence += e.key;

            // Limpiar secuencia después de 1 segundo
            clearTimeout(this.sequenceTimer);
            this.sequenceTimer = setTimeout(() => {
                this.sequence = '';
            }, 1000);

            // Verificar si hay un atajo que coincida
            if (this.shortcuts[this.sequence]) {
                e.preventDefault();
                this.executeShortcut(this.sequence);
                this.sequence = '';
            }
        });

        // Mostrar indicador de atajos disponibles
        this.createShortcutIndicator();
    }

    executeShortcut(shortcut) {
        const action = this.shortcuts[shortcut];
        if (action) {
            action();
        }
    }

    openNewTaskModal() {
        const newTaskBtn = document.querySelector('[data-action="new-task"]');
        if (newTaskBtn) {
            newTaskBtn.click();
        }
    }

    openNewGroupModal() {
        const newGroupBtn = document.querySelector('[data-action="new-group"]');
        if (newGroupBtn) {
            newGroupBtn.click();
        }
    }

    focusSearch() {
        const searchInput = document.querySelector('input[type="search"], input[name="search"]');
        if (searchInput) {
            searchInput.focus();
        }
    }

    closeModals() {
        // Cerrar todos los modales abiertos
        document.querySelectorAll('.modal.active, .confirm-modal-overlay.active').forEach(modal => {
            modal.classList.remove('active');
        });
        document.body.style.overflow = '';
    }

    showShortcutsHelp() {
        const helpHTML = `
            <div class="shortcuts-help-modal">
                <div class="shortcuts-help-content">
                    <h2>Atajos de Teclado</h2>
                    <div class="shortcuts-grid">
                        <div class="shortcut-section">
                            <h3>Navegación</h3>
                            <div class="shortcut-item">
                                <kbd>g</kbd> <kbd>h</kbd>
                                <span>Ir a inicio</span>
                            </div>
                            <div class="shortcut-item">
                                <kbd>g</kbd> <kbd>d</kbd>
                                <span>Ir a dashboard</span>
                            </div>
                            <div class="shortcut-item">
                                <kbd>g</kbd> <kbd>c</kbd>
                                <span>Ir a calendario</span>
                            </div>
                            <div class="shortcut-item">
                                <kbd>g</kbd> <kbd>t</kbd>
                                <span>Ir a tareas</span>
                            </div>
                            <div class="shortcut-item">
                                <kbd>g</kbd> <kbd>g</kbd>
                                <span>Ir a grupos</span>
                            </div>
                        </div>
                        <div class="shortcut-section">
                            <h3>Acciones</h3>
                            <div class="shortcut-item">
                                <kbd>n</kbd> <kbd>t</kbd>
                                <span>Nueva tarea</span>
                            </div>
                            <div class="shortcut-item">
                                <kbd>n</kbd> <kbd>g</kbd>
                                <span>Nuevo grupo</span>
                            </div>
                            <div class="shortcut-item">
                                <kbd>/</kbd>
                                <span>Buscar</span>
                            </div>
                            <div class="shortcut-item">
                                <kbd>Esc</kbd>
                                <span>Cerrar modales</span>
                            </div>
                            <div class="shortcut-item">
                                <kbd>?</kbd>
                                <span>Mostrar ayuda</span>
                            </div>
                        </div>
                    </div>
                    <button class="btn-close-help" onclick="this.closest('.shortcuts-help-modal').remove()">
                        Cerrar
                    </button>
                </div>
            </div>
        `;

        document.body.insertAdjacentHTML('beforeend', helpHTML);
    }

    createShortcutIndicator() {
        const style = document.createElement('style');
        style.textContent = `
            .shortcuts-help-modal {
                position: fixed;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: rgba(0, 0, 0, 0.7);
                backdrop-filter: blur(4px);
                display: flex;
                align-items: center;
                justify-content: center;
                z-index: 10001;
                animation: fadeIn 0.3s ease;
            }

            .shortcuts-help-content {
                background: white;
                border-radius: 16px;
                padding: 30px;
                max-width: 600px;
                width: 90%;
                max-height: 80vh;
                overflow-y: auto;
            }

            .shortcuts-help-content h2 {
                font-family: 'Bebas Neue', sans-serif;
                font-size: 2rem;
                color: var(--azul-principal);
                margin-bottom: 20px;
                text-align: center;
            }

            .shortcuts-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px;
                margin-bottom: 20px;
            }

            .shortcut-section h3 {
                font-size: 1.2rem;
                color: var(--naranja-eiwa);
                margin-bottom: 10px;
            }

            .shortcut-item {
                display: flex;
                align-items: center;
                gap: 10px;
                padding: 8px 0;
            }

            .shortcut-item kbd {
                display: inline-block;
                padding: 4px 8px;
                background: #e9ecef;
                border: 1px solid #ced4da;
                border-radius: 4px;
                font-family: monospace;
                font-size: 0.875rem;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            }

            .shortcut-item span {
                color: #6c757d;
            }

            .btn-close-help {
                width: 100%;
                padding: 12px;
                background: var(--naranja-eiwa);
                color: white;
                border: none;
                border-radius: 8px;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s ease;
            }

            .btn-close-help:hover {
                background: var(--naranja-pastel);
                transform: translateY(-2px);
            }

            @keyframes fadeIn {
                from {
                    opacity: 0;
                }
                to {
                    opacity: 1;
                }
            }

            @media (max-width: 768px) {
                .shortcuts-grid {
                    grid-template-columns: 1fr;
                }
            }
        `;
        document.head.appendChild(style);
    }
}

// Inicializar atajos de teclado
new KeyboardShortcuts();
