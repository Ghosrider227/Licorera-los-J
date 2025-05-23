from django.db import models
from django.db.models import JSONField

# Create your models here.

# Brido


class Usuarios(models.Model):
    nombre = models.CharField(max_length=50)
    apellido = models.CharField(max_length=50)
    tipo_cuenta = (
        ('1', 'Administrador'),
        ('2', 'Cliente'),
    )
    cuenta = models.CharField(max_length=1, choices=tipo_cuenta, default=2)
    email = models.EmailField(max_length=50, default="")
    contrasena = models.CharField(max_length=254, default="")
    telefono = models.IntegerField()
    fecha_nacimiento = models.DateField(
        help_text='AAAA-MM-DD', null=True, blank=True)
    direccion = models.CharField(max_length=100, null=True, blank=True)
    foto = models.ImageField(
        upload_to='usuario/', default='usuario/default.png', null=True, blank=True)
    # Almacena el carrito como una lista JSON
    carrito = JSONField(default=list, blank=True)

    def __str__(self):
        return (f'{self.nombre}, {self.get_cuenta_display()}')

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'


class Proveedores(models.Model):
    administrador = models.ForeignKey('Usuarios', on_delete=models.DO_NOTHING)
    empresa = models.CharField(max_length=100)
    correo = models.CharField(max_length=50)
    nombre = models.CharField(max_length=50)
    apellido = models.CharField(max_length=50)
    telefono = models.IntegerField()

    class Meta:
        verbose_name = "Proveedor"
        verbose_name_plural = "Proveedores"


# PARTE DE JOHAN
class Inventario(models.Model):
    usuario = models.ForeignKey('Usuarios', on_delete=models.DO_NOTHING)
    producto = models.ForeignKey('Productos', on_delete=models.DO_NOTHING)
    tipo_de_producto = models.CharField(max_length=50)
    cantidad = models.IntegerField()
    valor_compra = models.DecimalField(max_digits=10, decimal_places=2)
    valor_venta = models.DecimalField(max_digits=10, decimal_places=2)
    descripcion = models.TextField()

    class Meta:
        verbose_name = 'Inventario'
        verbose_name_plural = 'Inventarios'


class Facturas(models.Model):
    cliente = models.ForeignKey('Usuarios', on_delete=models.DO_NOTHING)
    valor_pedido = models.IntegerField()
    valor_total = models.IntegerField()
    fecha_factura = models.DateField(help_text='AAAA-MM-DD')
    hora_factura = models.TimeField(help_text='HH:MM')

    class Meta:
        verbose_name = 'Factura'
        verbose_name_plural = 'Facturas'

# parte Johan V2


class DetallesFacturas(models.Model):
    producto = models.ForeignKey('Productos', on_delete=models.DO_NOTHING)
    factura = models.ForeignKey('Facturas', on_delete=models.DO_NOTHING)
    cantidad = models.IntegerField(default=0)
    subtotal = models.IntegerField()
    hora_compra = models.TimeField(help_text='HH:MM', null=True, blank=True)  # Nuevo campo

    class Meta:
        verbose_name = 'Detalle Factura'
        verbose_name_plural = 'Detalles Facturas'
    
    def __str__(self):
        return f"{self.producto.nombre_producto} x {self.cantidad} (${self.subtotal})"


class Productos(models.Model):
    nombre_producto = models.CharField(max_length=100)
    categoria = (
        ('1', 'Vino'),
        ('2', 'Ron'),
        ('3', 'Cerveza'),
        ('4', 'Vodka'),
        ('5', 'Wisky'),
        ('6', 'Tequila'),
        ('7', 'Guaro'),
        ('8', 'Champan'),
    )
    tipo_producto = models.CharField(max_length=1, choices=categoria)
    medidas = models.CharField(max_length=100)
    precio = models.IntegerField()
    descripcion = models.TextField(max_length=200)
    cantidad = models.IntegerField()
    foto = models.ImageField(
        upload_to='producto/', default='producto/default.svg', null=True, blank=True)

    def __str__(self):
        return f'{self.nombre_producto}, {self.get_tipo_producto_display()}'

    class Meta:
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'
