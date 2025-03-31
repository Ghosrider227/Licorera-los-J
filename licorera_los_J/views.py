from django.shortcuts import render, redirect
from .models import *
from django.contrib import messages


from django.db.utils import IntegrityError
from django.contrib import messages

from django.core.mail import send_mail
from django.conf import settings

from .utils import *



# Create your views here.

def index(request):
    # Traigo la informacion de la BD y se la mando al index con el contexto
    p = Productos.objects.all()
    contexto = {
        'data' : p,
    }
    return render(request, 'index.html', contexto)

def login(request):
    return render(request, 'login.html')

def logout(request):
    try:
        del request.session["sesion"]
        return redirect("login")
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
        if clave_actual == q.password:      # cambiar esto por decrypt..
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
        return render(request, "usuarios/cambiar_clave.html")



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
                        contrasena = contrasena,
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
    query = request.GET.get('q', '')  # Obtén la consulta de búsqueda
    if query:
        productos = Productos.objects.filter(nombre__icontains=query)  # Filtra por nombre
    else:
        productos = Productos.objects.all()  # Muestra todos los productos si no hay búsqueda
    return render(request, 'catalogo.html', {'productos': productos})
