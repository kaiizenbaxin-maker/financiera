from .models import Cliente, Prestamo, Pago
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.views.decorators.csrf import csrf_exempt
import json
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
@csrf_exempt
def login(request):
    if request.method == 'POST':
        data = json.loads(request.body)

        user = authenticate(
            username=data.get('username'),
            password=data.get('password')
        )

        if user:
            refresh = RefreshToken.for_user(user)

            return JsonResponse({
                'success': True,
                'access': str(refresh.access_token),
            })

        return JsonResponse({'success': False})


# 👥 CLIENTES
def clientes(request):
    data = []

    for c in Cliente.objects.all():
        prestamos = []

        for p in c.prestamo_set.all():
            prestamos.append({
                "id": p.id,
                "monto": float(p.monto),
                "deuda": float(p.deuda_restante())  # ✅ CORREGIDO
            })

        data.append({
            "id": c.id,
            "nombre": c.nombre,
            "telefono": c.telefono,
            "prestamos": prestamos
        })

    return JsonResponse(data, safe=False)


# 💰 REGISTRAR PAGO
def registrar_pago(request):
    if request.method == 'POST':
        data = json.loads(request.body)

        prestamo = Prestamo.objects.get(id=data['prestamo_id'])
        monto = float(data['monto'])

        # ⚠️ usa un usuario por defecto (luego lo mejoramos con login real)
        usuario = prestamo.empleado

        Pago.objects.create(
            prestamo=prestamo,
            monto=monto,
            registrado_por=usuario  # ✅ OBLIGATORIO
        )

        return JsonResponse({"ok": True})


# 📄 PAGOS POR PRÉSTAMO
def pagos_prestamo(request, id):
    pagos = Pago.objects.filter(prestamo_id=id)

    data = []
    for p in pagos:
        data.append({
            "monto": float(p.monto),
            "fecha": str(p.fecha)
        })

    return JsonResponse(data, safe=False)