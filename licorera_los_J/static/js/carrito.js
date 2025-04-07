document.addEventListener('DOMContentLoaded', () => {
    const cartButton = document.getElementById('cartButton');
    const cartMenu = document.getElementById('cartMenu');
    const closeCartMenu = document.getElementById('closeCartMenu');
    const cartContent = document.querySelector('.cart-content');
    const totalPriceElement = document.querySelector('.total-price');
    const addToCartButtons = document.querySelectorAll('.add-to-cart');
    const cartCountElement = document.getElementById('cartCount');

    // Función para actualizar el contador del carrito
    function actualizarContadorCarrito() {
        const cart = JSON.parse(localStorage.getItem('cart')) || [];
        const totalItems = cart.reduce((sum, item) => sum + item.cantidad, 0);
        cartCountElement.textContent = totalItems;
    }

    // Llama a la función al cargar la página
    actualizarContadorCarrito();

    // Almacenar productos en localStorage
    addToCartButtons.forEach(button => {
        button.addEventListener('click', () => {
            const productId = button.getAttribute('data-id');
            const productName = button.getAttribute('data-nombre');
            const productPrice = parseFloat(button.getAttribute('data-precio'));
            const productImage = button.getAttribute('data-imagen');

            let cart = JSON.parse(localStorage.getItem('cart')) || [];
            const existingProduct = cart.find(item => item.id === productId);

            if (existingProduct) {
                existingProduct.cantidad += 1;
            } else {
                cart.push({
                    id: productId,
                    nombre: productName,
                    precio: productPrice,
                    imagen: productImage,
                    cantidad: 1
                });
            }

            localStorage.setItem('cart', JSON.stringify(cart));
            alert('Producto agregado al carrito');
            actualizarContadorCarrito(); // Actualiza el contador después de agregar
        });
    });

    // Abrir el menú del carrito
    cartButton.addEventListener('click', (e) => {
        e.preventDefault();
        cartMenu.classList.add('open');
        cargarCarrito();
    });

    // Cerrar el menú del carrito
    closeCartMenu.addEventListener('click', () => {
        cartMenu.classList.remove('open');
    });

    // Cerrar el menú si se hace clic fuera de él
    document.addEventListener('click', (e) => {
        if (!cartMenu.contains(e.target) && e.target !== cartButton) {
            cartMenu.classList.remove('open');
        }
    });

    // Cargar los datos del carrito
    function cargarCarrito() {
        const cart = JSON.parse(localStorage.getItem('cart')) || [];
        if (cart.length === 0) {
            cartContent.innerHTML = '<p>Tu carrito está vacío.</p>';
            totalPriceElement.textContent = 'Total: $0';
        } else {
            cartContent.innerHTML = cart.map(item => `
                <div class="cart-item">
                    <img src="${item.imagen}" alt="${item.nombre}">
                    <div class="cart-item-info">
                        <h5>${item.nombre}</h5>
                        <p>$${item.precio} x ${item.cantidad}</p>
                    </div>
                    <div class="cart-item-actions">
                        <button class="decrease" data-id="${item.id}">-</button>
                        <button class="increase" data-id="${item.id}">+</button>
                        <button class="remove" data-id="${item.id}">&times;</button>
                    </div>
                </div>
            `).join('');
            const total = cart.reduce((sum, item) => sum + item.precio * item.cantidad, 0);
            totalPriceElement.textContent = `Total: $${total.toFixed(2)}`;
        }
    }

    // Actualizar cantidad o eliminar productos
    cartContent.addEventListener('click', (e) => {
        const cart = JSON.parse(localStorage.getItem('cart')) || [];
        const button = e.target;
        const productId = button.getAttribute('data-id');

        if (button.classList.contains('decrease')) {
            const product = cart.find(item => item.id === productId);
            if (product.cantidad > 1) {
                product.cantidad -= 1;
            } else {
                const index = cart.indexOf(product);
                cart.splice(index, 1);
            }
        } else if (button.classList.contains('increase')) {
            const product = cart.find(item => item.id === productId);
            product.cantidad += 1;
        } else if (button.classList.contains('remove')) {
            const index = cart.findIndex(item => item.id === productId);
            cart.splice(index, 1);
        }

        localStorage.setItem('cart', JSON.stringify(cart));
        cargarCarrito();
        actualizarContadorCarrito(); // Actualiza el contador después de modificar/eliminar
    });

    // Obtener el token CSRF
    function getCSRFToken() {
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            const [name, value] = cookie.trim().split('=');
            if (name === 'csrftoken') {
                return value;
            }
        }
        return null;
    }
});