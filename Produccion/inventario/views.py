from django.db.models.deletion import ProtectedError
from rest_framework import generics, status
from rest_framework.response import Response

from .models import Factura, Proveedor
from .serializers import FacturaSerializer, ProveedorSerializer

class FacturaListCreateAPIView(generics.ListCreateAPIView):
    queryset = Factura.objects.all()
    serializer_class = FacturaSerializer


class ProveedorListCreateAPIView(generics.ListCreateAPIView):
    queryset = Proveedor.objects.all()
    serializer_class = ProveedorSerializer


class ProveedorDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Proveedor.objects.all()
    serializer_class = ProveedorSerializer

    def destroy(self, request, *args, **kwargs):
        proveedor = self.get_object()
        try:
            self.perform_destroy(proveedor)
        except ProtectedError:
            return Response(
                {"detail": "No se puede eliminar este proveedor porque tiene facturas asociadas."},
                status=status.HTTP_409_CONFLICT,
            )
        return Response(status=status.HTTP_204_NO_CONTENT)
