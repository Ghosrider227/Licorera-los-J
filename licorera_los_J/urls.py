from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    #Principales
    path('index/', views.index, name='index'),
    path('', views.verificacion, name='verificacion'),
    path('login/', views.login, name='login'),
    path("logout/", views.logout, name="logout"),
    path('register/', views.register, name='register'),
    path('catalogo/', views.catalogo, name='catalogo'),
    path('compra/', views.compra, name='compra'),
    path('pago/', views.pago, name='pago'),
    path('procesar_pago/', views.procesar_pago, name='procesar_pago'),
    path('producto/<int:id>/', views.detalle_producto, name='detalle_producto'),
    path('cobertura/', views.cobertura, name='cobertura'),
    path('api/agregar_carrito/', views.agregar_carrito, name='agregar_carrito'),
    path('api/carrito/', views.obtener_carrito, name='obtener_carrito'),

    #ADMINISTRADOR/PRODUCTOS
    path("productos/", views.productos, name='productos'),
    path("eliminar_productos/<int:id_producto>/", views.eliminar_productos, name='eliminar_productos'),
    path("agregar_productos/", views.agregar_productos, name="agregar_productos"),
    path("editar_productos/<int:id_productos>/", views.editar_productos, name='editar_producto'),

    #ADMINISTRADOR/USUARIOS
    path("usuarios/", views.usuarios, name='usuarios'),
    path("editar_usuario/<int:id_usuario>/", views.editar_usuario, name='editar_usuario'),

    #ADMINISTRADOR/Facturas
    path('facturas/', views.facturas, name='facturas'),  # Vista para listar facturas


    #COMPRAS
    path('vaciar_bolsa/', views.vaciar_bolsa, name='vaciar_bolsa'),
    path('eliminar_producto/<int:producto_id>/', views.eliminar_producto, name='eliminar_producto'),
    
    
    path('editar_perfil/', views.editar_perfil, name='editar_perfil'),
    
    
    #Facturas
     
    path('procesar_pago/', views.procesar_pago, name='procesar_pago'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)