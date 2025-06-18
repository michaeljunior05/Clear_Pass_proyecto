    // frontend/static/js/products.js

    /**
     * @file products.js
     * @description Centraliza la lógica de carga, búsqueda, paginación y visualización de productos.
     */

    import { showMessage } from './ui.js'; 

    // Variables de estado para la paginación y filtros
    let currentPage = 1;
    const productsPerPage = 10;
    let totalPages = 1;
    let currentSearchTerm = '';
    let currentCategory = ''; 

    // Referencias a elementos del DOM (se inicializan en las funciones de inicialización)
    let productList, paginationControls, prevPageButton, nextPageButton, pageNumbersContainer;
    let searchForm, searchInput, categoriesButton, categoriesDropdown;
    let productDetailContainer;

    /**
     * Carga y muestra productos según los filtros y la paginación.
     * @param {string} searchTerm - Término de búsqueda.
     * @param {string} category - Categoría de productos.
     * @param {number} page - Número de página actual.
     * @param {number} limit - Límite de productos por página.
     */
    async function loadProducts(searchTerm = '', category = '', page = 1, limit = productsPerPage) {
        console.log(`products.js: Iniciando loadProducts con searchTerm='${searchTerm}', category='${category}', page=${page}.`); // Nuevo log
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
            console.log(`products.js: Realizando fetch a ${url}`); // Nuevo log
            
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
            console.error('products.js: Error al cargar productos:', error); // Log actualizado
            productList.innerHTML = `<p class="error-message">Error al cargar productos: ${error.message}. Por favor, inténtalo de nuevo.</p>`;
        }
    }

    /**
     * Actualiza los controles de paginación (botones Anterior, Siguiente y números de página).
     */
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

    /**
     * Carga y muestra las categorías de productos disponibles.
     */
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
            console.error('products.js: Error al cargar categorías:', error); // Log actualizado
            categoriesDropdown.innerHTML = `<p style="padding: 10px; color: red;">Error al cargar categorías.</p>`;
        }
    }


    /**
     * Inicializa la lógica para la página de productos.
     */
    export function initializeProductsPage() {
        console.log("products.js: Inicializando products page."); // Nuevo log
        // Asignar referencias a los elementos del DOM
        searchForm = document.querySelector('.search-form');
        searchInput = document.getElementById('search-input');
        productList = document.getElementById('product-list'); 
        paginationControls = document.getElementById('pagination-controls');
        prevPageButton = document.getElementById('prev-page');
        nextPageButton = document.getElementById('next-page');
        pageNumbersContainer = document.getElementById('page-numbers');
        categoriesButton = document.getElementById('categories-button');
        categoriesDropdown = document.getElementById('categories-dropdown');
        
        // Listener para el botón de página anterior
        if (prevPageButton) {
            prevPageButton.addEventListener('click', () => {
                if (currentPage > 1) {
                    loadProducts(currentSearchTerm, currentCategory, currentPage - 1, productsPerPage);
                }
            });
        }

        // Listener para el botón de página siguiente
        if (nextPageButton) {
            nextPageButton.addEventListener('click', () => {
                if (currentPage < totalPages) {
                    loadProducts(currentSearchTerm, currentCategory, currentPage + 1, productsPerPage);
                }
            });
        }

        // Listener para el formulario de búsqueda
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

        // Lógica para el botón de categorías
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

        // Carga inicial de productos al entrar a la página
        const urlParams = new URLSearchParams(window.location.search);
        const initialSearchQuery = urlParams.get('query') || '';
        const initialCategory = urlParams.get('category') || '';
        const initialPage = parseInt(urlParams.get('page')) || 1;

        if (searchInput) searchInput.value = initialSearchQuery; 
        
        loadProducts(initialSearchQuery, initialCategory, initialPage, productsPerPage);
    }

    /**
     * Inicializa la lógica para la página de detalles de producto.
     */
    export async function initializeProductDetailPage() {
        console.log("products.js: Inicializando product detail page."); // Nuevo log
        productDetailContainer = document.querySelector('.product-detail-container'); 
        const productId = window.location.pathname.split('/').pop(); 
        console.log(`products.js: Cargando detalles para el producto ID: ${productId}`); // Log actualizado
        
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
                    const addToCartButton = productDetailContainer.querySelector('.add-to-cart-detail-button');
                    if (addToCartButton) {
                        addToCartButton.addEventListener('click', () => {
                            showMessage('Funcionalidad de añadir al carrito aún no implementada.', 'info');
                        });
                    }
                }

            } catch (error) {
                console.error('products.js: Error al cargar detalles del producto:', error); // Log actualizado
                if (productDetailContainer) productDetailContainer.innerHTML = `<p class="error-message">Error al cargar detalles: ${error.message}.</p>`;
            }
        } else {
            if (productDetailContainer) productDetailContainer.innerHTML = '<p>ID de producto no proporcionado.</p>';
        }
    }
    