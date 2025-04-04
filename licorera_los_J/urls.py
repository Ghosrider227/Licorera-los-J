from django.urls import path
from . import views

urlpatterns = [
    #Principales
    path('', views.index, name='index'),
    path('login/', views.login, name='login'),
    path("logout/", views.logout, name="logout"),
    path('register/', views.register, name='register'),
    path('catalogo/', views.catalogo, name='catalogo'),
    path('cart/', views.cart, name='cart'),
    path('cobertura/', views.cobertura, name='cobertura'),
    path('api/agregar_carrito/', views.agregar_carrito, name='agregar_carrito'),
    path('api/carrito/', views.obtener_carrito, name='obtener_carrito'),
]