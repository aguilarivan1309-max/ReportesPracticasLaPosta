
from decimal import Decimal

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import SimpleTestCase
from rest_framework.exceptions import ValidationError

from .conceptos_xml import extraer_conceptos_factura


class ExtraccionConceptosXMLTests(SimpleTestCase):

    def crear_xml(self, conceptos):
        contenido = f"""<?xml version="1.0" encoding="UTF-8"?>
        <cfdi:Comprobante
            xmlns:cfdi="http://www.sat.gob.mx/cfd/4"
            Version="4.0"
            Folio="PRUEBA-001">
            <cfdi:Conceptos>
                {conceptos}
            </cfdi:Conceptos>
        </cfdi:Comprobante>
        """

        return SimpleUploadedFile(
            "factura_prueba.xml",
            contenido.encode("utf-8"),
            content_type="application/xml",
        )

    def concepto(
        self,
        descripcion="Memoria RAM 16 GB",
        cantidad="6.000000",
        precio="850.00",
        importe="5100.00",
    ):
        return f"""
        <cfdi:Concepto
            ClaveProdServ="43201400"
            NoIdentificacion="RAM-16"
            Cantidad="{cantidad}"
            ClaveUnidad="H87"
            Unidad="Pieza"
            Descripcion="{descripcion}"
            ValorUnitario="{precio}"
            Importe="{importe}"
            ObjetoImp="02"
        />
        """

    def test_extraer_un_concepto(self):
        archivo = self.crear_xml(self.concepto())

        conceptos = extraer_conceptos_factura(archivo)

        self.assertEqual(len(conceptos), 1)
        self.assertEqual(
            conceptos[0]["descripcion"],
            "Memoria RAM 16 GB",
        )
        self.assertEqual(conceptos[0]["cantidad"], Decimal("6.000000"))
        self.assertEqual(conceptos[0]["importe"], Decimal("5100.00"))

    def test_extraer_varios_conceptos(self):
        contenido = (
            self.concepto()
            + self.concepto(
                descripcion="Disco SSD 1 TB",
                cantidad="2.000000",
                precio="1200.00",
                importe="2400.00",
            )
        )

        archivo = self.crear_xml(contenido)
        conceptos = extraer_conceptos_factura(archivo)

        self.assertEqual(len(conceptos), 2)
        self.assertEqual(conceptos[0]["numero_concepto"], 1)
        self.assertEqual(conceptos[1]["numero_concepto"], 2)
        self.assertEqual(
            conceptos[1]["descripcion"],
            "Disco SSD 1 TB",
        )

    def test_conservar_atributos_originales(self):
        archivo = self.crear_xml(self.concepto())

        concepto = extraer_conceptos_factura(archivo)[0]

        self.assertEqual(
            concepto["cantidad_original"],
            "6.000000",
        )
        self.assertEqual(
            concepto["valor_unitario_original"],
            "850.00",
        )
        self.assertEqual(
            concepto["atributos_originales"]["NoIdentificacion"],
            "RAM-16",
        )
        self.assertIn("Concepto", concepto["xml_concepto"])

    def test_rechazar_xml_sin_conceptos(self):
        archivo = self.crear_xml("")

        with self.assertRaises(ValidationError):
            extraer_conceptos_factura(archivo)

    def test_rechazar_cantidad_cero(self):
        archivo = self.crear_xml(
            self.concepto(cantidad="0.000000", importe="0.00")
        )

        with self.assertRaises(ValidationError):
            extraer_conceptos_factura(archivo)

    def test_rechazar_cantidad_negativa(self):
        archivo = self.crear_xml(
            self.concepto(cantidad="-2.000000", importe="1700.00")
        )

        with self.assertRaises(ValidationError):
            extraer_conceptos_factura(archivo)

    def test_rechazar_importe_invalido(self):
        archivo = self.crear_xml(
            self.concepto(importe="importe-invalido")
        )

        with self.assertRaises(ValidationError):
            extraer_conceptos_factura(archivo)

    def test_rechazar_descripcion_vacia(self):
        archivo = self.crear_xml(
            self.concepto(descripcion="")
        )

        with self.assertRaises(ValidationError):
            extraer_conceptos_factura(archivo)

    def test_rechazar_xml_malformado(self):
        archivo = SimpleUploadedFile(
            "incorrecto.xml",
            b"<Comprobante><Conceptos>",
            content_type="application/xml",
        )

        with self.assertRaises(ValidationError):
            extraer_conceptos_factura(archivo)
