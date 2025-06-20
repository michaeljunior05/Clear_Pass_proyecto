// frontend/static/js/main.js

/**
 * @file main.js
 * @description Punto de entrada principal para la aplicación frontend.
 * Coordina la inicialización de los diferentes módulos.
 */

// Eliminar initializeGoogleSignIn de la importación
import { initializeAuthForms } from './auth.js'; 
import { initializeProductsPage, initializeProductDetailPage } from './products.js';

/**
 * Inicializa la lógica específica de la página de inicio.
 * Contiene el scroll suave. El efecto parallax ahora es manejado por CSS nativo en el body.
 */
function initializeHomePage() {
    console.log("main.js: Inicializando lógica para la página de Inicio.");

    // Funcionalidad del botón "¿Quiénes somos?" (scroll suave)
    const btnQuienesSomos = document.querySelector("a[href='#quienes-somos']");
    const sectionQuienesSomos = document.getElementById("quienes-somos");

    if (btnQuienesSomos && sectionQuienesSomos) {
        btnQuienesSomos.addEventListener("click", function(event) {
            event.preventDefault(); // Previene el comportamiento de ancla por defecto
            sectionQuienesSomos.scrollIntoView({ behavior: "smooth" });
        });
    }
}

// Cuando el DOM esté completamente cargado, inicializar los módulos pertinentes.
document.addEventListener('DOMContentLoaded', () => {
    console.log("main.js: DOMContentLoaded disparado."); 

    // Las funciones de autenticación pueden necesitar inicializarse en varias páginas
    initializeAuthForms();
    // ELIMINAR LA LLAMADA A initializeGoogleSignIn(); YA NO SE EXPORTA NI SE NECESITA
    // initializeGoogleSignIn(); 

    // La lógica de productos y detalles solo se inicializa en sus respectivas páginas.
    if (window.location.pathname === '/productos') {
        console.log("main.js: Inicializando lógica para /productos."); 
        initializeProductsPage();
    } else if (window.location.pathname.startsWith('/product/')) {
        console.log("main.js: Inicializando lógica para /product/detail."); 
        initializeProductDetailPage();
    } else if (window.location.pathname === '/') { // Llamar a la lógica de la página de inicio
        initializeHomePage();
    } else {
        console.log("main.js: Ruta no reconocida para lógica específica."); 
    }

    // Lógica para el menú hamburguesa (universal en el header)
    const menuButton = document.getElementById('menu-button');
    const mainNav = document.getElementById('main-nav');

    if (menuButton && mainNav) {
        menuButton.addEventListener('click', () => {
            mainNav.classList.toggle('hidden'); // Alternar la visibilidad de Tailwind
            mainNav.classList.toggle('active'); // Alternar nuestra clase CSS si hay estilos en home.css que la usen
        });
    }
});
