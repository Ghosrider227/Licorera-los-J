function toggleDetalles(id) {
    const detalleDiv = document.getElementById(id);
    if (detalleDiv.style.display === "none") {
        detalleDiv.style.display = "block";
    } else {
        detalleDiv.style.display = "none";
    }
}