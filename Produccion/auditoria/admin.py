from django.contrib import admin

from .models import RegistroAuditoria


@admin.register(RegistroAuditoria)
class RegistroAuditoriaAdmin(admin.ModelAdmin):
    list_display = ("fecha", "usuario_nombre", "accion", "registro_afectado", "campo_modificado")
    list_filter = ("accion", "fecha", "usuario")
    search_fields = (
        "usuario_nombre", "registro_afectado", "campo_modificado",
        "valor_anterior", "valor_nuevo",
    )
    readonly_fields = [field.name for field in RegistroAuditoria._meta.fields]
    list_select_related = ("usuario",)
    actions = None

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
