// frontend/static/js/main.js

// Importa las funciones de inicialización de otros módulos JS
// CORREGIDO: initializeAuthPage a initializeAuthForms
import { initializeAuthForms } from './auth.js'; 
import { initializeProductsPage, initializeProductDetailPage } from './products.js';
import { showMessage } from './ui.js'; 

/**
 * Inicializa la lógica JavaScript para la página principal (home.html).
 * Maneja la barra de búsqueda para redirigir a la página de productos.
 */
function initializeHomePage() {
    console.log("main.js: Inicializando lógica para la página principal.");
    const homeSearchInput = document.getElementById('search-input');
    const homeSearchButton = document.getElementById('search-button');

    if (homeSearchInput && homeSearchButton) {
        console.log("main.js: Elementos de búsqueda encontrados en home.html.");

        const performSearchRedirect = (event) => {
            if (event) {
                event.preventDefault(); // Evita el comportamiento predeterminado del formulario o botón
            }
            const query = homeSearchInput.value.trim();
            if (query) {
                console.log(`main.js: Redirigiendo a /productos con query: ${query}`);
                window.location.href = `/productos?query=${encodeURIComponent(query)}`;
            } else {
                console.log("main.js: Búsqueda vacía, redirigiendo a /productos sin query.");
                window.location.href = `/productos`; // Redirige sin query si está vacío
            }
        };

        // Event listener para el clic en el botón de búsqueda
        homeSearchButton.addEventListener('click', performSearchRedirect);

        // Event listener para la tecla Enter en el input de búsqueda
        homeSearchInput.addEventListener('keypress', (event) => {
            if (event.key === 'Enter') {
                performSearchRedirect(event);
            }
        });
    } else {
        console.warn("main.js: No se encontraron elementos de búsqueda en home.html (search-input o search-button).");
    }
}

/**
 * Inicializa la página de FAQ.
 */
function initializeFaqPage() {
    console.log("main.js: Inicializando página de FAQ.");
    // Lógica específica para la página de FAQ (si la hay)
}

/**
 * Inicializa la página de Contacto.
 */
function initializeContactPage() {
    console.log("main.js: Inicializando página de Contacto.");
    // Lógica específica para la página de Contacto (si la hay)
}

/**
 * Inicializa la página de Compras.
 */
function initializePurchasesPage() {
    console.log("main.js: Inicializando página de Compras.");
    // Lógica específica para la página de Compras (si la hay)
}

/**
 * Inicializa la página de Perfil.
 */
function initializeProfilePage() {
    console.log("main.js: Inicializando página de Perfil.");
    // Lógica específica para la página de Perfil (si la hay)
}

/**
 * Inicializa la página de Historial.
 */
function initializeHistoryPage() {
    console.log("main.js: Inicializando página de Historial.");
    // Lógica específica para la página de Historial (si la hay)
}

/**
 * Inicializa la página de Créditos.
 */
function initializeCreditsPage() {
    console.log("main.js: Inicializando página de Créditos.");
    // Lógica específica para la página de Créditos (si la hay)
}


// Se ejecuta cuando el DOM está completamente cargado.
document.addEventListener('DOMContentLoaded', () => {
    const path = window.location.pathname;
    console.log(`main.js: DOMContentLoaded. Ruta actual: ${path}`);

    // Determina qué función de inicialización llamar según la ruta
    if (path === '/login' || path === '/register') {
        // CORREGIDO: initializeAuthPage a initializeAuthForms
        initializeAuthForms(); 
    } else if (path === '/productos') {
        initializeProductsPage();
    } else if (path.startsWith('/product/')) {
        initializeProductDetailPage();
    } else if (path === '/faq') {
        initializeFaqPage();
    } else if (path === '/contact') {
        initializeContactPage();
    } else if (path === '/purchases') {
        initializePurchasesPage();
    } else if (path === '/perfil') {
        initializeProfilePage();
    } else if (path === '/history') {
        initializeHistoryPage();
    } else if (path === '/credits') {
        initializeCreditsPage();
    } else if (path === '/') { // La página principal
        initializeHomePage();
    } else {
        console.warn(`main.js: No hay lógica de inicialización específica para la ruta: ${path}`);
    }
});
