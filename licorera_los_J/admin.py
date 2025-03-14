from django.contrib import admin
from .models import *
# Register your models here.

@admin.register(Usuario)
class Usuario(admin.ModelAdmin):
    list_display = ['id', 'nombre', 'apellido', 'tipoUsuario', 'telefono', 'correo']
    search_list = []

@admin.register(Proveedor)
class Provedor(admin.ModelAdmin):
    list_display = ['id', 'empresa', 'correo', 'nombre', 'apellido', 'telefono']
    list_filter=['empresa']
    list_editable =['telefono']

@admin.register(Inventario)
class Inventario(admin.ModelAdmin):
    list_display = ['producto', 'tipo_de_producto', 'cantidad', 'valor_compra', 'valor_venta', 'descripcion']

@admin.register(Factura)
class Factura(admin.ModelAdmin):
    list_display = ['id','cliente','valor_pedido',"valor_total","fecha_factura","fecha_factura"]

@admin.register(DetalleFactura)
class DetallesFacturas(admin.ModelAdmin):
    list_display = ['id', 'producto', 'factura']

@admin.register(Producto)
class Producto(admin.ModelAdmin):
    list_display = ['id', 'nombre_Producto', 'tipo_Producto', 'descripcion', 'precio','cantidad']
    list_filter=["tipo_Producto"]
    list_editable=["tipo_Producto","nombre_Producto"]