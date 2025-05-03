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


def index(request):
    # Traigo la informacion de la BD y se la mando al index con el contexto
    p = Productos.objects.all()
    contexto = {
        'data': p,
    }
    return render(request, 'index.html', contexto)


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
                        "fecha_nacimiento": u.fecha_nacimiento,
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
            # Guarda el carrito en el modelo
            u.carrito = sesion.get("carrito", [])
            u.save()
        del request.session["sesion"]
        return redirect("index")
    except Exception as e:
        messages.info(request, "No se pudo cerrar sesión, intente de nuevo")
        return redirect("inicio")


def cambiar_clave(request):
    if request.method == "POST":
        clave_actual = request.POST.get("clave_actual")
        nueva = request.POST.get("nueva")
        repite_nueva = request.POST.get("repite_nueva")
        logueado = request.session.get("auth", False)

        q = Usuarios.objects.get(pk=logueado["id"])
        if verify_password(clave_actual, q.password):
            if nueva == repite_nueva:
                q.password = hash_password(nueva)       # utils.py
                q.save()
                messages.success(request, "Contraseña cambiada con éxito!!")
            else:
                messages.info(request, "Contraseñas nuevas no coinciden...")
        else:
            messages.warning(request, "Contraseña no concuerda...")
        return redirect("cambiar_clave")
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
        id_producto = request.POST.get('id_producto')
        cantidad = request.POST.get('cantidad')        
        # Obtén la sesión actual
        sesion = request.session.get("sesion", None)
            
        if not sesion:
            messages.warning(request, "Debes iniciar sesión para agregar productos al carrito.")
            return redirect("catalogo")
        else:
            carrito = sesion.get("carrito", [])
            
            # Verifica si el producto ya está en el carrito
            for item in carrito:
                if item['id_producto'] == id_producto:
                    item['cantidad'] += cantidad
                    break
            else:
                # Si no está, agrega un nuevo producto al carrito
                producto = get_object_or_404(Productos, id=id_producto)
                carrito.append({
                    'id_producto': id_producto,
                    'nombre': producto.nombre_producto,
                    'precio': producto.precio,
                    'cantidad': cantidad,
                })
                
            # Actualiza el carrito en la sesión
            sesion["carrito"] = carrito
            request.session["sesion"] = sesion
            
            messages.success(request, "Producto agregado al carrito.")
            return redirect("catalogo")
    else:
        return render(request, "catalogo.html")

def compra(request):
    sesion = request.session.get("sesion", None)
    if not sesion:
        messages.error(request, "Debes iniciar sesión para acceder al carrito.")
        return redirect('login')

    carrito = request.session.get("carrito", [])
    productos_carrito = []
    subtotal = 0
    puede_proceder = True  # Variable para verificar si se puede proceder al pago

    # Inicializar la variable de actualización en la sesión si no existe
    if 'actualizado' not in request.session:
        request.session['actualizado'] = False

    # Manejar las acciones del formulario
    if request.method == "POST":
        action = request.POST.get("action", None)

        # Manejar la acción de Actualizar
        if action and action.startswith("update_"):
            producto_id = int(action.split("_")[1])
            nueva_cantidad = int(request.POST.get(f"cantidad_{producto_id}", 1))
            producto = get_object_or_404(Productos, id=producto_id)

            if nueva_cantidad > producto.cantidad:
                messages.error(request, f"La cantidad ingresada para {producto.nombre_producto} excede el stock disponible ({producto.cantidad}).")
            elif nueva_cantidad < 1:
                messages.error(request, "La cantidad debe ser mayor a 0.")
            else:
                for item in carrito:
                    if item['id_producto'] == producto_id:
                        item['cantidad'] = nueva_cantidad
                        request.session['actualizado'] = True  # Marcar como actualizado
                        break
                messages.success(request, f"Cantidad actualizada para {producto.nombre_producto}.")

            # Guardar el carrito actualizado en la sesión
            request.session['carrito'] = carrito
            request.session.modified = True
            return redirect('compra')  # Redirigir para evitar reenvío del formulario

        # Validar y proceder al pago
        elif action == "checkout":
            if not request.session['actualizado']:
                messages.error(request, "Debes actualizar las cantidades antes de proceder al pago.")
                return redirect('compra')

            for item in carrito:
                producto_id = item['id_producto']
                producto = get_object_or_404(Productos, id=producto_id)

                if item['cantidad'] > producto.cantidad:
                    messages.error(request, f"La cantidad ingresada para {producto.nombre_producto} excede el stock disponible ({producto.cantidad}).")
                    puede_proceder = False

            if puede_proceder:
                # Limpiar la variable de actualización después de proceder al pago
                request.session['actualizado'] = False
                messages.success(request, "Todo está correcto. Procediendo al pago...")
                return redirect('pago')  # Redirigir a la página de pago

    # Cargar los productos del carrito desde la base de datos
    for item in carrito:
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
            # Si el producto no existe, lo eliminamos del carrito
            carrito = [i for i in carrito if i['id_producto'] != item['id_producto']]
            request.session['carrito'] = carrito
            request.session.modified = True

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
        messages.error(request, "Debes iniciar sesión para acceder al carrito.")
        return redirect('login')

    # Vaciar el carrito
    request.session['carrito'] = []
    request.session.modified = True  # Asegurar que la sesión se actualice
    messages.success(request, "Todos los productos han sido eliminados de la bolsa.")
    return redirect('compra')  # Redirigir a la bolsa

def eliminar_producto(request, producto_id):
    sesion = request.session.get("sesion", None)
    if not sesion:
        messages.error(request, "Debes iniciar sesión para acceder al carrito.")
        return redirect('login')

    carrito = request.session.get("carrito", [])
    # Eliminar el producto del carrito
    carrito = [item for item in carrito if item['id_producto'] != producto_id]
    request.session['carrito'] = carrito
    request.session.modified = True  # Asegurar que la sesión se actualice
    messages.success(request, "Producto eliminado del carrito.")
    return redirect('compra')  # Redirigir a la bolsa

def detalle_producto(request, id):
    producto = get_object_or_404(Productos, id=id)
    return render(request, 'detalle_producto.html', {'producto': producto})

def obtener_carrito(request):
    carrito = request.session.get('carrito', [])
    total = sum(item['precio'] * item['cantidad'] for item in carrito)
    return JsonResponse({'success': True, 'carrito': carrito, 'total': total})

def agregar_carrito(request):
    if request.method == 'POST':
        id_producto = int(request.POST.get('id_producto'))
        cantidad = int(request.POST.get('cantidad', 1))

        # Verificar si el usuario está logueado
        sesion = request.session.get("sesion", None)
        if not sesion:
            messages.warning(request, "Debes iniciar sesión para agregar productos al carrito.")
            return redirect("catalogo")

        # Obtener el carrito de la sesión
        carrito = request.session.get("carrito", [])

        # Verificar si el producto ya está en el carrito
        producto_existente = next((item for item in carrito if item['id_producto'] == id_producto), None)
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
        request.session['carrito'] = carrito
        request.session.modified = True  # Asegurar que la sesión se actualice
        messages.success(request, "Producto agregado al carrito.")
        return redirect("catalogo")

def catalogo(request):
    # Obtiene el valor seleccionado en el <select>
    # Por defecto, vacío si no se selecciona nada
    tipo_producto = request.GET.get('tipo_producto', '')

    # Filtra los productos según el tipo seleccionado
    if tipo_producto:
        productos = Productos.objects.filter(tipo_producto=tipo_producto)
    else:
        # Si no se selecciona nada, muestra todos los productos
        productos = Productos.objects.all()

    contexto = {
        'productos': productos,
        'tipo_producto': tipo_producto,  # Pasamos el valor seleccionado al template
    }
    return render(request, 'catalogo.html', contexto)

def cobertura(request):
    return render(request, 'cobertura.html')

#ADMINISTRADOR
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
        messages.success(request, "Productos eliminado exitosamente!")

    except IntegrityError:
        messages.error(
            request, "Error: No se puede eliminar el producto porque está en uso.")
    except Exception as e:
        messages.error(request, f"Error: {e}")

        print(f"Error: {e}")

    return redirect("productos")

@validar_administrador
def agregar_productos(request):
    if request.method == "POST":
        nombre_producto = request.POST.get("nombre_producto")
        tipo_producto = request.POST.get("tipo_producto")
        medidas = request.POST.get("medidas"),
        precio = request.POST.get("precio")
        descripcion = request.POST.get("descripcion")
        cantidad = request.POST.get("cantidad")
        try:
            q = Productos(
                nombre_producto=nombre_producto,
                tipo_producto=tipo_producto,
                medidas=medidas,
                precio=precio,
                descripcion=descripcion,
                cantidad=cantidad
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
            q.precio = float(request.POST.get("precio"))
            q.descripcion = request.POST.get("descripcion")
            q.cantidad = request.POST.get("cantidad")
            q.save()
            messages.success(request, "Producto actualizado correctamente!")
            return redirect("productos")
        except Exception as e:
            print(f"Error: {e}")
            messages.error(request, f"Error: {e}")
            return redirect("editar_producto", id_productos=id_productos)
    else:
        q = Productos.objects.get(pk=id_productos)
        contexto = {"datos": q}
        print(q)

        print(q.precio)
        return render(request, "administrador/formulario_productos.html", contexto)


# ADMINISTRADOR/USUARIOS

@validar_administrador
def usuarios(request):
    u = Usuarios.objects.all()
    contexto = {
        "dato": u
    }
    return render(request, "administrador/listar_usuarios.html", contexto)


@validar_administrador
def editar_usuario(request, id_usuario):
    if request.method == "POST":
        try:
            q = Usuarios.objects.get(pk=id_usuario)
            q.cuenta = request.POST.get("cuenta")
            q.save()
            messages.success(request, "Usuario actualizado correctamente!")
            return redirect("usuarios")
        except Exception as e:
            print(f"Error: {e}")
            messages.error(request, f"Error: {e}")
            return redirect("editar_usuario", id_usuario=id_usuario)
    else:
        q = Usuarios.objects.get(pk=id_usuario)
        contexto = {"usuarios": q}
        print(q)

        print(q.contrasena)
        return render(request, "administrador/formulario_usuario.html", contexto)




#PAGOS Y CARRITO
def pago(request):
    sesion = request.session.get("sesion", None)
    if not sesion:
        messages.error(request, "Debes iniciar sesión para proceder al pago.")
        return redirect('login')

    carrito = request.session.get("carrito", [])
    productos_carrito = []
    subtotal = 0

    # Cargar los productos del carrito desde la base de datos
    for item in carrito:
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
            # Si el producto no existe, lo eliminamos del carrito
            carrito = [i for i in carrito if i['id_producto'] != item['id_producto']]
            request.session['carrito'] = carrito
            request.session.modified = True

    return render(request, 'pago.html', {
        'productos_carrito': productos_carrito,
        'total': subtotal
    })

def procesar_pago(request):
    if request.method == "POST":
        sesion = request.session.get("sesion", None)
        if not sesion:
            messages.error(request, "Debes iniciar sesión para realizar un pago.")
            return redirect('login')

        carrito = sesion.get("carrito", [])
        errores = []

        # Validar cantidades disponibles
        for item in carrito:
            producto = get_object_or_404(Productos, id=item['id_producto'])
            if item['cantidad'] > producto.cantidad:
                errores.append(f"No hay suficiente stock para {producto.nombre_producto}. Disponible: {producto.cantidad}.")

        if errores:
            for error in errores:
                messages.error(request, error)
            return redirect('compra')

        # Procesar el pago si no hay errores
        messages.success(request, "Pago realizado con éxito. ¡Gracias por tu compra!")
        return redirect('index')
    else:
        messages.error(request, "Hubo un error al procesar el pago.")
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
        u.direccion = request.POST.get('ciudad')
        fecha_nacimiento = request.POST.get('fecha_nacimiento')

        # Validar mayoría de edad
        if fecha_nacimiento:
            fecha_nacimiento = date.fromisoformat(fecha_nacimiento)
            hoy = date.today()
            edad = hoy.year - fecha_nacimiento.year - ((hoy.month, hoy.day) < (fecha_nacimiento.month, fecha_nacimiento.day))
            if edad < 18:
                messages.error(request, "Debes ser mayor de edad para editar tu perfil.")
                return render(request, 'editar_perfil.html', {'user': u})

            u.fecha_nacimiento = fecha_nacimiento

        # Manejar la actualización de la foto
        if 'foto' in request.FILES:
            u.foto = request.FILES['foto']

        # Guardar los cambios
        u.save()
        messages.success(request, "Perfil actualizado con éxito.")
        return redirect('editar_perfil')  # Redirige al inicio o a otra página

    return render(request, 'editar_perfil.html', {'user': u})



#PAGOS


def procesar_pago(request):
    if request.method == "POST":
        sesion = request.session.get("sesion", None)
        if not sesion:
            messages.error(request, "Debes iniciar sesión para realizar un pago.")
            return redirect('login')

        usuario = Usuarios.objects.get(id=sesion['id'])
        if not usuario.fecha_nacimiento:
            messages.error(request, "Debes actualizar tu perfil con tu fecha de nacimiento antes de proceder al pago.")
            return redirect('editar_perfil')

        carrito = request.session.get("carrito", [])
        errores = []
        total_pagado = 0

        # Crear la factura
        factura = Facturas.objects.create(
            cliente=usuario,
            valor_pedido=0,  # Se calculará después
            valor_total=0,  # Se calculará después
            fecha_factura=date.today(),
            hora_factura=date.today().strftime("%H:%M:%S")
        )

        # Crear los detalles de la factura
        for item in carrito:
            producto = get_object_or_404(Productos, id=item['id_producto'])
            if item['cantidad'] > producto.cantidad:
                errores.append(f"No hay suficiente stock para {producto.nombre_producto}. Disponible: {producto.cantidad}.")
            else:
                producto.cantidad -= item['cantidad']
                producto.save()

                subtotal = producto.precio * item['cantidad']
                total_pagado += subtotal

                cantidad = int(item['cantidad'])  # Convierte a entero si es necesario
                DetallesFacturas.objects.create(
                    producto=producto,
                    factura=factura,
                    subtotal=subtotal
                )

        if errores:
            for error in errores:
                messages.error(request, error)
            return redirect('compra')

        # Actualizar el total de la factura
        factura.valor_pedido = total_pagado
        factura.valor_total = total_pagado
        factura.save()

        # Limpiar el carrito
        request.session['carrito'] = []
        request.session.modified = True

        messages.success(request, f"Pago realizado con éxito. Factura #{factura.id} generada.")
        return redirect('facturas')
    else:
        messages.error(request, "Hubo un error al procesar el pago.")
        return redirect('pago')
    
    
