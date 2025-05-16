document.addEventListener('DOMContentLoaded', function () {
    const metodoPagoSelect = document.getElementById('metodo_pago');
    const formTarjeta = document.getElementById('form-tarjeta');
    const formPaypal = document.getElementById('form-paypal');
    const formTransferencia = document.getElementById('form-transferencia');

    metodoPagoSelect.addEventListener('change', function () {
        // Ocultar todos los formularios
        formTarjeta.style.display = 'none';
        formPaypal.style.display = 'none';
        formTransferencia.style.display = 'none';

        // Mostrar el formulario correspondiente
        const metodoSeleccionado = metodoPagoSelect.value;
        if (metodoSeleccionado === 'tarjeta') {
            formTarjeta.style.display = 'block';
        } else if (metodoSeleccionado === 'paypal') {
            formPaypal.style.display = 'block';
        } else if (metodoSeleccionado === 'transferencia') {
            formTransferencia.style.display = 'block';
        }
    });
});
