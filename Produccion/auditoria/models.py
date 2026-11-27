from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models


class RegistroAuditoria(models.Model):
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="registros_auditoria",
        verbose_name="Usuario",
    )
    usuario_nombre = models.CharField(
        max_length=150, default="Sistema", verbose_name="Usuario (respaldo)",
        help_text="Conserva el nombre aunque se elimine la cuenta.",
    )
    accion = models.CharField(max_length=120, db_index=True, verbose_name="Acción")
    fecha = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name="Fecha y hora")
    content_type = models.ForeignKey(
        ContentType, on_delete=models.SET_NULL, null=True, blank=True,
        verbose_name="Tipo de registro",
    )
    object_id = models.CharField(max_length=255, blank=True, verbose_name="Identificador")
    objeto = GenericForeignKey("content_type", "object_id")
    registro_afectado = models.CharField(max_length=500, verbose_name="Registro afectado")
    campo_modificado = models.CharField(max_length=150, blank=True, verbose_name="Campo")
    valor_anterior = models.TextField(blank=True, verbose_name="Valor anterior")
    valor_nuevo = models.TextField(blank=True, verbose_name="Valor nuevo")
    descripcion = models.TextField(blank=True, verbose_name="Descripción")
    ip = models.GenericIPAddressField(null=True, blank=True, verbose_name="Dirección IP")

    class Meta:
        ordering = ["-fecha", "-pk"]
        verbose_name = "Registro de auditoría"
        verbose_name_plural = "Registros de auditoría"

    def __str__(self):
        return f"{self.accion}: {self.registro_afectado}"
