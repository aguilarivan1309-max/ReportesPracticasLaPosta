from django.urls import path 
from .views import FacturaListCreateAPIView

urlpatterns = [
    path(
        "facturas/",
        FacturaListCreateAPIView.as_view(),
        name="factura-list-create",
    ),
]