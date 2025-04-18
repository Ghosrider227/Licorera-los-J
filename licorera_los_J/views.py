from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import *
import re
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from .utils import *
from django.views.decorators.csrf import csrf_exempt
import json
from django.db.utils import IntegrityError
from django.conf import settings
from django.http import JsonResponse

def index(request):
    # Traigo la informacion de la BD y se la mando al index con el contexto
    p = Productos.objects.all()
    contexto = {
        'data' : p,
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
                        "id" : u.id,
                        "nombre" : u.nombre,
                        "cuenta" : u.cuenta,
                        "email" : u.email,
                        "carrito" : [],
                    }
                else:
                    request.session["sesion"] = {
                        "id" : u.id,
                        "nombre" : u.nombre,
                        "cuenta" : u.cuenta,
                        "email" : u.email,
                        "fecha_nacimiento" : u.fecha_nacimiento,
                        "carrito" : [],
                    }
                return redirect("index")
            else:
                raise Usuarios.DoesNotExist()
        except Usuarios.DoesNotExist:
            messages.warning(request, "Correo incorrecto o Contrasena incorrecta")
            request.session["sesion"] = None
        except Exception as e:
            messages.warning(request, f"Error: ",{e})
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
            messages.warning(request, 'El telefono debe contener solo numeros y tener 10 digitos')
            return redirect('register')
        
        if u.filter(email=email).exists():
            messages.warning(request, 'El correo ya esta registrado')
            return redirect('register')
        else:
            if contrasena == confirmar_contrasena:
                try:
                    u = Usuarios (
                        nombre = nombre,
                        apellido = apellido,
                        cuenta = cuenta,
                        email = email,
                        contrasena = hash_password(contrasena),
                        telefono = telefono,
                        fecha_nacimiento = None,
                        direccion = None
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

def catalogo(request):
    return render(request, 'catalogo.html')


@login_required
def compra(request):
   # Obtén el carrito de la sesión
    carrito = request.session.get('carrito', {})
    productos_carrito = []

    # Carga los productos del carrito desde la base de datos
    for producto_id, cantidad in carrito.items():
        producto = get_object_or_404(Productos, id=producto_id)
        productos_carrito.append({
            'producto': producto,
            'cantidad': cantidad,
            'subtotal': producto.precio * cantidad
        })

    # Productos sugeridos (puedes personalizar esta lógica)
    productos_sugeridos = Productos.objects.all()[:4]

    return render(request, 'compra.html', {
        'productos_carrito': productos_carrito,
        'productos_sugeridos': productos_sugeridos
    })

def detalle_producto(request, id):
    producto = get_object_or_404(Productos, id=id)
    return render(request, 'detalle_producto.html', {'producto': producto})

def cobertura(request):
    return render(request, 'cobertura.html')

def obtener_carrito(request):
    carrito = request.session.get('carrito', [])
    total = sum(item['precio'] * item['cantidad'] for item in carrito)
    return JsonResponse({'success': True, 'carrito': carrito, 'total': total})

def agregar_carrito(request):
    if request.method == 'POST':
        id_producto = request.POST.get('id_producto')
        cantidad = int(request.POST.get('cantidad', 1))
        return render(request, 'index.html')

def catalogo(request):
    # Obtiene el valor seleccionado en el <select>
    tipo_producto = request.GET.get('tipo_producto', '')  # Por defecto, vacío si no se selecciona nada
    
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



def validar_administrador(request):
    sesion= request.session.get("sesion", None)
    if not sesion or sesion.get("cuenta") != "1":
        messages.error(request, "No tienes permisos para acceder")
        return False
    return True




#ADMINISTRADOR
def productos(request):
    # all() -> todos      filter() -> algunos      get() -> 1 único
    q = Productos.objects.all()
    contexto = {
        "data": q
    }
    return render(request, "administrador/listar_productos.html",contexto)

def eliminar_productos(request, id_producto):
    # Obtener la instancia
    try:
        q = Productos.objects.get(pk = id_producto)
        q.delete()
        messages.success(request, "Productos eliminado exitosamente!")
    
    except IntegrityError:
        messages.error(request, "Error: No se puede eliminar el producto porque está en uso.")
    except Exception as e:
        messages.error(request, f"Error: {e}")
        
        print(f"Error: {e}")

    return redirect("productos")

def agregar_productos(request):
    if request.method == "POST":
        nombre_producto = request.POST.get("nombre_producto")
        tipo_producto = request.POST.get("tipo_producto")
        medidas=request.POST.get("medidas"),
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
    
    
def editar_productos(request, id_productos):
    if request.method == "POST":
        try:
            q = Productos.objects.get(pk=id_productos)

            q.nombre_producto=request.POST.get("nombre_producto")
            q.tipo_producto=request.POST.get("tipo_producto")
            q.precio=float(request.POST.get("precio"))
            q.descripcion=request.POST.get("descripcion")
            q.cantidad=request.POST.get("cantidad")
            q.save()
            messages.success(request, "Producto actualizado correctamente!")
            return redirect("productos")
        except Exception as e:
            print (f"Error: {e}")
            messages.error(request, f"Error: {e}")
            return redirect("editar_producto", id_productos=id_productos)
    else:
        q = Productos.objects.get(pk=id_productos)
        contexto = {"datos": q}
        print(q)
        
        print (q.precio)
        return render(request, "administrador/formulario_productos.html", contexto)


#ADMINISTRADOR/USUARIOS

def usuarios(request):
    u = Usuarios.objects.all()
    contexto = {
        "dato": u
    }
    return render(request, "administrador/listar_usuarios.html",contexto)

def editar_usuario(request, id_usuario):
    if request.method == "POST":
        try:
            q = Usuarios.objects.get(pk=id_usuario)
            q.cuenta=request.POST.get("cuenta")
            q.save()
            messages.success(request, "Usuario actualizado correctamente!")
            return redirect("usuarios")
        except Exception as e:
            print (f"Error: {e}")
            messages.error(request, f"Error: {e}")
            return redirect("editar_usuario", id_usuario=id_usuario)
    else:
        q = Usuarios.objects.get(pk=id_usuario)
        contexto = {"usuarios": q}
        print(q)
        
        print (q.contrasena)
        return render(request, "administrador/formulario_usuario.html", contexto)