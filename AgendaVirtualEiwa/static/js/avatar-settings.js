// ============================================
// AVATAR SETTINGS - JAVASCRIPT
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
    
    // SVG color elements
    const svgColorToggle = document.getElementById('svgColorToggle');
    const svgColorGroup = document.getElementById('svgColorGroup');
    const svgColorPreview = document.getElementById('svgColorPreview');
    const svgColorSelector = document.getElementById('svgColorSelector');
    const svgCustomColorPicker = document.getElementById('svgCustomColorPicker');
    const svgVisualColorPicker = document.getElementById('svgVisualColorPicker');
    const svgColorR = document.getElementById('svgColorR');
    const svgColorG = document.getElementById('svgColorG');
    const svgColorB = document.getElementById('svgColorB');
    const svgHexValue = document.getElementById('svgHexValue');

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

    // SVG Templates
    const svgTemplates = {
        smile: '<svg viewBox="0 0 100 100" fill="none"><circle cx="35" cy="40" r="5" fill="currentColor"/><circle cx="65" cy="40" r="5" fill="currentColor"/><path d="M30 60 Q50 75 70 60" stroke="currentColor" stroke-width="5" stroke-linecap="round" fill="none"/></svg>',
        cat: '<svg viewBox="0 0 100 100" fill="none"><path d="M20 30 L30 15 L35 30 Z" fill="currentColor"/><path d="M80 30 L70 15 L65 30 Z" fill="currentColor"/><circle cx="35" cy="45" r="4" fill="currentColor"/><circle cx="65" cy="45" r="4" fill="currentColor"/><path d="M40 60 L50 65 L60 60" stroke="currentColor" stroke-width="3" stroke-linecap="round" fill="none"/><path d="M50 65 L50 55" stroke="currentColor" stroke-width="3" stroke-linecap="round"/></svg>',
        'star-eyes': '<svg viewBox="0 0 100 100" fill="none"><path d="M35 40 L37 46 L43 46 L38 50 L40 56 L35 52 L30 56 L32 50 L27 46 L33 46 Z" fill="currentColor"/><path d="M65 40 L67 46 L73 46 L68 50 L70 56 L65 52 L60 56 L62 50 L57 46 L63 46 Z" fill="currentColor"/><circle cx="50" cy="65" r="8" fill="currentColor"/></svg>',
        robot: '<svg viewBox="0 0 100 100" fill="none"><rect x="30" y="25" width="40" height="45" rx="5" fill="currentColor"/><rect x="35" y="35" width="10" height="10" rx="2" fill="white"/><rect x="55" y="35" width="10" height="10" rx="2" fill="white"/><rect x="40" y="55" width="20" height="5" rx="2" fill="white"/><circle cx="50" cy="20" r="3" fill="currentColor"/><line x1="50" y1="17" x2="50" y2="25" stroke="currentColor" stroke-width="2"/></svg>',
        heart: '<svg viewBox="0 0 100 100" fill="none"><path d="M35 40 C35 35 30 32 27 35 C24 32 19 35 19 40 C19 45 27 50 27 50 C27 50 35 45 35 40 Z" fill="currentColor"/><path d="M81 40 C81 35 76 32 73 35 C70 32 65 35 65 40 C65 45 73 50 73 50 C73 50 81 45 81 40 Z" fill="currentColor"/><path d="M35 65 Q50 75 65 65" stroke="currentColor" stroke-width="4" stroke-linecap="round" fill="none"/></svg>',
        glasses: '<svg viewBox="0 0 100 100" fill="none"><circle cx="35" cy="42" r="12" stroke="currentColor" stroke-width="3" fill="none"/><circle cx="65" cy="42" r="12" stroke="currentColor" stroke-width="3" fill="none"/><line x1="47" y1="42" x2="53" y2="42" stroke="currentColor" stroke-width="3"/><path d="M35 60 Q50 68 65 60" stroke="currentColor" stroke-width="4" stroke-linecap="round" fill="none"/></svg>',
        music: '<svg viewBox="0 0 100 100" fill="none"><circle cx="35" cy="42" r="4" fill="currentColor"/><circle cx="65" cy="42" r="4" fill="currentColor"/><path d="M40 30 L45 25 L50 30 L55 25 L60 30" stroke="currentColor" stroke-width="3" stroke-linecap="round" fill="none"/><path d="M35 60 Q50 72 65 60" stroke="currentColor" stroke-width="4" stroke-linecap="round" fill="none"/></svg>',
        wink: '<svg viewBox="0 0 100 100" fill="none"><line x1="28" y1="40" x2="42" y2="40" stroke="currentColor" stroke-width="4" stroke-linecap="round"/><circle cx="65" cy="40" r="5" fill="currentColor"/><path d="M32 62 Q50 75 68 62" stroke="currentColor" stroke-width="4" stroke-linecap="round" fill="none"/></svg>',
        cool: '<svg viewBox="0 0 100 100" fill="none"><rect x="20" y="35" width="60" height="15" rx="7" fill="currentColor"/><line x1="20" y1="42" x2="15" y2="42" stroke="currentColor" stroke-width="3" stroke-linecap="round"/><line x1="80" y1="42" x2="85" y2="42" stroke="currentColor" stroke-width="3" stroke-linecap="round"/><path d="M38 65 L62 65" stroke="currentColor" stroke-width="4" stroke-linecap="round"/></svg>',
        bear: '<svg viewBox="0 0 100 100" fill="none"><circle cx="25" cy="25" r="10" fill="currentColor"/><circle cx="75" cy="25" r="10" fill="currentColor"/><circle cx="35" cy="45" r="4" fill="currentColor"/><circle cx="65" cy="45" r="4" fill="currentColor"/><ellipse cx="50" cy="58" rx="8" ry="10" fill="currentColor"/><path d="M42 65 Q50 70 58 65" stroke="currentColor" stroke-width="3" stroke-linecap="round" fill="none"/></svg>',
        lightning: '<svg viewBox="0 0 100 100" fill="none"><path d="M30 35 L38 25 L35 40 L42 40 L34 55 L37 40 L30 40 Z" fill="currentColor"/><path d="M68 35 L60 25 L63 40 L56 40 L64 55 L61 40 L68 40 Z" fill="currentColor"/><path d="M35 65 Q50 75 65 65" stroke="currentColor" stroke-width="4" stroke-linecap="round" fill="none"/></svg>',
        flower: '<svg viewBox="0 0 100 100" fill="none"><circle cx="35" cy="42" r="4" fill="currentColor"/><circle cx="65" cy="42" r="4" fill="currentColor"/><circle cx="30" cy="25" r="6" fill="currentColor"/><circle cx="40" cy="20" r="6" fill="currentColor"/><circle cx="50" cy="18" r="6" fill="currentColor"/><circle cx="60" cy="20" r="6" fill="currentColor"/><circle cx="70" cy="25" r="6" fill="currentColor"/><path d="M35 60 Q50 70 65 60" stroke="currentColor" stroke-width="4" stroke-linecap="round" fill="none"/></svg>',
        alien: '<svg viewBox="0 0 100 100" fill="none"><ellipse cx="35" cy="42" rx="8" ry="12" fill="currentColor"/><ellipse cx="65" cy="42" rx="8" ry="12" fill="currentColor"/><ellipse cx="50" cy="65" rx="15" ry="8" fill="currentColor"/><circle cx="40" cy="20" r="5" fill="currentColor"/><circle cx="60" cy="20" r="5" fill="currentColor"/></svg>',
        crown: '<svg viewBox="0 0 100 100" fill="none"><path d="M25 25 L35 35 L50 20 L65 35 L75 25 L70 45 L30 45 Z" fill="currentColor"/><circle cx="35" cy="45" r="4" fill="currentColor"/><circle cx="65" cy="45" r="4" fill="currentColor"/><path d="M38 62 Q50 70 62 62" stroke="currentColor" stroke-width="4" stroke-linecap="round" fill="none"/></svg>',
        ninja: '<svg viewBox="0 0 100 100" fill="none"><rect x="20" y="30" width="60" height="25" rx="3" fill="currentColor"/><rect x="28" y="38" width="12" height="8" rx="1" fill="white"/><rect x="60" y="38" width="12" height="8" rx="1" fill="white"/></svg>',
        party: '<svg viewBox="0 0 100 100" fill="none"><path d="M35 20 L40 35 L45 20 L50 35 L55 20 L60 35 L65 20" stroke="currentColor" stroke-width="3" stroke-linecap="round" fill="none"/><circle cx="32" cy="45" r="5" fill="currentColor"/><circle cx="68" cy="45" r="5" fill="currentColor"/><path d="M30 62 Q50 78 70 62" stroke="currentColor" stroke-width="5" stroke-linecap="round" fill="none"/></svg>',
        rocket: '<svg viewBox="0 0 100 100" fill="none"><path d="M50 15 L60 40 L55 70 L45 70 L40 40 Z" fill="currentColor"/><circle cx="50" cy="50" r="8" fill="white"/><path d="M35 70 L30 80 L40 75 Z" fill="currentColor"/><path d="M65 70 L70 80 L60 75 Z" fill="currentColor"/></svg>',
        pizza: '<svg viewBox="0 0 100 100" fill="none"><path d="M50 20 L80 70 L20 70 Z" fill="currentColor"/><circle cx="45" cy="45" r="5" fill="white"/><circle cx="60" cy="50" r="5" fill="white"/><circle cx="50" cy="60" r="5" fill="white"/></svg>',
        coffee: '<svg viewBox="0 0 100 100" fill="none"><rect x="30" y="40" width="40" height="35" rx="5" fill="currentColor"/><path d="M35 30 Q40 25 45 30" stroke="currentColor" stroke-width="3" fill="none"/><path d="M50 30 Q55 25 60 30" stroke="currentColor" stroke-width="3" fill="none"/><rect x="70" y="50" width="10" height="15" rx="3" fill="currentColor"/></svg>',
        game: '<svg viewBox="0 0 100 100" fill="none"><rect x="25" y="35" width="50" height="30" rx="8" fill="currentColor"/><circle cx="40" cy="50" r="6" fill="white"/><path d="M65 45 L65 55 M60 50 L70 50" stroke="white" stroke-width="3"/></svg>',
        book: '<svg viewBox="0 0 100 100" fill="none"><rect x="30" y="25" width="40" height="50" rx="3" fill="currentColor"/><path d="M50 25 L50 75" stroke="white" stroke-width="2"/><path d="M35 35 L45 35 M35 45 L45 45 M35 55 L45 55" stroke="white" stroke-width="2"/></svg>',
        camera: '<svg viewBox="0 0 100 100" fill="none"><rect x="25" y="35" width="50" height="35" rx="5" fill="currentColor"/><circle cx="50" cy="52" r="12" fill="white"/><circle cx="50" cy="52" r="8" fill="currentColor"/><rect x="45" y="28" width="10" height="7" rx="2" fill="currentColor"/></svg>',
        headphones: '<svg viewBox="0 0 100 100" fill="none"><path d="M30 50 Q30 25 50 25 Q70 25 70 50" stroke="currentColor" stroke-width="5" fill="none"/><rect x="25" y="50" width="10" height="20" rx="3" fill="currentColor"/><rect x="65" y="50" width="10" height="20" rx="3" fill="currentColor"/></svg>',
        palette: '<svg viewBox="0 0 100 100" fill="none"><ellipse cx="50" cy="50" rx="30" ry="25" fill="currentColor"/><circle cx="40" cy="40" r="4" fill="white"/><circle cx="55" cy="38" r="4" fill="white"/><circle cx="45" cy="52" r="4" fill="white"/><circle cx="60" cy="50" r="4" fill="white"/></svg>',
        umbrella: '<svg viewBox="0 0 100 100" fill="none"><path d="M50 30 Q30 30 25 45 L50 45 L75 45 Q70 30 50 30" fill="currentColor"/><path d="M50 45 L50 70 Q50 75 55 75" stroke="currentColor" stroke-width="3" fill="none"/></svg>',
        balloon: '<svg viewBox="0 0 100 100" fill="none"><ellipse cx="50" cy="40" rx="20" ry="25" fill="currentColor"/><path d="M50 65 L50 80" stroke="currentColor" stroke-width="2"/><path d="M45 68 Q50 70 55 68" stroke="currentColor" stroke-width="2" fill="none"/></svg>',
        plane: '<svg viewBox="0 0 100 100" fill="none"><path d="M50 30 L70 50 L50 55 L30 50 Z" fill="currentColor"/><rect x="48" y="30" width="4" height="40" fill="currentColor"/><path d="M40 65 L50 70 L60 65" fill="currentColor"/></svg>',
        bicycle: '<svg viewBox="0 0 100 100" fill="none"><circle cx="35" cy="60" r="12" stroke="currentColor" stroke-width="3" fill="none"/><circle cx="65" cy="60" r="12" stroke="currentColor" stroke-width="3" fill="none"/><path d="M35 60 L50 40 L65 60 M50 40 L50 30" stroke="currentColor" stroke-width="3"/></svg>',
        icecream: '<svg viewBox="0 0 100 100" fill="none"><circle cx="50" cy="35" r="15" fill="currentColor"/><circle cx="40" cy="40" r="12" fill="currentColor"/><circle cx="60" cy="40" r="12" fill="currentColor"/><path d="M40 50 L50 75 L60 50" fill="currentColor"/></svg>',
        cake: '<svg viewBox="0 0 100 100" fill="none"><rect x="30" y="50" width="40" height="25" rx="3" fill="currentColor"/><path d="M40 50 L40 40 M50 50 L50 40 M60 50 L60 40" stroke="currentColor" stroke-width="2"/><ellipse cx="40" cy="38" rx="3" ry="5" fill="currentColor"/><ellipse cx="50" cy="38" rx="3" ry="5" fill="currentColor"/><ellipse cx="60" cy="38" rx="3" ry="5" fill="currentColor"/></svg>',
        gift: '<svg viewBox="0 0 100 100" fill="none"><rect x="30" y="45" width="40" height="30" rx="3" fill="currentColor"/><rect x="25" y="40" width="50" height="8" rx="2" fill="currentColor"/><path d="M50 40 L50 75 M30 40 Q40 30 50 40 Q60 30 70 40" stroke="white" stroke-width="3"/></svg>',
        trophy: '<svg viewBox="0 0 100 100" fill="none"><path d="M40 30 L40 50 Q40 60 50 60 Q60 60 60 50 L60 30 Z" fill="currentColor"/><rect x="35" y="25" width="30" height="8" rx="2" fill="currentColor"/><path d="M50 60 L50 70 M40 70 L60 70" stroke="currentColor" stroke-width="4"/><path d="M35 30 L25 35 L25 45 L35 45" stroke="currentColor" stroke-width="2" fill="none"/><path d="M65 30 L75 35 L75 45 L65 45" stroke="currentColor" stroke-width="2" fill="none"/></svg>',
        gem: '<svg viewBox="0 0 100 100" fill="none"><path d="M50 25 L70 40 L60 65 L40 65 L30 40 Z" fill="currentColor"/><path d="M50 25 L50 65 M30 40 L70 40" stroke="white" stroke-width="2"/></svg>',
        leaf: '<svg viewBox="0 0 100 100" fill="none"><path d="M50 20 Q70 30 70 50 Q70 70 50 80 Q50 50 50 20" fill="currentColor"/><path d="M50 20 L50 80 M50 35 Q60 40 60 50" stroke="white" stroke-width="2"/></svg>',
        sun: '<svg viewBox="0 0 100 100" fill="none"><circle cx="50" cy="50" r="15" fill="currentColor"/><path d="M50 20 L50 30 M50 70 L50 80 M20 50 L30 50 M70 50 L80 50 M30 30 L35 35 M65 35 L70 30 M30 70 L35 65 M65 65 L70 70" stroke="currentColor" stroke-width="3" stroke-linecap="round"/></svg>',
        cloud: '<svg viewBox="0 0 100 100" fill="none"><path d="M30 55 Q30 45 40 45 Q40 35 50 35 Q60 35 60 45 Q70 45 70 55 Q70 65 60 65 L40 65 Q30 65 30 55" fill="currentColor"/></svg>',
        anchor: '<svg viewBox="0 0 100 100" fill="none"><circle cx="50" cy="30" r="8" stroke="currentColor" stroke-width="3" fill="none"/><path d="M50 38 L50 70 M35 60 L35 70 Q35 75 50 75 Q65 75 65 70 L65 60" stroke="currentColor" stroke-width="3"/><path d="M40 50 L60 50" stroke="currentColor" stroke-width="3"/></svg>',
        compass: '<svg viewBox="0 0 100 100" fill="none"><circle cx="50" cy="50" r="25" stroke="currentColor" stroke-width="3" fill="none"/><path d="M50 30 L55 50 L50 70 L45 50 Z" fill="currentColor"/><circle cx="50" cy="50" r="4" fill="currentColor"/></svg>',
        key: '<svg viewBox="0 0 100 100" fill="none"><circle cx="35" cy="50" r="12" stroke="currentColor" stroke-width="3" fill="none"/><circle cx="35" cy="50" r="6" fill="currentColor"/><path d="M47 50 L70 50 L70 45 M70 50 L70 55" stroke="currentColor" stroke-width="3"/></svg>',
        feather: '<svg viewBox="0 0 100 100" fill="none"><path d="M30 70 Q40 40 50 20 Q60 40 70 70" stroke="currentColor" stroke-width="3" fill="none"/><path d="M50 20 L35 35 M50 30 L38 42 M50 40 L40 50 M50 50 L42 58 M50 60 L45 65" stroke="currentColor" stroke-width="2"/><path d="M50 20 L65 35 M50 30 L62 42 M50 40 L60 50 M50 50 L58 58 M50 60 L55 65" stroke="currentColor" stroke-width="2"/></svg>'
    };

    let currentStyle = window.AVATAR_CONFIG?.style || 'smile';
    let currentBgColor = window.AVATAR_CONFIG?.bgColor || '#FF0000';
    let currentSvgColor = window.AVATAR_CONFIG?.svgColor || '#FFFFFF';

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
                <input type="radio" name="bg_color" value="${color.value}" ${index === 1 ? 'checked' : ''}>
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

        // SVG colors
        colorPalette.forEach((color, index) => {
            const label = document.createElement('label');
            label.className = 'color-option';
            label.innerHTML = `
                <input type="radio" name="svg_color" value="${color.value}" ${index === 0 ? 'checked' : ''}>
                <span class="color-preview" style="background: ${color.value}; ${color.value === '#FFFFFF' ? 'border: 2px solid #e0e0e0;' : ''}" title="${color.name}">
                    <span class="color-check">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3">
                            <polyline points="20 6 9 17 4 12"></polyline>
                        </svg>
                    </span>
                </span>
            `;
            svgColorSelector.appendChild(label);
        });

        // Custom color option for SVG
        const svgCustomLabel = document.createElement('label');
        svgCustomLabel.className = 'color-option custom-color-option';
        svgCustomLabel.innerHTML = `
            <input type="radio" name="svg_color" value="custom" id="svgCustomColorRadio">
            <span class="color-preview custom-color-preview" id="svgCustomColorPreview" title="Color Personalizado">
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
        svgColorSelector.appendChild(svgCustomLabel);

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

        // SVG color listeners
        document.querySelectorAll('input[name="svg_color"]').forEach(input => {
            input.addEventListener('change', function() {
                if (this.value === 'custom') {
                    svgCustomColorPicker.classList.add('active');
                    updateSvgCustomColor();
                } else {
                    svgCustomColorPicker.classList.remove('active');
                    currentSvgColor = this.value;
                    svgColorPreview.style.background = this.value;
                    if (this.value === '#FFFFFF') {
                        svgColorPreview.style.border = '2px solid #e0e0e0';
                    } else {
                        svgColorPreview.style.border = 'none';
                    }
                    updatePreview();
                }
                addBounceAnimation();
            });
        });

        // Background visual picker
        bgVisualColorPicker.addEventListener('input', function() {
            const color = this.value;
            currentBgColor = color;
            updateRGBFromHex(color, 'bg');
            bgColorPreview.style.background = color;
            document.getElementById('bgCustomColorPreview').style.background = color;
            updatePreview();
        });

        // SVG visual picker
        svgVisualColorPicker.addEventListener('input', function() {
            const color = this.value;
            currentSvgColor = color;
            updateRGBFromHex(color, 'svg');
            svgColorPreview.style.background = color;
            document.getElementById('svgCustomColorPreview').style.background = color;
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

        [svgColorR, svgColorG, svgColorB].forEach(input => {
            input.addEventListener('input', function() {
                if (this.value < 0) this.value = 0;
                if (this.value > 255) this.value = 255;
                updateSvgCustomColor();
            });
        });

        // HEX inputs
        bgHexValue.addEventListener('input', function() {
            handleHexInput(this.value, 'bg');
        });

        svgHexValue.addEventListener('input', function() {
            handleHexInput(this.value, 'svg');
        });
    }

    // Toggle sections
    bgColorToggle.addEventListener('click', function() {
        this.classList.toggle('active');
        bgColorGroup.classList.toggle('collapsed');
    });

    svgColorToggle.addEventListener('click', function() {
        this.classList.toggle('active');
        svgColorGroup.classList.toggle('collapsed');
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
        
        // Set SVG color
        const svgColorInput = document.querySelector('input[name="svg_color"][value="' + currentSvgColor + '"]');
        if (svgColorInput) {
            svgColorInput.checked = true;
        }
        svgColorPreview.style.background = currentSvgColor;
        if (currentSvgColor === '#FFFFFF') {
            svgColorPreview.style.border = '2px solid #e0e0e0';
        }
        
        // Update RGB inputs
        updateRGBFromHex(currentBgColor, 'bg');
        updateRGBFromHex(currentSvgColor, 'svg');
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

    function updateSvgCustomColor() {
        const r = parseInt(svgColorR.value) || 0;
        const g = parseInt(svgColorG.value) || 0;
        const b = parseInt(svgColorB.value) || 0;
        
        currentSvgColor = rgbToHex(r, g, b);
        svgHexValue.value = currentSvgColor;
        svgVisualColorPicker.value = currentSvgColor;
        svgColorPreview.style.background = currentSvgColor;
        document.getElementById('svgCustomColorPreview').style.background = currentSvgColor;
        
        if (document.getElementById('svgCustomColorRadio').checked) {
            updatePreview();
        }
    }

    function updateRGBFromHex(hex, type) {
        const r = parseInt(hex.substr(1, 2), 16);
        const g = parseInt(hex.substr(3, 2), 16);
        const b = parseInt(hex.substr(5, 2), 16);
        
        if (type === 'bg') {
            bgColorR.value = r;
            bgColorG.value = g;
            bgColorB.value = b;
            bgHexValue.value = hex.toUpperCase();
        } else {
            svgColorR.value = r;
            svgColorG.value = g;
            svgColorB.value = b;
            svgHexValue.value = hex.toUpperCase();
        }
    }

    function handleHexInput(value, type) {
        let hex = value.trim();
        if (hex && !hex.startsWith('#')) {
            hex = '#' + hex;
        }
        
        if (/^#[0-9A-Fa-f]{6}$/.test(hex)) {
            if (type === 'bg') {
                currentBgColor = hex.toUpperCase();
                updateRGBFromHex(hex, 'bg');
                bgVisualColorPicker.value = hex;
                bgColorPreview.style.background = hex;
                document.getElementById('bgCustomColorPreview').style.background = hex;
                if (document.getElementById('bgCustomColorRadio').checked) {
                    updatePreview();
                }
            } else {
                currentSvgColor = hex.toUpperCase();
                updateRGBFromHex(hex, 'svg');
                svgVisualColorPicker.value = hex;
                svgColorPreview.style.background = hex;
                document.getElementById('svgCustomColorPreview').style.background = hex;
                if (document.getElementById('svgCustomColorRadio').checked) {
                    updatePreview();
                }
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
        // Asegurarse de que el estilo existe en los templates
        const style = svgTemplates[currentStyle] ? currentStyle : 'smile';
        avatarPreview.innerHTML = svgTemplates[style];
        
        const lighterBgColor = lightenColor(currentBgColor, 20);
        avatarPreview.style.background = `linear-gradient(135deg, ${currentBgColor} 0%, ${lighterBgColor} 100%)`;
        
        const svgElement = avatarPreview.querySelector('svg');
        if (svgElement) {
            svgElement.style.color = currentSvgColor;
        }
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
        const selectedSvgColor = document.querySelector('input[name="svg_color"]:checked');
        
        if (!selectedStyle || !selectedBgColor || !selectedSvgColor) {
            alert('Por favor selecciona un avatar y ambos colores');
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
        svgColorInput.value = selectedSvgColor.value === 'custom' ? currentSvgColor : selectedSvgColor.value;
        
        let categoryInput = form.querySelector('input[name="avatar_category"][type="hidden"]');
        if (!categoryInput) {
            categoryInput = document.createElement('input');
            categoryInput.type = 'hidden';
            categoryInput.name = 'avatar_category';
            form.appendChild(categoryInput);
        }
        categoryInput.value = 'eiwa';
        
        // Debug: mostrar lo que se va a enviar
        console.log('Enviando datos:', {
            avatar_style: styleInput.value,
            bg_color: bgColorInput.value,
            svg_color: svgColorInput.value,
            avatar_category: 'eiwa'
        });
        
        // Submit form normalmente
        form.submit();
    });
});
