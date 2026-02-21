// Validación en tiempo real de formularios
class FormValidator {
    constructor() {
        this.validators = {
            required: (value) => value.trim() !== '',
            email: (value) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value),
            minLength: (value, min) => value.length >= min,
            maxLength: (value, max) => value.length <= max,
            pattern: (value, pattern) => new RegExp(pattern).test(value),
            date: (value) => !isNaN(Date.parse(value)),
            futureDate: (value) => new Date(value) > new Date(),
            pastDate: (value) => new Date(value) < new Date(),
            number: (value) => !isNaN(value) && value !== '',
            min: (value, min) => parseFloat(value) >= min,
            max: (value, max) => parseFloat(value) <= max,
        };

        this.messages = {
            required: 'Este campo es obligatorio',
            email: 'Ingresa un email válido',
            minLength: 'Mínimo {min} caracteres',
            maxLength: 'Máximo {max} caracteres',
            pattern: 'Formato inválido',
            date: 'Fecha inválida',
            futureDate: 'La fecha debe ser futura',
            pastDate: 'La fecha debe ser pasada',
            number: 'Debe ser un número',
            min: 'Valor mínimo: {min}',
            max: 'Valor máximo: {max}',
        };

        this.init();
    }

    init() {
        document.addEventListener('DOMContentLoaded', () => {
            this.attachValidators();
        });
    }

    attachValidators() {
        // Validar inputs con data-validate
        document.querySelectorAll('[data-validate]').forEach(input => {
            const rules = input.dataset.validate.split('|');

            // Validar en tiempo real
            input.addEventListener('input', () => {
                this.validateField(input, rules);
            });

            // Validar al perder foco
            input.addEventListener('blur', () => {
                this.validateField(input, rules);
            });
        });

        // Validar formularios antes de enviar
        document.querySelectorAll('form[data-validate-form]').forEach(form => {
            form.addEventListener('submit', (e) => {
                if (!this.validateForm(form)) {
                    e.preventDefault();
                }
            });
        });
    }

    validateField(input, rules) {
        const value = input.value;
        let isValid = true;
        let errorMessage = '';

        for (const rule of rules) {
            const [validatorName, ...params] = rule.split(':');
            const validator = this.validators[validatorName];

            if (validator && !validator(value, ...params)) {
                isValid = false;
                errorMessage = this.messages[validatorName];

                // Reemplazar placeholders en mensaje
                params.forEach((param, index) => {
                    errorMessage = errorMessage.replace(`{${Object.keys(this.validators)[index]}}`, param);
                });

                break;
            }
        }

        this.showValidationResult(input, isValid, errorMessage);
        return isValid;
    }

    validateForm(form) {
        let isValid = true;
        const inputs = form.querySelectorAll('[data-validate]');

        inputs.forEach(input => {
            const rules = input.dataset.validate.split('|');
            if (!this.validateField(input, rules)) {
                isValid = false;
            }
        });

        return isValid;
    }

    showValidationResult(input, isValid, message) {
        // Remover mensajes anteriores
        const existingError = input.parentElement.querySelector('.validation-error');
        if (existingError) {
            existingError.remove();
        }

        // Remover clases anteriores
        input.classList.remove('is-valid', 'is-invalid');

        if (!isValid && input.value !== '') {
            input.classList.add('is-invalid');

            // Agregar mensaje de error
            const errorDiv = document.createElement('div');
            errorDiv.className = 'validation-error';
            errorDiv.textContent = message;
            input.parentElement.appendChild(errorDiv);
        } else if (input.value !== '') {
            input.classList.add('is-valid');
        }
    }
}

// Inicializar validador
new FormValidator();

// Validaciones específicas para la app
document.addEventListener('DOMContentLoaded', () => {
    // Validar código de grupo
    const groupCodeInput = document.querySelector('input[name="invite_code"]');
    if (groupCodeInput) {
        groupCodeInput.addEventListener('input', async (e) => {
            const code = e.target.value.trim();
            if (code.length >= 6) {
                // Aquí podrías hacer una petición AJAX para verificar si el código existe
                // Por ahora solo validamos el formato
                const isValid = /^[A-Z0-9]{6,8}$/.test(code);
                if (!isValid) {
                    e.target.classList.add('is-invalid');
                } else {
                    e.target.classList.remove('is-invalid');
                    e.target.classList.add('is-valid');
                }
            }
        });
    }

    // Validar fechas de vencimiento
    const dueDateInputs = document.querySelectorAll('input[type="date"][name*="due"]');
    dueDateInputs.forEach(input => {
        input.addEventListener('change', (e) => {
            const selectedDate = new Date(e.target.value);
            const today = new Date();
            today.setHours(0, 0, 0, 0);

            if (selectedDate < today) {
                e.target.classList.add('is-invalid');
                showToast('La fecha de vencimiento no puede ser en el pasado', 'warning');
            } else {
                e.target.classList.remove('is-invalid');
                e.target.classList.add('is-valid');
            }
        });
    });

    // Validar nombre de grupo duplicado
    const groupNameInput = document.querySelector('input[name="name"]');
    if (groupNameInput && groupNameInput.form.action.includes('create')) {
        let debounceTimer;
        groupNameInput.addEventListener('input', (e) => {
            clearTimeout(debounceTimer);
            debounceTimer = setTimeout(async () => {
                const name = e.target.value.trim();
                if (name.length >= 3) {
                    // Aquí podrías hacer una petición AJAX para verificar si el nombre existe
                    // Por ahora solo validamos longitud
                    if (name.length > 50) {
                        e.target.classList.add('is-invalid');
                    } else {
                        e.target.classList.remove('is-invalid');
                        e.target.classList.add('is-valid');
                    }
                }
            }, 500);
        });
    }
});
