from django.db import models
from django.forms import Textarea

MONTH_CHOICES = (
    ('Enero', 'Enero'),
    ('Febrero', 'Febrero'),
    ('Marzo', 'Marzo'),
    ('Abril', 'Abril'),
    ('Mayo', 'Mayo'),
    ('Junio', 'Junio'),
    ('Julio', 'Julio'),
    ('Agosto', 'Agosto'),
    ('Septiembre', 'Septiembre'),
    ('Octubre', 'Octubre'),
    ('Noviembre', 'Noviembre'),
    ('Diciembre', 'Diciembre'),
)

PRODUCT_CHOICES = (
    ('one', 'One'),
    ('duoplay', 'Duo play'),
    ('tripleplay', 'Triple play'),
)

STATE_CHOICES = (
    ('solicitado', 'Solicitado'),
    ('instalado', 'Instalado'),
)


CANAL = (
    ('FVD', 'FVD'),
    ('CU', 'CU'),
)
# Create your models here.


class Person(models.Model):
    cc_id = models.BigIntegerField()
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    address = models.CharField(max_length=100)
    email = models.EmailField(max_length=45)
    celphone = models.CharField(max_length=30)
    canal_de_venta = models.CharField(
        max_length=20, choices=CANAL, default='FVD')

    def __str__(self):
        return self.first_name+" "+self.last_name


class Solicitud(models.Model):

    product_name = models.CharField(
        max_length=20, choices=PRODUCT_CHOICES, default='One')

    status = models.CharField(
        max_length=20, choices=STATE_CHOICES, default='Solicitado')

    dia = models.IntegerField(default=1)

    mes = models.CharField(
        max_length=20, choices=MONTH_CHOICES, default='Enero')
        
    anio = models.IntegerField(default=2019)

    notes = models.CharField(max_length=500)
    product_cant = models.IntegerField(default=1)
    asesor = models.ForeignKey(Person, on_delete=models.CASCADE)



class Metas(models.Model):
    meta_ingresada = models.IntegerField(default=0)
    meta_instalada = models.IntegerField(default=0)
    mes = models.CharField(
        max_length=20, choices=MONTH_CHOICES, default='Enero')
    anio = models.IntegerField(default=2019)
    canal_venta = models.CharField(
        max_length=20, choices=CANAL, default='FVD')


   
