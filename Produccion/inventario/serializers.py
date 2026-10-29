
from django.db import IntegrityError, transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .models import Factura
from .inventario.validadores import validar_pdf, validar_xml
from .lectura_xml import extraer_datos_factura


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
