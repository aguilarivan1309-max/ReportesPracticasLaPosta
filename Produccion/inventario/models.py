
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
