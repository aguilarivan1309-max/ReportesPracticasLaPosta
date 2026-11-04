import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("inventario", "0008_factura_proveedor"),
        ("inventario", "0010_factura_proveedor_movimiento_componenteinstalado"),
    ]
    operations = [
        migrations.AlterField(
            model_name="factura", name="proveedor",
            field=models.ForeignKey(
                "inventario.proveedor", on_delete=django.db.models.deletion.PROTECT,
                related_name="facturas", null=True, blank=True,
                verbose_name="Proveedor relacionado",
            ),
        ),
    ]
