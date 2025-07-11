from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import logout
from django.contrib.auth import authenticate,login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import  RegistroUserForm
from .models import Categoria, Planta, Boleta, detalle_boleta
from .forms import PlantaForm, RegistroUserForm, EditProfileForm
from core.compras import Carrito
from django.core.paginator import Paginator
from core.utils import obtener_tasa_cambio
from django.http import HttpResponse, JsonResponse
from django.core.mail import send_mail
from django.conf import settings
from transbank.webpay.webpay_plus.transaction import Transaction
from transbank.common.options import WebpayOptions
from transbank.common.integration_type import IntegrationType
from django.views.decorators.csrf import csrf_exempt
from random import randint
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.mail import EmailMultiAlternatives
from django.db.models import Sum, Avg, F, FloatField
import openpyxl

def index(request):
    return render(request, 'index.html')

@login_required
def productos(request):
    if not request.user.is_staff:
        return render(request, '404.html')

    datos = Planta.objects.all()
    categorias = Categoria.objects.all()

    buscar = request.GET.get('buscar')
    if buscar:
        datos = datos.filter(nombre__icontains=buscar)

    categoria_seleccionada = request.GET.get('categoria')
    if categoria_seleccionada:
        datos = datos.filter(categoria__idCategoria=categoria_seleccionada)

    total_cantidad = datos.aggregate(total_stock=Sum('stock'))['total_stock'] or 0

    total_valor = datos.aggregate(
        total_valor=Sum(F('stock') * F('precio'), output_field=FloatField())
    )['total_valor'] or 0

    return render(request, 'productos.html', {
        "datos": datos,
        "categorias": categorias,
        "total_cantidad": total_cantidad,
        "total_valor": total_valor,
    })


@login_required
def contacto(request):
    return render(request, 'contacto.html')

def registrar(request):
    data={                          
        'form': RegistroUserForm()
    }
    if request.method=="POST":
        formulario = RegistroUserForm(data=request.POST)
        if formulario.is_valid():
            formulario.save()       
            user = authenticate(username=formulario.cleaned_data["username"], 
                    password=formulario.cleaned_data["password1"])
            login(request,user)
            return redirect('index') 
        data["form"]=formulario           
    return render(request, 'registration/registrar.html',data)

def cerrar(request):
    logout(request)
    return redirect('index')

@login_required
def perfil(request):
    usuario = request.user
    context = {
        'usuario': usuario,
        'email': usuario.email,
        'nombre': usuario.first_name,
        'apellido': usuario.last_name,

    }
    return render(request, 'perfil.html', context)

@login_required
def crear(request):
    if request.method=='POST':
        plantaForm = PlantaForm(request.POST, request.FILES)
        if plantaForm.is_valid():
            plantaForm.save()         
            return redirect ('productos')
    else:
        plantaForm = PlantaForm()
    return render (request, 'crear.html', {'plantaForm': plantaForm })  


def detalle(request, id):
    planta = get_object_or_404(Planta, idPlanta=id)   
    return render(request, 'detalle.html', {'planta': planta})

@login_required
def modificar(request, id):
    planta = Planta.objects.get(idPlanta=id)  
    datos ={
        'forModificar': PlantaForm(instance=planta), 
        'planta': planta 
    }
    if request.method=='POST':
        formulario = PlantaForm(request.POST,request.FILES,instance=planta)
        if formulario.is_valid():
            formulario.save()           
            return redirect('productos')
    return render(request, 'modificar.html', datos)

@login_required
def eliminar(request, id):
    planta = get_object_or_404(Planta, idPlanta=id)   
    if request.method=='POST':
        if 'elimina' in request.POST:
            planta.delete()           
            return redirect('productos')
    return render(request, 'eliminar.html', {'planta': planta})    

def tienda(request):
    planta = Planta.objects.all()
    datos={
        'planta':planta
    }
    return render(request, 'tienda.html', datos)

@login_required
def agregar_producto(request,id):
    carrito_compra= Carrito(request)
    planta = Planta.objects.get(idPlanta=id)
    carrito_compra.agregar(planta=planta)
    return redirect('tienda')

def eliminar_producto(request, id):
    carrito_compra= Carrito(request)
    planta = Planta.objects.get(idPlanta=id)
    carrito_compra.eliminar(planta=planta)
    return redirect('tienda')

def restar_producto(request, id):
    carrito_compra= Carrito(request)
    planta = Planta.objects.get(idPlanta=id)
    carrito_compra.restar(planta=planta)
    return redirect('tienda')

def limpiar_carrito(request):
    carrito_compra= Carrito(request)
    carrito_compra.limpiar()
    return redirect('tienda')

@login_required
def generarBoleta(request):
    carrito = Carrito(request)
    total_carrito = carrito.total() 
    tipo_envio = request.POST.get('tipo_envio', 'retiro')  

    costo_envio = 0
    if tipo_envio == "envio":  
        costo_envio = 4990  
        total_carrito += costo_envio  

    boleta = Boleta(total=total_carrito)
    boleta.save()

    productos = []
    for key, value in request.session['carrito'].items():
        producto = Planta.objects.get(idPlanta=value['planta_id'])
        cant = value['cantidad']
        subtotal = cant * int(value['precio'])

        if producto.stock >= cant:
            producto.stock -= cant
            producto.save()
            verificar_stock_bajo(producto)
        else:
            messages.error(request, f"Stock insuficiente para {producto.nombre}. Solo queda {producto.stock} disponible")
            return redirect('carrito')

        detalle = detalle_boleta(id_boleta=boleta, id_producto=producto, cantidad=cant, subtotal=subtotal)
        detalle.save()
        productos.append(detalle)

    datos = {
        'productos': productos,
        'fecha': boleta.fechaCompra,
        'total': total_carrito,  
        'costo_envio': costo_envio,
        'tipo_envio': tipo_envio.upper(),
    }

    request.session['boleta'] = boleta.id_boleta
    carrito.limpiar()

    return render(request, 'detallecarrito.html', datos)

def Nosotros(request):
    return render(request, 'sobrenosotros.html')

@login_required
def carrito(request):
    carrito_compra = Carrito(request)
    total = carrito_compra.total()
    return render(request, 'carritomenu.html', {
        'total_carrito': total
    })


@login_required
def listar_boletas(request):
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')

    boletas = Boleta.objects.all().order_by('-fechaCompra')

    if fecha_inicio and fecha_fin:
        boletas = boletas.filter(fechaCompra__range=[fecha_inicio, fecha_fin])

    total_ventas = boletas.aggregate(Sum('total'))['total__sum'] or 0
    cantidad_boletas = boletas.count()
    promedio_venta = boletas.aggregate(Avg('total'))['total__avg'] or 0

    paginator = Paginator(boletas, 10)
    page_number = request.GET.get('page')
    boletas_page = paginator.get_page(page_number)

    return render(request, 'listar_boletas.html', {
        'boletas': boletas_page,
        'total_ventas': total_ventas,
        'cantidad_boletas': cantidad_boletas,
        'promedio_venta': promedio_venta,
    })

@login_required
def editarperfil(request):
    if request.method == 'POST':
        form = EditProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, '¡Tu perfil ha sido actualizado!')
            return redirect('perfil')  
    else:
        form = EditProfileForm(instance=request.user)
    
    return render(request, 'editarperfil.html', {'form': form})

def tienda(request):
    planta = Planta.objects.all()
    categorias = Categoria.objects.all()

    tasa_cambio = obtener_tasa_cambio()
    moneda = request.session.get('moneda', 'CLP')

    if request.method == 'POST':
        moneda = request.POST.get('currency', 'CLP')  
        request.session['moneda'] = moneda  


    if moneda == 'USD':
        for p in planta:
            p.precio = round(p.precio / tasa_cambio, 2)  
        tasa_cambio_texto = "USD"
    else:
        tasa_cambio_texto = "CLP"

    categoria_id = request.GET.get('categoria')
    if categoria_id:
        planta = planta.filter(categoria__idCategoria=categoria_id)

    buscar = request.GET.get('buscar')
    if buscar:
        planta = planta.filter(nombre__icontains=buscar)

    paginator = Paginator(planta, 8)  
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'tienda.html', {
        'planta': page_obj,  
        'categorias': categorias,
        'categoria_seleccionada': categoria_id,
        'tasa_cambio': tasa_cambio,
        'moneda': moneda,
        'tasa_cambio_texto': tasa_cambio_texto
    })


@login_required
def detalle_boleta_view(request, id_boleta):
    boleta = get_object_or_404(Boleta, id_boleta=id_boleta)
    detalles = detalle_boleta.objects.filter(id_boleta=boleta)

    return render(request, 'detalle_boleta.html', {'boleta': boleta, 'detalles': detalles})

def tasa_cambio(request):
    tasa_cambio = obtener_tasa_cambio()
    return JsonResponse({'tasa_cambio': tasa_cambio})

def suscripcion(request):
    if request.method == "POST":
        correo_usuario = request.POST.get("email")

        if not correo_usuario:
            return JsonResponse({"success": False, "message": "Por favor, ingresa un correo."}, status=400)

        asunto = "🎉 ¡Gracias por suscribirte a Maestranzas!"
        mensaje = "Gracias por unirte a Maestranzas. Pronto recibirás nuestras mejores promociones."
        
        html_mensaje = """
        <div style="font-family:Arial, sans-serif; text-align:center; background:#f9f9f9; padding:20px;">
            <img src="https://chatgpt.com/backend-api/public_content/enc/eyJpZCI6Im1fNjg3MDNkODBmMjRjODE5MTg2OTRmNWQ3ZjkwMWQ5MzU6ZmlsZV8wMDAwMDAwMGQ1ZTQ2MWY5OTgwNGNlNDYxYWRiYTNmMiIsInRzIjoiNDg2NzIwIiwicCI6InB5aSIsInNpZyI6IjkzYTk1MWNiMGJiNzBkNTNiMjMzOTNkZDUwOTQyZmU2YjcxZWE2OGRiYzFkYTZiNjQyYmE4N2UwMjBhNjgzZmEiLCJ2IjoiMCIsImdpem1vX2lkIjpudWxsfQ==" alt="Maestranzas" width="120" />
            <h2 style="color:#1A5276;">¡Gracias por suscribirte a Maestranzas!</h2>
            <p style="font-size:16px;">Nos alegra que formes parte de nuestra comunidad.</p>
            <p style="font-size:16px;">A partir de ahora, te llegarán ofertas exclusivas y novedades sobre nuestros productos.</p>
            <img src="https://media3.giphy.com/media/v1.Y2lkPTc5MGI3NjExMnYyejJrOTh4YXo4MnA3ejB4a25vcGw5YWkybXd5bWF4YmhuOXBlaSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/zs19LOebTcTHCZhedn/giphy.gif" alt="Suscripción exitosa" style="width:80%; max-width:400px; margin:20px auto;" />
            <p><a href="https://7eb92a94-aaaf-4865-903f-f176f280be41-00-lfw5zt0l473s.picard.replit.dev/" style="display:inline-block; background-color:#1A5276; color:white; padding:10px 20px; text-decoration:none; border-radius:5px;">Visita nuestra tienda</a></p>
            <p style="color:gray; font-size:12px;">Este correo fue enviado por Maestranzas. Gracias por confiar en nosotros.</p>
        </div>
        """

        try:
            send_mail(
                subject=asunto,
                message=mensaje,  
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[correo_usuario],
                fail_silently=False,
                html_message=html_mensaje  
            )
            return JsonResponse({"success": True, "message": "¡Gracias por suscribirte! Revisa tu correo."})
        except Exception as e:
            return JsonResponse({"success": False, "message": f"Error: {str(e)}"}, status=500)

    return JsonResponse({"success": False, "message": "Método no permitido."}, status=405)

transaction = Transaction(
    WebpayOptions(
        commerce_code='597055555532',
        api_key='579B532A7440BB0C9079DED94D31EA1615BACEB56610332264630D42D0A36B1C',
        integration_type=IntegrationType.TEST
    )
)
@login_required
def redirigir_a_webpay(request):
    
    carrito_compra = Carrito(request)
    total = carrito_compra.total()
    tipo_envio = request.POST.get('tipo_envio', 'retiro')  

    costo_envio = 0
    if tipo_envio == "envio":  
        costo_envio = 4990  
        total += costo_envio 
    try:
        response = transaction.create(
            buy_order=str(randint(100000, 999999)),
            session_id=str(randint(100000, 999999)),
            amount=total,
            return_url='https://56c92eb4-6fb3-4986-a4ec-bf1e200abad0-00-dn6zyxf59efw.janeway.replit.dev/webpay/respuesta/'  
        )
        return render(request, 'webpay_redirigir.html', {
            'url': response['url'],
            'token': response['token']
        })
    except Exception as e:
        return render(request, '404.html', {'mensaje': f'Error al crear transacción: {e}'})

@csrf_exempt  
def webpay_respuesta(request):
    token = request.POST.get('token_ws') or request.GET.get('token_ws')
    if not token:
        return render(request, '404.html', {'mensaje': 'Token no recibido desde Webpay'})

    try:
        result = transaction.commit(token)
        
        if result['status'] != 'AUTHORIZED':
            return render(request, 'webpay_respuesta.html', {'resultado': result})

        carrito = Carrito(request)
        total_carrito = carrito.total() 
        tipo_envio = request.session.get('tipo_envio', 'retiro') 

        costo_envio = 0
        if tipo_envio == "envio":  
            costo_envio = 4990  
            total_carrito += costo_envio  

        boleta = Boleta(total=total_carrito)
        boleta.save()

        productos = []
        for key, value in request.session['carrito'].items():
            producto = Planta.objects.get(idPlanta=value['planta_id'])
            cant = value['cantidad']
            subtotal = cant * int(value['precio'])

            if producto.stock >= cant:
                producto.stock -= cant
                producto.save()
                verificar_stock_bajo(producto)
            else:
                messages.error(request, f"Stock insuficiente para {producto.nombre}. Solo queda {producto.stock} disponible")
                return redirect('carrito')

            detalle = detalle_boleta(id_boleta=boleta, id_producto=producto, cantidad=cant, subtotal=subtotal)
            detalle.save()
            productos.append(detalle)

        datos = {
            'productos': productos,
            'fecha': boleta.fechaCompra,
            'total': total_carrito,
            'costo_envio': costo_envio,
            'tipo_envio': tipo_envio.upper(),
        }

        subject = f'Comprobante de compra - Boleta #{boleta.id_boleta}'
        html_message = render_to_string('comprobante_compra.html', datos)
        plain_message = strip_tags(html_message)
        from_email = None
        to_email = [request.user.email]

        send_mail(subject, plain_message, from_email, to_email, html_message=html_message)

        request.session['boleta'] = boleta.id_boleta
        carrito.limpiar()

        return render(request, 'detallecarrito.html', datos)

    except Exception as e:
        return render(request, '404.html', {'mensaje': f'Error al confirmar transacción: {e}'})
@login_required
@csrf_exempt
def procesar_pago(request):
    if request.method == 'POST':
        metodo_pago = request.POST.get('metodo_pago')
        tipo_envio = request.POST.get('tipo_envio')

        request.session['tipo_envio'] = tipo_envio
        request.session['metodo_pago'] = metodo_pago

        if metodo_pago == 'debito_credito':
            return redirect('webpay_iniciar')
        elif metodo_pago == 'transferencia':
            return redirect('mostrar_transferencia')
        else:
            messages.error(request, 'Método de pago no válido.')
            return redirect('carrito')
        
@login_required
def mostrar_transferencia(request):
    carrito = Carrito(request)
    total_carrito = carrito.total()
    tipo_envio = request.session.get('tipo_envio', 'retiro')

    costo_envio = 0
    if tipo_envio == "envio":
        costo_envio = 4990
        total_carrito += costo_envio

    boleta = Boleta(total=total_carrito)
    boleta.save()

    productos = []
    for key, value in request.session['carrito'].items():
        producto = Planta.objects.get(idPlanta=value['planta_id'])
        cant = value['cantidad']
        subtotal = cant * int(value['precio'])

        if producto.stock >= cant:
            producto.stock -= cant
            producto.save()
            verificar_stock_bajo(producto)
        else:
            messages.error(request, f"Stock insuficiente para {producto.nombre}. Solo queda {producto.stock} disponible")
            return redirect('carrito')

        detalle = detalle_boleta(id_boleta=boleta, id_producto=producto, cantidad=cant, subtotal=subtotal)
        detalle.save()
        productos.append(detalle)

    datos = {
        'boleta': boleta,
        'productos': productos,
        'fecha': boleta.fechaCompra,
        'total': total_carrito,
        'costo_envio': costo_envio,
        'tipo_envio': tipo_envio.upper(),
        'banco': 'Banco Estado',
        'cuenta': '123456789',
        'rut': '11.111.111-1',
        'titular': 'Maestranzas',
        'correo': 'servicio.vivero.duoc@gmail.com'
    }
    subject = f'Comprobante de compra - Boleta #{boleta.id_boleta}'
    html_message = render_to_string('comprobante_compra.html', datos)
    plain_message = strip_tags(html_message)
    from_email = None
    to_email = [request.user.email]

    send_mail(subject, plain_message, from_email, to_email, html_message=html_message)

    request.session['boleta'] = boleta.id_boleta
    carrito.limpiar()

    return render(request, 'detalle_transferencia.html', datos)

def verificar_stock_bajo(producto):
    UMBRAL_STOCK_BAJO = 5
    if producto.stock <= UMBRAL_STOCK_BAJO:
        asunto = f"⚠️ Alerta de stock bajo: {producto.nombre}"
        from_email = settings.EMAIL_HOST_USER
        to_email = ['servicio.vivero.duoc@gmail.com']

        texto_plano = (
            f"El producto '{producto.nombre}' tiene un stock bajo.\n"
            f"Quedan solo {producto.stock} unidades disponibles.\n\n"
            "Por favor, considera reponer el inventario a la brevedad."
        )

        html_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif; background-color: #f9f9f9; padding: 20px;">
                <div style="max-width: 600px; margin: auto; background: white; border-radius: 8px; padding: 20px; border: 1px solid #ddd;">
                    <h2 style="color: #d9534f;">⚠️ Alerta de stock bajo</h2>
                    <p>El producto <strong>{producto.nombre}</strong> tiene un stock bajo.</p>
                    <p><strong>Stock disponible:</strong> {producto.stock} unidad(es)</p>
                    <p>Por favor, considera reponer el inventario a la brevedad para evitar faltantes.</p>
                    <hr style="border:none; border-top:1px solid #eee; margin: 20px 0;">
                    <p style="font-size: 12px; color: #666;">Este es un correo automático generado por el sistema de inventario.</p>
                </div>
            </body>
        </html>
        """

        try:
            msg = EmailMultiAlternatives(asunto, texto_plano, from_email, to_email)
            msg.attach_alternative(html_content, "text/html")
            msg.send()
        except Exception as e:
            print(f"Error al enviar correo de stock bajo: {e}")

@login_required
def exportar_boletas_excel(request):
    boletas = Boleta.objects.all().order_by('-fechaCompra')

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Boletas"

    ws.append(['ID Boleta', 'Total', 'Fecha de Compra'])

    for boleta in boletas:
        ws.append([
            boleta.id_boleta,
            float(boleta.total),
            boleta.fechaCompra.strftime('%Y-%m-%d %H:%M:%S')
        ])

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=boletas.xlsx'
    wb.save(response)

    return response

