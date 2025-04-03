from django.shortcuts import render, redirect
from .models import *
from django.db.utils import IntegrityError
from django.contrib import messages
from django.conf import settings

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
        fecha_nacimiento = request.POST.get('fecha_nacimiento')
        direccion = request.POST.get('direccion')
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
                        fecha_nacimiento = fecha_nacimiento,
                        direccion = direccion
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
        productos = Productos.objects.filter(tipo_de_producto__icontains=tipo_producto)
    else:
        # Si no se selecciona nada, muestra todos los productos
        productos = Productos.objects.all()
    
    contexto = {
        'productos': productos,
        'tipo_producto': tipo_producto,  # Pasamos el valor seleccionado al template
    }
    return render(request, 'catalogo.html', contexto)
