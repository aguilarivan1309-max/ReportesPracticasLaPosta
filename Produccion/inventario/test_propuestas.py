import tempfile
from datetime import date
from decimal import Decimal

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from rest_framework import status
from rest_framework.test import APITestCase

from .models import (
    Articulo,
    EstadoActivo,
    Factura,
    PropuestaInventario,
    TipoBien,
)

XML_DOS_CONCEPTOS = b"""<?xml version="1.0" encoding="UTF-8"?>
<cfdi:Comprobante xmlns:cfdi="http://www.sat.gob.mx/cfd/4" Version="4.0" Folio="P-001">
  <cfdi:Conceptos>
    <cfdi:Concepto ClaveProdServ="43201400" NoIdentificacion="RAM-16"
        Cantidad="6.000000" ClaveUnidad="H87" Unidad="Pieza"
        Descripcion="Memoria RAM 16 GB" ValorUnitario="850.000000"
        Importe="5100.00" ObjetoImp="02"/>
    <cfdi:Concepto ClaveProdServ="43211500" NoIdentificacion="LAP-01"
        Cantidad="2" ClaveUnidad="H87" Unidad="Pieza"
        Descripcion="Laptop 14 pulgadas" ValorUnitario="15000.00"
        Importe="30000.00" ObjetoImp="02"/>
  </cfdi:Conceptos>
</cfdi:Comprobante>
"""


@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class PropuestaInventarioAPITests(APITestCase):

    def setUp(self):
        self.factura = Factura.objects.create(
            folio="P-001",
            fecha_emision=date(2026, 11, 1),
            proveedor_nombre="Proveedor de prueba",
            archivo_xml=SimpleUploadedFile(
                "factura.xml", XML_DOS_CONCEPTOS, content_type="application/xml"
            ),
        )
        self.url_generar = f"/api/facturas/{self.factura.id}/propuestas/"

    def generar(self):
        return self.client.post(self.url_generar)

    def test_generar_propuestas_desde_xml(self):
        respuesta = self.generar()
        self.assertEqual(respuesta.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(respuesta.data), 2)
        ram = PropuestaInventario.objects.get(indice_concepto=1)
        self.assertEqual(ram.cantidad, Decimal("6"))
        self.assertEqual(ram.valor_unitario, Decimal("850.00"))
        self.assertEqual(ram.estado_revision, "pendiente")
        self.assertEqual(ram.tipo_registro, "por_clasificar")

    def test_generar_dos_veces_no_duplica(self):
        self.generar()
        respuesta = self.generar()
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.assertEqual(PropuestaInventario.objects.count(), 2)

    def test_factura_sin_xml(self):
        sin_xml = Factura.objects.create(
            folio="SIN-XML", fecha_emision=date(2026, 11, 1),
            proveedor_nombre="X",
        )
        respuesta = self.client.post(f"/api/facturas/{sin_xml.id}/propuestas/")
        self.assertEqual(respuesta.status_code, status.HTTP_400_BAD_REQUEST)

    def test_factura_inexistente(self):
        respuesta = self.client.post("/api/facturas/9999/propuestas/")
        self.assertEqual(respuesta.status_code, status.HTTP_404_NOT_FOUND)

    def test_listar_con_filtros(self):
        self.generar()
        r = self.client.get("/api/propuestas/?estado=pendiente")
        self.assertEqual(len(r.data["results"] if "results" in r.data else r.data), 2)
        r = self.client.get("/api/propuestas/?estado=aceptada")
        self.assertEqual(len(r.data["results"] if "results" in r.data else r.data), 0)

    def test_editar_clasificacion(self):
        self.generar()
        p = PropuestaInventario.objects.get(indice_concepto=1)
        r = self.client.patch(
            f"/api/propuestas/{p.id}/",
            {"tipo_registro": "componente", "marca": "Kingston"},
            format="json",
        )
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        p.refresh_from_db()
        self.assertEqual(p.tipo_registro, "componente")
        self.assertEqual(p.marca, "Kingston")

    def test_no_se_edita_dato_del_xml(self):
        self.generar()
        p = PropuestaInventario.objects.get(indice_concepto=1)
        self.client.patch(
            f"/api/propuestas/{p.id}/", {"cantidad": "99"}, format="json"
        )
        p.refresh_from_db()
        self.assertEqual(p.cantidad, Decimal("6"))

    def test_no_aceptar_sin_clasificar(self):
        self.generar()
        p = PropuestaInventario.objects.get(indice_concepto=1)
        r = self.client.post(f"/api/propuestas/{p.id}/aceptar/")
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

    def test_activo_requiere_articulo_y_estado(self):
        self.generar()
        p = PropuestaInventario.objects.get(indice_concepto=2)
        self.client.patch(
            f"/api/propuestas/{p.id}/", {"tipo_registro": "activo"}, format="json"
        )
        r = self.client.post(f"/api/propuestas/{p.id}/aceptar/")
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("articulo", r.data)

        tipo = TipoBien.objects.create(nombre="Equipo de cómputo")
        articulo = Articulo.objects.create(tipo_bien=tipo, nombre="Laptop")
        estado = EstadoActivo.objects.create(nombre="Disponible")
        self.client.patch(
            f"/api/propuestas/{p.id}/",
            {"articulo": articulo.id, "estado_activo": estado.id},
            format="json",
        )
        r = self.client.post(f"/api/propuestas/{p.id}/aceptar/")
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertEqual(r.data["estado_revision"], "aceptada")
        self.assertIsNotNone(r.data["fecha_revision"])

    def test_rechazar_y_no_reeditar(self):
        self.generar()
        p = PropuestaInventario.objects.get(indice_concepto=1)
        r = self.client.post(f"/api/propuestas/{p.id}/rechazar/")
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertEqual(r.data["estado_revision"], "rechazada")
        r = self.client.patch(
            f"/api/propuestas/{p.id}/", {"marca": "X"}, format="json"
        )
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)
        r = self.client.post(f"/api/propuestas/{p.id}/aceptar/")
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

    def test_detalle_factura(self):
        r = self.client.get(f"/api/facturas/{self.factura.id}/")
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertEqual(r.data["folio"], "P-001")

    def test_no_eliminar_factura_con_propuestas(self):
        self.generar()
        r = self.client.delete(f"/api/facturas/{self.factura.id}/")
        self.assertEqual(r.status_code, status.HTTP_409_CONFLICT)
        self.assertTrue(Factura.objects.filter(id=self.factura.id).exists())

    def test_eliminar_factura_sin_relaciones(self):
        r = self.client.delete(f"/api/facturas/{self.factura.id}/")
        self.assertEqual(r.status_code, status.HTTP_204_NO_CONTENT)
