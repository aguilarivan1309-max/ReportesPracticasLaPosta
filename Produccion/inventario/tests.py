import tempfile
from django.test import override_settings
from django.urls import reverse

from datetime import date
from decimal import Decimal

from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Factura, Proveedor


class FacturaAPITests(APITestCase):

    def setUp(self):
        media = tempfile.TemporaryDirectory()
        self.addCleanup(media.cleanup)
        settings = override_settings(MEDIA_ROOT=media.name)
        settings.enable()
        self.addCleanup(settings.disable)
        self.factura = Factura.objects.create(
            folio="TEST-FACTURA-001",
            fecha_emision=date(2026, 10, 21),
            proveedor_nombre="Proveedor de prueba",
            proveedor_rfc="XAXX010101000",
            importe_total=Decimal("1500.00"),
        )

        self.url = "/api/facturas/"

    def crear_xml_prueba(self):
        contenido_xml = b"""<?xml version="1.0" encoding="UTF-8"?>
<cfdi:Comprobante
    xmlns:cfdi="http://www.sat.gob.mx/cfd/4"
    xmlns:tfd="http://www.sat.gob.mx/TimbreFiscalDigital"
    Version="4.0"
    Folio="TEST-FACTURA-002"
    Fecha="2026-10-21T12:00:00"
    Total="2500.00">
    <cfdi:Emisor
        Rfc="AAA010101AAA"
        Nombre="Otro proveedor"/>
    <cfdi:Receptor
        Rfc="XAXX010101000"
        Nombre="Cliente de prueba"/>
    <cfdi:Complemento>
        <tfd:TimbreFiscalDigital
            UUID="12345678-1234-1234-1234-123456789012"/>
    </cfdi:Complemento>
</cfdi:Comprobante>
"""

        return SimpleUploadedFile(
            "factura_prueba.xml",
            contenido_xml,
            content_type="application/xml",
        )

    def test_listar_facturas(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, "TEST-FACTURA-001")

    def test_crear_factura(self):
        datos = {
            "archivo_xml": self.crear_xml_prueba(),
        }

        response = self.client.post(
            self.url,
            datos,
            format="multipart",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
            response.data,
        )

        self.assertTrue(
            Factura.objects.filter(
                folio="TEST-FACTURA-002"
            ).exists()
        )
class ProveedorAPITests(APITestCase):
    def setUp(self):
        self.proveedor = Proveedor.objects.create(nombre="Proveedor de prueba", rfc="CCC010101CCC")
        self.url = reverse("proveedor-list-create")
        self.detalle = reverse("proveedor-detail", args=[self.proveedor.pk])

    def test_listar_proveedores(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, self.proveedor.nombre)

    def test_crear_proveedor(self):
        response = self.client.post(self.url, {"nombre": "Nuevo proveedor"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Proveedor.objects.filter(pk=response.data["id"], nombre="Nuevo proveedor").exists())

    def test_consultar_proveedor(self):
        response = self.client.get(self.detalle)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.proveedor.pk)

    def test_actualizar_proveedor(self):
        response = self.client.patch(self.detalle, {"telefono": "2281112233"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.proveedor.refresh_from_db()
        self.assertEqual(self.proveedor.telefono, "2281112233")

    def test_eliminar_proveedor_sin_facturas(self):
        response = self.client.delete(self.detalle)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Proveedor.objects.filter(pk=self.proveedor.pk).exists())

    def test_no_eliminar_proveedor_con_facturas(self):
        factura = Factura.objects.create(
            folio="FACTURA-PROVEEDOR-001", fecha_emision=date(2026, 10, 21),
            proveedor_nombre=self.proveedor.nombre, proveedor_rfc=self.proveedor.rfc,
            importe_total="3500.00", proveedor=self.proveedor,
        )
        response = self.client.delete(self.detalle)
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(response.data["detail"], "No se puede eliminar este proveedor porque tiene facturas asociadas.")
        self.assertTrue(Proveedor.objects.filter(pk=self.proveedor.pk).exists())
        factura.refresh_from_db()
        self.assertEqual(factura.proveedor_id, self.proveedor.pk)

    def test_consultar_proveedor_inexistente(self):
        url = reverse("proveedor-detail", args=[self.proveedor.pk + 999999])
        self.assertEqual(self.client.get(url).status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(self.client.delete(url).status_code, status.HTTP_404_NOT_FOUND)
