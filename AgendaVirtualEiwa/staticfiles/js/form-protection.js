// Protección contra múltiples envíos de formularios

(function () {
    'use strict';

    // Prevenir múltiples envíos de formularios
    document.addEventListener('DOMContentLoaded', function () {
        // Proteger todos los formularios
        const forms = document.querySelectorAll('form');

        forms.forEach(form => {
            form.addEventListener('submit', function (e) {
                // Si tiene bypass-protection, permitir el envío sin protección
                if (form.classList.contains('bypass-protection')) {
                    return true;
                }

                const submitButton = form.querySelector('button[type="submit"], input[type="submit"]');

                // Si el formulario ya está siendo enviado, prevenir
                if (form.classList.contains('submitting')) {
                    e.preventDefault();
                    return false;
                }

                // Marcar como enviando
                form.classList.add('submitting');

                // Deshabilitar botón de envío
                if (submitButton) {
                    submitButton.disabled = true;
                    const originalText = submitButton.innerHTML || submitButton.textContent || submitButton.value;
                    submitButton.dataset.originalText = originalText;

                    if (submitButton.tagName === 'BUTTON') {
                        submitButton.innerHTML = '<span class="spinner-small"></span> Enviando...';
                    } else {
                        submitButton.value = 'Enviando...';
                    }
                }

                // Re-habilitar después de 5 segundos (por si hay error)
                setTimeout(() => {
                    form.classList.remove('submitting');
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
                }, 5000);
            });
        });

        // Proteger botones con data-single-click
        const singleClickButtons = document.querySelectorAll('[data-single-click]');

        singleClickButtons.forEach(button => {
            button.addEventListener('click', function (e) {
                if (button.disabled) {
                    e.preventDefault();
                    return false;
                }

                button.disabled = true;
                const originalText = button.textContent;
                button.dataset.originalText = originalText;
                button.innerHTML = '<span class="spinner-small"></span> Procesando...';

                // Re-habilitar después de 3 segundos
                setTimeout(() => {
                    button.disabled = false;
                    button.textContent = originalText;
                }, 3000);
            });
        });
    });

    // Agregar estilos para el spinner
    const style = document.createElement('style');
    style.textContent = `
        .spinner-small {
            display: inline-block;
            width: 14px;
            height: 14px;
            border: 2px solid rgba(255,255,255,0.3);
            border-top-color: white;
            border-radius: 50%;
            animation: spin 0.6s linear infinite;
            margin-right: 5px;
            vertical-align: middle;
        }

        @keyframes spin {
            to { transform: rotate(360deg); }
        }

        form.submitting {
            opacity: 0.7;
            pointer-events: none;
        }
    `;
    document.head.appendChild(style);
})();
