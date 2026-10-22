from rest_framework import generics

from .models import Factura 
from .serializers import FacturaSerializer

class FacturaListCreateAPIView(generics.ListCreateAPIView):
    queryset = Factura.objects.all()
    serializer_class = FacturaSerializer
