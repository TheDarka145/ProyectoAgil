import datetime
from django.db import models

class Categoria(models.Model):
    idCategoria = models.IntegerField(primary_key=True, verbose_name='Id de la Categoria')
    NombreCategoria =  models.CharField(max_length=50, verbose_name='Nombre de la Categoria')

    def __str__(self):
        return self.NombreCategoria

class Planta(models.Model):
    idPlanta = models.CharField(primary_key=True, max_length=4,verbose_name='Id de Planta')
    nombre = models.CharField(max_length=50, verbose_name='Nombre de la Planta')
    imagen = models.ImageField(upload_to="imagenes", null=True, verbose_name='Imagen')
    descripcion = models.CharField(blank=True, null=True,max_length=100, verbose_name='Descripcion')
    categoria = models.ForeignKey ('Categoria', default=1, on_delete=models.CASCADE, verbose_name='Categoria')
    precio = models.IntegerField(blank=True, null=True,verbose_name='Precio de la Planta')
    stock = models.IntegerField(blank=True, null=True,verbose_name='Stock de Planta')

    def __str__(self):
        return self.nombre
    
class Boleta(models.Model):
    id_boleta=models.AutoField(primary_key=True)
    total=models.BigIntegerField()
    fechaCompra=models.DateTimeField(blank=False, null=False, default = datetime.datetime.now)
  
    def __str__(self):
        return str(self.id_boleta)

class detalle_boleta(models.Model):
    id_boleta = models.ForeignKey('Boleta', blank=True, on_delete=models.CASCADE)
    id_detalle_boleta = models.AutoField(primary_key=True)
    id_producto = models.ForeignKey('Planta', on_delete=models.CASCADE)
    cantidad = models.IntegerField()
    subtotal = models.BigIntegerField()

    def __str__(self):
        return str(self.id_detalle_boleta)
