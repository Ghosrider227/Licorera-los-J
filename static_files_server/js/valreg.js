function myFunction(event) {
    let contrasena = document.getElementById('contrasena').value;
    let confirmar_contrasena = document.getElementById('confirmar_contrasena').value;
    let mensajeError = document.getElementById('mensaje_error');

    if (contrasena != confirmar_contrasena) {
        mensajeError.style.display = 'block';
        mensajeError.textContent = 'Las contraseñas no coinciden';
        event.preventDefault(); // Evita el envío del formulario
        return false;
    } else {
        mensajeError.style.display = 'none'; // Oculta el mensaje de error
        return true; // Permite el envío del formulario
    }
}

let validator = document.getElementById('registrar');
// Agregar evento onclick
validator.addEventListener('click', function(event) {
    myFunction(event);
});