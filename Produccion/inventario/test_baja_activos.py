from datetime import date

from django.db.models.deletion import ProtectedError
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from .models import (
    Activo,
    Articulo,
    Componente,
    ComponenteInstalado,
    EstadoActivo,
    EstadoComponente,
    Movimiento,
    Responsable,
    TipoBien,
    Ubicacion,
)
from .pruebas_utils import autenticar
from .roles import ADMINISTRADOR, CONSULTA, OPERADOR


class BajaActivoAPITests(APITestCase):

    def setUp(self):
        autenticar(self.client, ADMINISTRADOR)

        self.tipo_bien = TipoBien.objects.create(nombre="Equipo de cómputo")
        self.articulo = Articulo.objects.create(
            tipo_bien=self.tipo_bien,
            nombre="Laptop Dell Latitude",
            marca="Dell",
            modelo="5440",
        )
        self.estado_operativo = EstadoActivo.objects.create(nombre="Asignado")
        self.ubicacion = Ubicacion.objects.create(nombre="Laboratorio de Redes")
        self.responsable = Responsable.objects.create(
            nombre="Ana",
            apellidos="López",
            numero_empleado="EMP-101",
        )

        self.activo = Activo.objects.create(
            numero_inventario="INV-2026-0001",
            articulo=self.articulo,
            estado=self.estado_operativo,
            ubicacion=self.ubicacion,
            responsable=self.responsable,
            numero_serie="SN-ABC-123",
        )

        self.movimiento_alta = Movimiento.objects.create(
            activo=self.activo,
            tipo=Movimiento.TipoMovimiento.ALTA,
            responsable_destino=self.responsable,
            ubicacion_destino=self.ubicacion,
            observaciones="Alta inicial de prueba.",
        )

        self.url = reverse("activo-baja", args=[self.activo.pk])

    def test_dar_baja_activo_exitoso_conserva_datos_e_historial(self):
        motivo = "Daño irreparable en tarjeta madre tras diagnóstico técnico."
        response = self.client.post(
            self.url,
            {"motivo": motivo},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)

        self.activo.refresh_from_db()
        # 1. El estado cambia a Baja
        self.assertEqual(self.activo.estado.nombre, "Baja")
        # 2. Se conservan responsable y ubicación
        self.assertEqual(self.activo.responsable_id, self.responsable.pk)
        self.assertEqual(self.activo.ubicacion_id, self.ubicacion.pk)

        # 3. Se conserva el historial previo y se crea el movimiento de baja
        movimientos = Movimiento.objects.filter(activo=self.activo)
        self.assertEqual(movimientos.count(), 2)
        self.assertTrue(
            movimientos.filter(pk=self.movimiento_alta.pk).exists()
        )

        movimiento_baja = movimientos.get(tipo=Movimiento.TipoMovimiento.BAJA)
        self.assertEqual(movimiento_baja.observaciones, motivo)
        self.assertEqual(
            movimiento_baja.responsable_origen_id, self.responsable.pk
        )
        self.assertEqual(
            movimiento_baja.ubicacion_origen_id, self.ubicacion.pk
        )
        self.assertIsNotNone(movimiento_baja.usuario)
        self.assertIsNotNone(movimiento_baja.fecha)

        self.assertEqual(response.data["estado"], "Baja")
        self.assertEqual(response.data["movimiento_id"], movimiento_baja.id)

    def test_motivo_baja_es_obligatorio(self):
        for payload in [{}, {"motivo": ""}, {"motivo": "     "}]:
            response = self.client.post(self.url, payload, format="json")
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn("motivo", response.data)

        self.activo.refresh_from_db()
        self.assertEqual(self.activo.estado_id, self.estado_operativo.pk)

    def test_rechazar_baja_si_activo_ya_esta_dado_de_baja(self):
        primera = self.client.post(
            self.url,
            {"motivo": "Primera baja válida por obsolescencia."},
            format="json",
        )
        self.assertEqual(primera.status_code, status.HTTP_200_OK)

        segunda = self.client.post(
            self.url,
            {"motivo": "Intento de baja duplicada."},
            format="json",
        )
        self.assertEqual(segunda.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("estado", segunda.data)
        self.assertEqual(
            Movimiento.objects.filter(
                activo=self.activo,
                tipo=Movimiento.TipoMovimiento.BAJA,
            ).count(),
            1,
        )

    def test_bloquear_baja_con_componentes_instalados_sin_retirar(self):
        estado_comp = EstadoComponente.objects.create(nombre="Instalado")
        componente = Componente.objects.create(
            nombre="Memoria RAM DDR4 16GB",
            numero_serie="RAM-9988",
            estado=estado_comp,
        )
        ComponenteInstalado.objects.create(
            activo=self.activo,
            componente=componente,
            fecha_instalacion=date(2026, 11, 1),
            fecha_retiro=None,
        )

        response = self.client.post(
            self.url,
            {"motivo": "Intento de baja con RAM aún instalada."},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("componentes_instalados", response.data)
        self.assertIn("Memoria RAM DDR4 16GB", str(response.data))

        self.activo.refresh_from_db()
        self.assertEqual(self.activo.estado_id, self.estado_operativo.pk)

    def test_permitir_baja_despues_de_retirar_componentes(self):
        estado_comp = EstadoComponente.objects.create(nombre="Instalado")
        componente = Componente.objects.create(
            nombre="SSD NVMe 512GB",
            estado=estado_comp,
        )
        instalacion = ComponenteInstalado.objects.create(
            activo=self.activo,
            componente=componente,
            fecha_instalacion=date(2026, 11, 1),
            fecha_retiro=None,
        )

        # Se registra el retiro previo del componente
        instalacion.fecha_retiro = date(2026, 11, 20)
        instalacion.save(update_fields=["fecha_retiro"])

        response = self.client.post(
            self.url,
            {"motivo": "Baja autorizada tras retirar almacenamiento."},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.activo.refresh_from_db()
        self.assertEqual(self.activo.estado.nombre, "Baja")

    def test_eliminacion_fisica_del_activo_esta_prohibida(self):
        with self.assertRaises(ProtectedError):
            self.activo.delete()

        self.assertTrue(Activo.objects.filter(pk=self.activo.pk).exists())

    def test_activo_inexistente_devuelve_404(self):
        url_inexistente = reverse(
            "activo-baja", args=[self.activo.pk + 999999]
        )
        response = self.client.post(
            url_inexistente,
            {"motivo": "Prueba sobre activo inexistente."},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_permisos_por_rol_para_ejecutar_baja(self):
        # 1. Usuario sin autenticar
        cliente_anonimo = APIClient()
        resp_anon = cliente_anonimo.post(
            self.url,
            {"motivo": "Intento sin sesión."},
            format="json",
        )
        self.assertIn(
            resp_anon.status_code,
            (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN),
        )

        # 2. Rol Consulta (solo lectura -> 403)
        cliente_consulta = APIClient()
        autenticar(cliente_consulta, CONSULTA)
        resp_consulta = cliente_consulta.post(
            self.url,
            {"motivo": "Intento desde rol consulta."},
            format="json",
        )
        self.assertEqual(resp_consulta.status_code, status.HTTP_403_FORBIDDEN)

        # 3. Rol Operador (permitido -> 200)
        cliente_operador = APIClient()
        autenticar(cliente_operador, OPERADOR)
        resp_operador = cliente_operador.post(
            self.url,
            {"motivo": "Baja ejecutada por operador autorizado."},
            format="json",
        )
        self.assertEqual(resp_operador.status_code, status.HTTP_200_OK)