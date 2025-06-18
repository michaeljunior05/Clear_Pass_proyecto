/**
 * @file script.js
 * @description Centraliza la lógica del frontend para la autenticación (login, registro, Google Sign-In),
 * búsqueda de productos, filtrado por categorías, paginación y visualización de detalles.
 * Sigue el principio de Responsabilidad Única (SRP) en sus funciones individuales
 * y cohesión para la gestión de la interfaz de usuario.
 */

// --- FUNCIONES GLOBALES (ACCESIBLES DESDE CUALQUIER PARTE DEL SCRIPT) ---

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

/**
 * Función para manejar la respuesta del código de autorización de Google.
 * Esta función es un callback invocado por la librería GSI.
 * @param {Object} response - Objeto de respuesta de Google que contiene el código de autorización.
 */
async function handleGoogleAuthCode(response) {
    console.log("Respuesta de Google Auth Code recibida:", response);
    const code = response.code;

    if (code) {
        console.log("Enviando código de Google a /api/auth/google/callback...");
        try {
            const fetchResponse = await fetch('/api/auth/google/callback', {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                body: new URLSearchParams({ code }),
            });
            const data = await fetchResponse.json();

            if (fetchResponse.ok) {
                showMessage('Inicio de sesión con Google exitoso. Redirigiendo...', 'success');
                console.log('Inicio de sesión con Google exitoso (backend response):', data);
                window.location.href = '/productos'; 
            } else {
                showMessage(data.message || 'Error al iniciar sesión con Google', 'error');
                console.error('Error en el inicio de sesión con Google (backend error):', data);
            }
        } catch (error) {
            console.error('Error de red al intentar enviar el código de Google al backend:', error);
            showMessage('Error de red al intentar iniciar sesión con Google', 'error');
        }
    } else {
        console.error("No se recibió el código de autorización de Google. Respuesta:", response);
        showMessage('Error al iniciar sesión con Google: No se obtuvo el código de autorización.', 'error');
    }
}


// --- LISTENERS DE EVENTOS PRINCIPALES ---

document.addEventListener('DOMContentLoaded', async () => { 

    // --- Lógica de Autenticación (Login y Registro) para formularios normales ---
    const loginForm = document.getElementById('login-form');
    const registerForm = document.getElementById('register-form');


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
                    window.location.href = '/productos'; 
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
                    // MODIFICADO AQUÍ: Mostrar mensaje y redirigir
                    showMessage(data.message || 'Registro exitoso. Redirigiendo para iniciar sesión.', 'success');
                    console.log('Registro exitoso:', data);
                    // Redirigir a la página de login después de un breve retraso
                    setTimeout(() => {
                        window.location.href = '/login'; 
                    }, 1500); // Dar tiempo al usuario para ver el mensaje
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

    // --- Lógica Específica para la Página de Productos (`/productos`) y detalles (`/product/`) ---
    if (window.location.pathname === '/productos' || window.location.pathname.startsWith('/product/')) {
        const searchForm = document.querySelector('.search-form');
        const searchInput = document.getElementById('search-input');
        const productList = document.getElementById('product-list'); 
        const paginationControls = document.getElementById('pagination-controls');
        const prevPageButton = document.getElementById('prev-page');
        const nextPageButton = document.getElementById('next-page');
        const pageNumbersContainer = document.getElementById('page-numbers');
        const categoriesButton = document.getElementById('categories-button');
        const categoriesDropdown = document.getElementById('categories-dropdown');
        const productDetailContainer = document.querySelector('.product-detail-container'); 

        let currentPage = 1;
        const productsPerPage = 10;
        let totalPages = 1;
        let currentSearchTerm = '';
        let currentCategory = ''; 

        async function loadProducts(searchTerm = '', category = '', page = 1, limit = productsPerPage) {
            if (!productList) { 
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

                const responseData = await response.json(); 
                const productsData = responseData.products;
                totalPages = responseData.total_pages;

                productList.innerHTML = ''; 

                if (productsData && productsData.length > 0) {
                    productsData.forEach(product => {
                        const productItem = document.createElement('div');
                        productItem.classList.add('product-item');
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
                updatePaginationControls(); 
            } catch (error) {
                console.error('Error al cargar productos:', error);
                productList.innerHTML = `<p class="error-message">Error al cargar productos: ${error.message}. Por favor, inténtalo de nuevo.</p>`;
            }
        }

        function updatePaginationControls() {
            if (!paginationControls) return;

            prevPageButton.disabled = currentPage === 1;
            nextPageButton.disabled = currentPage === totalPages || totalPages === 0; 

            pageNumbersContainer.innerHTML = '';
            const maxPageButtons = 5; 
            let startPage = Math.max(1, currentPage - Math.floor(maxPageButtons / 2));
            let endPage = Math.min(totalPages, startPage + maxPageButtons - 1);

            if (endPage - startPage + 1 < maxPageButtons) {
                startPage = Math.max(1, endPage - maxPageButtons + 1);
            }
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
                    const newUrl = new URL(window.location.href);
                    newUrl.searchParams.set('page', i);
                    window.history.pushState({ path: newUrl.href }, '', newUrl.href);
                });
                pageNumbersContainer.appendChild(pageButton);
            }
        }

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

        if (searchForm) { 
            searchForm.addEventListener('submit', function(event) {
                event.preventDefault();
                const searchTerm = searchInput.value;
                loadProducts(searchTerm, '', 1, productsPerPage); 
                const newUrl = new URL(window.location.href);
                newUrl.searchParams.set('query', searchTerm);
                newUrl.searchParams.delete('category'); 
                newUrl.searchParams.set('page', '1');
                window.history.pushState({ path: newUrl.href }, '', newUrl.href);
            });
        }

        if (categoriesButton) { 
            loadCategories(); 

            categoriesButton.addEventListener('click', (event) => {
                event.stopPropagation(); 
                categoriesDropdown.classList.toggle('show');
                categoriesButton.classList.toggle('active'); 
            });

            document.addEventListener('click', (event) => {
                if (categoriesDropdown && categoriesDropdown.classList.contains('show') && !categoriesDropdown.contains(event.target) && event.target !== categoriesButton && !categoriesButton.contains(event.target)) {
                    categoriesDropdown.classList.remove('show');
                    categoriesButton.classList.remove('active'); 
                }
            });
        }

        async function loadCategories() {
            if (!categoriesDropdown) return;
            categoriesDropdown.innerHTML = '<p class="loading-categories">Cargando categorías...</p>'; 

            try {
                const response = await fetch('/api/products/categories');
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                const categories = await response.json();

                categoriesDropdown.innerHTML = ''; 

                if (categories && categories.length > 0) {
                    const allCategoriesLink = document.createElement('a');
                    allCategoriesLink.href = '#';
                    allCategoriesLink.textContent = 'Todas las categorías';
                    allCategoriesLink.addEventListener('click', (e) => {
                        e.preventDefault();
                        loadProducts(currentSearchTerm, '', 1, productsPerPage); 
                        categoriesDropdown.classList.remove('show');
                        categoriesButton.classList.remove('active'); 
                        const newUrl = new URL(window.location.href);
                        newUrl.searchParams.delete('category');
                        newUrl.searchParams.set('page', '1');
                        window.history.pushState({ path: newUrl.href }, '', newUrl.href);
                    });
                    categoriesDropdown.appendChild(allCategoriesLink);


                    categories.forEach(category => {
                        const categoryLink = document.createElement('a');
                        categoryLink.href = `#`; 
                        categoryLink.textContent = category.charAt(0).toUpperCase() + category.slice(1); 
                        categoryLink.addEventListener('click', (e) => {
                            e.preventDefault();
                            loadProducts('', category, 1, productsPerPage); 
                            if (searchInput) searchInput.value = ''; 
                            categoriesDropdown.classList.remove('show'); 
                            categoriesButton.classList.remove('active'); 
                            const newUrl = new URL(window.location.href);
                            newUrl.searchParams.set('category', category);
                            newUrl.searchParams.delete('query'); 
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


        if (window.location.pathname.startsWith('/product/')) {
            const productId = window.location.pathname.split('/').pop(); 
            console.log(`Cargando detalles para el producto ID: ${productId}`);
            
            if (productDetailContainer) { 
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
                            <img src="${product.image_url}" alt="${product.name}" class="product-image"
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

        if (window.location.pathname === '/productos' && productList) {
            const urlParams = new URLSearchParams(window.location.search);
            const initialSearchQuery = urlParams.get('query') || '';
            const initialCategory = urlParams.get('category') || '';
            const initialPage = parseInt(urlParams.get('page')) || 1;

            if (searchInput) searchInput.value = initialSearchQuery; 
            
            loadProducts(initialSearchQuery, initialCategory, initialPage, productsPerPage);
        }
    }
});

// AÑADIDO: Listener para window.onload para la inicialización del botón de Google
window.addEventListener('load', () => {
    // Asegúrate de que el ID del botón es 'googleSignIn' en tu HTML
    const googleSignInButton = document.getElementById('googleSignIn'); 
    const googleClientId = '967793497246-m78gm3m77u9ebqgpev7h10op0lbpqepg.apps.googleusercontent.com'; 

    if (googleSignInButton) {
        if (typeof google !== 'undefined' && google.accounts && google.accounts.oauth2) {
            const client = google.accounts.oauth2.initCodeClient({
                client_id: googleClientId,
                scope: 'openid email profile',
                redirect_uri: 'https://127.0.0.1:5000/api/auth/google/callback', // AHORA ES HTTPS
                ux_mode: 'popup', 
                callback: handleGoogleAuthCode 
                // Elimina o comenta si existe: auto_select: true,
            });

            // Mover client.requestCode() DENTRO del listener de clic del botón
            googleSignInButton.addEventListener('click', () => {
                console.log("Botón de Google clickeado. Solicitando código...");
                client.requestCode({
                    redirect_uri: 'https://127.0.0.1:5000/api/auth/google/callback' // Asegurar que es HTTPS
                });
            });
        } else {
            console.warn("Google API client no cargado. El botón de inicio de sesión de Google podría no funcionar.");
        }
    }
});
