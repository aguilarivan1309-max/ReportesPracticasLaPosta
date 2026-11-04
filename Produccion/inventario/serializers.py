from rest_framework import serializers 
from .models import Factura, Proveedor
class FacturaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Factura 
        fields = [
            "id",
            "folio",
            "fecha_emision",
            "proveedor",
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

class ProveedorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Proveedor
        fields = ["id", "nombre", "rfc", "contacto", "correo", "telefono", "activo"]
        read_only_fields = ["id"]
