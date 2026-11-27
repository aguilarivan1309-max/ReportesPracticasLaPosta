from django.contrib.auth.models import Group

ADMINISTRADOR = "Administrador"
OPERADOR = "Operador"
CONSULTA = "Consulta"

ROLES = [ADMINISTRADOR, OPERADOR, CONSULTA]


def crear_roles(**kwargs):
    """Crea los grupos de roles si no existen. Se ejecuta tras cada migrate."""
    for nombre in ROLES:
        Group.objects.get_or_create(name=nombre)