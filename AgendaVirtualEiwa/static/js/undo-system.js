// Sistema de deshacer acciones
class UndoSystem {
    constructor() {
        this.undoStack = [];
        this.maxStackSize = 10;
        this.undoTimeout = 5000; // 5 segundos para deshacer
        this.init();
    }

    init() {
        this.createUndoBar();
    }

    createUndoBar() {
        const undoBarHTML = `
            <div id="undoBar" class="undo-bar">
                <div class="undo-content">
                    <span class="undo-message"></span>
                    <button class="undo-btn">Deshacer</button>
                </div>
                <div class="undo-progress"></div>
            </div>
        `;
        document.body.insertAdjacentHTML('beforeend', undoBarHTML);
        this.undoBar = document.getElementById('undoBar');
        this.undoMessage = this.undoBar.querySelector('.undo-message');
        this.undoBtn = this.undoBar.querySelector('.undo-btn');
        this.undoProgress = this.undoBar.querySelector('.undo-progress');
    }

    addAction(action) {
        // Agregar acción al stack
        this.undoStack.push(action);

        // Limitar tamaño del stack
        if (this.undoStack.length > this.maxStackSize) {
            this.undoStack.shift();
        }

        // Mostrar barra de deshacer
        this.showUndoBar(action);
    }

    showUndoBar(action) {
        this.undoMessage.textContent = action.message;
        this.undoBar.classList.add('show');

        // Animar progreso
        this.undoProgress.style.animation = 'none';
        setTimeout(() => {
            this.undoProgress.style.animation = `undoProgress ${this.undoTimeout}ms linear`;
        }, 10);

        // Handler para deshacer
        const undoHandler = async () => {
            await action.undo();
            this.hideUndoBar();
            showToast('Acción deshecha', 'success');
        };

        this.undoBtn.onclick = undoHandler;

        // Auto-ocultar después del timeout
        clearTimeout(this.hideTimer);
        this.hideTimer = setTimeout(() => {
            this.hideUndoBar();
            // Ejecutar confirmación si existe
            if (action.onConfirm) {
                action.onConfirm();
            }
        }, this.undoTimeout);
    }

    hideUndoBar() {
        this.undoBar.classList.remove('show');
        clearTimeout(this.hideTimer);
    }

    // Acciones específicas
    taskCompleted(taskId, taskName) {
        this.addAction({
            message: `Tarea "${taskName}" completada`,
            undo: async () => {
                // Hacer petición para desmarcar como completada
                const response = await fetch(`/tasks/${taskId}/toggle-complete/`, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': this.getCsrfToken(),
                        'Content-Type': 'application/json',
                    },
                });

                if (response.ok) {
                    location.reload();
                }
            },
            onConfirm: () => {
                // Acción confirmada, no hacer nada
            }
        });
    }

    taskDeleted(taskId, taskData) {
        this.addAction({
            message: `Tarea "${taskData.name}" eliminada`,
            undo: async () => {
                // Hacer petición para restaurar tarea
                const response = await fetch(`/tasks/restore/${taskId}/`, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': this.getCsrfToken(),
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(taskData)
                });

                if (response.ok) {
                    location.reload();
                }
            }
        });
    }

    leftGroup(groupId, groupName) {
        this.addAction({
            message: `Saliste del grupo "${groupName}"`,
            undo: async () => {
                // Hacer petición para volver a unirse
                const response = await fetch(`/groups/${groupId}/rejoin/`, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': this.getCsrfToken(),
                    },
                });

                if (response.ok) {
                    location.reload();
                }
            }
        });
    }

    getCsrfToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]')?.value ||
            document.cookie.match(/csrftoken=([^;]+)/)?.[1];
    }
}

// CSS para el sistema de deshacer
const style = document.createElement('style');
style.textContent = `
    .undo-bar {
        position: fixed;
        bottom: -100px;
        left: 50%;
        transform: translateX(-50%);
        background: #333;
        color: white;
        padding: 16px 24px;
        border-radius: 12px 12px 0 0;
        box-shadow: 0 -4px 12px rgba(0, 0, 0, 0.3);
        z-index: 9998;
        transition: bottom 0.3s ease;
        min-width: 300px;
        max-width: 500px;
    }

    .undo-bar.show {
        bottom: 0;
    }

    .undo-content {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 20px;
    }

    .undo-message {
        font-size: 0.95rem;
        flex: 1;
    }

    .undo-btn {
        background: var(--naranja-eiwa);
        color: white;
        border: none;
        padding: 8px 20px;
        border-radius: 6px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
        white-space: nowrap;
    }

    .undo-btn:hover {
        background: var(--naranja-pastel);
        transform: scale(1.05);
    }

    .undo-progress {
        position: absolute;
        bottom: 0;
        left: 0;
        height: 3px;
        background: var(--naranja-eiwa);
        width: 100%;
        transform-origin: left;
    }

    @keyframes undoProgress {
        from {
            transform: scaleX(1);
        }
        to {
            transform: scaleX(0);
        }
    }

    @media (max-width: 768px) {
        .undo-bar {
            left: 10px;
            right: 10px;
            transform: none;
            min-width: auto;
        }

        .undo-content {
            flex-direction: column;
            gap: 10px;
        }

        .undo-btn {
            width: 100%;
        }
    }
`;
document.head.appendChild(style);

// Inicializar sistema
const undoSystem = new UndoSystem();
window.undoSystem = undoSystem;
