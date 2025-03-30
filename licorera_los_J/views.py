from django.shortcuts import render, redirect
from .models import *
from django.contrib import messages
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