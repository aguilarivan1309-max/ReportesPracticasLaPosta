
from django.db import models


class Factura(models.Model):
    folio = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Folio de factura",
    )
    fecha_emision = models.DateField(
        verbose_name="Fecha de emisión",
    )
    proveedor_nombre = models.CharField(
        max_length=200,
        verbose_name="Nombre del proveedor",
    )
    proveedor_rfc = models.CharField(
        max_length=13,
        blank=True,
        verbose_name="RFC del proveedor",
    )
    importe_total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Importe total",
    )
    archivo = models.FileField(
        upload_to="facturas/",
        null=True,
        blank=True,
        verbose_name="Documento de factura",
    )
    fecha_registro = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de registro",
    )

    class Meta:
        ordering = ["-fecha_emision"]
        verbose_name = "Factura"
        verbose_name_plural = "Facturas"

    def __str__(self):
        return self.folio


class TipoBien(models.Model):
    nombre = models.CharField(max_length=100, verbose_name="Nombre")
    descripcion = models.TextField(blank=True, verbose_name="Descripción")
    modo_control = models.CharField(
        max_length=30, default="individual", verbose_name="Modo de control"
    )
    requiere_qr = models.BooleanField(default=True, verbose_name="Requiere código QR")
    permite_instalacion = models.BooleanField(default=False, verbose_name="Permite instalación")
    activo = models.BooleanField(default=True, verbose_name="Activo")

    class Meta:
        ordering = ["nombre"]
        verbose_name = "Tipo de bien"
        verbose_name_plural = "Tipos de bien"

    def __str__(self):
        return self.nombre


class Articulo(models.Model):
    tipo_bien = models.ForeignKey(
        TipoBien,
        on_delete=models.PROTECT,
        related_name="articulos",
        verbose_name="Tipo de bien",
    )
    nombre = models.CharField(max_length=200, verbose_name="Nombre")
    descripcion = models.TextField(blank=True, verbose_name="Descripción")
    marca = models.CharField(max_length=100, blank=True, verbose_name="Marca")
    modelo = models.CharField(max_length=100, blank=True, verbose_name="Modelo")
    unidad_medida = models.CharField(
        max_length=30, default="pieza", verbose_name="Unidad de medida"
    )
    activo = models.BooleanField(default=True, verbose_name="Activo")

    class Meta:
        ordering = ["nombre"]
        verbose_name = "Artículo"
        verbose_name_plural = "Artículos"

    def __str__(self):
        return self.nombre
