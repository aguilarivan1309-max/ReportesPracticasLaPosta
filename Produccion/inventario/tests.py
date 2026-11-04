
from datetime import date
from decimal import Decimal

from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Factura, Proveedor


class FacturaAPITests(APITestCase):

    def setUp(self):
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
        self.proveedor = Proveedor.objects.create(
            nombre="Proveedor de prueba",
            rfc="AAA010101AAA",
            contacto="Ana Lopez",
            correo="proveedor@example.com",
            telefono="2281234567",
            activo=True,
        )

        self.url = "/api/proveedores/"

    def test_listar_proveedores(self):
        response = self.client.get(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertContains(response, "Proveedor de prueba")

    def test_crear_proveedor(self):
        datos = {
            "nombre": "Nuevo proveedor",
            "rfc": "BBB010101BBB",
            "contacto": "Carlos Perez",
            "correo": "nuevo@example.com",
            "telefono": "2287654321",
            "activo": True,
        }

        response = self.client.post(
            self.url,
            datos,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
            response.data,
        )

        self.assertTrue(
            Proveedor.objects.filter(
                nombre="Nuevo proveedor"
            ).exists()
        )

    def test_consultar_proveedor(self):
        response = self.client.get(
            f"{self.url}{self.proveedor.pk}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["nombre"],
            "Proveedor de prueba",
        )

    def test_actualizar_proveedor(self):
        datos = {
            "telefono": "2289999999",
        }

        response = self.client.patch(
            f"{self.url}{self.proveedor.pk}/",
            datos,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            response.data,
        )

        self.proveedor.refresh_from_db()

        self.assertEqual(
            self.proveedor.telefono,
            "2289999999",
        )

    def test_eliminar_proveedor(self):
        response = self.client.delete(
            f"{self.url}{self.proveedor.pk}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
        )

        self.assertFalse(
            Proveedor.objects.filter(
                pk=self.proveedor.pk
            ).exists()
        )