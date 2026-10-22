
from datetime import date

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Factura


class FacturaAPITests(APITestCase):
    def setUp(self):
        self.factura = Factura.objects.create(
            folio="TEST-FACTURA-001",
            fecha_emision=date(2026, 10, 21),
            proveedor_nombre="Proveedor de prueba",
            proveedor_rfc="XAXX010101000",
            importe_total="1500.00",
        )
        self.url = "/api/facturas/"

    def test_listar_facturas(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, "TEST-FACTURA-001")

    def test_crear_factura(self):
        datos = {
            "folio": "TEST-FACTURA-002",
            "fecha_emision": "2026-10-21",
            "proveedor_nombre": "Otro proveedor",
            "proveedor_rfc": "XAXX010101000",
            "importe_total": "2500.00",
        }

        response = self.client.post(self.url, datos, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            Factura.objects.filter(folio="TEST-FACTURA-002").exists()
        )
