from django.shortcuts import render, redirect
from .models import *
from django.db.utils import IntegrityError
from django.contrib import messages
from django.conf import settings
import re

from .utils import *
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
                    }
                else:
                    request.session["sesion"] = {
                        "id" : u.id,
                        "nombre" : u.nombre,
                        "cuenta" : u.cuenta,
                        "email" : u.email,
                    }
                messages.success(request, "Bienvenido")
                return redirect("index")
            else:
                raise Usuarios.DoesNotExist()
            
        except Usuarios.DoesNotExist:
            messages.warning(request, "Contrasena incorrecta")
            request.session["sesion"] = None
        except Exception as e:
            messages.warning(request, f"No se pudo iniciar sesión, intente de nuevo",{e})
            request.session["sesion"] = None
        return redirect("login")
    else:
        verificar = request.session.get('sesion', False)

        if verificar:
            return redirect('index')
        else:
            return render(request, 'login.html')

def logout(request):
    try:
        del request.session["sesion"]
        return redirect("login")
    except Exception as e:
        messages.info(request, "No se pudo cerrar sesión, intente de nuevo")
        return redirect("inicio")


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
        
        if not re.match(r'^[A-Za-z\s]+$', nombre):
            messages.warning(request, 'El nombre solo debe contener letras')
            return redirect('register')
        
        if not re.match(r'^[A-Za-z\s]+$', apellido):
            messages.warning(request, 'El apellido solo debe contener letras')
            return redirect('register')
        
        if not telefono.isdigit():
            messages.warning(request, 'El telefono debe contener solo numeros')
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
                    return redirect('login')
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

def cart(request):
    return render(request, 'cart.html')

def cobertura(request):
    return render(request, 'cobertura.html')

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



#ADMINISTRADOR
def productos(request):
    # all() -> todos      filter() -> algunos      get() -> 1 único
    q = Productos.objects.all()
    contexto = {
        "data": q
    }
    return render(request, "administrador/listar_productos.html",contexto)

def eliminar_productos(request, id_productos):
    # Obtener la instancia
    try:
        q = Productos.objects.get(pk = id_productos)
        q.delete()
        messages.success(request, "Productos eliminado exitosamente!")
    
    except Exception as e:
        messages.error(request, f"Error: {e}")

    return redirect("productos")

def agregar_productos(request):
    if request.method == "POST":
        nombre_producto = request.POST.get("nombre_producto")
        tipo_producto = request.POST.get("tipo_producto")
        precio = request.POST.get("precio")
        descripcion = request.POST.get("descripcion")
        cantidad = request.POST.get("cantidad")
        try:
            q = Productos(
                nombre_producto=nombre_producto,
                tipo_producto=tipo_producto,
                precio=precio,
                descripcion=descripcion,
                cantidad=cantidad
            )
            q.save()
            messages.success(request, "Producto agregado exitosamente!")
            return redirect("administrador/productos")
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
    



