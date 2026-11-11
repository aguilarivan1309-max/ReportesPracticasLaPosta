import xml.etree.ElementTree as ET
from django.core.exceptions import ValidationError

def validar_pdf(archivo):
    if not archivo.name.lower().endswith(".pdf"):
        raise ValidationError("Solo se permiten archivos PDF.")
    try:
        archivo.seek(0)
        encabezado = archivo.read(5)
        archivo.seek(0)
    except (OSError, AttributeError):
        raise ValidationError("No se pudo leer el archivo PDF.")
    if encabezado != b"%PDF-":
        raise ValidationError(
            "El  archivo no contiene una cabecera PDF valida."
        )

def validar_xml(archivo):
    if not archivo.name.lower().endswith(".xml"):
            raise ValidationError("Solo se permiten archivos XML")
    try:
         archivo.seek(0)
         contenido = archivo.read()
         archivo.seek(0)
         ET.fromstring(contenido)
    except ET.ParseError:
         raise ValidationError("El archivo no contiene XML valido.")
    except(OSError, UnicodeError, ValueError):
         raise ValidationError("No se puede leer el archivo XML.")
