from django.contrib import admin
from .models import *
# Register your models here.

@admin.register(Usuarios)
class Usuario(admin.ModelAdmin):
    list_display = ['id', 'nombre', 'apellido', 'cuenta', 'telefono', 'email']
    search_list = []

@admin.register(Proveedores)
class Provedor(admin.ModelAdmin):
    list_display = ['id', 'empresa', 'correo', 'nombre', 'apellido', 'telefono']
    list_filter=['empresa']
    list_editable =['telefono']

@admin.register(Inventario)
class Inventario(admin.ModelAdmin):
    list_display = ['producto', 'tipo_de_producto', 'cantidad', 'valor_compra', 'valor_venta', 'descripcion']

@admin.register(Facturas)
class Factura(admin.ModelAdmin):
    list_display = ['id','cliente','valor_pedido',"valor_total","fecha_factura","fecha_factura"]

@admin.register(DetallesFacturas)
class DetallesFacturas(admin.ModelAdmin):
    list_display = ['id', 'producto', 'factura']

@admin.register(Productos)
class Producto(admin.ModelAdmin):
    list_display = ['id', 'nombre_producto', 'tipo_producto', 'descripcion', 'precio','cantidad']
    list_filter=["tipo_producto"]
    list_editable=['precio', 'cantidad']