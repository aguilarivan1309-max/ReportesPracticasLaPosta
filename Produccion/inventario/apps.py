from django.apps import AppConfig
from django.db.models.signals import post_migrate

class InventarioConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "inventario"

    def ready(self):
        from .roles import crear_roles

        post_migrate.connect(crear_roles, sender=self)
