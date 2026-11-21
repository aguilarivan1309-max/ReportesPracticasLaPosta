from contextvars import ContextVar
from ipaddress import ip_address

_peticion_actual = ContextVar("auditoria_peticion", default=None)


def obtener_usuario_actual():
    request = _peticion_actual.get()
    usuario = getattr(request, "user", None)
    if usuario is not None and getattr(usuario, "is_authenticated", False):
        return usuario
    return None


def extraer_ip(request):
    valor = request.META.get("REMOTE_ADDR")
    try:
        return str(ip_address(valor)) if valor else None
    except ValueError:
        return None


def obtener_ip_actual():
    request = _peticion_actual.get()
    return extraer_ip(request) if request is not None else None


class AuditoriaMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Se lee el usuario al guardar: DRF puede autenticarlo después del middleware.
        token = _peticion_actual.set(request)
        try:
            return self.get_response(request)
        finally:
            _peticion_actual.reset(token)
