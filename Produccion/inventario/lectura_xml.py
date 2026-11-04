
import xml.etree.ElementTree as ET
from datetime import datetime
from decimal import Decimal, InvalidOperation

from rest_framework.exceptions import ValidationError


def nombre_local(etiqueta):
    """Obtiene el nombre de una etiqueta aunque tenga namespace XML."""
    return etiqueta.rsplit("}", 1)[-1].split(":")[-1]


def buscar_elemento(raiz, nombre):
    """Busca un elemento XML por su nombre, ignorando el namespace."""
    for elemento in raiz.iter():
        if nombre_local(elemento.tag) == nombre:
            return elemento
    return None


def extraer_datos_factura(archivo):
    """Extrae los datos principales de un XML de factura."""
    try:
        archivo.seek(0)
        contenido = archivo.read()
        archivo.seek(0)
        raiz = ET.fromstring(contenido)
    except (ET.ParseError, OSError, ValueError):
        raise ValidationError({
            "archivo_xml": "El XML no tiene una estructura válida."
        })

    comprobante = (
        raiz
        if nombre_local(raiz.tag) == "Comprobante"
        else buscar_elemento(raiz, "Comprobante")
    )

    emisor = buscar_elemento(raiz, "Emisor")
    timbre = buscar_elemento(raiz, "TimbreFiscalDigital")

    if comprobante is None or emisor is None:
        raise ValidationError({
            "archivo_xml": (
                "El XML debe contener los elementos Comprobante y Emisor."
            )
        })

    atributos = comprobante.attrib
    datos_emisor = emisor.attrib

    folio_xml = atributos.get("Folio", "").strip()
    serie = atributos.get("Serie", "").strip()

    folio = (
        f"{serie}-{folio_xml}"
        if serie and folio_xml
        else folio_xml or serie
    )

    fecha_texto = atributos.get("Fecha", "").strip()
    total_texto = atributos.get("Total", "").strip()
    proveedor_nombre = datos_emisor.get("Nombre", "").strip()
    proveedor_rfc = datos_emisor.get("Rfc", "").strip()

    errores = {}

    if not folio:
        errores["folio"] = "El XML no contiene Folio ni Serie."

    if not fecha_texto:
        errores["fecha_emision"] = "El XML no contiene Fecha."

    if not proveedor_nombre:
        errores["proveedor_nombre"] = (
            "El XML no contiene el nombre del emisor."
        )

    if not proveedor_rfc:
        errores["proveedor_rfc"] = "El XML no contiene RFC del emisor."

    if not total_texto:
        errores["importe_total"] = "El XML no contiene Total."

    fecha = None
    if fecha_texto:
        try:
            fecha = datetime.fromisoformat(
                fecha_texto.replace("Z", "+00:00")
            ).date()
        except ValueError:
            errores["fecha_emision"] = "La fecha del XML no es válida."

    total = None
    if total_texto:
        try:
            total = Decimal(total_texto)
            if not total.is_finite() or total < 0:
                raise InvalidOperation
        except (InvalidOperation, ValueError):
            errores["importe_total"] = "El total del XML no es válido."

    if errores:
        raise ValidationError(errores)

    return {
        "folio": folio,
        "fecha_emision": fecha,
        "proveedor_nombre": proveedor_nombre,
        "proveedor_rfc": proveedor_rfc,
        "importe_total": total,
        "uuid_fiscal": (
            timbre.attrib.get("UUID", "").strip() or None
            if timbre is not None
            else None
        ),
    }
