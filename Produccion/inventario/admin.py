
from django.contrib import admin
from .models import Articulo, Factura, TipoBien


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
    list_filter = ("fecha_emision",)
    ordering = ("-fecha_emision",)


@admin.register(TipoBien)
class TipoBienAdmin(admin.ModelAdmin):
    list_display = (
        "nombre",
        "modo_control",
        "requiere_qr",
        "permite_instalacion",
        "activo",
    )
    search_fields = ("nombre", "descripcion")
    list_filter = (
        "modo_control",
        "requiere_qr",
        "activo",
    )


@admin.register(Articulo)
class ArticuloAdmin(admin.ModelAdmin):
    list_display = (
        "nombre",
        "tipo_bien",
        "marca",
        "modelo",
        "unidad_medida",
        "activo",
    )
    search_fields = (
        "nombre",
        "marca",
        "modelo",
    )
    list_filter = (
        "tipo_bien",
        "activo",
    )
