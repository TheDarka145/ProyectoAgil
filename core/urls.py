from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from .views import suscripcion

urlpatterns=[
    path('', views.index, name="index"),
    path('productos/', views.productos, name="productos"),
    path('contacto/', views.contacto, name="contacto"),
    path('registrar/', views.registrar, name="registrar"),
    path('logout/', views.cerrar, name="cerrar"),
    path('perfil/', views.perfil, name='perfil'),
    path('crear/', views.crear, name="crear"),
    path('detalle/<id>/', views.detalle, name="detalle"),
    path('modificar/<id>/', views.modificar, name="modificar"),
    path('eliminar/<id>/', views.eliminar, name="eliminar"),
    path('tienda/', views.tienda, name="tienda"),
    path('agregar/<id>', views.agregar_producto, name="agregar"),
    path('limpiar/', views.limpiar_carrito, name="limpiar"),
    path('generarBoleta/', views.generarBoleta,name="generarBoleta"),
    path('restar/<id>', views.restar_producto, name="restar"),
    path('Nosotros/', views.Nosotros, name="Nosotros"),
    path('Carrito/', views.carrito, name="carrito"),
    path('password_reset/',auth_views.PasswordResetView.as_view(),name='password_reset'),
    path('password_reset/done/',auth_views.PasswordResetDoneView.as_view(),name='password_reset_done'),
    path('reset/<uidb64>/<token>/',auth_views.PasswordResetConfirmView.as_view(),name='password_reset_confirm'),
    path('reset/done/',auth_views.PasswordResetCompleteView.as_view(),name='password_reset_complete'),
    path('boleta/', views.listar_boletas, name='listar_boletas'),
    path('editar/', views.editarperfil, name='editar'),
    path('detalle_boleta/<int:id_boleta>/', views.detalle_boleta_view, name='detalle_boleta'),
    path('api/tasa-cambio/', views.tasa_cambio, name='tasa_cambio'),
    path('suscripcion/', suscripcion, name='suscripcion'),
    path('webpay/iniciar/', views.redirigir_a_webpay, name='webpay_iniciar'),
    path('webpay/respuesta/', views.webpay_respuesta, name='webpay_respuesta'),	
    path('pago/procesar/', views.procesar_pago, name='procesar_pago'),
    path('pago/transferencia/', views.mostrar_transferencia, name='mostrar_transferencia'),
    path('exportar-boletas/', views.exportar_boletas_excel, name='exportar_boletas_excel'),
]
    
