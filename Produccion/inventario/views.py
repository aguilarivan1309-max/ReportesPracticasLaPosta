from decimal import ROUND_HALF_UP, Decimal

from django.db import transaction
from django.db.models.deletion import ProtectedError
from django.shortcuts import get_object_or_404
from django.utils import timezone
from drf_spectacular.utils import extend_schema
from rest_framework import generics, status
from rest_framework.exceptions import ValidationError
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response

from .conceptos_xml import extraer_conceptos_factura
from .models import Factura, Proveedor, PropuestaInventario
from .serializers import (
    FacturaActualizarSerializer,
    FacturaSerializer,
    ProveedorSerializer,
    PropuestaInventarioSerializer,
)

CENTAVOS = Decimal("0.01")


@extend_schema(request=FacturaSerializer)
class FacturaListCreateAPIView(generics.ListCreateAPIView):
    queryset = Factura.objects.all().order_by("-fecha_registro")
    serializer_class = FacturaSerializer
    parser_classes = [MultiPartParser, FormParser]


class FacturaDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """Consulta, actualiza (proveedor y PDF) y elimina una factura."""

    queryset = Factura.objects.all()
    http_method_names = ["get", "patch", "delete", "head", "options"]

    def get_serializer_class(self):
        if self.request.method == "PATCH":
            return FacturaActualizarSerializer
        return FacturaSerializer

    def destroy(self, request, *args, **kwargs):
        factura = self.get_object()
        try:
            self.perform_destroy(factura)
        except ProtectedError:
            return Response(
                {
                    "detail": (
                        "No se puede eliminar esta factura porque tiene "
                        "activos, componentes o propuestas asociados."
                    )
                },
                status=status.HTTP_409_CONFLICT,
            )
        return Response(status=status.HTTP_204_NO_CONTENT)


class ProveedorListCreateAPIView(generics.ListCreateAPIView):
    queryset = Proveedor.objects.all().order_by("nombre")
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


class FacturaPropuestasAPIView(generics.ListAPIView):
    """
    GET: lista las propuestas de una factura.
    POST: genera una propuesta por cada concepto del XML (sin duplicar).
    """

    serializer_class = PropuestaInventarioSerializer
    pagination_class = None

    def get_queryset(self):
        factura = get_object_or_404(Factura, pk=self.kwargs["factura_id"])
        return PropuestaInventario.objects.filter(factura=factura)

    @extend_schema(
        request=None,
        responses={
            200: PropuestaInventarioSerializer(many=True),
            201: PropuestaInventarioSerializer(many=True),
        },
    )
    def post(self, request, factura_id):
        factura = get_object_or_404(Factura, pk=factura_id)

        if not factura.archivo_xml:
            raise ValidationError({
                "archivo_xml": "La factura no tiene un XML adjunto."
            })

        try:
            with factura.archivo_xml.open("rb") as archivo:
                conceptos = extraer_conceptos_factura(archivo)
        except FileNotFoundError:
            raise ValidationError({
                "archivo_xml": "No se encontró el archivo XML de la factura."
            })

        creadas = 0
        with transaction.atomic():
            for c in conceptos:
                _, creada = PropuestaInventario.objects.get_or_create(
                    factura=factura,
                    indice_concepto=c["numero_concepto"],
                    defaults={
                        "clave_prodserv": c["clave_prod_serv"],
                        "no_identificacion": c["no_identificacion"],
                        "descripcion": c["descripcion"],
                        "cantidad": c["cantidad"],
                        "clave_unidad": c["clave_unidad"],
                        "unidad": c["unidad"],
                        "valor_unitario": c["valor_unitario"].quantize(
                            CENTAVOS, rounding=ROUND_HALF_UP
                        ),
                        "importe": c["importe"].quantize(
                            CENTAVOS, rounding=ROUND_HALF_UP
                        ),
                        "objeto_impuesto": c["objeto_impuesto"],
                    },
                )
                creadas += int(creada)

        datos = self.get_serializer(self.get_queryset(), many=True).data
        codigo = status.HTTP_201_CREATED if creadas else status.HTTP_200_OK
        return Response(datos, status=codigo)


class PropuestaListAPIView(generics.ListAPIView):
    """Lista propuestas. Filtros opcionales: ?estado=pendiente&factura=1"""

    serializer_class = PropuestaInventarioSerializer

    def get_queryset(self):
        queryset = PropuestaInventario.objects.all()
        estado = self.request.query_params.get("estado")
        factura = self.request.query_params.get("factura")
        if estado:
            queryset = queryset.filter(estado_revision=estado)
        if factura and factura.isdigit():
            queryset = queryset.filter(factura_id=int(factura))
        return queryset


class PropuestaDetailAPIView(generics.RetrieveUpdateAPIView):
    """Consulta y edita (clasificación, artículo, estado, marca, modelo)."""

    queryset = PropuestaInventario.objects.all()
    serializer_class = PropuestaInventarioSerializer
    http_method_names = ["get", "patch", "head", "options"]


class PropuestaRevisionAPIView(generics.GenericAPIView):
    serializer_class = PropuestaInventarioSerializer
    nuevo_estado = None

    def validar(self, propuesta):
        """Reglas extra antes de cambiar el estado."""

    @extend_schema(request=None, responses=PropuestaInventarioSerializer)
    def post(self, request, pk):
        with transaction.atomic():
            propuesta = get_object_or_404(
                PropuestaInventario.objects.select_for_update(), pk=pk
            )
            if (
                propuesta.estado_revision
                != PropuestaInventario.EstadoRevision.PENDIENTE
            ):
                raise ValidationError({
                    "estado_revision": "Solo se pueden revisar propuestas pendientes."
                })
            self.validar(propuesta)
            propuesta.estado_revision = self.nuevo_estado
            propuesta.fecha_revision = timezone.now()
            propuesta.save(update_fields=["estado_revision", "fecha_revision"])
        return Response(self.get_serializer(propuesta).data)


class PropuestaAceptarAPIView(PropuestaRevisionAPIView):
    nuevo_estado = PropuestaInventario.EstadoRevision.ACEPTADA

    def validar(self, propuesta):
        tipos = PropuestaInventario.TipoRegistro
        if propuesta.tipo_registro == tipos.POR_CLASIFICAR:
            raise ValidationError({
                "tipo_registro": "Clasifica la propuesta antes de aceptarla."
            })
        if propuesta.tipo_registro == tipos.ACTIVO:
            errores = {}
            if propuesta.articulo_id is None:
                errores["articulo"] = "Un activo requiere un artículo."
            if propuesta.estado_activo_id is None:
                errores["estado_activo"] = "Un activo requiere un estado inicial."
            if errores:
                raise ValidationError(errores)


class PropuestaRechazarAPIView(PropuestaRevisionAPIView):
    nuevo_estado = PropuestaInventario.EstadoRevision.RECHAZADA