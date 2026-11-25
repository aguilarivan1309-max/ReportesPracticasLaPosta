from io import BytesIO

import qrcode
from django.conf import settings
from django.db import transaction
from django.shortcuts import get_object_or_404
from .models import Activo, EtiquetaQR


def construir_url_qr(etiqueta):
    token = etiqueta.token
    return f"{settings.QR_PUBLIC_BASE_URL.rstrip('/')}/{token}/"


def generar_imagen_qr(contenido):
    codigo = qrcode.QRCode(
        version=None, error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10, border=4,
    )
    codigo.add_data(contenido)
    codigo.make(fit=True)
    imagen = codigo.make_image(fill_color="black", back_color="white")
    archivo = BytesIO()
    imagen.save(archivo, format="PNG")
    archivo.seek(0)
    return archivo


@transaction.atomic
def obtener_o_crear_etiqueta(activo_id):
    activo = get_object_or_404(Activo.objects.select_for_update(), pk=activo_id)
    return EtiquetaQR.objects.get_or_create(activo=activo)
