/**
 * @file script.js
 * @description Centraliza la lógica del frontend para la autenticación (login, registro, Google Sign-In),
 * búsqueda de productos, filtrado por categorías, paginación y visualización de detalles.
 * Sigue el principio de Responsabilidad Única (SRP) en sus funciones individuales
 * y cohesión para la gestión de la interfaz de usuario.
 */

document.addEventListener('DOMContentLoaded', () => {

    // --- Función de Utilidad: Mostrar Mensajes al Usuario ---
    /**
     * Muestra un mensaje temporal al usuario en la parte superior de la pantalla.
     * @param {string} message - El texto del mensaje a mostrar.
     * @param {'info' | 'success' | 'error'} type - El tipo de mensaje para aplicar estilos (info, success, error).
     * @param {number} duration - Duración en milisegundos que el mensaje estará visible (por defecto 3000ms).
     */
    function showMessage(message, type = 'info', duration = 3000) {
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

    // --- Lógica de Autenticación (Login y Registro) ---
    const loginForm = document.getElementById('login-form');
    const registerForm = document.getElementById('register-form');
    const googleSignInButton = document.getElementById('googleSignIn');
    // Asegúrate de que este Client ID es correcto para tu configuración de Google
    const googleClientId = '222270840199-pcntooj9dsvmsn79j11glth1fueaurij.apps.googleusercontent.com'; 

    if (loginForm) {
        loginForm.addEventListener('submit', async (event) => {
            event.preventDefault();
            const emailInput = loginForm.querySelector('input[name="email"]');
            const passwordInput = loginForm.querySelector('input[name="password"]');
            const email = emailInput.value;
            const password = passwordInput.value;

            try {
                const response = await fetch('/api/login', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                    body: new URLSearchParams({ email, password }),
                });
                const data = await response.json();

                if (response.ok) {
                    showMessage('Inicio de sesión exitoso. Redirigiendo...', 'success');
                    console.log('Inicio de sesión exitoso:', data);
                    window.location.href = '/productos'; // Redirige a la página de productos
                } else {
                    showMessage(data.message || 'Error al iniciar sesión', 'error');
                    console.error('Error en el inicio de sesión:', data);
                }
            } catch (error) {
                console.error('Error de red:', error);
                showMessage('Error de red al intentar iniciar sesión', 'error');
            }
        });
    }

    if (registerForm) {
        registerForm.addEventListener('submit', async (event) => {
            event.preventDefault();
            const emailInput = registerForm.querySelector('input[name="email"]');
            const passwordInput = registerForm.querySelector('input[name="password"]');
            const confirmPasswordInput = registerForm.querySelector('input[name="confirm_password"]');
            const email = emailInput.value;
            const password = passwordInput.value;
            const confirmPassword = confirmPasswordInput.value;

            if (password !== confirmPassword) {
                showMessage('Las contraseñas no coinciden', 'error');
                return;
            }

            try {
                const response = await fetch('/api/register', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                    body: new URLSearchParams({ email, password, confirm_password }),
                });
                const data = await response.json();

                if (response.ok) {
                    showMessage(data.message || 'Registro exitoso. Redirigiendo para iniciar sesión.', 'success');
                    console.log('Registro exitoso:', data);
                    // REDIRECCIÓN INMEDIATA A LA PÁGINA DE INICIO DE SESIÓN
                    window.location.href = '/login'; 
                } else {
                    showMessage(data.message || 'Error al registrarse', 'error');
                    console.error('Error al registrarse:', data);
                }
            } catch (error) {
                console.error('Error de red:', error);
                showMessage('Error de red al intentar registrarse', 'error');
            }
        });
    }

    // Lógica de Google Sign-In
    if (googleSignInButton) {
        if (typeof google !== 'undefined' && google.accounts && google.accounts.oauth2) {
            const client = google.accounts.oauth2.initCodeClient({
                client_id: googleClientId,
                scope: 'openid email profile',
                // ¡IMPORTANTE! Esta URL debe coincidir con la URL de tu Blueprint en Flask
                redirect_uri: 'http://127.0.0.1:5000/api/auth/google/callback', 
            });
            googleSignInButton.addEventListener('click', () => {
                client.requestCode();
            });
        } else {
            console.warn("Google API client no cargado. El botón de inicio de sesión de Google podría no funcionar.");
        }
    }

    // Manejo del callback de Google al cargar la ventana
    window.addEventListener('load', async () => {
        const urlParams = new URLSearchParams(window.location.search);
        const code = urlParams.get('code');

        if (code) {
            console.log("Código de Google detectado en la URL. Procesando callback...");
            try {
                const response = await fetch('/api/auth/google/callback', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                    body: new URLSearchParams({ code }),
                });
                const data = await response.json();

                if (response.ok) {
                    showMessage('Inicio de sesión con Google exitoso. Redirigiendo...', 'success');
                    console.log('Inicio de sesión con Google exitoso:', data);
                    window.location.href = '/productos'; // Redirige a la página de productos
                } else {
                    showMessage(data.message || 'Error al iniciar sesión con Google', 'error');
                    console.error('Error en el inicio de sesión con Google:', data);
                }
            } catch (error) {
                console.error('Error de red al intentar iniciar sesión con Google:', error);
                showMessage('Error de red al intentar iniciar sesión con Google', 'error');
            }
            // Eliminar el código de la URL para evitar re-procesamiento y limpiar la URL
            urlParams.delete('code');
            const newUrl = `${window.location.pathname}${urlParams.toString() ? '?' + urlParams.toString() : ''}`;
            window.history.replaceState({}, document.title, newUrl);
        }
    });

    // --- Lógica Específica para la Página de Productos (`/productos`) ---
    // Esto se ejecuta solo si el pathname es '/productos' o '/product/...'
    if (window.location.pathname === '/productos' || window.location.pathname.startsWith('/product/')) {
        const searchForm = document.querySelector('.search-form');
        const searchInput = document.getElementById('search-input');
        const productList = document.getElementById('product-list'); // Usamos ID para ser más específicos
        const paginationControls = document.getElementById('pagination-controls');
        const prevPageButton = document.getElementById('prev-page');
        const nextPageButton = document.getElementById('next-page');
        const pageNumbersContainer = document.getElementById('page-numbers');
        const categoriesButton = document.getElementById('categories-button');
        const categoriesDropdown = document.getElementById('categories-dropdown');
        const productDetailContainer = document.querySelector('.product-detail-container'); // Para product_detail.html

        let currentPage = 1;
        const productsPerPage = 10;
        let totalPages = 1;
        let currentSearchTerm = '';
        let currentCategory = ''; // Para almacenar la categoría activa

        /**
         * Carga y muestra los productos desde la API, con soporte para búsqueda, filtrado y paginación.
         * Se ejecuta en la página `/productos`.
         * @param {string} searchTerm - Término de búsqueda.
         * @param {string} category - Categoría para filtrar.
         * @param {number} page - Número de página actual.
         * @param {number} limit - Cantidad de productos por página.
         */
        async function loadProducts(searchTerm = '', category = '', page = 1, limit = productsPerPage) {
            if (!productList) { // Asegura que el elemento exista en la página actual
                console.warn("Elemento 'product-list' no encontrado. Esto no es la página /productos.");
                return;
            }

            productList.innerHTML = '<p class="loading-message">Cargando productos...</p>';
            currentSearchTerm = searchTerm;
            currentCategory = category;
            currentPage = page;

            try {
                const params = new URLSearchParams();
                if (searchTerm) params.append('query', searchTerm);
                if (category) params.append('category', category);
                params.append('page', page);
                params.append('limit', limit);

                const url = `/api/products?${params.toString()}`;
                
                const response = await fetch(url, {
                    headers: { 'X-Requested-With': 'XMLHttpRequest' }
                });

                if (!response.ok) {
                    const errorData = await response.json().catch(() => ({ message: 'Error desconocido' }));
                    throw new Error(`HTTP error! status: ${response.status} - ${errorData.message || 'Error al obtener productos'}`);
                }

                const responseData = await response.json(); // Ahora esperamos un objeto con 'products' y 'total_pages'
                const productsData = responseData.products;
                totalPages = responseData.total_pages;

                productList.innerHTML = ''; // Limpiar mensaje de carga

                if (productsData && productsData.length > 0) {
                    productsData.forEach(product => {
                        const productItem = document.createElement('div');
                        productItem.classList.add('product-item');
                        // Atributo de datos para el ID del producto, útil para el detalle
                        productItem.dataset.productId = product.id; 

                        productItem.innerHTML = `
                            <img src="${product.image_url}" alt="${product.name}" class="product-image"
                                 onerror="this.onerror=null;this.src='https://placehold.co/200x200/cccccc/333333?text=No+Image';" >
                            <h3>${product.name}</h3>
                            <p>${product.description.substring(0, 100)}...</p>
                            <p class="product-price">$${product.price.toFixed(2)}</p>
                            <button class="view-details-button" data-product-id="${product.id}">Ver Detalles</button>
                        `;
                        productList.appendChild(productItem);
                    });
                    // Añadir event listeners para los botones de detalle después de que los productos se carguen
                    document.querySelectorAll('.view-details-button').forEach(button => {
                        button.addEventListener('click', (e) => {
                            const productId = e.target.dataset.productId;
                            if (productId) {
                                window.location.href = `/product/${productId}`;
                            }
                        });
                    });
                } else {
                    productList.innerHTML = '<p class="no-products-message">No se encontraron productos que coincidan con tu búsqueda o filtros.</p>';
                }
                updatePaginationControls(); // Actualizar los controles de paginación
            } catch (error) {
                console.error('Error al cargar productos:', error);
                productList.innerHTML = `<p class="error-message">Error al cargar productos: ${error.message}. Por favor, inténtalo de nuevo.</p>`;
            }
        }

        /**
         * Actualiza el estado y la visibilidad de los botones de paginación.
         * Se ejecuta en la página `/productos`.
         */
        function updatePaginationControls() {
            if (!paginationControls) return;

            prevPageButton.disabled = currentPage === 1;
            nextPageButton.disabled = currentPage === totalPages || totalPages === 0; // También deshabilitar si no hay páginas

            pageNumbersContainer.innerHTML = '';
            const maxPageButtons = 5; // Número máximo de botones de página a mostrar
            let startPage = Math.max(1, currentPage - Math.floor(maxPageButtons / 2));
            let endPage = Math.min(totalPages, startPage + maxPageButtons - 1);

            // Ajustar si la ventana de páginas es demasiado pequeña al final
            if (endPage - startPage + 1 < maxPageButtons) {
                startPage = Math.max(1, endPage - maxPageButtons + 1);
            }
            // Asegurarse de que al menos un botón de página se muestre si hay páginas
            if (totalPages > 0 && startPage === 0) startPage = 1;


            for (let i = startPage; i <= endPage; i++) {
                const pageButton = document.createElement('button');
                pageButton.textContent = i;
                pageButton.classList.add('page-number-button');
                if (i === currentPage) {
                    pageButton.classList.add('active');
                }
                pageButton.addEventListener('click', () => {
                    loadProducts(currentSearchTerm, currentCategory, i, productsPerPage);
                    // Actualiza la URL para reflejar la página
                    const newUrl = new URL(window.location.href);
                    newUrl.searchParams.set('page', i);
                    window.history.pushState({ path: newUrl.href }, '', newUrl.href);
                });
                pageNumbersContainer.appendChild(pageButton);
            }
        }

        // Event Listeners para Paginación (solo si estamos en /productos)
        if (prevPageButton) {
            prevPageButton.addEventListener('click', () => {
                if (currentPage > 1) {
                    loadProducts(currentSearchTerm, currentCategory, currentPage - 1, productsPerPage);
                }
            });
        }

        if (nextPageButton) {
            nextPageButton.addEventListener('click', () => {
                if (currentPage < totalPages) {
                    loadProducts(currentSearchTerm, currentCategory, currentPage + 1, productsPerPage);
                }
            });
        }

        // Manejar el envío del formulario de búsqueda (solo en productos.html)
        if (searchForm) { // searchForm existe solo en productos.html
            searchForm.addEventListener('submit', function(event) {
                event.preventDefault();
                const searchTerm = searchInput.value;
                
                // Cargar/filtrar productos (siempre en la página de productos)
                loadProducts(searchTerm, '', 1, productsPerPage); // Reiniciar a la primera página y sin categoría
                // Actualiza la URL para reflejar la búsqueda
                const newUrl = new URL(window.location.href);
                newUrl.searchParams.set('query', searchTerm);
                newUrl.searchParams.delete('category'); // Limpiar categoría al buscar
                newUrl.searchParams.set('page', '1');
                window.history.pushState({ path: newUrl.href }, '', newUrl.href);
            });
        }

        // Lógica para el botón de Categorías (solo en productos.html)
        if (categoriesButton) { // categoriesButton existe solo en productos.html
            loadCategories(); // Cargar categorías al inicio

            categoriesButton.addEventListener('click', (event) => {
                event.stopPropagation(); // Evita que el clic se propague al documento
                categoriesDropdown.classList.toggle('show');
                categoriesButton.classList.toggle('active'); // Para rotar el icono
            });

            // Cerrar el dropdown si se hace clic fuera de él
            document.addEventListener('click', (event) => {
                if (categoriesDropdown && categoriesDropdown.classList.contains('show') && !categoriesDropdown.contains(event.target) && event.target !== categoriesButton && !categoriesButton.contains(event.target)) {
                    categoriesDropdown.classList.remove('show');
                    categoriesButton.classList.remove('active'); // Restaurar icono
                }
            });
        }

        /**
         * Fetches and displays product categories in the dropdown.
         * Se ejecuta en la página `/productos`.
         */
        async function loadCategories() {
            if (!categoriesDropdown) return;
            categoriesDropdown.innerHTML = '<p class="loading-categories">Cargando categorías...</p>'; // Mensaje de carga

            try {
                const response = await fetch('/api/products/categories');
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                const categories = await response.json();

                categoriesDropdown.innerHTML = ''; // Limpiar mensaje de carga

                if (categories && categories.length > 0) {
                    // Añadir opción "Todas las categorías"
                    const allCategoriesLink = document.createElement('a');
                    allCategoriesLink.href = '#';
                    allCategoriesLink.textContent = 'Todas las categorías';
                    allCategoriesLink.addEventListener('click', (e) => {
                        e.preventDefault();
                        loadProducts(currentSearchTerm, '', 1, productsPerPage); // Cargar sin filtro de categoría
                        categoriesDropdown.classList.remove('show');
                        categoriesButton.classList.remove('active'); // Restaurar icono
                        // Actualiza la URL
                        const newUrl = new URL(window.location.href);
                        newUrl.searchParams.delete('category');
                        newUrl.searchParams.set('page', '1');
                        window.history.pushState({ path: newUrl.href }, '', newUrl.href);
                    });
                    categoriesDropdown.appendChild(allCategoriesLink);


                    categories.forEach(category => {
                        const categoryLink = document.createElement('a');
                        categoryLink.href = `#`; // Usaremos JS para el filtrado, no una URL de navegación
                        categoryLink.textContent = category.charAt(0).toUpperCase() + category.slice(1); // Capitalizar
                        categoryLink.addEventListener('click', (e) => {
                            e.preventDefault();
                            loadProducts('', category, 1, productsPerPage); // Buscar por categoría, resetear búsqueda y página
                            if (searchInput) searchInput.value = ''; // Limpiar la barra de búsqueda al seleccionar categoría
                            categoriesDropdown.classList.remove('show'); // Cerrar dropdown
                            categoriesButton.classList.remove('active'); // Restaurar icono
                            // Actualiza la URL para reflejar el filtro de categoría
                            const newUrl = new URL(window.location.href);
                            newUrl.searchParams.set('category', category);
                            newUrl.searchParams.delete('query'); // Limpiar query al filtrar por categoría
                            newUrl.searchParams.set('page', '1');
                            window.history.pushState({ path: newUrl.href }, '', newUrl.href);
                        });
                        categoriesDropdown.appendChild(categoryLink);
                    });
                } else {
                    categoriesDropdown.innerHTML = '<p style="padding: 10px; color: #777; font-style: italic;">No hay categorías disponibles.</p>';
                }
            } catch (error) {
                console.error('Error al cargar categorías:', error);
                categoriesDropdown.innerHTML = `<p style="padding: 10px; color: red;">Error al cargar categorías.</p>`;
            }
        }


        // --- Lógica de carga inicial para product_detail.html ---
        // Esto se ejecutará si la URL empieza con /product/
        if (window.location.pathname.startsWith('/product/')) {
            const productId = window.location.pathname.split('/').pop(); // Extrae el ID del último segmento de la URL
            console.log(`Cargando detalles para el producto ID: ${productId}`);
            
            if (productDetailContainer) { // Asegúrate de que el contenedor exista
                productDetailContainer.innerHTML = '<p>Cargando detalles del producto...</p>';
            }

            if (productId) {
                try {
                    const response = await fetch(`/api/products/${productId}`);
                    if (!response.ok) {
                        if (response.status === 404) {
                            if (productDetailContainer) productDetailContainer.innerHTML = '<p>Producto no encontrado o no es de una categoría tecnológica válida.</p>';
                        } else {
                            throw new Error(`HTTP error! status: ${response.status}`);
                        }
                        return;
                    }

                    const product = await response.json();

                    if (productDetailContainer) {
                        productDetailContainer.innerHTML = `
                            <img src="${product.image_url}" alt="${product.name}" class="product-detail-image"
                                 onerror="this.onerror=null;this.src='https://placehold.co/400x400/cccccc/333333?text=No+Image';">
                            <div class="product-detail-info">
                                <h1 class="product-detail-title">${product.name}</h1>
                                <p class="product-detail-category">Categoría: ${product.category}</p>
                                <p class="product-detail-origin">Origen: ${product.origin || 'No especificado'}</p>
                                <p class="product-detail-price">$${product.price.toFixed(2)}</p>
                                <p class="product-detail-description">${product.description}</p>
                                <div class="product-detail-rating">
                                    Calificación: ${product.rating.rate} <i class="fas fa-star"></i> (${product.rating.count} votos)
                                </div>
                                <button class="add-to-cart-detail-button">Añadir al Carrito</button>
                            </div>
                        `;
                        // Añadir evento para el botón "Añadir al Carrito" (implementación futura)
                        const addToCartButton = productDetailContainer.querySelector('.add-to-cart-detail-button');
                        if (addToCartButton) {
                            addToCartButton.addEventListener('click', () => {
                                showMessage('Funcionalidad de añadir al carrito aún no implementada.', 'info');
                            });
                        }
                    }

                } catch (error) {
                    console.error('Error al cargar detalles del producto:', error);
                    if (productDetailContainer) productDetailContainer.innerHTML = `<p class="error-message">Error al cargar detalles: ${error.message}.</p>`;
                }
            } else {
                if (productDetailContainer) productDetailContainer.innerHTML = '<p>ID de producto no proporcionado.</p>';
            }
        }

        // Carga inicial de productos para /productos
        if (window.location.pathname === '/productos' && productList) {
            const urlParams = new URLSearchParams(window.location.search);
            const initialSearchQuery = urlParams.get('query') || '';
            const initialCategory = urlParams.get('category') || '';
            const initialPage = parseInt(urlParams.get('page')) || 1;

            if (searchInput) searchInput.value = initialSearchQuery; // Rellena la barra de búsqueda si hay un query en la URL
            
            // Cargar los productos con los parámetros iniciales de la URL
            loadProducts(initialSearchQuery, initialCategory, initialPage, productsPerPage);
        }
    }
});
