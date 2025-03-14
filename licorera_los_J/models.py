from django.db import models


# Create your models here.

# Brido
class Usuario(models.Model):
    nombre = models.CharField(max_length=50)
    apellido = models.CharField(max_length=50)
    usuarios = (
        ('1', 'Administrador'),
        ('2', 'Cliente'),
    )
    tipoUsuario = models.CharField(max_length = 1, choices = usuarios, default = 2)
    telefono = models.IntegerField()
    direccion = models.CharField(max_length=100)
    correo = models.CharField(max_length=50)
    gender = (
        ('M', 'Masculino'),
        ('F', 'Femenino'),
        ('N', 'No binario'),
    )
    genero = models.CharField(max_length=1, choices=gender)
    
    def __str__(self):
        return (f'{self.nombre}, {self.get_tipoUsuario_display()}')

class Proveedor(models.Model):
    administrador = models.ForeignKey('Usuario', on_delete=models.DO_NOTHING)
    empresa = models.CharField(max_length=100)
    correo = models.CharField(max_length=50)
    nombre = models.CharField(max_length=50)
    apellido = models.CharField(max_length=50)
    telefono = models.IntegerField()
    
    class Meta:
        verbose_name = "Proveedor"
        verbose_name_plural = "Proveedores"


#PARTE DE JOHAN
class Inventario(models.Model):
    usuario = models.ForeignKey('Usuario', on_delete=models.DO_NOTHING)
    producto = models.ForeignKey('Producto', on_delete=models.DO_NOTHING)
    tipo_de_producto = models.CharField(max_length=50)
    cantidad = models.IntegerField()
    valor_compra = models.DecimalField(max_digits=10, decimal_places=2)
    valor_venta = models.DecimalField(max_digits=10, decimal_places=2)
    descripcion = models.TextField()
    
class Factura(models.Model):
    cliente = models.ForeignKey('Usuario', on_delete=models.DO_NOTHING)
    valor_pedido = models.DecimalField(max_digits=10, decimal_places=2)
    valor_total = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_factura = models.DateField(help_text='AAAA-MM-DD')
    hora_factura = models.TimeField(help_text='HH:MM')
    
#parte Johan V2
class DetalleFactura(models.Model):
    producto = models.ForeignKey('Producto', on_delete=models.DO_NOTHING)
    factura = models.ForeignKey('Factura', on_delete=models.DO_NOTHING)

class Producto(models.Model):
    nombre_Producto = models.CharField(max_length = 100)
    categoria = (
        ('1', 'Vino'),
        ('2', 'Ron'),
        ('3', 'Cerveza'),
        ('4', 'vodka'),
        ('5', 'Ginebra'),
        ('6', 'Tequila'),
        ('7', 'Guaro'),
        ('8', 'smirnoff'),
        ('9', 'Four Loko'),
    )
    tipo_Producto = models.CharField(max_length = 1, choices = categoria)
    medidas = models.CharField(max_length = 100)
    precio = models.FloatField()
    descripcion = models.TextField(max_length=200)
    cantidad = models.IntegerField()
    peso = models.DecimalField(max_digits=10, decimal_places=2)
