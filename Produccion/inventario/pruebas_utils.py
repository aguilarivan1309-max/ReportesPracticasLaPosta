from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

from .roles import crear_roles 

def crear_usuario(rol=None, username=None, password="ClaveSegura123"):
    """Crear un usuario de prueba"""
    crear_roles()
    User = get_user_model()
    usuario = User.objects.create_user(
        username=username or f"usuario_{rol or 'sinrol'}",
        password=password,
    )
    if rol: 
        usuario.groups.add(Group.objects.get(name=rol))
    return usuario
def autenticar(client, rol):
    """Autenticar el cliente de pruebas con un usuario de rol indicado"""
    usuario = crear_usuario(rol)
    client.force_authenticate(user=usuario)
    return usuario
