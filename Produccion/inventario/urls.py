
from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import (
    ActivoBajaAPIView,
    FacturaDetailAPIView,
    FacturaListCreateAPIView,
    FacturaPropuestasAPIView,
    PropuestaAceptarAPIView,
    PropuestaDetailAPIView,
    PropuestaListAPIView,
    PropuestaRegistrarAPIView,
    PropuestaRechazarAPIView,
    ProveedorDetailAPIView,
    ProveedorListCreateAPIView,
    UsuarioActualAPIView,
)

urlpatterns = [
    # Autenticación (JWT)
    path("auth/token/", TokenObtainPairView.as_view(), name="token-obtain"),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("auth/yo/", UsuarioActualAPIView.as_view(), name="auth-yo"),

    # Facturas
    path("facturas/", FacturaListCreateAPIView.as_view(), name="factura-list-create"),
    path("facturas/<int:pk>/", FacturaDetailAPIView.as_view(), name="factura-detail"),
    path(
        "facturas/<int:factura_id>/propuestas/",
        FacturaPropuestasAPIView.as_view(),
        name="factura-propuestas",
    ),

    # Propuestas de inventario
    path("propuestas/", PropuestaListAPIView.as_view(), name="propuesta-list"),
    path("propuestas/<int:pk>/", PropuestaDetailAPIView.as_view(), name="propuesta-detail"),
    path("propuestas/<int:pk>/aceptar/", PropuestaAceptarAPIView.as_view(), name="propuesta-aceptar"),
    path("propuestas/<int:pk>/registrar/", PropuestaRegistrarAPIView.as_view(), name="propuesta-registrar"),
    path("propuestas/<int:pk>/rechazar/", PropuestaRechazarAPIView.as_view(), name="propuesta-rechazar"),

    # Baja de activos
    path("activos/<int:pk>/baja/", ActivoBajaAPIView.as_view(), name="activo-baja"),

    # Proveedores
    path("proveedores/", ProveedorListCreateAPIView.as_view(), name="proveedor-list-create"),
    path("proveedores/<int:pk>/", ProveedorDetailAPIView.as_view(), name="proveedor-detail"),
]
