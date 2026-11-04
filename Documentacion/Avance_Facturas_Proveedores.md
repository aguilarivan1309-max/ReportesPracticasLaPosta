# Avance: facturas y proveedores

4 de noviembre de 2026

## Trabajo realizado

Se revisó la relación entre las facturas y los proveedores. En la copia del proyecto todavía no estaba creada, así que se agregó. Las facturas anteriores conservan sus datos y pueden seguir sin un proveedor seleccionado. No se asignaron proveedores automáticamente.

También se agregaron las opciones para consultar, registrar, editar y eliminar proveedores desde la API. Cuando un proveedor tiene facturas asociadas, el sistema conserva el registro y responde: "No se puede eliminar este proveedor porque tiene facturas asociadas."

## Comprobaciones

Las nueve pruebas automatizadas terminaron correctamente. Se comprobó que un proveedor con facturas no se pueda eliminar y que consultar uno que no existe devuelva una respuesta de no encontrado.

Además, se hicieron solicitudes HTTP al servicio local con registros temporales:

- Consultar proveedores: 200.
- Registrar un proveedor: 201.
- Consultarlo y editarlo: 200.
- Eliminarlo mientras tenía una factura: 409; el proveedor se conservó.
- Eliminarlo después de retirar la factura de prueba: 204.
- Consultarlo después de eliminarlo: 404.

Los registros temporales se retiraron al terminar. No se eliminaron proveedores ni facturas anteriores.

La página de Swagger respondió correctamente y su esquema se validó sin errores. Las operaciones se comprobaron mediante solicitudes HTTP directas; no se ejecutaron con los botones de Swagger.

## Base de datos y entrega

Se creó y aplicó la migración 0008_factura_proveedor. Fue necesaria porque faltaba la relación, aunque la guía suponía que ya existía. No quedaron cambios de modelos pendientes de migración.

Los cambios quedaron preparados localmente para revisión. No se realizó commit ni push como parte de esta actividad.
