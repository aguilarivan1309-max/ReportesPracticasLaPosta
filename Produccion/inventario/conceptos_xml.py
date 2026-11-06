
import xml.etree.ElementTree as ET
from decimal import Decimal, InvalidOperation

from rest_framework.exceptions import ValidationError


def obtener_nombre_local(etiqueta):
    """Obtiene el nombre de una etiqueta XML sin su namespace."""
    return etiqueta.rsplit("}", 1)[-1].split(":")[-1]


def obtener_atributo(elemento, nombre):
    """Obtiene un atributo XML de manera segura."""
    return elemento.attrib.get(nombre, "").strip()


def convertir_decimal(valor, campo, indice, obligatorio=True):
    """Convierte un valor XML a Decimal y valida su contenido."""
    if not valor:
        if obligatorio:
            raise ValidationError({
                "archivo_xml": (
                    f"El concepto {indice} no contiene el campo {campo}."
                )
            })
        return None

    try:
        numero = Decimal(valor)

        if not numero.is_finite():
            raise InvalidOperation

        return numero

    except (InvalidOperation, ValueError):
        raise ValidationError({
            "archivo_xml": (
                f"El campo {campo} del concepto {indice} "
                "no contiene un valor numérico válido."
            )
        })


def extraer_conceptos_factura(archivo):
    """
    Extrae todos los conceptos de un CFDI.

    Conserva los atributos originales y la estructura XML
    de cada concepto para facilitar su posterior revisión.
    """
    try:
        archivo.seek(0)
        contenido = archivo.read()
        archivo.seek(0)

        raiz = ET.fromstring(contenido)

    except (ET.ParseError, OSError, ValueError):
        raise ValidationError({
            "archivo_xml": "No fue posible interpretar el XML."
        })

    comprobante = (
        raiz
        if obtener_nombre_local(raiz.tag) == "Comprobante"
        else next(
            (
                elemento
                for elemento in raiz.iter()
                if obtener_nombre_local(elemento.tag) == "Comprobante"
            ),
            None,
        )
    )

    if comprobante is None:
        raise ValidationError({
            "archivo_xml": "No se encontró el comprobante CFDI."
        })

    nodo_conceptos = next(
        (
            elemento
            for elemento in comprobante.iter()
            if obtener_nombre_local(elemento.tag) == "Conceptos"
        ),
        None,
    )

    if nodo_conceptos is None:
        raise ValidationError({
            "archivo_xml": "La factura no contiene conceptos."
        })

    elementos = [
        elemento
        for elemento in nodo_conceptos
        if obtener_nombre_local(elemento.tag) == "Concepto"
    ]

    if not elementos:
        raise ValidationError({
            "archivo_xml": "La factura no contiene conceptos registrados."
        })

    conceptos = []

    for indice, elemento in enumerate(elementos, start=1):

        atributos = {
            nombre: valor
            for nombre, valor in elemento.attrib.items()
        }

        descripcion = obtener_atributo(elemento, "Descripcion")

        if not descripcion:
            raise ValidationError({
                "archivo_xml": (
                    f"El concepto {indice} no contiene descripción."
                )
            })

        cantidad_original = obtener_atributo(elemento, "Cantidad")
        precio_original = obtener_atributo(elemento, "ValorUnitario")
        importe_original = obtener_atributo(elemento, "Importe")
        descuento_original = obtener_atributo(elemento, "Descuento")

        cantidad = convertir_decimal(
            cantidad_original,
            "Cantidad",
            indice,
        )

        valor_unitario = convertir_decimal(
            precio_original,
            "ValorUnitario",
            indice,
        )

        importe = convertir_decimal(
            importe_original,
            "Importe",
            indice,
        )

        descuento = convertir_decimal(
            descuento_original,
            "Descuento",
            indice,
            obligatorio=False,
        )

        if cantidad <= 0:
            raise ValidationError({
                "archivo_xml": (
                    f"La cantidad del concepto {indice} debe ser mayor que cero."
                )
            })

        if valor_unitario < 0 or importe < 0:
            raise ValidationError({
                "archivo_xml": (
                    f"El concepto {indice} contiene importes negativos."
                )
            })

        if descuento is not None and descuento < 0:
            raise ValidationError({
                "archivo_xml": (
                    f"El descuento del concepto {indice} no puede ser negativo."
                )
            })

        conceptos.append({
            "numero_concepto": indice,
            "clave_prod_serv": obtener_atributo(
                elemento, "ClaveProdServ"
            ),
            "no_identificacion": obtener_atributo(
                elemento, "NoIdentificacion"
            ),
            "cantidad_original": cantidad_original,
            "cantidad": cantidad,
            "clave_unidad": obtener_atributo(
                elemento, "ClaveUnidad"
            ),
            "unidad": obtener_atributo(
                elemento, "Unidad"
            ),
            "descripcion": descripcion,
            "valor_unitario_original": precio_original,
            "valor_unitario": valor_unitario,
            "importe_original": importe_original,
            "importe": importe,
            "descuento_original": descuento_original,
            "descuento": descuento,
            "objeto_impuesto": obtener_atributo(
                elemento, "ObjetoImp"
            ),
            "atributos_originales": atributos,
            "xml_concepto": ET.tostring(
                elemento,
                encoding="unicode",
            ),
        })

    return conceptos
