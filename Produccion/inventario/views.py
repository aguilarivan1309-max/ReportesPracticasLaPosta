
from rest_framework import generics
from rest_framework.parsers import FormParser, MultiPartParser

from .models import Factura
from .serializers import FacturaSerializer
from drf_spectacular.utils import extend_schema


from .models import Factura
from .serializers import FacturaSerializer

@extend_schema(
    request=FacturaSerializer,
)
class FacturaListCreateAPIView(generics.ListCreateAPIView):
    queryset = Factura.objects.all().order_by("-fecha_registro")
    serializer_class = FacturaSerializer
    parser_classes = [MultiPartParser, FormParser]
