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