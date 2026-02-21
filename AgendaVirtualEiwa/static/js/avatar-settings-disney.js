// ============================================
// AVATAR SETTINGS - DISNEY CATEGORY
// Adaptado del código de Eiwa para usar imágenes
// ============================================

document.addEventListener('DOMContentLoaded', function() {
    const avatarPreview = document.getElementById('avatarPreview');
    const avatarOptions = document.querySelectorAll('input[name="avatar_style"]');
    
    // Background color elements
    const bgColorToggle = document.getElementById('bgColorToggle');
    const bgColorGroup = document.getElementById('bgColorGroup');
    const bgColorPreview = document.getElementById('bgColorPreview');
    const bgColorSelector = document.getElementById('bgColorSelector');
    const bgCustomColorPicker = document.getElementById('bgCustomColorPicker');
    const bgVisualColorPicker = document.getElementById('bgVisualColorPicker');
    const bgColorR = document.getElementById('bgColorR');
    const bgColorG = document.getElementById('bgColorG');
    const bgColorB = document.getElementById('bgColorB');
    const bgHexValue = document.getElementById('bgHexValue');

    // Color palette (25 colors including white)
    const colorPalette = [
        { value: '#FFFFFF', name: 'Blanco' },
        { value: '#FF0000', name: 'Rojo' },
        { value: '#FF6B6B', name: 'Rojo Coral' },
        { value: '#FF8B94', name: 'Rosa Suave' },
        { value: '#FF8C00', name: 'Naranja Oscuro' },
        { value: '#FFA07A', name: 'Salmón' },
        { value: '#FFD700', name: 'Dorado' },
        { value: '#FFFF00', name: 'Amarillo' },
        { value: '#FFD93D', name: 'Amarillo Dorado' },
        { value: '#00FF00', name: 'Verde Lima' },
        { value: '#32CD32', name: 'Verde Limón' },
        { value: '#A8E6CF', name: 'Verde Menta' },
        { value: '#98D8C8', name: 'Verde Agua' },
        { value: '#00FFFF', name: 'Cian' },
        { value: '#4ECDC4', name: 'Turquesa' },
        { value: '#0000FF', name: 'Azul' },
        { value: '#87A9E8', name: 'Azul Cielo' },
        { value: '#FF00FF', name: 'Magenta' },
        { value: '#B4A7D6', name: 'Lavanda' },
        { value: '#9370DB', name: 'Púrpura Medio' },
        { value: '#F7B7A3', name: 'Melocotón' },
        { value: '#808080', name: 'Gris' },
        { value: '#A9A9A9', name: 'Gris Oscuro' },
        { value: '#2C3E50', name: 'Azul Oscuro' },
        { value: '#34495E', name: 'Gris Azulado' }
    ];

    let currentStyle = window.AVATAR_CONFIG?.style || 'princess-1';
    let currentBgColor = window.AVATAR_CONFIG?.bgColor || '#FFB6C1';

    // Initialize
    generateColorSelectors();
    loadSavedSettings();
    updatePreview();

    // Generate color selectors
    function generateColorSelectors() {
        // Background colors
        colorPalette.forEach((color, index) => {
            const label = document.createElement('label');
            label.className = 'color-option';
            label.innerHTML = `
                <input type="radio" name="bg_color" value="${color.value}" ${color.value === currentBgColor ? 'checked' : ''}>
                <span class="color-preview" style="background: ${color.value}; ${color.value === '#FFFFFF' ? 'border: 2px solid #e0e0e0;' : ''}" title="${color.name}">
                    <span class="color-check">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3">
                            <polyline points="20 6 9 17 4 12"></polyline>
                        </svg>
                    </span>
                </span>
            `;
            bgColorSelector.appendChild(label);
        });

        // Custom color option for background
        const bgCustomLabel = document.createElement('label');
        bgCustomLabel.className = 'color-option custom-color-option';
        bgCustomLabel.innerHTML = `
            <input type="radio" name="bg_color" value="custom" id="bgCustomColorRadio">
            <span class="color-preview custom-color-preview" id="bgCustomColorPreview" title="Color Personalizado">
                <span class="color-icon">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M12 2.69l5.66 5.66a8 8 0 1 1-11.31 0z"></path>
                    </svg>
                </span>
                <span class="color-check">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3">
                        <polyline points="20 6 9 17 4 12"></polyline>
                    </svg>
                </span>
            </span>
        `;
        bgColorSelector.appendChild(bgCustomLabel);

        // Add event listeners
        setupColorListeners();
    }

    function setupColorListeners() {
        // Background color listeners
        document.querySelectorAll('input[name="bg_color"]').forEach(input => {
            input.addEventListener('change', function() {
                if (this.value === 'custom') {
                    bgCustomColorPicker.classList.add('active');
                    updateBgCustomColor();
                } else {
                    bgCustomColorPicker.classList.remove('active');
                    currentBgColor = this.value;
                    bgColorPreview.style.background = this.value;
                    updatePreview();
                }
                addBounceAnimation();
            });
        });

        // Background visual picker
        bgVisualColorPicker.addEventListener('input', function() {
            const color = this.value;
            currentBgColor = color;
            updateRGBFromHex(color);
            bgColorPreview.style.background = color;
            document.getElementById('bgCustomColorPreview').style.background = color;
            updatePreview();
        });

        // RGB inputs
        [bgColorR, bgColorG, bgColorB].forEach(input => {
            input.addEventListener('input', function() {
                if (this.value < 0) this.value = 0;
                if (this.value > 255) this.value = 255;
                updateBgCustomColor();
            });
        });

        // HEX input
        bgHexValue.addEventListener('input', function() {
            handleHexInput(this.value);
        });
    }

    // Toggle sections
    bgColorToggle.addEventListener('click', function() {
        this.classList.toggle('active');
        bgColorGroup.classList.toggle('collapsed');
    });

    // Load saved settings
    function loadSavedSettings() {
        // Set avatar style
        const styleInput = document.querySelector('input[name="avatar_style"][value="' + currentStyle + '"]');
        if (styleInput) {
            styleInput.checked = true;
        }
        
        // Set background color
        const bgColorInput = document.querySelector('input[name="bg_color"][value="' + currentBgColor + '"]');
        if (bgColorInput) {
            bgColorInput.checked = true;
        }
        bgColorPreview.style.background = currentBgColor;
        
        // Update RGB inputs
        updateRGBFromHex(currentBgColor);
    }

    // Avatar style change
    avatarOptions.forEach(option => {
        option.addEventListener('change', function() {
            currentStyle = this.value;
            updatePreview();
            addBounceAnimation();
        });
    });

    function updateBgCustomColor() {
        const r = parseInt(bgColorR.value) || 0;
        const g = parseInt(bgColorG.value) || 0;
        const b = parseInt(bgColorB.value) || 0;
        
        currentBgColor = rgbToHex(r, g, b);
        bgHexValue.value = currentBgColor;
        bgVisualColorPicker.value = currentBgColor;
        bgColorPreview.style.background = currentBgColor;
        document.getElementById('bgCustomColorPreview').style.background = currentBgColor;
        
        if (document.getElementById('bgCustomColorRadio').checked) {
            updatePreview();
        }
    }

    function updateRGBFromHex(hex) {
        const r = parseInt(hex.substr(1, 2), 16);
        const g = parseInt(hex.substr(3, 2), 16);
        const b = parseInt(hex.substr(5, 2), 16);
        
        bgColorR.value = r;
        bgColorG.value = g;
        bgColorB.value = b;
        bgHexValue.value = hex.toUpperCase();
    }

    function handleHexInput(value) {
        let hex = value.trim();
        if (hex && !hex.startsWith('#')) {
            hex = '#' + hex;
        }
        
        if (/^#[0-9A-Fa-f]{6}$/.test(hex)) {
            currentBgColor = hex.toUpperCase();
            updateRGBFromHex(hex);
            bgVisualColorPicker.value = hex;
            bgColorPreview.style.background = hex;
            document.getElementById('bgCustomColorPreview').style.background = hex;
            if (document.getElementById('bgCustomColorRadio').checked) {
                updatePreview();
            }
        }
    }

    function rgbToHex(r, g, b) {
        return "#" + [r, g, b].map(x => {
            const hex = x.toString(16);
            return hex.length === 1 ? "0" + hex : hex;
        }).join('').toUpperCase();
    }

    function updatePreview() {
        const selectedInput = document.querySelector('input[name="avatar_style"]:checked');
        const imgPath = selectedInput.dataset.img;
        
        const lighterBgColor = lightenColor(currentBgColor, 20);
        avatarPreview.style.background = `linear-gradient(135deg, ${currentBgColor} 0%, ${lighterBgColor} 100%)`;
        avatarPreview.innerHTML = `<img src="${imgPath}" alt="Avatar Preview" style="width: 100%; height: 100%; object-fit: contain;">`;
    }

    function lightenColor(color, percent) {
        const num = parseInt(color.replace("#", ""), 16);
        const amt = Math.round(2.55 * percent);
        const R = (num >> 16) + amt;
        const G = (num >> 8 & 0x00FF) + amt;
        const B = (num & 0x0000FF) + amt;
        return "#" + (0x1000000 + (R < 255 ? R < 1 ? 0 : R : 255) * 0x10000 +
            (G < 255 ? G < 1 ? 0 : G : 255) * 0x100 +
            (B < 255 ? B < 1 ? 0 : B : 255))
            .toString(16).slice(1).toUpperCase();
    }

    function addBounceAnimation() {
        avatarPreview.style.transform = 'scale(1.1) rotate(5deg)';
        setTimeout(() => {
            avatarPreview.style.transform = '';
        }, 300);
    }

    avatarPreview.style.transition = 'all 0.4s cubic-bezier(0.68, -0.55, 0.265, 1.55)';

    // Form submission
    const form = document.getElementById('avatarForm');
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        // Get selected values
        const selectedStyle = document.querySelector('input[name="avatar_style"]:checked');
        const selectedBgColor = document.querySelector('input[name="bg_color"]:checked');
        
        if (!selectedStyle || !selectedBgColor) {
            alert('Por favor selecciona un avatar y un color de fondo');
            return;
        }
        
        // Agregar campos hidden al formulario
        let styleInput = form.querySelector('input[name="avatar_style"][type="hidden"]');
        if (!styleInput) {
            styleInput = document.createElement('input');
            styleInput.type = 'hidden';
            styleInput.name = 'avatar_style';
            form.appendChild(styleInput);
        }
        styleInput.value = selectedStyle.value;
        
        let bgColorInput = form.querySelector('input[name="bg_color"][type="hidden"]');
        if (!bgColorInput) {
            bgColorInput = document.createElement('input');
            bgColorInput.type = 'hidden';
            bgColorInput.name = 'bg_color';
            form.appendChild(bgColorInput);
        }
        bgColorInput.value = selectedBgColor.value === 'custom' ? currentBgColor : selectedBgColor.value;
        
        let svgColorInput = form.querySelector('input[name="svg_color"][type="hidden"]');
        if (!svgColorInput) {
            svgColorInput = document.createElement('input');
            svgColorInput.type = 'hidden';
            svgColorInput.name = 'svg_color';
            form.appendChild(svgColorInput);
        }
        svgColorInput.value = '#FFFFFF';  // Usar blanco en lugar de transparent
        
        // Debug: mostrar lo que se va a enviar
        console.log('Enviando datos:', {
            avatar_style: styleInput.value,
            bg_color: bgColorInput.value,
            svg_color: svgColorInput.value,
            avatar_category: 'disney'
        });
        
        // Submit form normalmente
        form.submit();
    });
});
