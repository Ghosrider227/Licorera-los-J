 // Ocultar los mensajes después de 3 segundos
setTimeout(function() {
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        alert.classList.remove('show'); // Oculta el mensaje
        alert.classList.add('fade');   // Añade la animación de desvanecimiento
    });
}, 3000); // 3000 ms = 3 segundos