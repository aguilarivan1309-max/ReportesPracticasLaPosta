from django.contrib.contenttypes.models import ContentType
from django.db import DEFAULT_DB_ALIAS

from .middleware import obtener_ip_actual, obtener_usuario_actual
from .models import RegistroAuditoria

CAMPOS_SENSIBLES = {
    "password", "token", "access_token", "refresh_token", "secret", "api_key",
}


def es_sensible(nombre):
    nombre = nombre.lower()
    return any(parte in nombre for parte in CAMPOS_SENSIBLES)


def formatear_valor(instancia, field):
    if es_sensible(field.name):
        return "[DATO OMITIDO]"
    valor = getattr(instancia, field.attname)
    if valor is None or valor == "":
        return "Vacío"
    if field.choices:
        return str(getattr(instancia, f"get_{field.name}_display")())
    if field.is_relation:
        return str(valor)
    if isinstance(valor, bool):
        return "Sí" if valor else "No"
    return str(valor)


def registrar_auditoria(
    instancia, accion, *, campo_modificado="", valor_anterior="",
    valor_nuevo="", descripcion="", usuario=None, using=None,
    registro_afectado=None,
):
    alias = using or instancia._state.db or DEFAULT_DB_ALIAS
    usuario = usuario if usuario is not None else obtener_usuario_actual()
    nombre = usuario.get_username() if usuario is not None else "Sistema"
    usuario_id = None
    if usuario is not None and usuario.pk is not None:
        if usuario._meta.model._default_manager.using(alias).filter(pk=usuario.pk).exists():
            usuario_id = usuario.pk
    if es_sensible(campo_modificado):
        valor_anterior = valor_nuevo = "[DATO OMITIDO]"
    return RegistroAuditoria.objects.using(alias).create(
        usuario_id=usuario_id, usuario_nombre=str(nombre)[:150],
        accion=accion,
        content_type=ContentType.objects.db_manager(alias).get_for_model(instancia),
        object_id=str(instancia.pk),
        registro_afectado=(registro_afectado or str(instancia))[:500],
        campo_modificado=campo_modificado,
        valor_anterior=str(valor_anterior), valor_nuevo=str(valor_nuevo),
        descripcion=descripcion, ip=obtener_ip_actual(),
    )
