from django.contrib import admin
from .models import User, Cliente, Prestamo, Pago

class MorosoFilter(admin.SimpleListFilter):
    title = 'Estado'
    parameter_name = 'estado'

    def lookups(self, request, model_admin):
        return (
            ('moroso', 'Morosos'),
            ('al_dia', 'Al día'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'moroso':
            return [p for p in queryset if p.es_moroso()]
        if self.value() == 'al_dia':
            return [p for p in queryset if not p.es_moroso()]

@admin.register(Prestamo)
class PrestamoAdmin(admin.ModelAdmin):
    list_display = ('cliente', 'monto', 'interes', 'deuda_restante', 'es_moroso')
    list_filter = (MorosoFilter,)

admin.site.register(User)
admin.site.register(Cliente)
admin.site.register(Pago)