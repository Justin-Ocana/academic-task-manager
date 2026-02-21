// Sistema de modales de confirmación personalizados
class ConfirmModal {
    constructor() {
        this.createModal();
        this.setupEventListeners();
    }

    createModal() {
        const modalHTML = `
            <div id="confirmModal" class="confirm-modal-overlay">
                <div class="confirm-modal">
                    <div class="confirm-modal-icon">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path>
                        </svg>
                    </div>
                    <h3 class="confirm-modal-title"></h3>
                    <p class="confirm-modal-message"></p>
                    <div class="confirm-modal-actions">
                        <button class="confirm-modal-btn confirm-modal-cancel">Cancelar</button>
                        <button class="confirm-modal-btn confirm-modal-confirm">Confirmar</button>
                    </div>
                </div>
            </div>
        `;
        document.body.insertAdjacentHTML('beforeend', modalHTML);
        this.modal = document.getElementById('confirmModal');
        this.titleEl = this.modal.querySelector('.confirm-modal-title');
        this.messageEl = this.modal.querySelector('.confirm-modal-message');
        this.confirmBtn = this.modal.querySelector('.confirm-modal-confirm');
        this.cancelBtn = this.modal.querySelector('.confirm-modal-cancel');
    }

    setupEventListeners() {
        // Cerrar al hacer clic en el overlay
        this.modal.addEventListener('click', (e) => {
            if (e.target === this.modal) {
                this.hide();
            }
        });

        // Cerrar con ESC
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.modal.classList.contains('active')) {
                this.hide();
            }
        });
    }

    show(options = {}) {
        return new Promise((resolve) => {
            const {
                title = '¿Estás seguro?',
                message = 'Esta acción no se puede deshacer',
                confirmText = 'Confirmar',
                cancelText = 'Cancelar',
                type = 'warning' // warning, danger, info
            } = options;

            this.titleEl.textContent = title;
            this.messageEl.textContent = message;
            this.confirmBtn.textContent = confirmText;
            this.cancelBtn.textContent = cancelText;

            // Aplicar tipo
            this.modal.querySelector('.confirm-modal').className = `confirm-modal confirm-modal-${type}`;

            // Mostrar modal
            this.modal.classList.add('active');
            document.body.style.overflow = 'hidden';

            // Handlers
            const handleConfirm = () => {
                this.hide();
                resolve(true);
                cleanup();
            };

            const handleCancel = () => {
                this.hide();
                resolve(false);
                cleanup();
            };

            const cleanup = () => {
                this.confirmBtn.removeEventListener('click', handleConfirm);
                this.cancelBtn.removeEventListener('click', handleCancel);
            };

            this.confirmBtn.addEventListener('click', handleConfirm);
            this.cancelBtn.addEventListener('click', handleCancel);
        });
    }

    hide() {
        this.modal.classList.remove('active');
        document.body.style.overflow = '';
    }
}

// Inicializar modal global
const confirmModal = new ConfirmModal();

// Función helper global
window.showConfirm = (options) => confirmModal.show(options);

// Interceptar todos los onclick con confirm()
document.addEventListener('DOMContentLoaded', () => {
    // Interceptar formularios con onsubmit que usan confirm()
    document.querySelectorAll('form[onsubmit*="confirm"]').forEach(form => {
        const originalOnsubmit = form.getAttribute('onsubmit');
        const confirmMatch = originalOnsubmit.match(/confirm\(['"](.+?)['"]\)/);

        if (confirmMatch) {
            const message = confirmMatch[1];
            form.removeAttribute('onsubmit');

            form.addEventListener('submit', async (e) => {
                e.preventDefault();
                e.stopImmediatePropagation();

                const confirmed = await showConfirm({
                    message: message,
                    type: 'danger'
                });

                if (confirmed) {
                    // Remover el event listener de form-protection temporalmente
                    form.classList.add('bypass-protection');
                    form.submit();
                } else {
                    // Restaurar el estado del formulario y botón
                    form.classList.remove('submitting');
                    const submitButton = form.querySelector('button[type="submit"], input[type="submit"]');
                    if (submitButton) {
                        submitButton.disabled = false;
                        const originalText = submitButton.dataset.originalText;
                        if (originalText) {
                            if (submitButton.tagName === 'BUTTON') {
                                submitButton.innerHTML = originalText;
                            } else {
                                submitButton.value = originalText;
                            }
                        }
                    }
                }
            });
        }
    });

    // Interceptar botones con onclick que usan confirm()
    document.querySelectorAll('button[onclick*="confirm"], a[onclick*="confirm"]').forEach(element => {
        const originalOnclick = element.getAttribute('onclick');
        const confirmMatch = originalOnclick.match(/confirm\(['"](.+?)['"]\)/);

        if (confirmMatch) {
            const message = confirmMatch[1];
            element.removeAttribute('onclick');

            element.addEventListener('click', async (e) => {
                e.preventDefault();
                e.stopImmediatePropagation();

                const confirmed = await showConfirm({
                    message: message,
                    type: 'warning'
                });

                if (confirmed) {
                    // Si es un enlace, navegar
                    if (element.tagName === 'A') {
                        window.location.href = element.href;
                    }
                    // Si es un botón en un formulario, enviar el formulario
                    else if (element.form) {
                        element.form.classList.add('bypass-protection');
                        element.form.submit();
                    }
                } else {
                    // Restaurar el estado del botón si se canceló
                    if (element.disabled) {
                        element.disabled = false;
                        const originalText = element.dataset.originalText;
                        if (originalText) {
                            element.innerHTML = originalText;
                        }
                    }
                }
            });
        }
    });
});
