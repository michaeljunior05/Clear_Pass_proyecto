// frontend/static/js/products.js

import { showMessage } from './ui.js'; // Asegúrate de que esta importación sea correcta

const API_BASE_URL = '/api';
let currentPage = 1;
const productsPerPage = 10;
let totalPages = 1; // Variable global para almacenar el total de páginas

/**
 * Función para cargar y mostrar productos.
 */
export async function loadProducts(query = '', category = '') {
    const productsContainer = document.getElementById('products-container');
    const paginationControls = document.getElementById('pagination-controls');
    const loadingIndicator = document.getElementById('loading-indicator');

    if (!productsContainer || !paginationControls || !loadingIndicator) {
        console.error("Elementos del DOM para productos no encontrados (container, paginación, indicador).");
        return;
    }

    productsContainer.innerHTML = '';
    loadingIndicator.classList.remove('hidden');
    showMessage('Cargando productos...', 'info');

    // Cambiado 'offset' a 'page' para que coincida con el backend
    let url = `${API_BASE_URL}/products?page=${currentPage}&limit=${productsPerPage}`; 
    if (query) {
        url += `&query=${encodeURIComponent(query)}`;
    }
    if (category) {
        url += `&category=${encodeURIComponent(category)}`;
    }

    console.log(`products.js: Fetching products from: ${url}`); // Debugging

    try {
        const response = await fetch(url);
        
        if (!response.ok) {
            const errorText = await response.text(); // Obtener texto de error si JSON falla
            let errorData = { message: 'Error desconocido' };
            try {
                errorData = JSON.parse(errorText);
            } catch (e) {
                // Si no es JSON, usamos el texto plano
                errorData.message = errorText; 
            }
            throw new Error(errorData.message || `Error HTTP: ${response.status} ${response.statusText}`);
        }

        const data = await response.json(); // <-- RENOMBRADO a 'data' para evitar confusión

        loadingIndicator.classList.add('hidden'); 

        // === INICIO DE LA CORRECCIÓN CLAVE ===
        const productsArray = data.products; // <-- Ahora obtenemos el array de productos de la propiedad 'products'
        totalPages = data.total_pages; // Actualizar el total de páginas global
        // === FIN DE LA CORRECCIÓN CLAVE ===

        if (!productsArray || productsArray.length === 0) {
            productsContainer.innerHTML = '<p class="text-gray-600 text-center col-span-full py-8">No se encontraron productos que coincidan con la búsqueda.</p>';
            showMessage('No se encontraron productos.', 'info');
            paginationControls.classList.add('hidden'); 
            return;
        }

        productsArray.forEach(product => { // <-- Ahora se llama forEach en productsArray
            const productCard = `
                <div class="bg-white rounded-lg shadow-md overflow-hidden transform transition-transform duration-300 hover:scale-105 cursor-pointer" onclick="window.location.href='/product/${product.id}'">
                    <img src="${product.image_url || 'https://placehold.co/400x300/e0e0e0/ffffff?text=No+Image'}" alt="${product.name}" class="w-full h-48 object-cover">
                    <div class="p-4">
                        <h3 class="font-semibold text-lg mb-2 truncate">${product.name}</h3>
                        <p class="text-gray-700 text-sm mb-2">${product.category}</p>
                        <p class="font-bold text-gray-900 text-xl">$${product.price ? product.price.toFixed(2) : 'N/A'}</p>
                    </div>
                </div>
            `;
            productsContainer.innerHTML += productCard;
        });

        paginationControls.classList.remove('hidden'); 
        updatePaginationButtons(); // Ya no necesita currentProductsCount, usa totalPages
        showMessage('Productos cargados exitosamente.', 'success');

    } catch (error) {
        loadingIndicator.classList.add('hidden');
        console.error('Error al cargar productos:', error);
        showMessage(`Error al cargar productos: ${error.message}. Por favor, inténtalo de nuevo.`, 'error');
        productsContainer.innerHTML = '<p class="text-red-600 text-center col-span-full py-8">Error al cargar productos. Por favor, verifica tu conexión o inténtalo más tarde.</p>';
    }
}

/**
 * Actualiza el estado de los botones de paginación.
 */
function updatePaginationButtons() { // Ya no necesita currentProductsCount
    const prevButton = document.getElementById('prev-page');
    const nextButton = document.getElementById('next-page');

    if (prevButton) {
        prevButton.disabled = currentPage === 1;
        prevButton.classList.toggle('opacity-50', currentPage === 1);
        prevButton.classList.toggle('cursor-not-allowed', currentPage === 1);
    }
    if (nextButton) {
        // Habilitar siguiente solo si la página actual es menor que el total de páginas
        nextButton.disabled = currentPage >= totalPages; 
        nextButton.classList.toggle('opacity-50', currentPage >= totalPages);
        nextButton.classList.toggle('cursor-not-allowed', currentPage >= totalPages);
    }
}

/**
 * Maneja el clic en el botón "Anterior".
 */
function goToPrevPage() {
    if (currentPage > 1) {
        currentPage--;
        loadProducts(document.getElementById('search-input')?.value || '', document.getElementById('category-filter')?.value || '');
    }
}

/**
 * Maneja el clic en el botón "Siguiente".
 */
function goToNextPage() {
    if (currentPage < totalPages) { // Solo avanza si no es la última página
        currentPage++;
        loadProducts(document.getElementById('search-input')?.value || '', document.getElementById('category-filter')?.value || '');
    }
}

/**
 * Inicializa la página de productos.
 */
export function initializeProductsPage() {
    console.log("products.js: Inicializando página de productos.");

    const searchForm = document.querySelector('.search-form');
    const searchInput = document.getElementById('search-input');
    const categoryFilter = document.getElementById('category-filter'); 

    if (searchForm) {
        searchForm.addEventListener('submit', (event) => {
            event.preventDefault();
            currentPage = 1; // Resetear a la primera página en cada nueva búsqueda
            const query = searchInput.value;
            const category = categoryFilter ? categoryFilter.value : ''; 
            loadProducts(query, category);
        });
    }

    const prevButton = document.getElementById('prev-page');
    const nextButton = document.getElementById('next-page');

    if (prevButton) {
        prevButton.addEventListener('click', goToPrevPage);
    }
    if (nextButton) {
        nextButton.addEventListener('click', goToNextPage);
    }

    // Cargar categorías al iniciar la página
    loadCategories();

    // Cargar productos iniciales (considerando parámetros de URL)
    const urlParams = new URLSearchParams(window.location.search);
    const initialQuery = urlParams.get('query');
    const initialCategory = urlParams.get('category');
    if (initialQuery || initialCategory) {
        if (searchInput) {
            searchInput.value = initialQuery || ''; 
        }
        if (categoryFilter) {
            categoryFilter.value = initialCategory || '';
        }
        loadProducts(initialQuery || '', initialCategory || '');
    } else {
        loadProducts(); 
    }
}

/**
 * Función para cargar categorías dinámicamente en el filtro.
 */
async function loadCategories() {
    const categoryFilter = document.getElementById('category-filter');
    if (!categoryFilter) {
        console.warn("Elemento 'category-filter' no encontrado, no se cargarán categorías.");
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/categories`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const categories = await response.json();

        // Limpiar opciones existentes (excepto la primera "Todas las categorías" si la tienes fija)
        categoryFilter.innerHTML = '<option value="">Todas las categorías</option>'; 
        
        categories.forEach(category => {
            const option = document.createElement('option');
            option.value = category;
            option.textContent = category;
            categoryFilter.appendChild(option);
        });
        console.log("Categorías cargadas:", categories);
    } catch (error) {
        console.error('Error al cargar categorías:', error);
        showMessage(`Error al cargar categorías: ${error.message}`, 'error');
    }
}


/**
 * Inicializa la página de detalles de un producto.
 */
export async function initializeProductDetailPage() {
    console.log("products.js: Inicializando página de detalles del producto.");
    const productId = window.location.pathname.split('/').pop();
    const productDetailContainer = document.getElementById('product-detail-container');
    const loadingIndicator = document.getElementById('detail-loading-indicator');

    if (!productDetailContainer || !loadingIndicator) {
        console.error("Contenedor de detalles del producto o indicador de carga no encontrados.");
        return;
    }

    loadingIndicator.classList.remove('hidden');
    showMessage('Cargando detalles del producto...', 'info');

    try {
        const response = await fetch(`${API_BASE_URL}/products/${productId}`);
        if (!response.ok) {
            const errorText = await response.text();
            let errorData = { message: 'Error desconocido' };
            try {
                errorData = JSON.parse(errorText);
            } catch (e) {
                errorData.message = errorText;
            }
            throw new Error(errorData.message || `Error HTTP: ${response.status} ${response.statusText}`);
        }
        const product = await response.json();

        loadingIndicator.classList.add('hidden');
        if (product) {
            const detailHtml = `
                <div class="flex flex-col md:flex-row bg-white rounded-lg shadow-xl p-6 md:p-8 space-y-6 md:space-y-0 md:space-x-8 max-w-4xl mx-auto">
                    <div class="md:w-1/2 flex justify-center items-center">
                        <img src="${product.image_url || 'https://placehold.co/600x400/e0e0e0/ffffff?text=No+Image'}" alt="${product.name}" class="max-w-full h-auto rounded-lg shadow-md">
                    </div>
                    <div class="md:w-1/2 space-y-4">
                        <h1 class="text-3xl md:text-4xl font-bold text-gray-800">${product.name}</h1>
                        <p class="text-xl text-primary-purple">${product.category}</p>
                        <p class="text-gray-700">${product.description}</p>
                        <p class="text-4xl font-extrabold text-gray-900">$${product.price ? product.price.toFixed(2) : 'N/A'}</p>
                        <button class="bg-primary-purple text-white px-6 py-3 rounded-md font-semibold hover:bg-register-button-hover transition duration-200 shadow-md">
                            Añadir al Carrito
                        </button>
                    </div>
                </div>
            `;
            productDetailContainer.innerHTML = detailHtml;
            showMessage('Detalles del producto cargados.', 'success');
        } else {
            productDetailContainer.innerHTML = '<p class="text-red-600 text-center py-8">Producto no encontrado.</p>';
            showMessage('Producto no encontrado.', 'error');
        }
    } catch (error) {
        loadingIndicator.classList.add('hidden');
        console.error('Error al cargar detalles del producto:', error);
        showMessage(`Error al cargar detalles: ${error.message}.`, 'error');
        productDetailContainer.innerHTML = '<p class="text-red-600 text-center py-8">Error al cargar detalles del producto.</p>';
    }
}
