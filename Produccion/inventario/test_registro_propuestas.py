import tempfile
from datetime import date

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from rest_framework import status
from rest_framework.test import APITestCase

from .models import (
    Activo,
    Articulo,
    Componente,
    EstadoActivo,
    Factura,
    Movimiento,
    PropuestaInventario,
    TipoBien,
)
from .test_propuestas import XML_DOS_CONCEPTOS


@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class RegistroPropuestasAPITests(APITestCase):

    def setUp(self):
        self.factura = Factura.objects.create(
            folio="R-001",
            fecha_emision=date(2026, 11, 1),
            proveedor_nombre="Proveedor",
            archivo_xml=SimpleUploadedFile(
                "f.xml", XML_DOS_CONCEPTOS, content_type="application/xml"
            ),
        )
        self.client.post(f"/api/facturas/{self.factura.id}/propuestas/")
        self.ram = PropuestaInventario.objects.get(indice_concepto=1)     # cantidad 6
        self.laptop = PropuestaInventario.objects.get(indice_concepto=2)  # cantidad 2
        tipo = TipoBien.objects.create(nombre="Equipo de cómputo")
        self.articulo = Articulo.objects.create(tipo_bien=tipo, nombre="Laptop")
        self.estado = EstadoActivo.objects.create(nombre="Disponible")

    def aceptar(self, propuesta, tipo, **extra):
        datos = {"tipo_registro": tipo, **extra}
        self.client.patch(f"/api/propuestas/{propuesta.id}/", datos, format="json")
        return self.client.post(f"/api/propuestas/{propuesta.id}/aceptar/")

    def registrar(self, propuesta):
        return self.client.post(f"/api/propuestas/{propuesta.id}/registrar/")

    def aceptar_laptop(self):
        return self.aceptar(
            self.laptop, "activo",
            articulo=self.articulo.id, estado_activo=self.estado.id,
        )

    def test_registrar_activos_por_unidad_con_movimiento_alta(self):
        self.aceptar_laptop()
        r = self.registrar(self.laptop)
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)
        anio = r.data["activos"][0].split("-")[1]
        self.assertEqual(r.data["activos"], [f"INV-{anio}-0001", f"INV-{anio}-0002"])
        self.assertEqual(Activo.objects.count(), 2)
        activo = Activo.objects.first()
        self.assertEqual(activo.factura, self.factura)
        self.assertEqual(activo.propuesta_origen, self.laptop)
        self.assertEqual(activo.fecha_adquisicion, date(2026, 11, 1))
        self.assertEqual(Movimiento.objects.filter(tipo="alta").count(), 2)
        self.laptop.refresh_from_db()
        self.assertEqual(self.laptop.estado_revision, "registrada")

    def test_registrar_componentes_por_unidad(self):
        self.aceptar(self.ram, "componente", marca="Kingston")
        r = self.registrar(self.ram)
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(r.data["componentes"]), 6)
        self.assertEqual(Componente.objects.count(), 6)
        c = Componente.objects.first()
        self.assertEqual(c.estado.nombre, "Disponible")
        self.assertEqual(c.marca, "Kingston")
        self.assertEqual(c.factura, self.factura)

    def test_no_registra_si_no_esta_aceptada(self):
        r = self.registrar(self.laptop)
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Activo.objects.count(), 0)

    def test_no_registra_dos_veces(self):
        self.aceptar_laptop()
        self.registrar(self.laptop)
        r = self.registrar(self.laptop)
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Activo.objects.count(), 2)

    def test_no_inventariable_no_genera_registros(self):
        self.aceptar(self.ram, "no_inventariable")
        r = self.registrar(self.ram)
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cantidad_fraccionaria_no_se_registra(self):
        PropuestaInventario.objects.filter(id=self.laptop.id).update(cantidad="1.5")
        self.aceptar_laptop()
        r = self.registrar(self.laptop)
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Activo.objects.count(), 0)
        self.laptop.refresh_from_db()
        self.assertEqual(self.laptop.estado_revision, "aceptada")

    def test_consecutivo_continua_entre_propuestas(self):
        self.aceptar_laptop()
        self.registrar(self.laptop)
        PropuestaInventario.objects.filter(id=self.ram.id).update(cantidad="1")
        self.aceptar(
            self.ram, "activo",
            articulo=self.articulo.id, estado_activo=self.estado.id,
        )
        r = self.registrar(self.ram)
        self.assertTrue(r.data["activos"][0].endswith("-0003"))
