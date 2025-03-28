from django.shortcuts import render
from .models import *
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
