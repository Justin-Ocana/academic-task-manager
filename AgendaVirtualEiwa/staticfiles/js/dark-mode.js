/**
 * DARK MODE TOGGLE - AGENDA VIRTUAL EIWA
 * Gestiona el cambio entre modo claro y oscuro
 */

(function () {
    'use strict';

    // Constantes
    const THEME_KEY = 'eiwa-theme';
    const DARK_THEME = 'dark';
    const LIGHT_THEME = 'light';

    // Elementos del DOM
    let themeToggleBtn = null;
    let sunIcon = null;
    let moonIcon = null;

    /**
     * Inicializa el modo oscuro
     */
    function initDarkMode() {
        // Crear el botón de cambio de tema
        createThemeToggleButton();

        // Cargar el tema guardado o detectar preferencia del sistema
        const savedTheme = getSavedTheme();
        const systemPrefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        const initialTheme = savedTheme || (systemPrefersDark ? DARK_THEME : LIGHT_THEME);

        // Aplicar el tema inicial (sin animación para evitar flash)
        setTheme(initialTheme, false);

        // Marcar como listo para habilitar transiciones
        setTimeout(() => {
            document.documentElement.classList.add('theme-ready');
        }, 100);

        // Escuchar cambios en la preferencia del sistema
        window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
            if (!getSavedTheme()) {
                setTheme(e.matches ? DARK_THEME : LIGHT_THEME);
            }
        });
    }

    /**
     * Crea el botón de cambio de tema en el header
     * DESHABILITADO - El modo oscuro solo se controla desde la configuración
     */
    function createThemeToggleButton() {
        // Botón deshabilitado - solo se controla desde el toggle en configuración
        return;

        const headerRight = document.querySelector('.header-right');
        if (!headerRight) return;

        // Crear el botón
        themeToggleBtn = document.createElement('button');
        themeToggleBtn.className = 'theme-toggle';
        themeToggleBtn.setAttribute('aria-label', 'Cambiar tema');
        themeToggleBtn.setAttribute('title', 'Cambiar tema');

        // Iconos SVG
        const sunSVG = `
            <svg class="sun-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="5"></circle>
                <line x1="12" y1="1" x2="12" y2="3"></line>
                <line x1="12" y1="21" x2="12" y2="23"></line>
                <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line>
                <line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line>
                <line x1="1" y1="12" x2="3" y2="12"></line>
                <line x1="21" y1="12" x2="23" y2="12"></line>
                <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line>
                <line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line>
            </svg>
        `;

        const moonSVG = `
            <svg class="moon-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path>
            </svg>
        `;

        themeToggleBtn.innerHTML = sunSVG + moonSVG;

        // Insertar antes del contenedor de notificaciones
        const notificationsWrapper = headerRight.querySelector('.notifications-wrapper');
        if (notificationsWrapper) {
            headerRight.insertBefore(themeToggleBtn, notificationsWrapper);
        } else {
            headerRight.insertBefore(themeToggleBtn, headerRight.firstChild);
        }

        // Referencias a los iconos
        sunIcon = themeToggleBtn.querySelector('.sun-icon');
        moonIcon = themeToggleBtn.querySelector('.moon-icon');

        // Event listener
        themeToggleBtn.addEventListener('click', toggleTheme);
    }

    /**
     * Alterna entre modo claro y oscuro
     */
    function toggleTheme() {
        const currentTheme = getCurrentTheme();
        const newTheme = currentTheme === DARK_THEME ? LIGHT_THEME : DARK_THEME;
        setTheme(newTheme);
    }

    /**
     * Establece el tema
     * @param {string} theme - 'dark' o 'light'
     * @param {boolean} animate - Si debe animar el cambio
     */
    function setTheme(theme, animate = true) {
        const body = document.body;
        const html = document.documentElement;

        // Aplicar el tema
        html.setAttribute('data-theme', theme);
        body.setAttribute('data-theme', theme);

        // Guardar en localStorage
        saveTheme(theme);

        // Actualizar iconos
        updateThemeIcons(theme, animate);

        // Disparar evento personalizado
        window.dispatchEvent(new CustomEvent('themeChanged', { detail: { theme } }));

        // Mostrar notificación toast solo si fue un cambio manual (animate = true)
        // y solo una vez por sesión
        if (animate && typeof showToast === 'function') {
            const toastShownKey = 'theme-toast-shown-' + Date.now();
            const lastToastTime = sessionStorage.getItem('last-theme-toast');
            const now = Date.now();

            // Solo mostrar si han pasado más de 3 segundos desde el último toast
            if (!lastToastTime || (now - parseInt(lastToastTime)) > 3000) {
                const message = theme === DARK_THEME ? 'Modo oscuro activado' : 'Modo claro activado';
                showToast(message, 'info', 2000);
                sessionStorage.setItem('last-theme-toast', now.toString());
            }
        }
    }

    /**
     * Actualiza los iconos del botón según el tema
     * @param {string} theme - Tema actual
     * @param {boolean} animate - Si debe animar
     */
    function updateThemeIcons(theme, animate) {
        if (!sunIcon || !moonIcon) return;

        if (theme === DARK_THEME) {
            sunIcon.style.display = 'block';
            moonIcon.style.display = 'none';
        } else {
            sunIcon.style.display = 'none';
            moonIcon.style.display = 'block';
        }

        if (animate && themeToggleBtn) {
            themeToggleBtn.style.animation = 'none';
            setTimeout(() => {
                themeToggleBtn.style.animation = '';
            }, 10);
        }
    }

    /**
     * Obtiene el tema actual
     * @returns {string} 'dark' o 'light'
     */
    function getCurrentTheme() {
        return document.documentElement.getAttribute('data-theme') || LIGHT_THEME;
    }

    /**
     * Guarda el tema en localStorage
     * @param {string} theme - Tema a guardar
     */
    function saveTheme(theme) {
        try {
            localStorage.setItem(THEME_KEY, theme);
        } catch (e) {
            console.warn('No se pudo guardar el tema:', e);
        }
    }

    /**
     * Obtiene el tema guardado
     * @returns {string|null} Tema guardado o null
     */
    function getSavedTheme() {
        try {
            return localStorage.getItem(THEME_KEY);
        } catch (e) {
            console.warn('No se pudo leer el tema guardado:', e);
            return null;
        }
    }

    /**
     * API pública
     */
    window.DarkMode = {
        toggle: toggleTheme,
        setTheme: setTheme,
        getCurrentTheme: getCurrentTheme,
        isDark: () => getCurrentTheme() === DARK_THEME,
        isLight: () => getCurrentTheme() === LIGHT_THEME
    };

    // Inicializar cuando el DOM esté listo
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initDarkMode);
    } else {
        initDarkMode();
    }

})();
