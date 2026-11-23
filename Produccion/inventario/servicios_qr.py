from io import BytesIO

import qrcode
from django.conf import settings


def construir_url_qr(token):
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
