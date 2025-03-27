document.addEventListener('DOMContentLoaded', function() {
    // ---------- Navegación móvil ----------
    initMobileNavigation();
    
    // ---------- Formularios de búsqueda ----------
    initSearchForms();
    
    // ---------- Mensajes de alerta ----------
    initAlertMessages();
    
    // ---------- Lazy loading de imágenes ----------
    initLazyLoading();
    
    // ---------- Menú desplegable de usuario ----------
    initUserDropdownMenu();

});

/**
 * Inicializa la navegación móvil
 */
function initMobileNavigation() {
    // Mobile menu toggle
    const mobileMenuButton = document.getElementById('mobile-menu-button');
    const mobileMenu = document.getElementById('mobile-menu');
    
    if (mobileMenuButton && mobileMenu) {
        mobileMenuButton.addEventListener('click', function() {
            mobileMenu.classList.toggle('hidden');
        });
    }
    
    // Mobile category accordion
    const mobileCategoryButton = document.getElementById('mobile-category-button');
    const mobileCategoryMenu = document.getElementById('mobile-category-menu');
    
    if (mobileCategoryButton && mobileCategoryMenu) {
        mobileCategoryButton.addEventListener('click', function() {
            mobileCategoryMenu.classList.toggle('hidden');
            
            // Rotar icono
            const icon = mobileCategoryButton.querySelector('svg');
            if (mobileCategoryMenu.classList.contains('hidden')) {
                icon.classList.remove('rotate-180');
            } else {
                icon.classList.add('rotate-180');
            }
        });
    }
}

/**
 * Inicializa los formularios de búsqueda
 */
function initSearchForms() {
    const searchForms = document.querySelectorAll('form[action*="search"]');
    
    searchForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const input = form.querySelector('input[name="query"]');
            if (!input.value.trim()) {
                e.preventDefault();
            }
        });
    });
}

/**
 * Inicializa los mensajes de alerta
 */
function initAlertMessages() {
    const alerts = document.querySelectorAll('.alert-message');
    
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.classList.add('opacity-0');
            setTimeout(() => {
                alert.style.display = 'none';
            }, 300);
        }, 5000);
    });
}

/**
 * Inicializa el lazy loading de imágenes
 */
function initLazyLoading() {
    if ('loading' in HTMLImageElement.prototype) {
        const images = document.querySelectorAll('img[loading="lazy"]');
        images.forEach(img => {
            img.src = img.dataset.src;
        });
    } else {
        // Fallback para navegadores que no soportan lazy loading nativo
        const script = document.createElement('script');
        script.src = 'https://cdnjs.cloudflare.com/ajax/libs/lazysizes/5.3.2/lazysizes.min.js';
        document.body.appendChild(script);
    }
}

/**
 * Inicializa el menú desplegable de usuario
 */
function initUserDropdownMenu() {
    const menuButton = document.getElementById('user-menu-button');
    const menuContainer = document.getElementById('user-menu-container');
    const menuDropdown = document.getElementById('user-menu-dropdown');
    
    if (menuButton && menuDropdown && menuContainer) {
        let isOpen = false;
        let timeoutId;
        
        // Función para abrir el menú
        function openMenu() {
            clearTimeout(timeoutId); // Limpiar cualquier timeout pendiente
            menuDropdown.classList.remove('hidden');
            isOpen = true;
        }
        
        // Función para cerrar el menú con un pequeño retraso
        function closeMenuWithDelay() {
            timeoutId = setTimeout(() => {
                menuDropdown.classList.add('hidden');
                isOpen = false;
            }, 300); // 300ms de retraso antes de cerrar
        }
        
        // Abrir/cerrar al hacer clic en el botón
        menuButton.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            if (isOpen) {
                menuDropdown.classList.add('hidden');
                isOpen = false;
            } else {
                openMenu();
            }
        });
        
        // Manejar hover sobre el contenedor
        menuContainer.addEventListener('mouseenter', openMenu);
        menuContainer.addEventListener('mouseleave', closeMenuWithDelay);
        
        // Mantener abierto cuando el mouse está sobre el menú desplegable
        menuDropdown.addEventListener('mouseenter', function() {
            clearTimeout(timeoutId); // Cancelar el cierre si el mouse entra al dropdown
        });
        
        menuDropdown.addEventListener('mouseleave', closeMenuWithDelay);
        
        // Cerrar al hacer clic fuera
        document.addEventListener('click', function(e) {
            if (isOpen && !menuContainer.contains(e.target)) {
                menuDropdown.classList.add('hidden');
                isOpen = false;
            }
        });
    }
}

