from django.urls import reverse
from .servicios_qr import construir_url_qr
from django.db import IntegrityError, transaction
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .models import Factura, Proveedor, PropuestaInventario, EtiquetaQR
from .inventario.validadores import validar_pdf, validar_xml
from .lectura_xml import extraer_datos_factura
from .servicios import datos_faltantes


class FacturaSerializer(serializers.ModelSerializer):
    folio = serializers.CharField(required=False)
    fecha_emision = serializers.DateField(required=False)
    proveedor_nombre = serializers.CharField(required=False)
    proveedor_rfc = serializers.CharField(required=False)
    importe_total = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        required=False,
        allow_null=True,
    )
    uuid_fiscal = serializers.CharField(
        required=False,
        allow_null=True,
        allow_blank=True,
    )
    archivo_xml = serializers.FileField(required=True)
    archivo_pdf = serializers.FileField(required=False, allow_null=True)
    class Meta:
        model = Factura
        fields = [
            "id",
            "folio",
            "uuid_fiscal",
            "fecha_emision",
            "proveedor",
            "proveedor_nombre",
            "proveedor_rfc",
            "importe_total",
            "archivo_pdf",
            "archivo_xml",
            "fecha_registro",
        ]
        read_only_fields = [
            "id",
            "fecha_registro",
        ]

    def validate_archivo_pdf(self, value):
        if value:
            validar_pdf(value)
        return value
    def validate_archivo_xml(self, value):
        validar_xml(value)
        return value

    def validate(self, attrs):
        archivo_xml = attrs.get("archivo_xml")

        if archivo_xml is None:
            raise ValidationError({
                "archivo_xml": "Debes adjuntar el XML de la factura."
            })

        datos = extraer_datos_factura(archivo_xml)
        attrs.update(datos)

        if Factura.objects.filter(folio=datos["folio"]).exists():
            raise ValidationError({
                "folio": "Ya existe una factura con ese folio."
            })

        uuid_fiscal = datos["uuid_fiscal"]
        if uuid_fiscal and Factura.objects.filter(
            uuid_fiscal=uuid_fiscal
        ).exists():
            raise ValidationError({
                "uuid_fiscal": "Ya existe una factura con ese UUID fiscal."
            })

        return attrs

    @transaction.atomic
    def create(self, validated_data):
        try:
            return Factura.objects.create(**validated_data)
        except IntegrityError:
            raise ValidationError({
                "factura": (
                    "No se pudo registrar la factura. "
                    "Comprueba que el folio y el UUID no estén duplicados."
                )
            })
class ProveedorSerializer(serializers.ModelSerializer):

    class Meta:
        model = Proveedor
        fields = [
            "id",
            "nombre",
            "rfc",
            "contacto",
            "correo",
            "telefono",
            "activo",
        ]
        read_only_fields = ["id"]


class FacturaActualizarSerializer(serializers.ModelSerializer):
    """Permite cambiar solo el proveedor relacionado y el PDF de la factura."""

    class Meta:
        model = Factura
        fields = ["id", "proveedor", "archivo_pdf"]
        read_only_fields = ["id"]

    def validate_archivo_pdf(self, value):
        if value:
            validar_pdf(value)
        return value


class PropuestaInventarioSerializer(serializers.ModelSerializer):
    datos_faltantes = serializers.SerializerMethodField()
    completa = serializers.SerializerMethodField()

    @extend_schema_field(serializers.DictField(child=serializers.CharField()))
    def get_datos_faltantes(self, obj):
        """Campos que faltan para aceptar la propuesta, con su mensaje."""
        return datos_faltantes(obj)

    @extend_schema_field(serializers.BooleanField())
    def get_completa(self, obj):
        return not datos_faltantes(obj)

    class Meta:
        model = PropuestaInventario
        fields = [
            "id",
            "factura",
            "indice_concepto",
            "clave_prodserv",
            "no_identificacion",
            "descripcion",
            "cantidad",
            "clave_unidad",
            "unidad",
            "valor_unitario",
            "importe",
            "objeto_impuesto",
            "tipo_registro",
            "articulo",
            "estado_activo",
            "marca",
            "modelo",
            "estado_revision",
            "observaciones",
            "fecha_registro",
            "fecha_revision",
            "datos_faltantes",
            "completa",
        ]
        # Solo se editan los datos de clasificación; lo demás viene del XML.
        read_only_fields = [
            "id",
            "factura",
            "indice_concepto",
            "clave_prodserv",
            "no_identificacion",
            "descripcion",
            "cantidad",
            "clave_unidad",
            "unidad",
            "valor_unitario",
            "importe",
            "objeto_impuesto",
            "estado_revision",
            "fecha_registro",
            "fecha_revision",
        ]

    def validate(self, attrs):
        if (
            self.instance
            and self.instance.estado_revision
            != PropuestaInventario.EstadoRevision.PENDIENTE
        ):
            raise ValidationError({
                "estado_revision": "Solo se pueden editar propuestas pendientes."
            })
        return attrs

class EtiquetaQRSerializer(serializers.ModelSerializer):
    numero_inventario = serializers.CharField(source="activo.numero_inventario", read_only=True)
    url_imagen = serializers.SerializerMethodField()
    url_publica = serializers.SerializerMethodField()

    class Meta:
        model = EtiquetaQR
        fields = ["id", "activo", "numero_inventario", "token", "activa", "fecha_generacion",
                  "fecha_actualizacion", "url_imagen", "url_publica"]
        read_only_fields = fields

    @extend_schema_field(serializers.URLField())
    def get_url_imagen(self, obj):
        url = reverse("activo-qr-imagen", kwargs={"activo_id": obj.activo_id})
        request = self.context.get("request")
        return request.build_absolute_uri(url) if request else url

    @extend_schema_field(serializers.URLField())
    def get_url_publica(self, obj):
        return construir_url_qr(obj)
