from decimal import Decimal

from django.db import IntegrityError, transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from .models import (
    Activo,
    EtiquetaQR,
    Componente,
    EstadoComponente,
    Movimiento,
    PropuestaInventario,
)

PREFIJO_INVENTARIO = "INV"
MAX_UNIDADES = 1000
ESTADO_COMPONENTE_INICIAL = "Disponible"


def _siguiente_consecutivo(prefijo):
    """Devuelve el siguiente consecutivo para un prefijo INV-AAAA-."""
    ultimo = (
        Activo.objects.select_for_update()
        .filter(numero_inventario__startswith=prefijo)
        .order_by("-numero_inventario")
        .first()
    )
    if ultimo is None:
        return 1
    try:
        return int(ultimo.numero_inventario.rsplit("-", 1)[-1]) + 1
    except ValueError:
        return Activo.objects.filter(numero_inventario__startswith=prefijo).count() + 1


def datos_faltantes(propuesta):
    """
    Devuelve {campo: mensaje} con lo que aún falta para poder aceptar la
    propuesta. Un diccionario vacío significa que está completa.

    - por clasificar: falta clasificarla.
    - no inventariable: no necesita más datos.
    - activo: artículo, estado inicial, marca y modelo.
    - componente: marca y modelo.

    La marca y el modelo se consideran completos si están en la propuesta
    o, cuando hay artículo, en el artículo.
    """
    Tipo = PropuestaInventario.TipoRegistro
    tipo = propuesta.tipo_registro

    if tipo == Tipo.NO_INVENTARIABLE:
        return {}

    if tipo == Tipo.POR_CLASIFICAR:
        return {
            "tipo_registro": (
                "Clasifica la propuesta: activo, componente o no inventariable."
            )
        }

    faltantes = {}
    articulo = propuesta.articulo if propuesta.articulo_id else None

    if tipo == Tipo.ACTIVO:
        if articulo is None:
            faltantes["articulo"] = "Un activo requiere un artículo."
        if propuesta.estado_activo_id is None:
            faltantes["estado_activo"] = "Un activo requiere un estado inicial."

    marca = (propuesta.marca or "").strip() or (
        (articulo.marca or "").strip() if articulo else ""
    )
    modelo = (propuesta.modelo or "").strip() or (
        (articulo.modelo or "").strip() if articulo else ""
    )
    if not marca:
        faltantes["marca"] = "Indica la marca."
    if not modelo:
        faltantes["modelo"] = "Indica el modelo."

    return faltantes


def _unidades(propuesta):
    cantidad = propuesta.cantidad
    if cantidad != cantidad.to_integral_value():
        raise ValidationError({
            "cantidad": "La cantidad debe ser un número entero para registrar unidades."
        })
    unidades = int(cantidad)
    if unidades < 1 or unidades > MAX_UNIDADES:
        raise ValidationError({
            "cantidad": f"La cantidad debe estar entre 1 y {MAX_UNIDADES}."
        })
    return unidades


def registrar_propuesta(propuesta):
    """
    Convierte una propuesta aceptada en activos o componentes.

    Crea una unidad por cada pieza de la cantidad. Cada activo genera su
    movimiento de alta y la propuesta queda como registrada. Debe llamarse
    dentro de transaction.atomic con la propuesta bloqueada.
    """
    Tipo = PropuestaInventario.TipoRegistro

    if propuesta.estado_revision != PropuestaInventario.EstadoRevision.ACEPTADA:
        raise ValidationError({
            "estado_revision": "Solo se pueden registrar propuestas aceptadas."
        })

    if propuesta.tipo_registro not in (Tipo.ACTIVO, Tipo.COMPONENTE):
        raise ValidationError({
            "tipo_registro": "Este tipo de propuesta no genera registros de inventario."
        })

    unidades = _unidades(propuesta)
    factura = propuesta.factura
    activos = []
    componentes = []

    try:
        with transaction.atomic():
            if propuesta.tipo_registro == Tipo.ACTIVO:
                if propuesta.articulo_id is None or propuesta.estado_activo_id is None:
                    raise ValidationError({
                        "tipo_registro": "El activo requiere artículo y estado inicial."
                    })
                prefijo = f"{PREFIJO_INVENTARIO}-{timezone.now().year}-"
                consecutivo = _siguiente_consecutivo(prefijo)
                for i in range(unidades):
                    activo = Activo.objects.create(
                        numero_inventario=f"{prefijo}{consecutivo + i:04d}",
                        articulo=propuesta.articulo,
                        factura=factura,
                        propuesta_origen=propuesta,
                        estado=propuesta.estado_activo,
                        fecha_adquisicion=factura.fecha_emision,
                    )
                    if activo.articulo.tipo_bien.requiere_qr:
                        EtiquetaQR.objects.create(activo=activo)
                    Movimiento.objects.create(
                        activo=activo,
                        tipo=Movimiento.TipoMovimiento.ALTA,
                        observaciones=(
                            f"Alta desde factura {factura.folio}, "
                            f"concepto {propuesta.indice_concepto}."
                        ),
                    )
                    activos.append(activo)
            else:
                estado, _ = EstadoComponente.objects.get_or_create(
                    nombre=ESTADO_COMPONENTE_INICIAL
                )
                for _i in range(unidades):
                    componentes.append(
                        Componente.objects.create(
                            estado=estado,
                            nombre=propuesta.descripcion[:150],
                            marca=propuesta.marca,
                            modelo=propuesta.modelo,
                            factura=factura,
                            propuesta_origen=propuesta,
                        )
                    )

            propuesta.estado_revision = PropuestaInventario.EstadoRevision.REGISTRADA
            propuesta.save(update_fields=["estado_revision"])
    except IntegrityError:
        raise ValidationError({
            "detail": "No se pudo generar el número de inventario. Intenta de nuevo."
        })

    return activos, componentes