from io import BytesIO
from uuid import uuid4
from decimal import Decimal
from unittest.mock import patch

from PIL import Image
from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.test import override_settings
from django.urls import reverse
from rest_framework.test import APITestCase

from auditoria.models import RegistroAuditoria
from .models import Activo, Articulo, EstadoActivo, EtiquetaQR, TipoBien
from .serializers import EtiquetaQRSerializer
from .servicios_qr import construir_url_qr, generar_imagen_qr


class SistemaQRTests(APITestCase):
    def setUp(self):
        self.usuario = get_user_model().objects.create_user(username="usuario_qr", password="Prueba12345")
        self.client.force_login(self.usuario)
        tipo = TipoBien.objects.create(nombre="Equipo de cómputo")
        articulo = Articulo.objects.create(tipo_bien=tipo, nombre="Computadora")
        estado = EstadoActivo.objects.create(nombre="Almacenamiento")
        self.activo = Activo.objects.create(numero_inventario="INV-QR-001", articulo=articulo, estado=estado)
        self.url = reverse("activo-qr", args=[self.activo.pk])
        self.imagen = reverse("activo-qr-imagen", args=[self.activo.pk])

    def test_crea_y_reutiliza_sin_cambiar_token(self):
        primera = self.client.post(self.url)
        segunda = self.client.post(self.url)
        self.assertEqual(primera.status_code, 201)

        self.assertEqual(segunda.status_code, 200)
        self.assertEqual(primera.data["token"], segunda.data["token"])
        self.assertEqual(EtiquetaQR.objects.count(), 1)
        self.assertEqual(primera.data["numero_inventario"], "INV-QR-001")

    def test_requiere_autenticacion(self):
        self.client.logout()
        for url in (self.url, self.imagen):
            self.assertIn(self.client.get(url).status_code, (401, 403))
        self.assertFalse(EtiquetaQR.objects.exists())

    def test_activo_inexistente(self):
        for nombre in ("activo-qr", "activo-qr-imagen"):
            self.assertEqual(self.client.get(reverse(nombre, args=[999999])).status_code, 404)

    def test_descarga_no_crea_etiqueta(self):
        self.assertEqual(self.client.get(self.imagen).status_code, 404)
        self.assertFalse(EtiquetaQR.objects.exists())

    def test_etiqueta_desactivada(self):
        etiqueta = EtiquetaQR.objects.create(activo=self.activo, activa=False)
        self.assertEqual(self.client.post(self.url).status_code, 409)
        self.assertEqual(self.client.get(self.imagen).status_code, 404)
        etiqueta.refresh_from_db()
        self.assertFalse(etiqueta.activa)
        self.assertEqual(EtiquetaQR.objects.count(), 1)

    def test_descarga_png_con_url_de_la_etiqueta(self):
        etiqueta = EtiquetaQR.objects.create(activo=self.activo)
        with patch("inventario.views.generar_imagen_qr", wraps=generar_imagen_qr) as generar:
            respuesta = self.client.get(self.imagen)
        generar.assert_called_once_with(construir_url_qr(etiqueta))
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta["Content-Type"], "image/png")
        self.assertIn("qr_INV-QR-001.png", respuesta["Content-Disposition"])
        imagen = Image.open(BytesIO(respuesta.content))
        self.assertEqual(imagen.format, "PNG")
        imagen.verify()

    @override_settings(QR_PUBLIC_BASE_URL="https://ejemplo.test/consulta/qr/")
    def test_url_configurable(self):
        datos = self.client.post(self.url).data
        self.assertEqual(datos["url_publica"], f"https://ejemplo.test/consulta/qr/{datos['token']}/")

    def test_unica_etiqueta_por_activo(self):
        EtiquetaQR.objects.create(activo=self.activo)
        with self.assertRaises(IntegrityError), transaction.atomic():
            EtiquetaQR.objects.create(activo=self.activo)

    def test_auditoria_de_creacion_y_eliminacion(self):
        self.client.post(self.url)
        etiqueta = EtiquetaQR.objects.get(activo=self.activo)
        registros = RegistroAuditoria.objects.filter(content_type__model="etiquetaqr", object_id=str(etiqueta.pk))
        registro = registros.get(accion="Creación")
        self.assertEqual(registro.usuario, self.usuario)
        self.client.get(self.url)
        self.assertEqual(registros.filter(accion="Creación").count(), 1)
        self.activo.delete()
        self.assertFalse(EtiquetaQR.objects.exists())
        self.assertTrue(registros.filter(accion="Eliminación").exists())

    def test_serializer_no_permite_editar_token(self):
        etiqueta = EtiquetaQR.objects.create(activo=self.activo)
        token = etiqueta.token
        serializer = EtiquetaQRSerializer(etiqueta, data={"token": "otro", "activa": False}, partial=True)
        self.assertTrue(serializer.is_valid())
        serializer.save()
        etiqueta.refresh_from_db()
        self.assertEqual(etiqueta.token, token)
        self.assertTrue(etiqueta.activa)


    def test_get_no_genera_etiqueta(self):
        self.assertEqual(self.client.get(self.url).status_code, 404)
        self.assertFalse(EtiquetaQR.objects.exists())

    def test_consulta_publica_solo_muestra_datos_basicos(self):
        datos = self.client.post(self.url).data
        self.assertIn(self.imagen, datos["url_imagen"])
        self.client.logout()
        url = reverse("qr-consulta-publica", args=[datos["token"]])
        respuesta = self.client.get(url)
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(set(respuesta.data), {"numero_inventario", "articulo", "tipo_bien", "estado", "ultima_actualizacion"})
        self.assertEqual(respuesta.data["numero_inventario"], self.activo.numero_inventario)
        self.assertEqual(respuesta["Cache-Control"], "no-store")

    def test_desactivar_invalida_consulta_publica_e_imagen(self):
        datos = self.client.post(self.url).data
        etiqueta = EtiquetaQR.objects.get(activo=self.activo)
        antes = etiqueta.fecha_actualizacion
        self.assertEqual(self.client.delete(self.url).status_code, 204)
        etiqueta.refresh_from_db()
        self.assertFalse(etiqueta.activa)
        self.assertGreaterEqual(etiqueta.fecha_actualizacion, antes)
        self.assertEqual(self.client.get(self.imagen).status_code, 404)
        self.assertEqual(self.client.post(self.url).status_code, 409)
        self.assertTrue(RegistroAuditoria.objects.filter(content_type__model="etiquetaqr", object_id=str(etiqueta.pk), campo_modificado="activa", valor_nuevo="No").exists())
        self.client.logout()
        self.assertEqual(self.client.get(reverse("qr-consulta-publica", args=[datos["token"]])).status_code, 404)

    def test_token_inexistente(self):
        self.client.logout()
        self.assertEqual(self.client.get(reverse("qr-consulta-publica", args=[uuid4()])).status_code, 404)

    def test_anonimo_no_crea_ni_desactiva(self):
        self.client.post(self.url)
        self.client.logout()
        self.assertIn(self.client.post(self.url).status_code, (401, 403))
        self.assertIn(self.client.delete(self.url).status_code, (401, 403))
        self.assertTrue(EtiquetaQR.objects.get(activo=self.activo).activa)

    def test_alta_automatica_respeta_tipo_bien_y_rollback(self):
        from datetime import date
        from django.db import transaction
        from .models import Factura, PropuestaInventario
        from .servicios import registrar_propuesta
        factura = Factura.objects.create(folio="QR-AUTO", fecha_emision=date(2026, 11, 25), proveedor_nombre="Prueba")
        for indice, requiere in enumerate((True, False), 1):
            tipo = self.activo.articulo.tipo_bien
            tipo.requiere_qr = requiere
            tipo.save()
            propuesta = PropuestaInventario.objects.create(
                factura=factura, indice_concepto=indice, descripcion="Equipo", cantidad=Decimal("2"),
                tipo_registro="activo", estado_revision="aceptada",
                articulo=self.activo.articulo, estado_activo=self.activo.estado,
            )
            with transaction.atomic():
                activos, _ = registrar_propuesta(propuesta)
            self.assertEqual(EtiquetaQR.objects.filter(activo__in=activos).count(), 2 if requiere else 0)
        propuesta = PropuestaInventario.objects.create(
            factura=factura, indice_concepto=3, descripcion="Equipo", cantidad=Decimal("1"),
            tipo_registro="activo", estado_revision="aceptada",
            articulo=self.activo.articulo, estado_activo=self.activo.estado,
        )
        tipo.requiere_qr = True
        tipo.save()
        antes = EtiquetaQR.objects.count()
        with self.assertRaises(RuntimeError):
            with transaction.atomic():
                registrar_propuesta(propuesta)
                raise RuntimeError("Cancelar prueba")
        self.assertEqual(EtiquetaQR.objects.count(), antes)
