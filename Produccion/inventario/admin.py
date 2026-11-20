
from django.contrib import admin
from .models import EstadoComponente, Articulo, Factura, TipoBien, EstadoActivo, Ubicacion, Activo, Responsable, Proveedor, Componente, ComponenteInstalado, Movimiento


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

@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    list_display = ("nombre", "rfc", "contacto", "correo", "telefono", "activo")
    search_fields = ("nombre", "rfc", "contacto", "correo")
    list_filter = ("activo",)


@admin.register(Componente)
class ComponenteAdmin(admin.ModelAdmin):
    list_display = ("nombre", "numero_serie", "marca", "modelo", "estado", "activo")
    search_fields = ("nombre", "numero_serie", "marca", "modelo")
    list_filter = ("estado", "marca", "activo")


@admin.register(ComponenteInstalado)
class ComponenteInstaladoAdmin(admin.ModelAdmin):
    list_display = (
        "componente",
        "activo",
        "fecha_instalacion",
        "fecha_retiro",
    )
    search_fields = (
        "componente__nombre",
        "activo__numero_inventario",
    )
    search_fields = (
        "componente__nombre",
        "activo__numero_inventario",
    )
    list_filter = ("fecha_instalacion", "fecha_retiro")


@admin.register(Movimiento)
class MovimientoAdmin(admin.ModelAdmin):

    list_display = (
        "activo",
        "tipo",
        "fecha",
        "responsable_origen",
        "responsable_destino",
        "ubicacion_origen",
        "ubicacion_destino",
    )

    search_fields = (
        "activo__numero_inventario",
        "observaciones",
    )

    list_filter = ("tipo", "fecha")

    readonly_fields = ("fecha",)

@admin.register(EstadoComponente)
class EstadoComponenteAdmin(admin.ModelAdmin):
    list_display = ("nombre", "descripcion", "activo")
    search_fields = ("nombre", "descripcion")
    list_filter = ("activo",)
    ordering = ("nombre",)
