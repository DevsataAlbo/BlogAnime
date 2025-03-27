// static/js/theme.js
document.addEventListener('DOMContentLoaded', function() {
    const themeToggleButtons = document.querySelectorAll('#theme-toggle');
    
    // Función para alternar el tema
    function toggleTheme() {
        // Verificar preferencia actual
        const isDarkMode = document.documentElement.classList.contains('dark');
        
        // Cambiar el tema
        if (isDarkMode) {
            document.documentElement.classList.remove('dark');
            localStorage.setItem('theme', 'light');
            document.cookie = "theme=light; path=/; max-age=31536000"; // Expires in 1 year
        } else {
            document.documentElement.classList.add('dark');
            localStorage.setItem('theme', 'dark');
            document.cookie = "theme=dark; path=/; max-age=31536000"; // Expires in 1 year
        }
    }
    
    // Agregar evento de clic a los botones de cambio de tema
    themeToggleButtons.forEach(button => {
        button.addEventListener('click', toggleTheme);
    });
    
    // Inicializar tema según preferencia del usuario
    const savedTheme = localStorage.getItem('theme');
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    
    if (savedTheme === 'dark' || (savedTheme === null && prefersDark)) {
        document.documentElement.classList.add('dark');
        localStorage.setItem('theme', 'dark');
    } else {
        document.documentElement.classList.remove('dark');
        localStorage.setItem('theme', 'light');
    }
});