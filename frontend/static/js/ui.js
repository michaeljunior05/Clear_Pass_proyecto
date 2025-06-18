// frontend/static/js/ui.js

/**
 * @file ui.js
 * @description Contiene funciones de utilidad para la interfaz de usuario.
 */

/**
 * Muestra un mensaje temporal al usuario en la parte superior de la pantalla.
 * @param {string} message - El texto del mensaje a mostrar.
 * @param {'info' | 'success' | 'error'} type - El tipo de mensaje para aplicar estilos (info, success, error).
 * @param {number} duration - Duración en milisegundos que el mensaje estará visible (por defecto 3000ms).
 */
export function showMessage(message, type = 'info', duration = 3000) {
    let messageContainer = document.getElementById('app-message-container');
    if (!messageContainer) {
        messageContainer = document.createElement('div');
        messageContainer.id = 'app-message-container';
        Object.assign(messageContainer.style, {
            position: 'fixed',
            top: '20px',
            left: '50%',
            transform: 'translateX(-50%)',
            padding: '15px 25px',
            borderRadius: '8px',
            zIndex: '1000',
            textAlign: 'center',
            boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
            fontSize: '16px',
            color: '#fff',
            opacity: '0',
            transition: 'opacity 0.3s ease-in-out',
            fontFamily: 'Inter, sans-serif'
        });
        document.body.appendChild(messageContainer);
    }

    messageContainer.innerHTML = '';
    messageContainer.style.opacity = '0'; // Ocultar para resetear la transición

    if (type === 'success') {
        messageContainer.style.backgroundColor = '#4CAF50'; // Verde
    } else if (type === 'error') {
        messageContainer.style.backgroundColor = '#f44336'; // Rojo
    } else {
        messageContainer.style.backgroundColor = '#2196F3'; // Azul (info)
    }

    messageContainer.textContent = message;
    // Pequeño retardo para asegurar que la transición de opacidad funcione al reaparecer
    setTimeout(() => {
        messageContainer.style.opacity = '1';
    }, 50);

    setTimeout(() => {
        messageContainer.style.opacity = '0';
        setTimeout(() => {
            if (messageContainer.parentNode) {
                messageContainer.parentNode.removeChild(messageContainer);
            }
        }, 300); // Debe coincidir con la duración de la transición de opacidad a 0
    }, duration);
}
