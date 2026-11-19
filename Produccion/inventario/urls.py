from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import (
    FacturaDetailAPIView,
    FacturaListCreateAPIView,
    FacturaPropuestasAPIView,
    PropuestaAceptarAPIView,
    PropuestaDetailAPIView,
    PropuestaRegistrarAPIView,
    PropuestaListAPIView,
    PropuestaRechazarAPIView,
    ProveedorDetailAPIView,
    ProveedorListCreateAPIView,
    UsuarioActualAPIView,
)

urlpatterns = [
    # autenticacion (JWT)
    path("auth/token/", TokenObtainPairView.as_view(), name="token-obtain"),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("auth/yo/", UsuarioActualAPIView.as_view(), name="auth-yo"),

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
    path("propuestas/<int:pk>/registrar/", PropuestaRegistrarAPIView.as_view(), name="propuesta-registrar"),
    path("propuestas/<int:pk>/rechazar/", PropuestaRechazarAPIView.as_view(), name="propuesta-rechazar"),

    path("proveedores/", ProveedorListCreateAPIView.as_view(), name="proveedor-list-create"),
    path("proveedores/<int:pk>/", ProveedorDetailAPIView.as_view(), name="proveedor-detail"),
]