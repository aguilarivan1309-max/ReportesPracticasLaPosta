import json

from django.apps import apps
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db.models.signals import m2m_changed, post_delete, post_save, pre_delete, pre_save

from .services import es_sensible, formatear_valor, registrar_auditoria

User = get_user_model()
MODELOS_AUDITADOS = {
    "inventario.EtiquetaQR",
    User._meta.label, Group._meta.label,
    "inventario.Proveedor", "inventario.Factura", "inventario.PropuestaInventario",
    "inventario.Ubicacion", "inventario.TipoBien",
}
CAMPOS_IGNORADOS = {"id", "password", "last_login"}


def campos_modelo(instance):
    return [
        field for field in instance._meta.concrete_fields
        if not field.primary_key
        and field.name not in CAMPOS_IGNORADOS
        and not es_sensible(field.name)
    ]


def antes_guardar(sender, instance, using, raw=False, **kwargs):
    if raw:
        return
    anterior = None
    if instance.pk is not None:
        anterior = sender._default_manager.using(using).filter(pk=instance.pk).first()
    instance._auditoria_anterior = {
        field.name: (getattr(anterior, field.attname), formatear_valor(anterior, field))
        for field in campos_modelo(instance)
    } if anterior is not None else {}


def despues_guardar(sender, instance, created, using, raw=False, update_fields=None, **kwargs):
    if raw:
        return
    anterior = instance.__dict__.pop("_auditoria_anterior", {})
    if created:
        registrar_auditoria(instance, "Creación", using=using)
        return
    # Leer lo persistido evita registrar valores que save(update_fields=...) no guardó.
    actual = sender._default_manager.using(using).get(pk=instance.pk)
    for field in campos_modelo(actual):
        if update_fields is not None and field.name not in update_fields and field.attname not in update_fields:
            continue
        if field.name in anterior and anterior[field.name][0] != getattr(actual, field.attname):
            registrar_auditoria(
                actual, "Modificación", campo_modificado=field.name,
                valor_anterior=anterior[field.name][1],
                valor_nuevo=formatear_valor(actual, field), using=using,
            )


def antes_eliminar(sender, instance, **kwargs):
    instance._auditoria_nombre = str(instance)


def despues_eliminar(sender, instance, using, **kwargs):
    registrar_auditoria(
        instance, "Eliminación", using=using,
        registro_afectado=instance.__dict__.pop("_auditoria_nombre", str(instance.pk)),
    )


def obtener_valores_relacion(instance, relacion, campo_valor, using):
    return sorted(str(valor) for valor in
                  getattr(instance, relacion).using(using).values_list(campo_valor, flat=True))


def procesar_cambio_m2m(
    *, instance, relacion, campo_valor, action, campo, descripcion, sender, using,
):
    clave = f"_auditoria_{sender._meta.label_lower}_{relacion}"
    if action in ("pre_add", "pre_remove", "pre_clear"):
        instance.__dict__[clave] = obtener_valores_relacion(instance, relacion, campo_valor, using)
        return
    if action not in ("post_add", "post_remove", "post_clear"):
        return
    anteriores = instance.__dict__.pop(clave, [])
    nuevos = obtener_valores_relacion(instance, relacion, campo_valor, using)
    if anteriores != nuevos:
        registrar_auditoria(
            instance, "Cambio de permisos", campo_modificado=campo,
            valor_anterior=json.dumps(anteriores, ensure_ascii=False),
            valor_nuevo=json.dumps(nuevos, ensure_ascii=False),
            descripcion=descripcion, using=using,
        )


def relacion_modificada(sender, instance, action, reverse, using, **kwargs):
    for model, nombre_campo, campo_destino in (
        (User, "groups", "name"),
        (User, "user_permissions", "codename"),
        (Group, "permissions", "codename"),
    ):
        field = model._meta.get_field(nombre_campo)
        if sender is not field.remote_field.through:
            continue
        relacion = field.remote_field.get_accessor_name() if reverse else nombre_campo
        campo_valor = (User.USERNAME_FIELD if model is User else "name") if reverse else campo_destino
        procesar_cambio_m2m(
            instance=instance, relacion=relacion, campo_valor=campo_valor,
            action=action, campo=relacion, descripcion="Cambio de grupos o permisos",
            sender=sender, using=using,
        )


for etiqueta in MODELOS_AUDITADOS:
    modelo = apps.get_model(etiqueta)
    for signal, receiver in (
        (pre_save, antes_guardar), (post_save, despues_guardar),
        (pre_delete, antes_eliminar), (post_delete, despues_eliminar),
    ):
        signal.connect(receiver, sender=modelo, dispatch_uid=f"auditoria.{etiqueta}.{receiver.__name__}")

for modelo, nombre_campo in ((User, "groups"), (User, "user_permissions"), (Group, "permissions")):
    through = modelo._meta.get_field(nombre_campo).remote_field.through
    m2m_changed.connect(relacion_modificada, sender=through, dispatch_uid=f"auditoria.{through._meta.label}")
