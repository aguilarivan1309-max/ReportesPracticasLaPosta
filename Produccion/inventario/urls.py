from django.urls import path

from .views import (
    FacturaDetailAPIView,
    FacturaListCreateAPIView,
    FacturaPropuestasAPIView,
    PropuestaAceptarAPIView,
    PropuestaDetailAPIView,
    PropuestaListAPIView,
    PropuestaRechazarAPIView,
    ProveedorDetailAPIView,
    ProveedorListCreateAPIView,
)

urlpatterns = [
    path("facturas/", FacturaListCreateAPIView.as_view(), name="factura-list-create"),
    path("facturas/<int:pk>/", FacturaDetailAPIView.as_view(), name="factura-detail"),
    path(
        "facturas/<int:factura_id>/propuestas/",
        FacturaPropuestasAPIView.as_view(),
        name="factura-propuestas",
    ),

    path("propuestas/", PropuestaListAPIView.as_view(), name="propuesta-list"),
    path("propuestas/<int:pk>/", PropuestaDetailAPIView.as_view(), name="propuesta-detail"),
    path("propuestas/<int:pk>/aceptar/", PropuestaAceptarAPIView.as_view(), name="propuesta-aceptar"),
    path("propuestas/<int:pk>/rechazar/", PropuestaRechazarAPIView.as_view(), name="propuesta-rechazar"),

    path("proveedores/", ProveedorListCreateAPIView.as_view(), name="proveedor-list-create"),
    path("proveedores/<int:pk>/", ProveedorDetailAPIView.as_view(), name="proveedor-detail"),
]