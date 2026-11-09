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
    proveedor = models.ForeignKey(
        "Proveedor",
        on_delete=models.PROTECT,
        related_name="facturas",
        null=True,
        blank=True,
        verbose_name="Proveedor relacionado",
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
    factura = models.ForeignKey(
        Factura, 
        on_delete=models.PROTECT,
         related_name="activos_generados",
          null=True, 
          blank=True,
          verbose_name="Factura de adquisicion",
    )
    propuesta_origen = models.ForeignKey(
        "PropuestaInventario",
        on_delete=models.PROTECT,
        related_name="activos_generados",
        null=True, 
        blank=True,
        verbose_name="Propuesta de origen",
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


class EstadoComponente(models.Model):
    nombre = models.CharField(
        max_length=50, unique=True, verbose_name="Nombre del estado",
    )
    descripcion = models.TextField(blank=True, verbose_name="Descripción")
    activo = models.BooleanField(default=True, verbose_name="Activo")

    class Meta:
        ordering = ["nombre"]
        verbose_name = "Estado del componente"
        verbose_name_plural = "Estados de los componentes"

    def __str__(self):
        return self.nombre


class Componente(models.Model):
    estado = models.ForeignKey(
        EstadoComponente, on_delete=models.PROTECT,
        related_name="componentes", verbose_name="Estado",
    )
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
    factura = models.ForeignKey(
        Factura, 
        on_delete=models.PROTECT,
        related_name="componentes_generados",
        null=True,
        blank=True,
        verbose_name="Factura de adquisicion",
    )
    propuesta_origen = models.ForeignKey(
        "PropuestaInventario",
        on_delete=models.PROTECT,
        related_name="componentes_generados",
        null=True,
        blank=True, 
        verbose_name="Propuesta de origen",
    )

    class Meta:
        ordering = ["nombre"]
        verbose_name = "Componente"
        verbose_name_plural = "Componentes"

    def __str__(self):
        return self.nombre
class ComponenteInstalado(models.Model):
    activo = models.ForeignKey(
        Activo,
        on_delete=models.PROTECT,
        related_name="componentes_instalados",
        verbose_name="Activo",
    )
    componente = models.ForeignKey(
        Componente,
        on_delete=models.PROTECT,
        related_name="instalaciones",
        verbose_name="Componente",
    )
    fecha_instalacion = models.DateField(
        verbose_name="Fecha de instalacion",
    )
    fecha_retiro = models.DateField(
        null=True,
        blank=True,
        verbose_name="Fecha de retiro",
    )
    observaciones = models.TextField(
        blank=True,
        verbose_name="Observaciones",
    )
    class Meta:
        ordering = ["-fecha_instalacion"]
        verbose_name = "Componente instalado"
        verbose_name_plural = "Componentes instalados"
        constraints = [
            models.UniqueConstraint(
                fields=["componente"],
                condition=models.Q(fecha_retiro__isnull=True),
                name="componente_una_instalacion_activa",
            )
        ]
    def __str__(self):
        return f"{self.componente} - {self.activo}"

class Movimiento(models.Model):
    class TipoMovimiento(models.TextChoices):
        ALTA = "alta", "Alta"
        ASIGNACION = "asignacion", "Asignación"
        TRASLADO = "traslado", "Traslado"
        DEVOLUCION = "devolucion", "Devolución"
        MANTENIMIENTO = "mantenimiento", "Mantenimiento"
        BAJA = "baja", "Baja"

    activo = models.ForeignKey(
        Activo,
        on_delete=models.PROTECT,
        related_name="movimientos",
        verbose_name="Activo",
    )

    tipo = models.CharField(
        max_length=20,
        choices=TipoMovimiento.choices,
        verbose_name="Tipo de movimiento",
    )

    fecha = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de registro",
    )

    responsable_origen = models.ForeignKey(
        Responsable,
        on_delete=models.PROTECT,
        related_name="movimientos_origen",
        null=True,
        blank=True,
        verbose_name="Responsable anterior",
    )

    responsable_destino = models.ForeignKey(
        Responsable,
        on_delete=models.PROTECT,
        related_name="movimientos_destino",
        null=True,
        blank=True,
        verbose_name="Responsable nuevo",
    )

    ubicacion_origen = models.ForeignKey(
        Ubicacion,
        on_delete=models.PROTECT,
        related_name="movimientos_origen",
        null=True,
        blank=True,
        verbose_name="Ubicación anterior",
    )

    ubicacion_destino = models.ForeignKey(
        Ubicacion,
        on_delete=models.PROTECT,
        related_name="movimientos_destino",
        null=True,
        blank=True,
        verbose_name="Ubicación nueva",
    )

    observaciones = models.TextField(
        blank=True,
        verbose_name="Observaciones",
    )

    class Meta:
        ordering = ["-fecha"]
        verbose_name = "Movimiento"
        verbose_name_plural = "Movimientos"

    def __str__(self):
        return f"{self.activo.numero_inventario} - {self.get_tipo_display()}"

class PropuestaInventario(models.Model):

    class TipoRegistro(models.TextChoices):
        POR_CLASIFICAR = "por_clasificar", "Por clasificar"
        ACTIVO = "activo", "Activo"
        COMPONENTE = "componente", "Componente"
        NO_INVENTARIABLE = "no_inventariable", "No inventariable"

    class EstadoRevision(models.TextChoices):
        PENDIENTE = "pendiente", "Pendiente"
        ACEPTADA = "aceptada", "Aceptada"
        RECHAZADA = "rechazada", "Rechazada"
        REGISTRADA = "registrada", "Registrada"

    factura = models.ForeignKey(
        Factura,
        on_delete=models.PROTECT,
        related_name="propuestas_inventario",
        verbose_name="Factura de origen",
    )

    indice_concepto = models.PositiveIntegerField(
        verbose_name="Número de concepto en XML",
    )

    clave_prodserv = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="Clave de producto o servicio SAT",
    )

    no_identificacion = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Identificador del concepto",
    )

    descripcion = models.TextField(
        verbose_name="Descripción original",
    )

    cantidad = models.DecimalField(
        max_digits=12,
        decimal_places=6,
        verbose_name="Cantidad adquirida",
    )

    clave_unidad = models.CharField(
        max_length=10,
        blank=True,
        verbose_name="Clave de unidad SAT",
    )

    unidad = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Unidad de medida",
    )

    valor_unitario = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name="Valor unitario",
    )

    importe = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name="Importe",
    )

    objeto_impuesto = models.CharField(
        max_length=2,
        blank=True,
        verbose_name="Objeto de impuesto",
    )

    tipo_registro = models.CharField(
        max_length=20,
        choices=TipoRegistro.choices,
        default=TipoRegistro.POR_CLASIFICAR,
        verbose_name="Clasificación propuesta",
    )

    articulo = models.ForeignKey(
        "Articulo",
        on_delete=models.PROTECT,
        related_name="propuestas_inventario",
        null=True,
        blank=True,
        verbose_name="Artículo relacionado",
    )

    estado_activo = models.ForeignKey(
        "EstadoActivo",
        on_delete=models.PROTECT,
        related_name="propuestas_inventario",
        null=True,
        blank=True,
        verbose_name="Estado inicial del activo",
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

    estado_revision = models.CharField(
        max_length=15,
        choices=EstadoRevision.choices,
        default=EstadoRevision.PENDIENTE,
        verbose_name="Estado de revisión",
    )

    observaciones = models.TextField(
        blank=True,
        verbose_name="Observaciones de revisión",
    )

    fecha_registro = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de registro",
    )

    fecha_revision = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fecha de revisión",
    )

    class Meta:
        ordering = ["factura", "indice_concepto"]
        verbose_name = "Propuesta de inventario"
        verbose_name_plural = "Propuestas de inventario"
        constraints = [
            models.UniqueConstraint(
                fields=["factura", "indice_concepto"],
                name="propuesta_concepto_unico_por_factura",
            )
        ]

    def __str__(self):
        return (
            f"{self.factura.folio} - "
            f"Concepto {self.indice_concepto}"
        )
