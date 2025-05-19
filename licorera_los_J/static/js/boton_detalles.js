document.addEventListener('DOMContentLoaded', function () {
    const botonesDetalles = document.querySelectorAll('.btn-detalles');

    botonesDetalles.forEach(boton => {
        boton.addEventListener('click', function () {
            const detallesId = this.getAttribute('data-id'); // Obtener el ID del contenedor
            const detalles = document.getElementById(detallesId); // Buscar el contenedor por ID

            if (detalles) { // Verificar si el contenedor existe
                if (detalles.style.display === 'none' || detalles.style.display === '') {
                    detalles.style.display = 'block'; // Mostrar el contenedor
                } else {
                    detalles.style.display = 'none'; // Ocultar el contenedor
                }
            } else {
                console.error(`No se encontró el contenedor con ID: ${detallesId}`);
            }
        });
    });
});