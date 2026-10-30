from django.core.exceptions import ValidationError
from .inventario.validadores import validar_pdf, validar_xml
from django.db import models


class Factura(models.Model):
    folio = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Folio de factura",
    )
    uuid_fiscal = models.CharField(
        max_length=36,
        unique=True,
        null=True,
        blank=True,
        verbose_name="UUID fiscal del CFDI",
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
    archivo_pdf = models.FileField(
        upload_to="facturas/pdf/",
        validators=[validar_pdf],
        null=True,
        blank=True,
        verbose_name="Factura PDF",
    )
    archivo_xml = models.FileField(
        upload_to="facturas/xml/",
        validators=[validar_xml],
        null=True,
        blank=True,
        verbose_name="Factura en XML",
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
    nombre = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Nombre",
    )
    descripcion = models.TextField(
        blank=True,
        verbose_name="Descripción"
    )
    modo_control = models.CharField(
        max_length=30,
        default="individual",
        verbose_name="Modo de control",
    )
    requiere_qr = models.BooleanField(
        default=True,
        verbose_name="Requiere código QR",
    )
    permite_instalacion = models.BooleanField(
        default=False,
        verbose_name="Permite instalación",
    )
    activo = models.BooleanField(
        default=True,
        verbose_name="Activo",
    )

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
    nombre = models.CharField(
        max_length=200,
        verbose_name="Nombre",
    )
    descripcion = models.TextField(
        blank=True,
        verbose_name="Descripción",
    )
    marca = models.CharField(
        max_length=100,
        blank=True, verbose_name="Marca",
    )
    modelo = models.CharField(
        max_length=100, blank=True,
        verbose_name="Modelo",
    )
    unidad_medida = models.CharField(
        max_length=30, default="pieza",
        verbose_name="Unidad de medida",
    )
    activo = models.BooleanField(
        default=True,
        verbose_name="Activo",
    )

    class Meta:
        ordering = ["nombre"]
        verbose_name = "Artículo"
        verbose_name_plural = "Artículos"

    def __str__(self):
        return self.nombre


class EstadoActivo(models.Model):
    nombre = models.CharField(
        max_length=50,
        unique = True,
        verbose_name="Nombre del estado",
    )
    descripcion = models.TextField(
        blank=True,
        verbose_name="Descripcion",
    )
    activo = models.BooleanField(
        default=True,
        verbose_name="Activo",
    )
    class Meta:
        ordering = ["nombre"]
        verbose_name = "Estado del activo"
        verbose_name_plural = "Estados de los activos"
    def __str__(self):
        return self.nombre

class Ubicacion(models.Model):
    nombre = models.CharField(
        max_length=150,
        verbose_name="Nombre",
    )
    descripcion = models.TextField(
        blank=True,
        verbose_name="Descripcion",
    )
    ubicacion_padre = models.ForeignKey(
        "self",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="sububicaciones",
        verbose_name="Ubicacion superior",
    )
    activo = models.BooleanField(
        default=True,
        verbose_name="Activo",
    )
    class Meta:
        ordering = ["nombre"]
        verbose_name = "Ubicacion"
        verbose_name_plural = "Ubicaciones"
    def __str__(self):
        return self.nombre


class Responsable(models.Model):
    nombre = models.CharField(
        max_length=100,
        verbose_name="Nombre",
    )
    apellidos = models.CharField(
        max_length=150,
        verbose_name="Apellidos",
    )
    numero_empleado = models.CharField(
        max_length=30,
        unique=True,
        null=True,
        blank=True,
        verbose_name="Número de empleado",
    )
    correo = models.EmailField(
        blank=True,
        verbose_name="Correo electrónico",
    )
    activo = models.BooleanField(
        default=True,
        verbose_name="Activo",
    )

    class Meta:
        ordering = ["apellidos", "nombre"]
        verbose_name = "Responsable"
        verbose_name_plural = "Responsables"

    def __str__(self):
        return f"{self.nombre} {self.apellidos}"


class Activo(models.Model):
    numero_inventario = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Número de inventario",
    )
    articulo = models.ForeignKey(
        Articulo,
        on_delete=models.PROTECT,
        related_name="activos",
        verbose_name="Artículo",
    )
    estado = models.ForeignKey(
        EstadoActivo,
        on_delete=models.PROTECT,
        related_name="activos",
        verbose_name="Estado",
    )
    ubicacion = models.ForeignKey(
        Ubicacion,
        on_delete=models.PROTECT,
        related_name="activos",
        null=True,
        blank=True,
        verbose_name="Ubicación",
    )
    responsable = models.ForeignKey(
        Responsable,
        on_delete=models.PROTECT,
        related_name="activos",
        null=True,
        blank=True,
        verbose_name="Responsable actual",
    )
    numero_serie = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Número de serie",
    )
    fecha_adquisicion = models.DateField(
        null=True,
        blank=True,
        verbose_name="Fecha de adquisición",
    )
    observaciones = models.TextField(
        blank=True,
        verbose_name="Observaciones",
    )

    class Meta:
        ordering = ["numero_inventario"]
        verbose_name = "Activo"
        verbose_name_plural = "Activos"

    def __str__(self):
        return f"{self.numero_inventario} - {self.articulo.nombre}"

class Proveedor(models.Model):
    nombre = models.CharField(
        max_length=200,
        verbose_name="Nombre o razón social",
    )
    rfc = models.CharField(
        max_length=13,
        blank=True,
        verbose_name="RFC",
    )
    contacto = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="Persona de contacto",
        )
    correo = models.EmailField(
        blank=True,
        verbose_name="Correo electrónico",
        )
    telefono = models.CharField(
        max_length=30,
        blank=True,
        verbose_name="Teléfono",
    )
    activo = models.BooleanField(
        default=True,
        verbose_name="Activo",
    )

    class Meta:
        ordering = ["nombre"]
        verbose_name = "Proveedor"
        verbose_name_plural = "Proveedores"

    def __str__(self):
        return self.nombre


class Componente(models.Model):
    nombre = models.CharField(
        max_length=150,
        verbose_name="Nombre",
    )
    numero_serie = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Número de serie",
    )
    marca = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Marca",
    )
    modelo = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Modelo",
    )
    activo = models.BooleanField(
        default=True,
        verbose_name="Activo",
    )

    class Meta:
        ordering = ["nombre"]
        verbose_name = "Componente"
        verbose_name_plural = "Componentes"

    def __str__(self):
        return self.nombre
