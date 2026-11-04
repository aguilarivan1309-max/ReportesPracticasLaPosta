from rest_framework import generics
from rest_framework.parsers import FormParser, MultiPartParser
from drf_spectacular.utils import extend_schema

from .models import Factura, Proveedor
from .serializers import FacturaSerializer, ProveedorSerializer


@extend_schema(request=FacturaSerializer)
class FacturaListCreateAPIView(generics.ListCreateAPIView):
    queryset = Factura.objects.all().order_by("-fecha_registro")
    serializer_class = FacturaSerializer
    parser_classes = [MultiPartParser, FormParser]


class ProveedorListCreateAPIView(generics.ListCreateAPIView):
    queryset = Proveedor.objects.all().order_by("nombre")
    serializer_class = ProveedorSerializer


class ProveedorDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Proveedor.objects.all()
    serializer_class = ProveedorSerializer