/**
 * Animaciones y efectos para la página de inicio
 */

document.addEventListener('DOMContentLoaded', function() {
    
    // ============================================
    // LAZY LOADING Y AUTOPLAY OPTIMIZADO DE VIDEOS
    // ============================================
    const observerOptions = {
        threshold: 0.3,
        rootMargin: '50px'
    };
    
    // Reducir calidad de video para mejor rendimiento
    const optimizeVideo = (video) => {
        video.setAttribute('playbackRate', '1');
        // Reducir resolución si es posible
        if (video.videoWidth > 1280) {
            video.style.maxWidth = '1280px';
        }
    };
    
    // Observer para videos de características con lazy loading
    const videoObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            const video = entry.target;
            
            if (entry.isIntersecting) {
                // Cargar el video si aún no se ha cargado
                if (video.hasAttribute('data-lazy-video')) {
                    const source = video.querySelector('source[data-src]');
                    if (source && source.dataset.src) {
                        source.src = source.dataset.src;
                        video.load();
                        video.removeAttribute('data-lazy-video');
                        optimizeVideo(video);
                    }
                }
                
                // Reproducir cuando está visible con requestAnimationFrame
                requestAnimationFrame(() => {
                    video.play().catch(err => {
                        console.log('Autoplay prevented:', err);
                    });
                });
            } else {
                // Pausar cuando no está visible para ahorrar recursos
                video.pause();
            }
        });
    }, observerOptions);
    
    // Observar todos los videos
    document.querySelectorAll('video').forEach(video => {
        videoObserver.observe(video);
        
        // Configuración básica optimizada
        video.loop = true;
        video.muted = true;
        video.playsInline = true;
        
        // Reducir calidad para mejor rendimiento
        video.setAttribute('playbackRate', '1');
    });
    
    // ============================================
    // ANIMACIONES AL HACER SCROLL (OPTIMIZADAS)
    // ============================================
    const fadeObserverOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const fadeObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                requestAnimationFrame(() => {
                    entry.target.style.opacity = '1';
                    entry.target.style.transform = 'translateY(0)';
                });
                fadeObserver.unobserve(entry.target);
            }
        });
    }, fadeObserverOptions);
    
    // Animar cards de características
    document.querySelectorAll('.feature-card').forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(30px)';
        card.style.transition = `opacity 0.6s ease ${index * 0.1}s, transform 0.6s ease ${index * 0.1}s`;
        fadeObserver.observe(card);
    });
    
    // Animar video principal
    const mainVideoContainer = document.querySelector('.main-video-container');
    if (mainVideoContainer) {
        mainVideoContainer.style.opacity = '0';
        mainVideoContainer.style.transform = 'translateY(30px)';
        mainVideoContainer.style.transition = 'opacity 0.8s ease, transform 0.8s ease';
        fadeObserver.observe(mainVideoContainer);
    }
    
    // Animar sección CTA
    const ctaContent = document.querySelector('.cta-content');
    if (ctaContent) {
        ctaContent.style.opacity = '0';
        ctaContent.style.transform = 'translateY(30px)';
        ctaContent.style.transition = 'opacity 0.8s ease, transform 0.8s ease';
        fadeObserver.observe(ctaContent);
    }
    
    // ============================================
    // PREVENIR MENÚ CONTEXTUAL EN VIDEOS
    // ============================================
    document.querySelectorAll('video').forEach(video => {
        video.addEventListener('contextmenu', function(e) {
            e.preventDefault();
            return false;
        });
    });
    
    // ============================================
    // SMOOTH SCROLL PARA ENLACES INTERNOS
    // ============================================
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
    
    // ============================================
    // LIBERAR MEMORIA DE VIDEOS NO VISIBLES
    // ============================================
    const memoryObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            const video = entry.target;
            if (!entry.isIntersecting) {
                // Si el video está muy lejos, pausarlo y liberar recursos
                video.pause();
                // Resetear el video para liberar más memoria
                if (video.currentTime > 0) {
                    video.currentTime = 0;
                }
            }
        });
    }, {
        threshold: 0,
        rootMargin: '300px'
    });
    
    // Observar videos de características para gestión de memoria
    document.querySelectorAll('.feature-video').forEach(video => {
        memoryObserver.observe(video);
    });
    
    // ============================================
    // THROTTLE PARA EVENTOS DE SCROLL
    // ============================================
    let scrollTimeout;
    window.addEventListener('scroll', () => {
        if (scrollTimeout) {
            window.cancelAnimationFrame(scrollTimeout);
        }
        scrollTimeout = window.requestAnimationFrame(() => {
            // Aquí puedes agregar lógica adicional de scroll si es necesario
        });
    }, { passive: true });
    
    // ============================================
    // CONTADOR DE ESTADÍSTICAS (si se agregan)
    // ============================================
    function animateCounter(element, target, duration = 2000) {
        let start = 0;
        const increment = target / (duration / 16);
        
        const timer = setInterval(() => {
            start += increment;
            if (start >= target) {
                element.textContent = target;
                clearInterval(timer);
            } else {
                element.textContent = Math.floor(start);
            }
        }, 16);
    }
    
    // Activar contadores cuando sean visibles
    const counters = document.querySelectorAll('[data-counter]');
    if (counters.length > 0) {
        const counterObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const target = parseInt(entry.target.dataset.counter);
                    animateCounter(entry.target, target);
                    counterObserver.unobserve(entry.target);
                }
            });
        }, { threshold: 0.5 });
        
        counters.forEach(counter => counterObserver.observe(counter));
    }
});

