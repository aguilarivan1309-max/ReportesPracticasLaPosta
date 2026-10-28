
from django.contrib import admin
from .models import Articulo, Factura, TipoBien, EstadoActivo, Ubicacion, Activo, Responsable


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
@admin.register(EstadoActivo)
class EstadoActivoAdmin(admin.ModelAdmin):
    list_display = (
        "nombre",
        "descripcion",
        "activo",
    )
    search_fields = (
        "nombre",
        "descripcion",
    )
    list_filter = ("activo",)
    ordering = ("nombre",)
@admin.register(Ubicacion)
class UbicacionAdmin(admin.ModelAdmin):
    list_display = (
        "nombre",
        "ubicacion_padre",
        "activo",
    )
    search_fields = (
        "nombre",
        "descripcion",
    )
    list_filter = (
        "activo",
    )
    ordering = ("nombre",)


@admin.register(Responsable)
class ResponsableAdmin(admin.ModelAdmin):
    list_display = ("nombre", "apellidos", "numero_empleado", "correo", "activo")
    search_fields = ("nombre", "apellidos", "numero_empleado", "correo")
    list_filter = ("activo",)


@admin.register(Activo)
class ActivoAdmin(admin.ModelAdmin):
    list_display = (
        "numero_inventario",
        "articulo",
        "estado",
        "ubicacion",
        "responsable",
    )
    search_fields = ("numero_inventario", "numero_serie", "articulo__nombre")
    list_filter = ("estado", "ubicacion")