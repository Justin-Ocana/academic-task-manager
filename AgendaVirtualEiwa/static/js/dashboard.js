document.addEventListener('DOMContentLoaded', function () {
    const menuToggle = document.getElementById('menuToggle');
    const sidebar = document.getElementById('sidebar');
    const sidebarOverlay = document.getElementById('sidebarOverlay');

    if (menuToggle && sidebar) {
        menuToggle.addEventListener('click', function () {
            sidebar.classList.toggle('active');
            sidebarOverlay.classList.toggle('active');
        });
    }

    // Cerrar sidebar al hacer click en el overlay
    if (sidebarOverlay) {
        sidebarOverlay.addEventListener('click', function () {
            sidebar.classList.remove('active');
            sidebarOverlay.classList.remove('active');
        });
    }

    // Cerrar sidebar al hacer click en un enlace en móvil
    const navItems = document.querySelectorAll('.sidebar .nav-item');
    navItems.forEach(item => {
        item.addEventListener('click', function () {
            if (window.innerWidth <= 768) {
                sidebar.classList.remove('active');
                sidebarOverlay.classList.remove('active');
            }
        });
    });

    // Marcar item activo según la URL actual
    setActiveNavItem();
});

function setActiveNavItem() {
    const currentPath = window.location.pathname;
    const navItems = document.querySelectorAll('.sidebar .nav-item');

    // Remover clase active de todos los items
    navItems.forEach(item => item.classList.remove('active'));

    // Determinar qué item debe estar activo
    let activeItem = null;

    if (currentPath === '/dashboard/') {
        activeItem = document.querySelector('.nav-item[href="/dashboard/"]');
    } else if (currentPath.startsWith('/groups/')) {
        activeItem = document.querySelector('.nav-item[href*="group"]');
    } else if (currentPath.startsWith('/tasks/')) {
        activeItem = document.querySelector('.nav-item[href*="task"]');
    } else if (currentPath.startsWith('/calendar/')) {
        activeItem = document.querySelector('.nav-item[href*="calendar"]');
    } else if (currentPath.startsWith('/subjects/')) {
        activeItem = document.querySelector('.nav-item[href*="materia"]');
    } else if (currentPath.startsWith('/notifications/')) {
        activeItem = document.querySelector('.nav-item[href*="notificacion"]');
    }

    // Agregar clase active al item correspondiente
    if (activeItem) {
        activeItem.classList.add('active');
    }
}
