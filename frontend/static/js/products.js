// frontend/static/js/products.js

import { showMessage } from './ui.js'; 

const API_BASE_URL = '/api'; 
let currentPage = 1; 
const productsPerPage = 10; // Este es el número de productos que mostramos por página en el frontend
let totalProducts = 0; // Este será el total de productos FILTRADOS que la API tiene
let currentCategory = ''; 
let currentSearchQuery = ''; 

// Función para formatear el precio a moneda local (Argentina - ARS)
const formatPrice = (price) => {
    return new Intl.NumberFormat('es-AR', {
        style: 'currency',
        currency: 'ARS',
        minimumFractionDigits: 2
    }).format(price);
};

// Función para crear la tarjeta de producto HTML
const createProductCard = (product) => {
    const placeholderImageUrl = `https://placehold.co/200x150/E4E4E9/6479FF?text=No+Image`; 
    const imageUrl = product.image_url || placeholderImageUrl;

    const displayPrice = product.price ? formatPrice(product.price * 1000) : 'Precio no disponible';

    const hasOffer = (product.discount_percentage && product.discount_percentage > 0) ? true : false;
    const originalPrice = hasOffer ? formatPrice((product.price * 1000) / (1 - product.discount_percentage / 100)) : '';

    return `
        <div class="product-card bg-white rounded-xl shadow-md overflow-hidden 
                     transform transition-transform duration-300 hover:scale-105 cursor-pointer 
                     border border-product-card-border flex flex-col"
             onclick="window.location.href='/product/${product.id}'"> 
            <div class="w-full h-40 flex items-center justify-center overflow-hidden p-2">
                <img src="${imageUrl}" alt="${product.name}" 
                     class="w-full h-full object-contain" 
                     onerror="this.onerror=null;this.src='${placeholderImageUrl}';">
            </div>
            <div class="p-4 flex flex-col flex-grow">
                <h3 class="text-base font-semibold text-gray-800 mb-1 leading-tight line-clamp-2">${product.name}</h3>
                <p class="text-product-price-color text-xl font-bold mt-auto mb-1">
                    ${displayPrice}
                    ${hasOffer ? `<span class="text-gray-500 text-sm line-through ml-2">${originalPrice}</span>` : ''}
                </p>
                <p class="text-shipping-text-color text-sm mb-2">Envío gratis</p>
                <p class="text-gray-600 text-sm line-clamp-2 mb-3">${product.description}</p>
                <button class="mt-auto bg-international-buy-btn-bg text-white px-4 py-2 rounded-md font-semibold hover:bg-international-buy-btn-hover transition duration-200 text-sm">
                    COMPRA INTERNACIONAL
                </button>
            </div>
        </div>
    `;
};

// Función para renderizar los productos en la cuadrícula
const displayProducts = (products) => {
    const productGrid = document.getElementById('product-grid');
    if (productGrid) {
        productGrid.innerHTML = products.map(createProductCard).join('');
    }
};

// Función para actualizar los números de paginación
const updatePaginationNumbers = () => {
    const paginationNumbersContainer = document.getElementById('pagination-numbers');
    if (!paginationNumbersContainer) {
        console.warn("updatePaginationNumbers: Contenedor de números de paginación no encontrado.");
        return;
    }

    paginationNumbersContainer.innerHTML = '';
    const totalPages = Math.ceil(totalProducts / productsPerPage); 
    console.log(`updatePaginationNumbers: Total de productos (filtrados): ${totalProducts}, Productos por página: ${productsPerPage}, Páginas totales calculadas: ${totalPages}`);

    const maxPageButtons = 5; 
    let startPage, endPage;

    if (totalPages <= maxPageButtons) {
        startPage = 1;
        endPage = totalPages;
    } else {
        if (currentPage <= Math.floor(maxPageButtons / 2) + 1) { 
            startPage = 1;
            endPage = maxPageButtons;
        } else if (currentPage + Math.floor(maxPageButtons / 2) >= totalPages) {
            startPage = totalPages - maxPageButtons + 1;
            endPage = totalPages;
        } else {
            startPage = currentPage - Math.floor(maxPageButtons / 2);
            endPage = currentPage + Math.floor(maxPageButtons / 2);
        }
    }
    if (startPage < 1) startPage = 1;
    if (endPage > totalPages) endPage = totalPages;

    console.log(`updatePaginationNumbers: Páginas a mostrar en el control: ${startPage} a ${endPage}, Página actual: ${currentPage}`);

    for (let i = startPage; i <= endPage; i++) {
        const pageSpan = document.createElement('span');
        pageSpan.classList.add('px-3', 'py-1', 'rounded-md', 'cursor-pointer', 'hover:bg-gray-300', 'text-gray-800');
        pageSpan.textContent = i;
        if (i === currentPage) {
            pageSpan.classList.remove('bg-gray-200', 'text-gray-800', 'hover:bg-gray-300'); 
            pageSpan.classList.add('bg-app-button-bg', 'text-white', 'font-bold'); 
        } else {
            pageSpan.classList.add('bg-gray-200');
        }
        pageSpan.addEventListener('click', () => {
            currentPage = i;
            fetchProducts(currentSearchQuery, currentCategory); 
        });
        paginationNumbersContainer.appendChild(pageSpan);
    }

    const prevPageBtn = document.getElementById('prev-page-btn');
    const nextPageBtn = document.getElementById('next-page-btn');
    if (prevPageBtn && nextPageBtn) {
        prevPageBtn.disabled = currentPage === 1;
        prevPageBtn.classList.toggle('opacity-50', currentPage === 1);
        prevPageBtn.classList.toggle('cursor-not-allowed', currentPage === 1);

        nextPageBtn.disabled = currentPage >= totalPages;
        nextPageBtn.classList.toggle('opacity-50', currentPage >= totalPages);
        nextPageBtn.classList.toggle('cursor-not-allowed', currentPage >= totalPages);
        console.log(`updatePaginationNumbers: prevBtn disabled: ${prevPageBtn.disabled}, nextBtn disabled: ${nextPageBtn.disabled}`);
    }
};

// Función principal para obtener y renderizar productos
const fetchProducts = async (query = '', category = '') => {
    const productGrid = document.getElementById('product-grid');
    const loadingIndicator = document.getElementById('loading-indicator');
    const paginationControls = document.getElementById('pagination-controls');

    if (!productGrid || !loadingIndicator || !paginationControls) {
        console.error("fetchProducts: Error crítico: Elementos del DOM para productos o paginación no encontrados.");
        showMessage("Error interno: Fallo al iniciar la visualización de productos. Contacta a soporte.", "error");
        return; 
    }

    productGrid.innerHTML = ''; 
    loadingIndicator.classList.remove('hidden'); 
    paginationControls.classList.add('hidden'); 
    showMessage('Cargando productos...', 'info');

    try {
        let url = `${API_BASE_URL}/products?page=${currentPage}&limit=${productsPerPage}`;
        
        if (query) {
            url += `&query=${encodeURIComponent(query)}`;
            currentSearchQuery = query;
        } else {
            currentSearchQuery = ''; 
        }

        if (category) {
            url += `&category=${encodeURIComponent(category)}`;
            currentCategory = category;
        } else {
            currentCategory = ''; 
        }

        console.log(`fetchProducts: Realizando fetch a: ${url}`); 
        const response = await fetch(url);
        
        if (!response.ok) {
            const errorText = await response.text(); 
            let errorMessage = `Error HTTP: ${response.status} ${response.statusText}`;
            try {
                const errorData = JSON.parse(errorText);
                errorMessage = errorData.message || errorData.error || errorMessage;
            } catch (e) {
                errorMessage = `Error del servidor: ${errorText}`;
            }
            console.error(`fetchProducts: Error de respuesta HTTP para ${url}: ${errorMessage}`);
            throw new Error(errorMessage);
        }
        const data = await response.json();
        console.log("fetchProducts: Datos recibidos del backend:", data);
        
        const productsToDisplay = data.products;
        // ¡CORRECCIÓN CLAVE AQUÍ! Usar solo data.total_products para la paginación global
        totalProducts = data.total_products; 
        console.log(`fetchProducts: Total de productos recibido del backend para paginación: ${totalProducts}`);

        loadingIndicator.classList.add('hidden');
        
        if (!productsToDisplay || productsToDisplay.length === 0) {
            productGrid.innerHTML = '<p class="text-gray-600 text-center col-span-full py-8">No se encontraron productos que coincidan con la búsqueda o filtro.</p>';
            showMessage('No se encontraron productos.', 'info');
            return;
        }

        displayProducts(productsToDisplay); 
        updatePaginationNumbers(); 
        paginationControls.classList.remove('hidden'); 
        showMessage('Productos cargados exitosamente.', 'success');

    }
    catch (error) {
        console.error('fetchProducts: Error fetching products:', error);
        loadingIndicator.classList.add('hidden');
        paginationControls.classList.add('hidden');
        showMessage(`Error al cargar productos: ${error.message}. Por favor, inténtalo de nuevo.`, 'error');
        productGrid.innerHTML = '<p class="text-red-600 text-center col-span-full py-8">Error al cargar productos. Por favor, verifica tu conexión o inténtalo más tarde.</p>';
    }
};

// --- Manejo de Eventos ---
export function initializeProductsPage() {
    console.log("products.js: Inicializando página de productos.");

    const searchInput = document.getElementById('search-input');
    const searchButton = document.getElementById('search-button');
    const categoriesDropdown = document.getElementById('categorias-dropdown'); 
    const menuButton = document.getElementById('menu-button'); 
    const mainNav = document.getElementById('main-nav'); 

    if (menuButton && mainNav) {
        menuButton.addEventListener('click', () => {
            mainNav.classList.toggle('hidden');
            mainNav.classList.toggle('active'); 
            document.querySelectorAll('.absolute').forEach(openDropdown => { 
                if (!openDropdown.classList.contains('hidden')) { 
                    openDropdown.classList.add('hidden');
                }
            });
        });
        document.addEventListener('click', (event) => {
            if (!mainNav.contains(event.target) && !menuButton.contains(event.target) && !mainNav.classList.contains('hidden')) {
                mainNav.classList.add('hidden');
                mainNav.classList.remove('active');
            }
        });
    }

    if (searchButton) {
        searchButton.addEventListener('click', (event) => {
            event.preventDefault(); 
            currentPage = 1; 
            console.log("Search button clicked. Fetching products with query:", searchInput.value.trim());
            fetchProducts(searchInput.value.trim(), ''); 
        });
    }
    if (searchInput) {
        searchInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault(); 
                currentPage = 1; 
                console.log("Enter pressed in search input. Fetching products with query:", searchInput.value.trim());
                fetchProducts(searchInput.value.trim(), ''); 
            }
        });
    }

    if (categoriesDropdown) {
        categoriesDropdown.addEventListener('click', async (event) => { 
            event.preventDefault();
            const target = event.target;
            if (target.tagName === 'A' && target.dataset.category) {
                currentCategory = target.dataset.category;
                currentPage = 1; 
                searchInput.value = ''; 
                categoriesDropdown.classList.add('hidden'); 
                console.log("Category selected:", currentCategory, ". Fetching products.");
                await fetchProducts('', currentCategory); 
            }
        });
    }
    
    // Cargar categorías dinámicamente en el dropdown
    const loadCategoriesIntoDropdown = async () => {
        const categoriesDropdownElement = document.getElementById('categorias-dropdown');
        if (!categoriesDropdownElement) {
            console.warn("loadCategoriesIntoDropdown: Elemento 'categorias-dropdown' no encontrado.");
            return;
        }

        try {
            console.log("loadCategoriesIntoDropdown: Fetching categories from backend.");
            const response = await fetch(`${API_BASE_URL}/categories`);
            if (!response.ok) {
                const errorText = await response.text();
                let errorMessage = `Error HTTP: ${response.status} ${response.statusText}`;
                try {
                    const errorData = JSON.parse(errorText);
                    errorMessage = errorData.message || errorData.error || errorMessage;
                } catch (e) {
                    errorMessage = `Error del servidor: ${errorText}`;
                }
                console.error(`loadCategoriesIntoDropdown: Error de respuesta HTTP para /api/categories: ${errorMessage}`);
                throw new Error(errorMessage);
            }
            const categories = await response.json();
            console.log("loadCategoriesIntoDropdown: Categorías recibidas del backend:", categories);
            
            categoriesDropdownElement.innerHTML = ''; 
            const allCategoriesLink = document.createElement('a');
            allCategoriesLink.href = "#";
            allCategoriesLink.classList.add('block', 'px-4', 'py-2', 'hover:bg-gray-100');
            allCategoriesLink.dataset.category = "todas las categorias"; 
            allCategoriesLink.textContent = "Todas las categorías";
            categoriesDropdownElement.appendChild(allCategoriesLink);


            categories.forEach(category => {
                const categoryLink = document.createElement('a');
                categoryLink.href = "#";
                categoryLink.classList.add('block', 'px-4', 'py-2', 'hover:bg-gray-100');
                categoryLink.dataset.category = category.toLowerCase(); 
                categoryLink.textContent = category; 
                categoriesDropdownElement.appendChild(categoryLink);
            });
            console.log("Categorías cargadas en dropdown:", categories);
        } catch (error) {
            console.error('loadCategoriesIntoDropdown: Error al cargar categorías en dropdown:', error);
            showMessage(`Error al cargar categorías: ${error.message}`, 'error');
        }
    };
    loadCategoriesIntoDropdown(); 

    const prevPageBtn = document.getElementById('prev-page-btn');
    const nextPageBtn = document.getElementById('next-page-btn');

    if (prevPageBtn) {
        prevPageBtn.addEventListener('click', () => {
            if (currentPage > 1) {
                currentPage--;
                console.log("Previous page clicked. Current page:", currentPage);
                fetchProducts(currentSearchQuery, currentCategory);
            }
        });
    }

    if (nextPageBtn) {
        nextPageBtn.addEventListener('click', () => {
            const totalPages = Math.ceil(totalProducts / productsPerPage);
            if (currentPage < totalPages) {
                currentPage++;
                console.log("Next page clicked. Current page:", currentPage);
                fetchProducts(currentSearchQuery, currentCategory);
            }
        });
    }

    const urlParams = new URLSearchParams(window.location.search);
    const initialQueryFromUrl = urlParams.get('query');
    const initialCategoryFromUrl = urlParams.get('category');

    currentSearchQuery = initialQueryFromUrl || '';
    currentCategory = initialCategoryFromUrl || ''; 
    console.log("products.js: Initial load with query:", currentSearchQuery, "category:", currentCategory);
    fetchProducts(currentSearchQuery, currentCategory);
}


// --- Lógica para la página de detalle de producto (product_detail.html) ---

export async function initializeProductDetailPage() {
    console.log("products.js: Inicializando página de detalles del producto.");
    const productId = window.location.pathname.split('/').pop(); 
    const productDetailContainer = document.getElementById('product-detail-container');
    const loadingIndicator = document.getElementById('detail-loading-indicator');
    const volverButton = document.getElementById('volver-button'); 

    if (!productDetailContainer || !loadingIndicator || !productId) {
        console.error("initializeProductDetailPage: Elementos del DOM para detalles del producto no encontrados o ID de producto faltante.");
        showMessage("Error: No se pudo cargar el producto. ID faltante.", "error");
        return;
    }

    if (volverButton) {
        volverButton.addEventListener('click', () => {
            history.back(); 
        });
    }

    loadingIndicator.classList.remove('hidden');
    showMessage('Cargando detalles del producto...', 'info');

    try {
        const response = await fetch(`${API_BASE_URL}/products/${productId}`); 
        if (!response.ok) {
            const errorText = await response.text();
            let errorMessage = `Error HTTP: ${response.status} ${response.statusText}`;
            try {
                const errorData = JSON.parse(errorText);
                errorMessage = errorData.message || errorData.error || errorMessage;
            } catch (e) {
                errorMessage = `Error del servidor: ${errorText}`;
            }
            console.error(`initializeProductDetailPage: Error de respuesta HTTP para /products/${productId}: ${errorMessage}`);
            throw new Error(errorMessage);
        }
        const product = await response.json(); 
        console.log("initializeProductDetailPage: Datos de detalle de producto recibidos:", product);

        loadingIndicator.classList.add('hidden');
        if (product) {
            const imageUrl = product.image_url || `https://placehold.co/400x300/E4E4E9/6479FF?text=No+Image`;

            const displayPrice = product.price ? formatPrice(product.price * 1000) : 'Precio no disponible';

            const stars = Math.round(product.rating || 0); 
            const starIcons = '<i class="fas fa-star text-yellow-400"></i>'.repeat(stars) + 
                             '<i class="far fa-star text-gray-300"></i>'.repeat(5 - stars);

            const detailHtml = `
                <div class="flex flex-col md:flex-row bg-white rounded-xl shadow-xl p-6 md:p-8 space-y-6 md:space-y-0 md:space-x-8 max-w-6xl mx-auto">
                    <div class="md:w-1/2 flex justify-center items-center">
                        <img src="${imageUrl}" alt="${product.name}" class="w-full h-auto max-h-96 object-contain rounded-lg">
                    </div>
                    <div class="md:w-1/2 flex flex-col justify-between">
                        <div>
                            <p class="text-app-title-color font-semibold mb-2 text-sm">PERFIL DEL IMPORTADOR</p>
                            <h1 class="text-4xl md:text-5xl font-bold text-gray-900 mb-2">${product.name}</h1>
                            <div class="flex items-center text-gray-600 text-sm mb-4">
                                <span class="mr-2">${starIcons}</span> 
                                <span>${product.rating_count ? product.rating_count : 0} reseñas</span>
                            </div>
                            <p class="text-gray-700 text-lg font-bold mb-1">
                                ${displayPrice}
                            </p>
                            <p class="text-shipping-text-color text-base mb-4">Envío gratis</p>
                            
                            <hr class="my-4 border-gray-200">
                            
                            <h3 class="text-lg font-semibold text-gray-800 mb-2">Lo que tenés que saber de este producto:</h3>
                            <ul class="list-disc list-inside text-gray-700 text-base space-y-1">
                                <li>${product.description}</li>
                                ${product.category ? `<li>Categoría: ${product.category}</li>` : ''}
                                ${product.stock ? `<li>Stock: ${product.stock} unidades</li>` : ''}
                                ${product.brand ? `<li>Marca: ${product.brand}</li>` : ''}
                                ${product.weight ? `<li>Peso: ${product.weight} kg</li>` : ''}
                                ${product.dimensions && product.dimensions.width ? `<li>Dimensiones: ${product.dimensions.width}x${product.dimensions.height}x${product.dimensions.depth} cm</li>` : ''}
                                ${product.warrantyInformation ? `<li>Garantía: ${product.warrantyInformation}</li>` : ''}
                                ${product.shippingInformation ? `<li>Información de envío: ${product.shippingInformation}</li>` : ''}
                                ${product.availabilityStatus ? `<li>Estado de disponibilidad: ${product.availabilityStatus}</li>` : ''}
                                ${product.returnPolicy ? `<li>Política de devolución: ${product.returnPolicy}</li>` : ''}
                                ${product.minimumOrderQuantity ? `<li>Cantidad mínima de pedido: ${product.minimumOrderQuantity}</li>` : ''}
                            </ul>

                            <a href="#" class="text-app-title-color font-semibold mt-4 block hover:underline">Ver más productos de este importador</a>
                            <a href="#" class="text-app-title-color font-semibold mt-2 block hover:underline">Ver medios de pago</a>
                        </div>
                        
                        {# Botones de acción #}
                        <div class="mt-6 flex flex-col space-y-3">
                            <button class="bg-international-buy-btn-bg text-white px-6 py-3 rounded-md font-semibold text-lg shadow-md hover:bg-international-buy-btn-hover transition duration-200">
                                COMPRAR
                            </button>
                            <button class="bg-gray-200 text-gray-800 px-6 py-3 rounded-md font-semibold text-lg shadow-md hover:bg-gray-300 transition duration-200">
                                AÑADIR AL CARRITO
                            </button>
                        </div>
                    </div>
                </div>
                
                {# Sección de Características del Producto (Inferior) #}
                <div class="w-full max-w-6xl mx-auto bg-white rounded-xl shadow-xl p-6 md:p-8 mt-8">
                    <h2 class="text-2xl font-bold text-gray-900 mb-4">Características del producto</h2>
                    <ul class="list-disc list-inside text-gray-700 text-base space-y-1">
                        <li>Nombre: ${product.name}</li>
                        <li>Descripción: ${product.description}</li>
                        <li>Precio: ${displayPrice}</li>
                        <li>Categoría: ${product.category}</li>
                        <li>Stock: ${product.stock} unidades</li>
                        <li>Marca: ${product.brand}</li>
                        <li>Rating: ${product.rating} (${product.rating_count} reseñas)</li>
                        ${product.weight ? `<li>Peso: ${product.weight} kg</li>` : ''}
                        ${product.dimensions && product.dimensions.width ? `<li>Dimensiones: ${product.dimensions.width}x${product.dimensions.height}x${product.dimensions.depth} cm</li>` : ''}
                        ${product.warrantyInformation ? `<li>Garantía: ${product.warrantyInformation}</li>` : ''}
                        ${product.shippingInformation ? `<li>Información de envío: ${product.shippingInformation}</li>` : ''}
                        ${product.availabilityStatus ? `<li>Estado de disponibilidad: ${product.availabilityStatus}</li>` : ''}
                        ${product.returnPolicy ? `<li>Política de devolución: ${product.returnPolicy}</li>` : ''}
                        ${product.minimumOrderQuantity ? `<li>Cantidad mínima de pedido: ${product.minimumOrderQuantity}</li>` : ''}
                    </ul>
                </div>
            `;
            productDetailContainer.innerHTML = detailHtml;
            showMessage('Detalles del producto cargados exitosamente.', 'success');
        } else {
            productDetailContainer.innerHTML = '<p class="text-red-600 text-center text-lg py-8">Producto no encontrado.</p>';
            showMessage('Producto no encontrado.', 'error');
        }
    } catch (error) {
        console.error('Error fetching product details:', error);
        loadingIndicator.classList.add('hidden');
        showMessage(`Error al cargar detalles: ${error.message}.`, 'error');
        productDetailContainer.innerHTML = '<p class="text-red-600 text-center text-lg py-8">Error al cargar los detalles del producto. Por favor, inténtalo de nuevo.</p>';
    }
}
