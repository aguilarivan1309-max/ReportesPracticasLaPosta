from rest_framework.permissions import SAFE_METHODS, BasePermission

from .roles import ADMINISTRADOR, CONSULTA, OPERADOR


class PermisoPorRol(BasePermission):
    """
    Administrador (o superusuario): todas las operaciones.
    Operador: consultar, crear y editar; no puede eliminar.
    Consulta: solo lectura.
    Un usuario autenticado sin rol no puede usar la API.
    """

    message = "Tu rol no tiene permiso para realizar esta operación."

    def has_permission(self, request, view):
        usuario = request.user
        if not usuario or not usuario.is_authenticated:
            return False
        if usuario.is_superuser:
            return True

        roles = set(usuario.groups.values_list("name", flat=True))
        if ADMINISTRADOR in roles:
            return True
        if request.method in SAFE_METHODS:
            return bool(roles & {OPERADOR, CONSULTA})
        if request.method == "DELETE":
            return False
        return OPERADOR in roles