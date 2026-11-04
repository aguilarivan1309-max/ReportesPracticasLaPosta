from django.urls import path 
from .views import FacturaListCreateAPIView, ProveedorListCreateAPIView, ProveedorDetailAPIView

urlpatterns = [
    path("proveedores/", ProveedorListCreateAPIView.as_view(), name="proveedor-list-create"),
    path("proveedores/<int:pk>/", ProveedorDetailAPIView.as_view(), name="proveedor-detail"),
    path(
        "facturas/",
        FacturaListCreateAPIView.as_view(),
        name="factura-list-create",
    ),
]