from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models import Sum
from datetime import timedelta, date
from decimal import Decimal


# 🔐 USUARIOS CON ROLES
class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Administrador'),
        ('gerente', 'Gerente'),
        ('empleado', 'Empleado'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='empleado')

    def __str__(self):
        return f"{self.username} ({self.role})"


# 👤 CLIENTES
class Cliente(models.Model):
    nombre = models.CharField(max_length=100)
    telefono = models.CharField(max_length=20)
    direccion = models.TextField()
    identificacion = models.CharField(max_length=50)
    creado_por = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.nombre


# 💰 PRÉSTAMOS
class Prestamo(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    interes = models.DecimalField(max_digits=5, decimal_places=2)  # % (ej: 20.00)
    fecha_inicio = models.DateField()
    plazo_semanas = models.IntegerField()
    empleado = models.ForeignKey(User, on_delete=models.CASCADE)

    def total_a_pagar(self):
        return self.monto + (self.monto * self.interes / Decimal('100'))

    def total_pagado(self):
        return self.pago_set.aggregate(total=Sum('monto'))['total'] or Decimal('0')

    def deuda_restante(self):
        return self.total_a_pagar() - self.total_pagado()

    def fecha_limite(self):
        return self.fecha_inicio + timedelta(weeks=self.plazo_semanas)

    def es_moroso(self):
        return date.today() > self.fecha_limite() and self.deuda_restante() > 0

    def __str__(self):
        return f"Prestamo {self.id} - {self.cliente.nombre}"


# 💵 PAGOS
class Pago(models.Model):
    prestamo = models.ForeignKey(Prestamo, on_delete=models.CASCADE)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    fecha = models.DateTimeField(auto_now_add=True)
    registrado_por = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"${self.monto} - {self.fecha}"

    def save(self, *args, **kwargs):
        # 🔴 Validación: no permitir pagar de más
        if self.monto > self.prestamo.deuda_restante():
            raise ValueError("El pago excede la deuda restante")
        super().save(*args, **kwargs)