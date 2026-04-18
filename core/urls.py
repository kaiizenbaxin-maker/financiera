from django.urls import path
from .views import clientes, registrar_pago, pagos_prestamo, login

urlpatterns = [
    path('login/', login),
    path('clientes/', clientes),
    path('pago/', registrar_pago),
    path('pagos/<int:id>/', pagos_prestamo),
]
