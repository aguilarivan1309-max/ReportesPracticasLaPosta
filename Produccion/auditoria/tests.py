import json
from types import SimpleNamespace
from datetime import date
from decimal import Decimal

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser, Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from django.test import RequestFactory, TestCase
from django.utils.functional import SimpleLazyObject

from inventario.models import (
    Proveedor,
    Factura,
    PropuestaInventario,
    TipoBien,
    Articulo,
    EstadoActivo,
    EstadoComponente,
    Ubicacion,
    Responsable,
    Activo,
    Componente,
    ComponenteInstalado,
    Movimiento,
)
from .middleware import AuditoriaMiddleware, obtener_ip_actual, obtener_usuario_actual
from .models import RegistroAuditoria
from .services import registrar_auditoria

User = get_user_model()


class AuditoriaTests(TestCase):
    def setUp(self):
        self.usuario = User.objects.create_user(username="operador", password="clave-privada")
        RegistroAuditoria.objects.all().delete()

    def contexto(self, funcion, usuario=None):
        request = RequestFactory().post("/", REMOTE_ADDR="127.0.0.1",
                                        HTTP_X_FORWARDED_FOR="203.0.113.1")
        request.user = usuario or self.usuario
        return AuditoriaMiddleware(lambda request: funcion())(request)

    def test_creacion_con_usuario_ip_y_referencia(self):
        proveedor = self.contexto(
            lambda: Proveedor.objects.create(nombre="Ejemplo"),
            SimpleLazyObject(lambda: self.usuario),
        )
        registro = RegistroAuditoria.objects.get()
        self.assertEqual(registro.usuario, self.usuario)
        self.assertEqual(registro.usuario_nombre, "operador")
        self.assertEqual(registro.ip, "127.0.0.1")
        self.assertEqual(registro.objeto, proveedor)
        self.assertEqual(registro.accion, "Creación")

    def test_cambio_solo_de_campos_guardados(self):
        proveedor = Proveedor.objects.create(nombre="Antes")
        RegistroAuditoria.objects.all().delete()
        proveedor.nombre = "Después"
        proveedor.telefono = "sin guardar"
        proveedor.save(update_fields=["nombre"])
        registro = RegistroAuditoria.objects.get()
        self.assertEqual(registro.campo_modificado, "nombre")
        self.assertEqual(registro.valor_anterior, "Antes")
        self.assertEqual(registro.valor_nuevo, "Después")
        proveedor.refresh_from_db()
        proveedor.save()
        self.assertEqual(RegistroAuditoria.objects.count(), 1)

    def test_eliminacion_conserva_identidad(self):
        proveedor = Proveedor.objects.create(nombre="Proveedor eliminado")
        pk = proveedor.pk
        RegistroAuditoria.objects.all().delete()
        self.contexto(proveedor.delete)
        registro = RegistroAuditoria.objects.get()
        self.assertEqual(registro.accion, "Eliminación")
        self.assertEqual(registro.object_id, str(pk))
        self.assertEqual(registro.registro_afectado, "Proveedor eliminado")
        self.assertIsNone(registro.objeto)

    def test_usuario_eliminado_conserva_nombre(self):
        self.contexto(lambda: Proveedor.objects.create(nombre="Ejemplo"))
        registro = RegistroAuditoria.objects.get()
        self.usuario.delete()
        registro.refresh_from_db()
        self.assertIsNone(registro.usuario)
        self.assertEqual(registro.usuario_nombre, "operador")

    def test_contrasenas_y_ultimo_acceso_no_se_registran(self):
        self.usuario.set_password("otra-clave")
        self.usuario.save()
        self.assertFalse(RegistroAuditoria.objects.exists())
        registro = registrar_auditoria(
            self.usuario, "Modificación", campo_modificado="access_token",
            valor_anterior="secreto-a", valor_nuevo="secreto-b",
        )
        self.assertEqual(registro.valor_anterior, "[DATO OMITIDO]")
        self.assertEqual(registro.valor_nuevo, "[DATO OMITIDO]")

    def test_contexto_se_limpia_incluso_con_error(self):
        def fallo():
            self.assertEqual(obtener_usuario_actual(), self.usuario)
            raise ValueError("prueba")
        with self.assertRaises(ValueError):
            self.contexto(fallo)
        self.assertIsNone(obtener_usuario_actual())
        self.assertIsNone(obtener_ip_actual())
        proveedor = Proveedor.objects.create(nombre="Sistema")
        self.assertEqual(RegistroAuditoria.objects.get(object_id=str(proveedor.pk)).usuario_nombre, "Sistema")

    def test_usuario_autenticado_durante_la_peticion(self):
        request = RequestFactory().post("/")
        request.user = AnonymousUser()
        def respuesta(request):
            request.user = self.usuario
            return Proveedor.objects.create(nombre="Autenticado")
        AuditoriaMiddleware(respuesta)(request)
        self.assertEqual(RegistroAuditoria.objects.get().usuario, self.usuario)

    def test_rollback_tambien_revierte_auditoria(self):
        with self.assertRaises(ValueError):
            with transaction.atomic():
                Proveedor.objects.create(nombre="No persistir")
                raise ValueError("cancelar")
        self.assertFalse(RegistroAuditoria.objects.exists())
        self.assertFalse(Proveedor.objects.exists())

    def test_admin_solo_consulta(self):
        administrador = admin.site._registry[RegistroAuditoria]
        request = RequestFactory().get("/")
        request.user = SimpleNamespace(is_active=True, is_superuser=True, has_perm=lambda p: True)
        self.assertTrue(administrador.has_view_permission(request))
        self.assertFalse(administrador.has_add_permission(request))
        self.assertFalse(administrador.has_change_permission(request))
        self.assertFalse(administrador.has_delete_permission(request))

    def test_update_requiere_registro_explicito(self):
        proveedor = Proveedor.objects.create(nombre="Antes")
        RegistroAuditoria.objects.all().delete()
        Proveedor.objects.filter(pk=proveedor.pk).update(nombre="Después")
        self.assertFalse(RegistroAuditoria.objects.exists())
        proveedor.refresh_from_db()
        registrar_auditoria(proveedor, "Modificación", campo_modificado="nombre",
                            valor_anterior="Antes", valor_nuevo="Después")
        self.assertEqual(RegistroAuditoria.objects.count(), 1)

    def test_grupos_desde_usuario_y_grupo(self):
        grupo = Group.objects.create(name="Inventario")
        RegistroAuditoria.objects.all().delete()
        self.usuario.groups.add(grupo)
        self.assertEqual(json.loads(RegistroAuditoria.objects.get().valor_nuevo), ["Inventario"])
        RegistroAuditoria.objects.all().delete()
        grupo.user_set.clear()
        registro = RegistroAuditoria.objects.get()
        self.assertEqual(json.loads(registro.valor_anterior), ["operador"])
        self.assertEqual(json.loads(registro.valor_nuevo), [])
        RegistroAuditoria.objects.all().delete()
        grupo.user_set.add(self.usuario)
        self.assertEqual(json.loads(RegistroAuditoria.objects.get().valor_nuevo), ["operador"])
        RegistroAuditoria.objects.all().delete()
        self.usuario.groups.remove(grupo)
        self.assertEqual(json.loads(RegistroAuditoria.objects.get().valor_anterior), ["Inventario"])

    def test_permisos_directos_e_inversos(self):
        permiso = Permission.objects.filter(codename="add_proveedor").get()
        grupo = Group.objects.create(name="Inventario")
        for manager, target, antes, despues in (
            (self.usuario.user_permissions, permiso, [], ["add_proveedor"]),
            (permiso.group_set, grupo, [], ["Inventario"]),
        ):
            RegistroAuditoria.objects.all().delete()
            manager.add(target)
            registro = RegistroAuditoria.objects.get()
            self.assertEqual(json.loads(registro.valor_anterior), antes)
            self.assertEqual(json.loads(registro.valor_nuevo), despues)
        RegistroAuditoria.objects.all().delete()
        permiso.user_set.remove(self.usuario)
        self.assertEqual(json.loads(RegistroAuditoria.objects.get().valor_anterior), ["operador"])
        RegistroAuditoria.objects.all().delete()
        grupo.permissions.clear()
        self.assertEqual(json.loads(RegistroAuditoria.objects.get().valor_anterior), ["add_proveedor"])

class CoberturaModelosInventarioTests(TestCase):

    def verificar_creacion_auditada(self, objeto):
        content_type = ContentType.objects.get_for_model(objeto)

        registro = RegistroAuditoria.objects.get(
            content_type=content_type,
            object_id=str(objeto.pk),
            accion="Creación",
        )

        self.assertEqual(registro.objeto, objeto)

    def test_creacion_de_modelos_inventario(self):
        proveedor = Proveedor.objects.create(
            nombre="Proveedor de prueba",
            rfc="XAXX010101000",
        )

        factura = Factura.objects.create(
            folio="FAC-TEST-001",
            fecha_emision=date(2026, 11, 23),
            proveedor_nombre=proveedor.nombre,
            proveedor=proveedor,
            importe_total=Decimal("15000.00"),
        )

        tipo_bien = TipoBien.objects.create(
            nombre="Equipo de cómputo",
        )

        articulo = Articulo.objects.create(
            tipo_bien=tipo_bien,
            nombre="Computadora de escritorio",
        )

        estado_activo = EstadoActivo.objects.create(
            nombre="Almacenamiento",
        )

        estado_componente = EstadoComponente.objects.create(
            nombre="Disponible",
        )

        ubicacion = Ubicacion.objects.create(
            nombre="Almacén principal",
        )

        responsable = Responsable.objects.create(
            nombre="Juan",
            apellidos="Pérez",
            numero_empleado="EMP-001",
        )

        propuesta = PropuestaInventario.objects.create(
            factura=factura,
            indice_concepto=1,
            descripcion="Computadora de escritorio",
            cantidad=Decimal("1.000000"),
        )

        activo = Activo.objects.create(
            numero_inventario="INV-TEST-001",
            articulo=articulo,
            factura=factura,
            propuesta_origen=propuesta,
            estado=estado_activo,
            ubicacion=ubicacion,
            responsable=responsable,
        )

        componente = Componente.objects.create(
            estado=estado_componente,
            nombre="Memoria RAM",
            factura=factura,
        )

        instalacion = ComponenteInstalado.objects.create(
            activo=activo,
            componente=componente,
            fecha_instalacion=date(2026, 11, 23),
        )

        movimiento = Movimiento.objects.create(
            activo=activo,
            tipo=Movimiento.TipoMovimiento.ALTA,
            ubicacion_destino=ubicacion,
            responsable_destino=responsable,
        )

        objetos = [
            proveedor,
            factura,
            tipo_bien,
            articulo,
            estado_activo,
            estado_componente,
            ubicacion,
            responsable,
            propuesta,
            activo,
            componente,
            instalacion,
            movimiento,
        ]

        for objeto in objetos:
            with self.subTest(modelo=objeto.__class__.__name__):
                self.verificar_creacion_auditada(objeto)

    def test_modificacion_de_activo(self):
        tipo = TipoBien.objects.create(nombre="Equipo")
        articulo = Articulo.objects.create(
            tipo_bien=tipo,
            nombre="Laptop",
        )
        estado = EstadoActivo.objects.create(
            nombre="En almacenamiento",
        )

        activo = Activo.objects.create(
            numero_inventario="INV-MOD-001",
            articulo=articulo,
            estado=estado,
            numero_serie="SERIE-ANTERIOR",
        )

        RegistroAuditoria.objects.all().delete()

        activo.numero_serie = "SERIE-NUEVA"
        activo.save()

        registro = RegistroAuditoria.objects.get(
            object_id=str(activo.pk),
            campo_modificado="numero_serie",
        )

        self.assertEqual(registro.accion, "Modificación")
        self.assertEqual(registro.valor_anterior, "SERIE-ANTERIOR")
        self.assertEqual(registro.valor_nuevo, "SERIE-NUEVA")

    def test_modificacion_de_componente_instalado(self):
        tipo = TipoBien.objects.create(nombre="Equipo")
        articulo = Articulo.objects.create(
            tipo_bien=tipo,
            nombre="Computadora",
        )
        estado_activo = EstadoActivo.objects.create(
            nombre="En uso",
        )
        estado_componente = EstadoComponente.objects.create(
            nombre="Instalado",
        )

        activo = Activo.objects.create(
            numero_inventario="INV-MOD-002",
            articulo=articulo,
            estado=estado_activo,
        )

        componente = Componente.objects.create(
            estado=estado_componente,
            nombre="Memoria RAM",
        )

        instalacion = ComponenteInstalado.objects.create(
            activo=activo,
            componente=componente,
            fecha_instalacion=date(2026, 11, 20),
        )

        RegistroAuditoria.objects.all().delete()

        instalacion.fecha_retiro = date(2026, 11, 23)
        instalacion.save()

        registro = RegistroAuditoria.objects.get(
            object_id=str(instalacion.pk),
            campo_modificado="fecha_retiro",
        )

        self.assertEqual(registro.accion, "Modificación")
        self.assertEqual(
            registro.valor_anterior,
            "Vacío",
        )
        self.assertEqual(
            registro.valor_nuevo,
            "2026-11-23",
        )

    def test_modificacion_de_propuesta_inventario(self):
        factura = Factura.objects.create(
            folio="FAC-MOD-001",
            fecha_emision=date(2026, 11, 23),
            proveedor_nombre="Proveedor de prueba",
        )

        propuesta = PropuestaInventario.objects.create(
            factura=factura,
            indice_concepto=1,
            descripcion="Memoria RAM",
            cantidad=Decimal("2.000000"),
        )

        RegistroAuditoria.objects.all().delete()

        propuesta.estado_revision = (
            PropuestaInventario.EstadoRevision.ACEPTADA
        )
        propuesta.save()

        registro = RegistroAuditoria.objects.get(
            object_id=str(propuesta.pk),
            campo_modificado="estado_revision",
        )

        self.assertEqual(registro.accion, "Modificación")
        self.assertEqual(registro.valor_anterior, "Pendiente")
        self.assertEqual(registro.valor_nuevo, "Aceptada")

    def test_eliminacion_de_ubicacion(self):
        ubicacion = Ubicacion.objects.create(
            nombre="Ubicación para eliminación",
        )

        content_type = ContentType.objects.get_for_model(ubicacion)
        object_id = str(ubicacion.pk)

        RegistroAuditoria.objects.all().delete()

        ubicacion.delete()

        registro = RegistroAuditoria.objects.get(
            content_type=content_type,
            object_id=object_id,
            accion="Eliminación",
        )

        self.assertIsNone(registro.objeto)
