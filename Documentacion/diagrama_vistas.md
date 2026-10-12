# Modelo de clases — vistas

Cada vista es un diagrama independiente. Las clases que aparecen solo con `id` son referencias a entidades que se detallan en otra vista.

| # | Vista | Alcance de esta etapa |
|---|-------|-----------------------|
| 1 | Núcleo de inventario | Sí |
| 2 | Adquisiciones y documentos de origen (incluye activos sin factura) | Sí |
| 3 | Usuarios, roles, permisos y auditoría | Sí |
| 4 | Trazabilidad e historial | Sí |
| 5 | Tickets, incidencias y reparaciones | Extensión futura |
| 6 | Garantías, mantenimiento y alertas | Extensión futura |
| 7 | Reservas, préstamos y bajas | Extensión futura |
| 8 | Integraciones e importaciones | Extensión futura |

---

## Vista 1. Núcleo de inventario

```mermaid
classDiagram
direction TB

class tipo_bien {
    int id PK
    string nombre
    string descripcion
    string modo_control
    boolean requiere_qr
    boolean permite_instalacion
    boolean activo
}

class articulo {
    int id PK
    int tipo_bien_id FK
    string nombre
    string descripcion
    string marca
    string modelo
    string unidad_medida
    boolean activo
}

class activo {
    int id PK
    string identificador
    int articulo_id FK
    string numero_serie
    int estado_actual_id FK
    int ubicacion_actual_id FK
    int responsable_actual_id FK
    int detalle_adquisicion_id FK
    date fecha_alta
    boolean activo
}

class existencia {
    int id PK
    int articulo_id FK
    int ubicacion_id FK
    decimal cantidad
    datetime fecha_actualizacion
}

class estado_activo {
    int id PK
    string nombre
    string descripcion
    boolean activo
}

class transicion_estado {
    int id PK
    int estado_origen_id FK
    int estado_destino_id FK
    boolean permitido
    boolean requiere_motivo
}

class ubicacion {
    int id PK
    string nombre
    string descripcion
    int ubicacion_padre_id FK
    boolean activo
}

class responsable {
    int id PK
    string nombre
    string apellido
    string correo
    string area
    string puesto
    boolean activo
}

class codigo_qr {
    int id PK
    int activo_id FK
    string codigo
    datetime fecha_generacion
    datetime fecha_desactivacion
    boolean activo
}

class archivo_activo {
    int id PK
    int activo_id FK
    string tipo
    string nombre_archivo
    string archivo
    string mime_type
    int tamano
    datetime fecha_carga
    string descripcion
}

tipo_bien "1" --> "0..*" articulo : clasifica
articulo "1" --> "0..*" activo : posee
articulo "1" --> "0..*" existencia : controla

ubicacion "1" --> "0..*" activo : alberga
ubicacion "1" --> "0..*" existencia : almacena
ubicacion "0..1" --> "0..*" ubicacion : contiene
estado_activo "1" --> "0..*" activo : estado_actual
responsable "0..1" --> "0..*" activo : resguarda

estado_activo "1" --> "0..*" transicion_estado : origen
estado_activo "1" --> "0..*" transicion_estado : destino

activo "1" --> "0..*" codigo_qr : identifica
activo "1" --> "0..*" archivo_activo : archivos
```

---

## Vista 2. Adquisiciones y documentos de origen

Esta vista incluye el ajuste para registrar activos **sin factura**. Los campos nuevos o modificados están marcados con `%% CAMBIO`.

```mermaid
classDiagram
direction TB

class proveedor {
    int id PK
    string nombre
    string rfc
    string correo
    string telefono
    string direccion
    boolean activo
}

class adquisicion {
    int id PK
    int proveedor_id FK "nullable"
    string tipo_origen "compra, donacion, transferencia, comodato, inventario_inicial, sin_documento"
    string estado_documentacion "completa, pendiente"
    string justificacion_sin_documento "obligatoria si pendiente"
    int usuario_registro_id FK
    string folio "nullable"
    date fecha
    decimal total "nullable"
    string moneda
    string observaciones
}

class detalle_adquisicion {
    int id PK
    int adquisicion_id FK
    int articulo_id FK
    decimal cantidad
    decimal costo_unitario "nullable"
    string observaciones
}

class documento_adquisicion {
    int id PK
    int adquisicion_id FK
    string tipo "factura, contrato, acta_donacion, oficio_transferencia, otro"
    string nombre_archivo
    string archivo
    string mime_type
    int tamano
    datetime fecha_carga
}

class articulo {
    int id PK
    string nombre
}

class activo {
    int id PK
    string identificador
    int detalle_adquisicion_id FK
}

class usuario_sistema {
    int id PK
    string username
}

proveedor "0..1" --> "0..*" adquisicion : suministra
usuario_sistema "1" --> "0..*" adquisicion : registra

adquisicion "1" --> "1..*" detalle_adquisicion : contiene
articulo "1" --> "0..*" detalle_adquisicion : adquirido
detalle_adquisicion "1" --> "0..*" activo : origina

adquisicion "1" --> "0..*" documento_adquisicion : documentos
```

### Flujo para dar de alta un activo sin factura

1. Se crea una `adquisicion` con `tipo_origen` (por ejemplo `sin_documento` o `inventario_inicial`), `estado_documentacion = pendiente`, `proveedor_id` y `folio` vacíos, y una `justificacion_sin_documento` obligatoria.
2. Se crea su `detalle_adquisicion` con `costo_unitario` vacío (el costo es desconocido).
3. Se crea el `activo` ligado a ese detalle, de modo que el activo siempre tiene documento de origen aunque sea provisional.
4. Cuando aparece la factura (o contrato, acta, oficio), se agrega un `documento_adquisicion`, se completan proveedor, folio y costos, y `estado_documentacion` pasa a `completa`. No se cambia el `activo` ni su historial.
5. Filtrar `adquisicion` por `estado_documentacion = pendiente` da la lista de activos por regularizar.

---

## Vista 3. Usuarios, roles, permisos y auditoría

```mermaid
classDiagram
direction TB

class responsable {
    int id PK
    string nombre
    string apellido
}

class usuario_sistema {
    int id PK
    int responsable_id FK
    string username
    string nombre
    string apellido
    string correo
    boolean activo
}

class rol {
    int id PK
    string nombre
    string descripcion
}

class permiso {
    int id PK
    string nombre
    string codigo
    string descripcion
}

class usuario_rol {
    int id PK
    int usuario_id FK
    int rol_id FK
}

class rol_permiso {
    int id PK
    int rol_id FK
    int permiso_id FK
}

class auditoria_operacion {
    int id PK
    int usuario_id FK
    string accion
    string entidad
    int entidad_id
    datetime fecha
    string ip
    string detalle
}

responsable "0..1" --> "0..1" usuario_sistema : cuenta

usuario_sistema "1" --> "0..*" usuario_rol : posee
rol "1" --> "0..*" usuario_rol : asigna

rol "1" --> "0..*" rol_permiso : posee
permiso "1" --> "0..*" rol_permiso : incluye

usuario_sistema "1" --> "0..*" auditoria_operacion : realiza
```

---

