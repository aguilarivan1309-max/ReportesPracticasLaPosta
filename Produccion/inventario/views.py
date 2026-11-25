from django.http import HttpResponse
from django.utils.http import content_disposition_header
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from drf_spectacular.types import OpenApiTypes
from .servicios_qr import construir_url_qr, generar_imagen_qr, obtener_o_crear_etiqueta
from decimal import ROUND_HALF_UP, Decimal

from django.db import transaction
from django.db.models.deletion import ProtectedError
from django.shortcuts import get_object_or_404
from django.utils import timezone
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import generics, serializers, status
from rest_framework.exceptions import ValidationError
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response

from .conceptos_xml import extraer_conceptos_factura
from .models import Factura, Proveedor, PropuestaInventario, Activo, EtiquetaQR, Movimiento
from .serializers import (
    EtiquetaQRSerializer,
    FacturaActualizarSerializer,
    FacturaSerializer,
    ProveedorSerializer,
    PropuestaInventarioSerializer,
)

from .servicios import registrar_propuesta

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

class PropuestaRegistrarAPIView(generics.GenericAPIView):
    serializer_class = PropuestaInventarioSerializer

    @extend_schema(
        request=None,
        responses={
            201: inline_serializer(
                name="RegistroPropuesta",
                fields={
                    "activos": serializers.ListField(child=serializers.CharField()),
                    "componentes": serializers.ListField(child=serializers.IntegerField()),
                },
            ),
        },
    )
    def post(self, request, pk):
        with transaction.atomic():
            propuesta = get_object_or_404(
                PropuestaInventario.objects.select_for_update(), pk=pk
            )
            self.check_object_permissions(request, propuesta)
            activos, componentes = registrar_propuesta(propuesta)
        return Response(
            {
                "activos": [activo.numero_inventario for activo in activos],
                "componentes": [componente.pk for componente in componentes],
            },
            status=status.HTTP_201_CREATED,
        )


class ActivoQRView(APIView):
    permission_classes = [IsAuthenticated]

    def respuesta(self, request, etiqueta, codigo=200):
        datos = EtiquetaQRSerializer(etiqueta, context={"request": request}).data
        response = Response(datos, status=codigo)
        response["Cache-Control"] = "no-store"
        return response

    @extend_schema(responses=EtiquetaQRSerializer)
    def get(self, request, activo_id):
        activo = get_object_or_404(Activo, pk=activo_id)
        etiqueta = get_object_or_404(EtiquetaQR, activo=activo)
        return self.respuesta(request, etiqueta)

    @extend_schema(request=None, responses={200: EtiquetaQRSerializer, 201: EtiquetaQRSerializer})
    def post(self, request, activo_id):
        etiqueta, creada = obtener_o_crear_etiqueta(activo_id)
        if not etiqueta.activa:
            return Response({"detail": "La etiqueta QR está desactivada."}, status=409)
        return self.respuesta(request, etiqueta, 201 if creada else 200)

    @extend_schema(request=None, responses={204: None})
    def delete(self, request, activo_id):
        with transaction.atomic():
            activo = get_object_or_404(Activo.objects.select_for_update(), pk=activo_id)
            etiqueta = get_object_or_404(EtiquetaQR, activo=activo)
            if etiqueta.activa:
                etiqueta.activa = False
                etiqueta.save(update_fields=["activa", "fecha_actualizacion"])
        return Response(status=204)


class ActivoQRImagenView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(responses={(200, "image/png"): OpenApiTypes.BINARY})
    def get(self, request, activo_id):
        activo = get_object_or_404(Activo, pk=activo_id)
        etiqueta = get_object_or_404(EtiquetaQR, activo=activo, activa=True)
        imagen = generar_imagen_qr(construir_url_qr(etiqueta))
        respuesta = HttpResponse(imagen.getvalue(), content_type="image/png")
        respuesta["Content-Disposition"] = content_disposition_header(False, f"qr_{activo.numero_inventario}.png")
        respuesta["Cache-Control"] = "no-store"
        respuesta["X-Content-Type-Options"] = "nosniff"
        return respuesta


class ConsultaQRPublicaView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    @extend_schema(responses=inline_serializer(name="ConsultaPublicaQR", fields={
        "numero_inventario": serializers.CharField(),
        "articulo": serializers.CharField(),
        "tipo_bien": serializers.CharField(),
        "estado": serializers.CharField(),
        "ultima_actualizacion": serializers.DateTimeField(),
    }))
    def get(self, request, token):
        etiqueta = get_object_or_404(
            EtiquetaQR.objects.select_related("activo__articulo__tipo_bien", "activo__estado"),
            token=token, activa=True,
        )
        activo = etiqueta.activo
        ultimo = Movimiento.objects.filter(activo=activo).order_by("-fecha", "-pk").first()
        response = Response({
            "numero_inventario": activo.numero_inventario,
            "articulo": activo.articulo.nombre,
            "tipo_bien": activo.articulo.tipo_bien.nombre,
            "estado": activo.estado.nombre,
            "ultima_actualizacion": ultimo.fecha if ultimo else etiqueta.fecha_actualizacion,
        })
        response["Cache-Control"] = "no-store"
        return response
