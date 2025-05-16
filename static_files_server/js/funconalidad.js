
function confirmar_eliminar(ruta){
    console.log(ruta);
    if(confirm("Está seguro? ")){
        location.href = ruta;
    }
}