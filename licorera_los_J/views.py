from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import *
import re
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from .utils import *
from django.db.utils import IntegrityError
from django.http import JsonResponse
import json
from datetime import date
from django.core.serializers.json import DjangoJSONEncoder
import random



def index(request):
    productos = list(Productos.objects.all())
    productos_aleatorios = random.sample(productos, min(4, len(productos)))
    return render(request, 'index.html', {'data': productos_aleatorios})


def login(request):
    if request.method == 'POST':
        cuenta = request.POST.get('cuenta')
        contrasena = request.POST.get('contrasena')
        try:
            u = Usuarios.objects.get(email=cuenta)
            if verify_password(contrasena, u.contrasena):
                if u.fecha_nacimiento == None:
                    request.session["sesion"] = {
                        "id": u.id,
                        "nombre": u.nombre,
                        "cuenta": u.cuenta,
                        "email": u.email,
                        "carrito": u.carrito,
                    }
                else:
                    request.session["sesion"] = {
                        "id": u.id,
                        "nombre": u.nombre,
                        "cuenta": u.cuenta,
                        "email": u.email,
                        "carrito": u.carrito,
                        # Convertir a cadena
                        "fecha_nacimiento": u.fecha_nacimiento.isoformat() if u.fecha_nacimiento else None,
                    }
                    return redirect("index")
            else:
                raise Usuarios.DoesNotExist()
        except Usuarios.DoesNotExist:
            messages.warning(
                request, "Correo incorrecto o Contrasena incorrecta")
            request.session["sesion"] = None
        except Exception as e:
            messages.warning(request, f"Error: {e}")
            request.session["sesion"] = None
        return redirect("index")
    else:
        verificar = request.session.get('sesion', False)
        if verificar:
            return redirect('index')
        else:
            return render(request, 'index.html')


def logout(request):
    try:
        sesion = request.session.get("sesion", None)
        if sesion:
            u = Usuarios.objects.get(pk=sesion["id"])
            # Obtén el carrito de la sesión
            carrito = sesion.get("carrito", [])
            if isinstance(carrito, list):  # Verifica que sea una lista
                # Serializa el carrito y guárdalo en el modelo
                u.carrito = carrito
                u.save()
            else:
                messages.warning(
                    request, "El carrito no tiene un formato válido.")
        # Elimina la sesión actual
        request.session.flush()
        return redirect("index")
    except Usuarios.DoesNotExist:
        messages.error(request, "El usuario no existe.")
        return redirect("index")
    except Exception as e:
        messages.error(request, f"Error inesperado: {e}")
        return redirect("index")


def cambiar_clave(request):
    sesion = request.session.get("sesion", None)
    if not sesion:
        messages.error(request, "Debes iniciar sesión para cambiar la contraseña.")
        return redirect('index')
    else:
        if request.method == "POST":
            clave_actual = request.POST.get("clave_actual")
            nueva = request.POST.get("nueva")
            repite_nueva = request.POST.get("repite_nueva")
            logueado = request.session.get("sesion", False)

            q = Usuarios.objects.get(id=logueado["id"])
            if verify_password(clave_actual, q.contrasena):
                if nueva == repite_nueva:
                    q.contrasena = hash_password(nueva)       # utils.py
                    q.save()
                    messages.success(request, "Contraseña cambiada con éxito!!")
                else:
                    messages.warning(request, "Contraseña nueva no coincide")
            else:
                messages.warning(request, "Contraseña actual incorrecta")
            return redirect("editar_perfil")
        else:
            return render(request, "cambiar_clave.html")


def register(request):
    u = Usuarios.objects.all()

    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        apellido = request.POST.get('apellido')
        cuenta = request.POST.get('cuenta')
        email = request.POST.get('email')
        contrasena = request.POST.get('contrasena')
        confirmar_contrasena = request.POST.get('confirmar_contrasena')
        telefono = request.POST.get('telefono')

        try:
            validate_email(email)
        except ValidationError:
            messages.warning(request, 'El correo no es valido')
            return redirect('register')

        if not re.match(r'^[A-Za-z\s]+$', nombre):
            messages.warning(request, 'El nombre solo debe contener letras')
            return redirect('register')

        if not re.match(r'^[A-Za-z\s]+$', apellido):
            messages.warning(request, 'El apellido solo debe contener letras')
            return redirect('register')

        if not telefono.isdigit() or len(telefono) != 10:
            messages.warning(
                request, 'El telefono debe contener solo numeros y tener 10 digitos')
            return redirect('register')

        if u.filter(email=email).exists():
            messages.warning(request, 'El correo ya esta registrado')
            return redirect('register')
        else:
            if contrasena == confirmar_contrasena:
                try:
                    u = Usuarios(
                        nombre=nombre,
                        apellido=apellido,
                        cuenta=cuenta,
                        email=email,
                        contrasena=hash_password(contrasena),
                        telefono=telefono,
                        fecha_nacimiento=None,
                        direccion=None
                    )
                    u.save()
                    return redirect('index')
                except Exception as e:
                    messages.error(request, f'Error: {e}')
                    return redirect('register')
            else:
                messages.warning(request, 'La contraseña no coincide')
                return redirect('register')
    else:
        q = request.session.get('sesion', None)
        if q:
            return redirect('index')
        else:
            return render(request, 'register.html')


def agregar_carrito(request):
    if request.method == 'POST':
        id_producto = int(request.POST.get('id_producto'))
        cantidad = int(request.POST.get('cantidad', 1))

        # Verificar si el usuario está logueado
        sesion = request.session.get("sesion", None)
        if not sesion:
            messages.warning(
                request, "Debes iniciar sesión para agregar productos al carrito.")
            return redirect("catalogo")

        # Obtener el carrito de la sesión
        carrito = sesion.get("carrito", [])

        # Verificar si el producto ya está en el carrito
        producto_existente = next(
            (item for item in carrito if item['id_producto'] == id_producto), None)
        if producto_existente:
            # Incrementar la cantidad si el producto ya está en el carrito
            producto_existente['cantidad'] += cantidad
        else:
            # Agregar un nuevo producto al carrito
            producto = get_object_or_404(Productos, id=id_producto)
            carrito.append({
                'id_producto': id_producto,
                'nombre': producto.nombre_producto,
                'precio': producto.precio,
                'cantidad': cantidad,
            })

        # Guardar el carrito actualizado en la sesión
        sesion["carrito"] = carrito
        sesion["agregado_desde_catalogo"] = True  # Establecer la bandera
        request.session["sesion"] = sesion
        request.session.modified = True  # Asegurar que la sesión se actualice

        messages.success(request, "Producto agregado al carrito.")
        return redirect("catalogo")
    else:
        return render(request, "catalogo.html")


def compra(request):
    sesion = request.session.get("sesion", None)
    if not sesion:
        messages.error(request, "Debes iniciar sesión para acceder al carrito.")
        return redirect('login')

    carrito = sesion.get("carrito", [])
    if verificar_productos_carrito(carrito):
        # Si se detectaron productos eliminados, redirigir al index
        sesion["carrito"] = carrito
        request.session["sesion"] = sesion
        request.session.modified = True
        messages.warning(request, "Uno o más productos en tu carrito ya no están disponibles. Por favor, revisa el catálogo.")
        return redirect('index')

    productos_carrito = []
    subtotal = 0
    puede_proceder = False  # Variable para verificar si se puede proceder al pago

    # Manejar las acciones del formulario
    if request.method == "POST":
        action = request.POST.get("action", None)

        # Manejar la acción de Actualizar
        if action and action.startswith("update_"):
            producto_id = int(action.split("_")[1])
            nueva_cantidad = int(request.POST.get(f"cantidad_{producto_id}", 1))
            producto = get_object_or_404(Productos, id=producto_id)

            if nueva_cantidad > producto.cantidad:
                messages.error(
                    request, f"La cantidad ingresada para {producto.nombre_producto} excede el stock disponible ({producto.cantidad}).")
            elif nueva_cantidad < 1:
                messages.error(request, "La cantidad debe ser mayor a 0.")
            else:
                for item in carrito:
                    if item['id_producto'] == producto_id:
                        item['cantidad'] = nueva_cantidad
                        break
                messages.success(
                    request, f"Cantidad actualizada para {producto.nombre_producto}.")

            # Guardar el carrito actualizado en la sesión
            sesion["carrito"] = carrito
            request.session["sesion"] = sesion
            request.session.modified = True
            return redirect('compra')  # Redirigir para evitar reenvío del formulario

        # Validar y proceder al pago
        elif action == "checkout":
            for item in carrito:
                producto_id = item['id_producto']
                cantidad_en_formulario = int(request.POST.get(
                    f"cantidad_{producto_id}", item['cantidad']))

                # Verificar si la cantidad en el formulario coincide con la del carrito
                if cantidad_en_formulario != item['cantidad']:
                    messages.error(
                        request, f"Debes dar clic en 'Actualizar' para confirmar la cantidad de {item['nombre']}.")
                    puede_proceder = False
                else:
                    puede_proceder = True

                # Validar stock
                producto = get_object_or_404(Productos, id=producto_id)
                if item['cantidad'] > producto.cantidad:
                    messages.error(
                        request, f"La cantidad ingresada para {producto.nombre_producto} excede el stock disponible ({producto.cantidad}).")
                    puede_proceder = False
                else:
                    puede_proceder = True

            if puede_proceder:
                messages.success(request, "Todo está correcto. Procediendo al pago...")
                return redirect('pago')  # Redirigir a la página de pago
            else:
                messages.error(request, "No se puede proceder al pago.")
                return redirect('compra')

    # Cargar los productos del carrito desde la base de datos
    for item in carrito[:]:  # Usamos una copia del carrito para modificarlo mientras iteramos
        try:
            producto = Productos.objects.get(id=item['id_producto'])
            cantidad = item['cantidad']
            subtotal_producto = producto.precio * cantidad
            productos_carrito.append({
                'producto': producto,
                'cantidad': cantidad,
                'subtotal': subtotal_producto
            })
            subtotal += subtotal_producto
        except Productos.DoesNotExist:
            # Si el producto no existe, eliminarlo del carrito
            carrito.remove(item)
            sesion["carrito"] = carrito
            request.session["sesion"] = sesion
            request.session.modified = True
            messages.warning(request, f"El producto con ID {item['id_producto']} ya no está disponible y fue eliminado del carrito.")

    # Productos sugeridos
    productos_sugeridos = Productos.objects.all()[:4]

    return render(request, 'compra.html', {
        'productos_carrito': productos_carrito,
        'subtotal': subtotal,
        'total': subtotal,  # Si hay impuestos o descuentos, ajusta aquí
        'productos_sugeridos': productos_sugeridos
    })
def vaciar_bolsa(request):
    sesion = request.session.get("sesion", None)
    if not sesion:
        messages.error(
            request, "Debes iniciar sesión para acceder al carrito.")
        return redirect('login')

    # Vaciar el carrito en la sesión
    sesion["carrito"] = []
    request.session["sesion"] = sesion
    request.session.modified = True  # Asegurar que la sesión se actualice
    messages.success(
        request, "Todos los productos han sido eliminados de la bolsa.")
    return redirect('compra')  # Redirigir a la bolsa


def eliminar_producto(request, producto_id):
    sesion = request.session.get("sesion", None)
    if not sesion:
        messages.error(
            request, "Debes iniciar sesión para acceder al carrito.")
        return redirect('login')

    carrito = sesion.get("carrito", [])

    # Filtrar el carrito para eliminar el producto con el ID especificado
    carrito = [item for item in carrito if int(
        item['id_producto']) != int(producto_id)]

    # Actualizar el carrito en la sesión
    sesion["carrito"] = carrito
    request.session["sesion"] = sesion
    request.session.modified = True  # Asegurar que la sesión se actualice

    messages.success(request, "Producto eliminado del carrito.")
    return redirect('compra')  # Redirigir al carrito


def detalle_producto(request, id):
    producto = get_object_or_404(Productos, id=id)
    return render(request, 'detalle_producto.html', {'producto': producto})


def obtener_carrito(request):
    carrito = request.session.get('carrito', [])
    total = sum(item['precio'] * item['cantidad'] for item in carrito)
    return JsonResponse({'success': True, 'carrito': carrito, 'total': total})


def catalogo(request):
    tipo_producto = request.GET.get('tipo_producto', '')
    filtro_precio = request.GET.get('filtro_precio', '')

    # Filtrar por tipo de producto
    if tipo_producto:
        productos = Productos.objects.filter(tipo_producto=tipo_producto)
    else:
        productos = Productos.objects.all()

    # Filtrar por precio
    if filtro_precio == 'baratos':
        productos = productos.filter(precio__lte=200000)
    elif filtro_precio == 'caros':
        productos = productos.filter(precio__gt=200000)

    contexto = {
        'productos': productos,
        'tipo_producto': tipo_producto,
        'filtro_precio': filtro_precio,  # Pasamos el filtro al template
    }
    return render(request, 'catalogo.html', contexto)


def cobertura(request):
    return render(request, 'cobertura.html')

# ADMINISTRADOR


@validar_administrador
def productos(request):
    # all() -> todos      filter() -> algunos      get() -> 1 único
    q = Productos.objects.all()
    
    contexto = {
        "data": q
    }
    return render(request, "administrador/listar_productos.html", contexto)


@validar_administrador
def eliminar_productos(request, id_producto):
    # Obtener la instancia
    try:
        q = Productos.objects.get(pk=id_producto)
        q.delete()

        # Eliminar el producto de las bolsas de los usuarios
        sesiones = Session.objects.all()
        for sesion in sesiones:
            try:
                data = sesion.get_decoded()
                carrito = data.get("sesion", {}).get("carrito", [])
                carrito_actualizado = [item for item in carrito if int(item['id_producto']) != int(id_producto)]
                if len(carrito) != len(carrito_actualizado):  # Si hubo cambios
                    data["sesion"]["carrito"] = carrito_actualizado
                    sesion.session_data = Session.objects.encode(data)
                    sesion.save()
            except Exception as e:
                messages.error(request, f"Error al actualizar el carrito en la sesión")

        messages.success(request, "El producto fue eliminado correctamente y se ha retirado de los carritos de los usuarios.")

    except IntegrityError:
        messages.error(
            request, "No se puede eliminar este producto porque está asociado a otras operaciones o registros.")
    except Productos.DoesNotExist:
        messages.error(request, "El producto que intentas eliminar no existe.")
    except Exception as e:
        messages.error(request, f"Ocurrió un error inesperado al eliminar el producto.")

    return redirect("productos")


@validar_administrador
def agregar_productos(request):
    if request.method == "POST":
        nombre_producto = request.POST.get("nombre_producto")
        tipo_producto = request.POST.get("tipo_producto")
        medidas = request.POST.get("medidas")
        precio_str = request.POST.get("precio")
        descripcion = request.POST.get("descripcion")
        cantidad_str = request.POST.get("cantidad")
        foto = request.FILES.get("foto")
        
        if not re.match(r'^[A-Za-z\s]+$', nombre_producto):
            messages.error(request, "El campo solo debe contener letras y espacios.")
            return redirect('agregar_productos')
        
        if not re.match(r'^[1-8]$', tipo_producto):
            messages.error(request, "El tipo de producto no es válido.")
            return redirect('agregar_productos')
        
        if not re.match(r'^[A-Za-z\s]+$', descripcion):
            messages.error(request, "El campo solo debe contener letras y espacios.")
            return redirect('agregar_productos')
            
        if not re.match(r'^[A-Za-z0-9\s]+$', medidas):
            messages.error(request, "El campo solo debe contener letras, números y espacios.")
            return redirect('agregar_productos')
        
        # Validar precio
        if not precio_str or not precio_str.isdigit() or int(precio_str) <= 0:
            messages.warning(request, "El precio debe ser un número positivo mayor a cero.")
            return redirect("agregar_productos")
        
        # Validar cantidad
        if not cantidad_str or not cantidad_str.isdigit() or int(cantidad_str) <= 0:
            messages.warning(request, "La cantidad debe ser un número positivo mayor a cero.")
            return redirect("agregar_productos")

        precio = int(precio_str)
        cantidad = int(cantidad_str)
        
        if not foto:
            messages.error(request, "Debes subir una imagen del producto.")
            return redirect("agregar_productos")
        
        if foto.content_type not in ['image/jpeg', 'image/png']:
            messages.error(request, "El archivo debe ser una imagen en formato .jpg, .jpeg o .png.")
            return redirect("agregar_productos")
        
        try:
            q = Productos(
                nombre_producto=nombre_producto,
                tipo_producto=tipo_producto,
                medidas=medidas,
                precio=precio,
                descripcion=descripcion,
                cantidad=cantidad,
                foto=foto
            )
            q.save()
            messages.success(request, "Producto agregado exitosamente!")
            return redirect("productos")
        except Exception as e:
            messages.error(request, f"Error: {e}")
            return redirect("agregar_productos")
    else:
        return render(request, "administrador/formulario_productos.html")


@validar_administrador
def editar_productos(request, id_productos):
    if request.method == "POST":
        try:
            q = Productos.objects.get(pk=id_productos)

            q.nombre_producto = request.POST.get("nombre_producto")
            q.tipo_producto = request.POST.get("tipo_producto")
            q.precio = request.POST.get("precio")
            q.descripcion = request.POST.get("descripcion")
            q.cantidad = request.POST.get("cantidad")
            q.medidas = request.POST.get("medidas")
            
            if not re.match(r'^[A-Za-z\s]+$', q.nombre_producto):
                messages.error(request, "El campo solo debe contener letras y espacios.")
                return redirect('editar_producto', id_productos=id_productos)
            
            if not re.match(r'^[1-8]$', q.tipo_producto):
                messages.error(request, "El tipo de producto no es válido.")
                return redirect("editar_producto", id_productos=id_productos)
            
            if not re.match(r'^[\w\s.,;:¡!¿?()"\-áéíóúÁÉÍÓÚñÑ]+$', q.descripcion):
                messages.error(request, "La descripción contiene caracteres no permitidos.")
                return redirect('agregar_productos')
            
            if not re.match(r'^[A-Za-z0-9\s]+$', q.medidas):
                messages.error(request, "El campo solo debe contener letras, números y espacios.")
                return redirect('editar_producto', id_productos=id_productos)
            
            # Validar precio
            if not q.precio or not str(q.precio).isdigit() or int(q.precio) <= 0:
                messages.warning(request, "El precio debe ser un número positivo mayor a cero.")
                return redirect("editar_producto", id_productos=id_productos)
            
            # Validar cantidad
            if not q.cantidad or not str(q.cantidad).isdigit() or int(q.cantidad) <= 0:
                messages.warning(request, "La cantidad debe ser un número positivo mayor a cero.")
                return redirect("editar_producto", id_productos=id_productos)
            
            q.precio = int(q.precio)
            q.cantidad = int(q.cantidad)
            
            if 'foto' in request.FILES:
                foto = request.FILES['foto']
                # Validar el tipo de archivo
                if foto.content_type not in ['image/jpeg', 'image/png']:
                    messages.error(request, "El archivo debe ser una imagen en formato .jpg, .jpeg o .png.")
                    return redirect("editar_producto", id_productos=id_productos)
                q.foto = foto  # Actualizar la foto si es válida
                
            q.save()
            messages.success(request, "Producto actualizado correctamente!")
            return redirect("productos")
        except Exception as e:
            messages.error(request, f"Error: {e}")
            return redirect("editar_producto", id_productos=id_productos)
    else:
        q = Productos.objects.get(pk=id_productos)
        contexto = {"datos": q}
        return render(request, "administrador/formulario_productos.html", contexto)

# ADMINISTRADOR/USUARIOS

@validar_administrador
def usuarios(request):
    sesion = request.session.get("sesion", None)
    if sesion and sesion.get("id") == 10:
        u = Usuarios.objects.exclude(pk="10")  # Excluir usuarios con cuenta 10
    else:
        u = Usuarios.objects.filter(cuenta="2")  # Filtrar usuarios con cuenta "2"
    
    contexto = {
        "dato": u
    }
    return render(request, "administrador/listar_usuarios.html", contexto)


@validar_administrador
def editar_usuario(request, id_usuario):
    # Obtener la sesión
    sesion = request.session.get("sesion", None)

    # Verificar si el administrador ya está editando un usuario
    id_en_edicion = sesion.get("id_en_edicion", None)
    if id_en_edicion and id_en_edicion != id_usuario:
        messages.error(request, "No puedes cambiar el usuario que estás editando.")
        return redirect("editar_usuario", id_usuario=id_en_edicion)  # Redirigir al usuario en edición actual

    # Verificar si el usuario existe
    usuario_a_editar = get_object_or_404(Usuarios, pk=id_usuario)

    # Almacenar el ID del usuario en edición en la sesión
    sesion["id_en_edicion"] = id_usuario
    request.session["sesion"] = sesion
    request.session.modified = True

    # Continuar con la lógica de edición
    if request.method == "POST":
        try:
            usuario_a_editar.cuenta = request.POST.get("cuenta")
            usuario_a_editar.save()

            # Limpiar el ID en edición después de guardar
            sesion.pop("id_en_edicion", None)
            request.session["sesion"] = sesion
            request.session.modified = True

            messages.success(request, "Usuario actualizado correctamente!")
            return redirect("usuarios")
        except Exception as e:
            messages.error(request, f"Error inesperado")
            return redirect("editar_usuario", id_usuario=id_usuario)
    else:
        contexto = {"usuarios": usuario_a_editar}
        return render(request, "administrador/formulario_usuario.html", contexto)
# PAGOS Y CARRITO

def pago(request):
    sesion = request.session.get("sesion", None)
    u = Usuarios.objects.get(pk=sesion["id"])
    if not sesion:
        messages.error(request, "Debes iniciar sesión para proceder al pago.")
        return redirect('login')

    carrito = sesion.get("carrito", [])
    if verificar_productos_carrito(carrito):
        # Si se detectaron productos eliminados, redirigir al index
        sesion["carrito"] = carrito
        request.session["sesion"] = sesion
        request.session.modified = True
        messages.warning(request, "Uno o más productos en tu carrito ya no están disponibles. Por favor, revisa el catálogo.")
        return redirect('index')

    if not carrito:
        messages.error(request, "Tu carrito está vacío.")
        return redirect('compra')

    productos_carrito = []
    subtotal = 0

    # Cargar los productos del carrito desde la base de datos
    for item in carrito[:]:  # Usamos una copia del carrito para modificarlo mientras iteramos
        try:
            producto = get_object_or_404(Productos, id=item['id_producto'])
            cantidad = item['cantidad']
            subtotal_producto = producto.precio * cantidad
            productos_carrito.append({
                'producto': producto,
                'cantidad': cantidad,
                'subtotal': subtotal_producto
            })
            subtotal += subtotal_producto
        except Productos.DoesNotExist:
            # Si el producto no existe, eliminarlo del carrito
            carrito.remove(item)
            sesion["carrito"] = carrito
            request.session["sesion"] = sesion
            request.session.modified = True
            messages.warning(request, f"El producto con ID {item['id_producto']} ya no está disponible y fue eliminado del carrito.")
            return redirect('index')  # Redirigir al index si un producto fue eliminado

    return render(request, 'pago.html', {
        'productos_carrito': productos_carrito,
        'total': subtotal,
        'usuario': u
    })

@validar_administrador
def facturas(request):
    facturas = Facturas.objects.all()  # Obtiene todas las facturas
    detalles_facturas = DetallesFacturas.objects.all()  # Obtiene todos los detalles de facturas
    contexto = {
        "facturas": facturas,
        "detalles_facturas": detalles_facturas
    }
    return render(request, "administrador/listar_facturas.html", contexto)


def procesar_pago(request):
    if request.method == "POST":
        sesion = request.session.get("sesion", None)
        if not sesion:
            messages.error(request, "Debes iniciar sesión para realizar un pago.")
            return redirect('login')

        carrito = sesion.get("carrito", [])
        if not carrito:
            messages.error(request, "Tu carrito está vacío.")
            return redirect('compra')

        # Obtener el usuario autenticado
        try:
            usuario = Usuarios.objects.get(id=sesion['id'])
        except Usuarios.DoesNotExist:
            messages.error(request, "El usuario no existe.")
            return redirect('login')

        # Validar información de envío
        calle = request.POST.get("calle")
        telefono = request.POST.get("telefono")
        calle = request.POST.get("calle")
        estado = request.POST.get("estado")
        codigo_postal = request.POST.get("ubicacion")
        
        # Validar que los campos no estén vacíos
        if not calle:
            messages.error(request, "El campo Calle es obligatorio.")
            return redirect('pago')
            
        if not telefono:
            messages.error(request, "El campo Teléfono es obligatorio.")
            return redirect('pago')
            
        if not ciudad:
            messages.error(request, "El campo Ciudad es obligatorio.")
            return redirect('pago')
            
        if not estado:
            messages.error(request, "El campo Referencias es obligatorio.")
            return redirect('pago')
            
        if not codigo_postal:
            messages.error(request, "El campo Código Postal es obligatorio.")
            return redirect('pago')
        
        # Validar formato de teléfono (solo números y longitud adecuada)
        if not telefono.isdigit() or len(telefono) != 10:
            messages.warning(request, 'El telefono debe contener solo numeros y tener 10 digitos')
            return redirect('pago')
            
        # Validar que la calle solo contenga letras y espacios
        if not re.match(r'^[A-Za-zÁáÉéÍíÓóÚúÑñ\s]+$', calle):
            messages.error(request, "La calle solo debe contener letras y espacios.")
            return redirect('pago')
            
        # Validar código postal (formato numérico para Colombia)
        if not re.match(r'^[1-5]$', codigo_postal):
            messages.error(request, "Ubicacion fuera del area de cobertura.")
            return redirect('pago')

        # Validar método de pago
        metodo_pago = request.POST.get("metodo_pago")
        if not metodo_pago:
            messages.error(request, "Debes seleccionar un método de pago.")
            return redirect('pago')
            
        # Validar detalles específicos según el método de pago
        if metodo_pago == "tarjeta":
            numero_tarjeta = request.POST.get("numero_tarjeta")
            nombre_tarjeta = request.POST.get("nombre_tarjeta")
            fecha_expiracion = request.POST.get("fecha_expiracion")
            cvv = request.POST.get("cvv")
            
            if not numero_tarjeta or not nombre_tarjeta or not fecha_expiracion or not cvv:
                messages.error(request, "Todos los campos de la tarjeta son obligatorios.")
                return redirect('pago')
                
            # Validar número de tarjeta (solo números, sin espacios, longitud entre 13-19 dígitos)
            numero_tarjeta = numero_tarjeta.replace(" ", "")
            if not numero_tarjeta.isdigit() or len(numero_tarjeta) < 13 or len(numero_tarjeta) > 19:
                messages.error(request, "El número de tarjeta debe contener entre 13 y 19 dígitos.")
                return redirect('pago')
                
            # Validar nombre en la tarjeta (solo letras y espacios)
            if not re.match(r'^[A-Za-zÁáÉéÍíÓóÚúÑñ\s]+$', nombre_tarjeta):
                messages.error(request, "El nombre en la tarjeta solo debe contener letras y espacios.")
                return redirect('pago')
                
            # Validar fecha de expiración (formato MM/AA o MM/AAAA)
            if not re.match(r'^(0[1-9]|1[0-2])\/([0-9]{2}|[0-9]{4})$', fecha_expiracion):
                messages.error(request, "La fecha de expiración debe tener el formato MM/AA o MM/AAAA.")
                return redirect('pago')
                
            # Validar CVV (3 o 4 dígitos)
            if not cvv.isdigit() or len(cvv) < 3 or len(cvv) > 4:
                messages.error(request, "El CVV debe ser un número de 3 o 4 dígitos.")
                return redirect('pago')
                
        elif metodo_pago == "paypal":
            correo_paypal = request.POST.get("correo_paypal")
            
            if not correo_paypal:
                messages.error(request, "El correo electrónico de PayPal es obligatorio.")
                return redirect('pago')
                
            # Validar formato de correo electrónico
            try:
                validate_email(correo_paypal)
            except ValidationError:
                messages.error(request, "El correo electrónico de PayPal no es válido.")
                return redirect('pago')
                
        elif metodo_pago == "transferencia":
            banco = request.POST.get("banco")
            numero_cuenta = request.POST.get("numero_cuenta")
            titular_cuenta = request.POST.get("titular_cuenta")
            
            if not banco or not numero_cuenta or not titular_cuenta:
                messages.error(request, "Todos los campos de la transferencia bancaria son obligatorios.")
                return redirect('pago')
                
            # Validar que el banco solo contenga letras y espacios
            if not re.match(r'^[A-Za-zÁáÉéÍíÓóÚúÑñ\s]+$', banco):
                messages.error(request, "El nombre del banco solo debe contener letras y espacios.")
                return redirect('pago')
                
            # Validar número de cuenta (solo números)
            if not numero_cuenta.isdigit():
                messages.error(request, "El número de cuenta debe contener solo números.")
                return redirect('pago')
                
            # Validar titular de la cuenta (solo letras y espacios)
            if not re.match(r'^[A-Za-zÁáÉéÍíÓóÚúÑñ\s]+$', titular_cuenta):
                messages.error(request, "El titular de la cuenta solo debe contener letras y espacios.")
                return redirect('pago')

        # Validar stock y calcular el total
        total_pagado = 0
        errores = []
        for item in carrito:
            producto = get_object_or_404(Productos, id=item['id_producto'])
            if item['cantidad'] > producto.cantidad:
                errores.append(
                    f"No hay suficiente stock para {producto.nombre_producto}. Disponible: {producto.cantidad}.")
            else:
                total_pagado += producto.precio * item['cantidad']

        if errores:
            for error in errores:
                messages.error(request, error)
            return redirect('compra')

        # Crear la factura
        factura = Facturas.objects.create(
            cliente=usuario,
            valor_pedido=total_pagado,
            valor_total=total_pagado,
            fecha_factura=date.today(),
            hora_factura=date.today().strftime("%H:%M:%S")
        )

        # Crear los detalles de la factura y descontar el stock
        for item in carrito:
            producto = get_object_or_404(Productos, id=item['id_producto'])
            producto.cantidad -= item['cantidad']
            producto.save()

            DetallesFacturas.objects.create(
                producto=producto,
                factura=factura,
                cantidad=item['cantidad'],
                subtotal=producto.precio * item['cantidad']
            )
        detalles = DetallesFacturas.objects.filter(factura=factura)
        # Limpiar el carrito
        sesion["carrito"] = []
        request.session["sesion"] = sesion
        request.session.modified = True

        # Redirigir al template de factura
        return render(request, 'factura.html', {
            'factura': factura,
            'detalles': detalles
        })

    else:
        messages.error(request, "Método no permitido.")
        return redirect('pago')


def editar_perfil(request):
    user = request.session.get('sesion', False)
    if not user:
        messages.error(request, "Debes iniciar sesión para editar tu perfil.")
        return redirect('login')

    u = Usuarios.objects.get(id=user['id'])

    if request.method == 'POST':
        # Obtener los datos del formulario
        u.nombre = request.POST.get('nombre')
        u.apellido = request.POST.get('apellidos')
        u.telefono = request.POST.get('telefono')
        u.email = request.POST.get('email')
        u.direccion = request.POST.get('calle')
        fecha_nacimiento = request.POST.get('fecha_nacimiento')
        
        try:
            validate_email(u.email)
        except ValidationError:
            messages.warning(request, 'El correo no es valido')
            return render(request, 'editar_perfil.html', {'user': u})

        if not re.match(r'^[A-Za-z\s]+$', u.nombre):
            messages.warning(request, 'El nombre solo debe contener letras')
            return render(request, 'editar_perfil.html', {'user': u})

        if not re.match(r'^[A-Za-z\s]+$', u.apellido):
            messages.warning(request, 'El apellido solo debe contener letras')
            return render(request, 'editar_perfil.html', {'user': u})

        if not u.telefono.isdigit() or len(u.telefono) != 10:
            messages.warning(
                request, 'El telefono debe contener solo numeros y tener 10 digitos')
            return render(request, 'editar_perfil.html', {'user': u})

        varios = Usuarios.objects.filter(email=u.email).exclude(id=u.id).exists()
        if varios:
            messages.warning(request, 'El correo ya está registrado por otro usuario')
            return render(request, 'editar_perfil.html', {'user': u})

        # Validar mayoría de edad
        if fecha_nacimiento:
            fecha_nacimiento = date.fromisoformat(fecha_nacimiento)
            hoy = date.today()
            edad = hoy.year - fecha_nacimiento.year - \
                ((hoy.month, hoy.day) < (fecha_nacimiento.month, fecha_nacimiento.day))
            if edad < 18:
                messages.error(
                    request, "Debes ser mayor de edad para editar tu perfil.")
                return render(request, 'editar_perfil.html', {'user': u})

            u.fecha_nacimiento = fecha_nacimiento

        # Manejar la actualización de la foto
        if 'foto' in request.FILES:
            foto = request.FILES['foto']
            # Validar el tipo de archivo
            if foto.content_type not in ['image/jpeg', 'image/png']:
                messages.error(request, "El archivo debe ser una imagen en formato .jpg, .jpeg o .png.")
                return render(request, 'editar_perfil.html', {'user': u})
            u.foto = foto  # Actualizar la foto si es válida

        # Guardar los cambios
        u.save()
        messages.success(request, "Perfil actualizado con éxito.")
        return redirect('editar_perfil')  # Redirige al inicio o a otra página

    return render(request, 'editar_perfil.html', {'user': u})



#FACTURAS DE USUARIO
def mis_facturas(request):
    sesion = request.session.get("sesion", None)
    if not sesion:
        messages.error(request, "Debes iniciar sesión para ver tus facturas.")
        return redirect('login')

    usuario = get_object_or_404(Usuarios, id=sesion['id'])
    # Ordenar las facturas por ID en orden descendente
    facturas = Facturas.objects.filter(cliente=usuario).order_by('-id')

    return render(request, 'mis_facturas.html', {'facturas': facturas})

def detalle_factura(request, factura_id):
    factura = get_object_or_404(Facturas, id=factura_id)
    return render(request, 'detalle_factura.html', {'factura': factura})





def verificar_productos_carrito(carrito):
    """
    Verifica si los productos en el carrito aún existen en la base de datos.
    Si algún producto no existe, lo elimina del carrito y devuelve True.
    """
    productos_eliminados = False
    for item in carrito[:]:  # Usamos una copia del carrito para modificarlo mientras iteramos
        if not Productos.objects.filter(id=item['id_producto']).exists():
            carrito.remove(item)
            productos_eliminados = True
    return productos_eliminados