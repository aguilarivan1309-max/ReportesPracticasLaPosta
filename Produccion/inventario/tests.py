
from datetime import date

from django.urls import reverse
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
