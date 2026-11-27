from django.contrib.auth.models import Group
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Proveedor
from .pruebas_utils import crear_usuario
from .roles import ADMINISTRADOR, CONSULTA, OPERADOR, ROLES

URL_PROVEEDORES = "/api/proveedores/"


class AutenticacionJWTTests(APITestCase):

    def setUp(self):
        self.usuario = crear_usuario(CONSULTA, username="ana", password="ClaveSegura123!")

    def obtener_token(self, password="ClaveSegura123!"):
        return self.client.post(
            "/api/auth/token/",
            {"username": "ana", "password": password},
            format="json",
        )

    def test_roles_se_crean_al_migrar(self):
        self.assertEqual(Group.objects.filter(name__in=ROLES).count(), 3)

    def test_sin_credenciales_no_hay_acceso(self):
        respuesta = self.client.get(URL_PROVEEDORES)
        self.assertEqual(respuesta.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_devuelve_tokens(self):
        respuesta = self.obtener_token()
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.assertIn("access", respuesta.data)
        self.assertIn("refresh", respuesta.data)

    def test_login_con_clave_incorrecta(self):
        respuesta = self.obtener_token("incorrecta")
        self.assertEqual(respuesta.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_token_permite_consultar(self):
        access = self.obtener_token().data["access"]
        respuesta = self.client.get(
            URL_PROVEEDORES, HTTP_AUTHORIZATION=f"Bearer {access}"
        )
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)

    def test_token_invalido_es_rechazado(self):
        respuesta = self.client.get(
            URL_PROVEEDORES, HTTP_AUTHORIZATION="Bearer token-falso"
        )
        self.assertEqual(respuesta.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_refrescar_token(self):
        refresh = self.obtener_token().data["refresh"]
        respuesta = self.client.post(
            "/api/auth/token/refresh/", {"refresh": refresh}, format="json"
        )
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.assertIn("access", respuesta.data)

    def test_yo_devuelve_usuario_y_roles(self):
        access = self.obtener_token().data["access"]
        respuesta = self.client.get(
            "/api/auth/yo/", HTTP_AUTHORIZATION=f"Bearer {access}"
        )
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.assertEqual(respuesta.data["username"], "ana")
        self.assertEqual(respuesta.data["roles"], [CONSULTA])

    def test_documentacion_es_accesible_sin_sesion(self):
        self.assertEqual(self.client.get("/api/schema/").status_code, 200)
        self.assertEqual(self.client.get("/api/docs/").status_code, 200)


class PermisosPorRolTests(APITestCase):

    def setUp(self):
        self.proveedor = Proveedor.objects.create(nombre="Proveedor de prueba")
        self.detalle = f"{URL_PROVEEDORES}{self.proveedor.pk}/"

    def entrar_como(self, rol):
        self.client.force_authenticate(user=crear_usuario(rol))

    def test_usuario_sin_rol_no_puede_usar_la_api(self):
        self.entrar_como(None)
        self.assertEqual(self.client.get(URL_PROVEEDORES).status_code, 403)

    def test_consulta_solo_lee(self):
        self.entrar_como(CONSULTA)
        self.assertEqual(self.client.get(URL_PROVEEDORES).status_code, 200)
        r = self.client.post(URL_PROVEEDORES, {"nombre": "Nuevo"}, format="json")
        self.assertEqual(r.status_code, 403)
        r = self.client.patch(self.detalle, {"telefono": "1"}, format="json")
        self.assertEqual(r.status_code, 403)
        self.assertEqual(self.client.delete(self.detalle).status_code, 403)

    def test_operador_crea_y_edita_pero_no_elimina(self):
        self.entrar_como(OPERADOR)
        r = self.client.post(URL_PROVEEDORES, {"nombre": "Nuevo"}, format="json")
        self.assertEqual(r.status_code, 201)
        r = self.client.patch(self.detalle, {"telefono": "1"}, format="json")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(self.client.delete(self.detalle).status_code, 403)
        self.assertTrue(Proveedor.objects.filter(pk=self.proveedor.pk).exists())

    def test_administrador_puede_todo(self):
        self.entrar_como(ADMINISTRADOR)
        r = self.client.post(URL_PROVEEDORES, {"nombre": "Nuevo"}, format="json")
        self.assertEqual(r.status_code, 201)
        self.assertEqual(self.client.delete(self.detalle).status_code, 204)

    def test_superusuario_puede_todo(self):
        from django.contrib.auth import get_user_model
        admin = get_user_model().objects.create_superuser("root", password="ClaveSegura123!")
        self.client.force_authenticate(user=admin)
        self.assertEqual(self.client.delete(self.detalle).status_code, 204)

    def test_permisos_aplican_a_propuestas(self):
        self.entrar_como(CONSULTA)
        self.assertEqual(self.client.get("/api/propuestas/").status_code, 200)
        self.assertEqual(self.client.post("/api/propuestas/1/aceptar/").status_code, 403)