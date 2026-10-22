from django.contrib import admin
from .models import Factura

@admin.register(Factura)
class FacturaAdmin(admin.ModelAdmin):
    list_display = (
        "folio",
        "fecha_emision",
        "proveedor_nombre",
        "proveedor_rfc",
        "importe_total",
    )
    search_fields = (
        "folio",
        "proveedor_nombre",
        "proveedor_rfc",
    )
    list_filter = (
        "fecha_emision",
    )
    odering = ("-fecha_emision",)