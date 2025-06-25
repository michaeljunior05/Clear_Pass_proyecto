// frontend/static/js/ui.js

/**
 * Muestra un mensaje de notificación en la UI.
 * @param {string} message - El texto del mensaje.
 * @param {'success' | 'error' | 'info'} type - Tipo de mensaje para aplicar estilos.
 */
export function showMessage(message, type = 'info') {
    const messageContainer = document.getElementById('message-container');
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

// Lógica para los dropdowns del header
document.addEventListener('DOMContentLoaded', () => {
    // Función genérica para manejar el toggle de dropdowns
    const setupDropdown = (buttonId, dropdownId) => {
        const button = document.getElementById(buttonId);
        const dropdown = document.getElementById(dropdownId);

        if (button && dropdown) {
            // Manejar clic para mostrar/ocultar
            button.addEventListener('click', (event) => {
                event.stopPropagation(); // Evitar que el clic cierre inmediatamente
                dropdown.classList.toggle('hidden');
            });

            // Cerrar el dropdown si se hace clic fuera de él o de su botón
            document.addEventListener('click', (event) => {
                if (!dropdown.contains(event.target) && !button.contains(event.target)) {
                    dropdown.classList.add('hidden');
                }
            });

            // Para desktops, también permitir hover (opcional, pero común)
            button.addEventListener('mouseenter', () => dropdown.classList.remove('hidden'));
            button.addEventListener('mouseleave', (event) => {
                // Solo ocultar si el mouse no está sobre el dropdown mismo
                if (!dropdown.contains(event.relatedTarget)) {
                    dropdown.classList.add('hidden');
                }
            });
            dropdown.addEventListener('mouseleave', () => dropdown.classList.add('hidden'));

        }
    };

    // Configurar cada dropdown
    setupDropdown('categorias-btn', 'categorias-dropdown');
    setupDropdown('ayuda-btn', 'ayuda-dropdown');
    setupDropdown('mi-perfil-btn', 'mi-perfil-dropdown');

    // Lógica específica para el tooltip del carrito (solo al pasar el ratón)
    const cartIcon = document.getElementById('cart-icon');
    const cartTooltip = document.getElementById('cart-tooltip');
    if (cartIcon && cartTooltip) {
        cartIcon.addEventListener('mouseenter', () => {
            cartTooltip.classList.remove('hidden');
        });
        cartIcon.addEventListener('mouseleave', () => {
            cartTooltip.classList.add('hidden');
        });
    }

    // Lógica para el botón de menú hamburguesa en móviles
    const menuButton = document.getElementById('menu-button');
    const mainNav = document.getElementById('main-nav');
    if (menuButton && mainNav) {
        menuButton.addEventListener('click', () => {
            mainNav.classList.toggle('hidden');
            mainNav.classList.toggle('active'); // Usa esta clase si tienes transiciones CSS para móviles
        });
        // Cerrar el menú si se hace clic fuera en móvil (solo si el menú está visible)
        document.addEventListener('click', (event) => {
            if (!mainNav.contains(event.target) && !menuButton.contains(event.target) && !mainNav.classList.contains('hidden')) {
                mainNav.classList.add('hidden');
                mainNav.classList.remove('active');
            }
        });
    }
});
