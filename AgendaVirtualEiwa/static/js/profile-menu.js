// Menú desplegable del perfil
document.addEventListener('DOMContentLoaded', () => {
    const userAvatar = document.querySelector('.user-avatar');
    const profileDropdown = document.querySelector('.profile-dropdown');

    if (!userAvatar || !profileDropdown) return;

    // Toggle dropdown
    userAvatar.addEventListener('click', (e) => {
        e.stopPropagation();
        profileDropdown.classList.toggle('active');
    });

    // Cerrar al hacer clic fuera
    document.addEventListener('click', (e) => {
        if (!profileDropdown.contains(e.target) && !userAvatar.contains(e.target)) {
            profileDropdown.classList.remove('active');
        }
    });

    // Cerrar con ESC
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            profileDropdown.classList.remove('active');
        }
    });

    // Prevenir cierre al hacer clic dentro del dropdown
    profileDropdown.addEventListener('click', (e) => {
        e.stopPropagation();
    });
});
