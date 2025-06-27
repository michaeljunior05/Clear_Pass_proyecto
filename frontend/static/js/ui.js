// frontend/static/js/ui.js

/**
 * Muestra un mensaje de notificación en la UI.
 * @param {string} message - El texto del mensaje.
 * @param {'success' | 'error' | 'info'} type - Tipo de mensaje para aplicar estilos.
 */
export function showMessage(message, type = 'info') {
    let messageContainer = document.getElementById('message-container');
    if (!messageContainer) {
        const body = document.querySelector('body');
        const container = document.createElement('div');
        container.id = 'message-container';
        container.classList.add('fixed', 'top-4', 'right-4', 'z-50', 'space-y-2');
        body.appendChild(container);
        messageContainer = container;
    }

    const messageElement = document.createElement('div');
    messageElement.classList.add(
        'p-3', 'rounded-md', 'shadow-lg', 'text-white', 'text-sm',
        'flex', 'items-center', 'space-x-2', 'opacity-0', 'transition-opacity', 'duration-300'
    );

    let bgColor = 'bg-gray-700';
    let iconClass = 'fas fa-info-circle';

    if (type === 'success') {
        bgColor = 'bg-green-500';
        iconClass = 'fas fa-check-circle';
    } else if (type === 'error') {
        bgColor = 'bg-red-500';
        iconClass = 'fas fa-times-circle';
    }

    messageElement.classList.add(bgColor);
    messageElement.innerHTML = `<i class="${iconClass}"></i><span>${message}</span>`;

    messageContainer.appendChild(messageElement);

    setTimeout(() => {
        messageElement.classList.remove('opacity-0');
        messageElement.classList.add('opacity-100');
    }, 10); 

    setTimeout(() => {
        messageElement.classList.remove('opacity-100');
        messageElement.classList.add('opacity-0');
        messageElement.addEventListener('transitionend', () => messageElement.remove());
    }, 5000); 
}

// Lógica para los dropdowns y tooltips del header
document.addEventListener('DOMContentLoaded', () => {
    // Función genérica para manejar el toggle de dropdowns por clic
    const setupClickDropdown = (buttonId, dropdownId) => {
        const button = document.getElementById(buttonId);
        const dropdown = document.getElementById(dropdownId);

        if (button && dropdown) {
            console.log(`ui.js: Configurando dropdown para botón ${buttonId} y dropdown ${dropdownId}`);
            button.addEventListener('click', (event) => {
                event.stopPropagation(); 
                console.log(`ui.js: Clic en botón ${buttonId}. Toggleando dropdown ${dropdownId}.`);
                dropdown.classList.toggle('hidden');
                
                document.querySelectorAll('.relative > div.absolute').forEach(openDropdown => { 
                    const isDropdown = openDropdown.id === 'categorias-dropdown' || 
                                       openDropdown.id === 'ayuda-dropdown' || 
                                       openDropdown.id === 'mi-perfil-dropdown';
                    
                    if (openDropdown !== dropdown && isDropdown && !openDropdown.classList.contains('hidden')) {
                        console.log(`ui.js: Ocultando otro dropdown: ${openDropdown.id}`);
                        openDropdown.classList.add('hidden');
                    }
                });
            });

            document.addEventListener('click', (event) => {
                if (!dropdown.contains(event.target) && !button.contains(event.target) && !dropdown.classList.contains('hidden')) {
                    console.log(`ui.js: Clic fuera de ${buttonId} o ${dropdownId}. Ocultando dropdown.`);
                    dropdown.classList.add('hidden');
                }
            });
            document.addEventListener('keydown', (event) => {
                if (event.key === 'Escape' && !dropdown.classList.contains('hidden')) {
                    console.log(`ui.js: Tecla ESC presionada. Ocultando dropdown ${dropdownId}.`);
                    dropdown.classList.add('hidden');
                }
            });
        } else {
            console.warn(`ui.js: Botón (${buttonId}) o Dropdown (${dropdownId}) no encontrado. (Esto es esperado si no está en la página actual).`);
        }
    };

    setupClickDropdown('categorias-btn', 'categorias-dropdown');
    setupClickDropdown('ayuda-btn', 'ayuda-dropdown');
    setupClickDropdown('mi-perfil-btn', 'mi-perfil-dropdown');

    const cartIcon = document.getElementById('cart-icon');
    const cartTooltip = document.getElementById('cart-tooltip');
    if (cartIcon && cartTooltip) {
        cartIcon.addEventListener('mouseenter', () => {
            console.log("ui.js: Mouse enter en cart-icon. Mostrando tooltip.");
            cartTooltip.classList.remove('hidden');
        });
        cartIcon.addEventListener('mouseleave', () => {
            console.log("ui.js: Mouse leave en cart-icon. Ocultando tooltip.");
            cartTooltip.classList.add('hidden');
        });
        cartIcon.addEventListener('click', (e) => {
            e.preventDefault(); 
            console.log("ui.js: Clic en cart-icon. Toggleando tooltip.");
            cartTooltip.classList.toggle('hidden');
        });
    } else {
        console.warn("ui.js: Icono de carrito (cart-icon) o tooltip (cart-tooltip) no encontrado. (Esto es esperado si no está en la página actual).");
    }

    // --- Lógica para el botón de menú hamburguesa en móviles (CENTRALIZADO AQUÍ) ---
    const menuButton = document.getElementById('menu-button');
    const mainNav = document.getElementById('main-nav');
    if (menuButton && mainNav) {
        console.log("ui.js: Configurando botón de menú hamburguesa y navegación principal.");
        menuButton.addEventListener('click', () => {
            console.log("ui.js: Clic en menu-button. Toggleando main-nav.");
            mainNav.classList.toggle('hidden'); // Solo toggleamos la clase 'hidden'
            console.log("ui.js: Clase 'hidden' en main-nav después del toggle:", mainNav.classList.contains('hidden') ? 'presente' : 'ausente'); // Debug log
            
            // Cerrar todos los dropdowns al abrir el menú móvil
            document.querySelectorAll('.relative > div.absolute').forEach(openDropdown => {
                const isDropdown = openDropdown.id === 'categorias-dropdown' || 
                                   openDropdown.id === 'ayuda-dropdown' || 
                                   openDropdown.id === 'mi-perfil-dropdown';
                if (isDropdown && !openDropdown.classList.contains('hidden')) {
                    console.log(`ui.js: Ocultando dropdown '${openDropdown.id}' al abrir menú hamburguesa.`);
                    openDropdown.classList.add('hidden');
                }
            });
        });
        // Cerrar el menú si se hace clic fuera en móvil (solo si el menú está visible)
        document.addEventListener('click', (event) => {
            // Asegurarse de que el menú móvil está visible y que el clic NO fue en el botón del menú ni dentro del menú
            if (window.getComputedStyle(mainNav).display !== 'none' && !mainNav.classList.contains('hidden') && 
                !mainNav.contains(event.target) && !menuButton.contains(event.target)) {
                console.log("ui.js: Clic fuera de main-nav o menu-button. Ocultando main-nav.");
                mainNav.classList.add('hidden');
            }
        });
    } else {
        console.warn("ui.js: Botón de menú (menu-button) o main-nav no encontrado. (Esto es esperado si no está en la página actual).");
    }
});
