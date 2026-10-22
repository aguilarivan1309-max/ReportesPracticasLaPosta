from rest_framework import serializers 
from .models import Factura 
class FacturaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Factura 
        fields = [
            "id",
            "folio",
            "fecha_emision",
            "proveedor_nombre", 
            "proveedor_rfc", 
            "importe_total", 
            "archivo",
            "fecha_registro",
        ]
        read_only_fields = [
            "id",
            "fecha_registro",
        ]