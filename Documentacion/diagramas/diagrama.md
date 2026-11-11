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


%% =====================================================
%% USUARIOS, ROLES Y PERMISOS
%% =====================================================

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


%% =====================================================
%% PROVEEDORES Y ADQUISICIONES
%% =====================================================

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
    int proveedor_id FK
    string folio
    date fecha
    decimal total
    string moneda
    string observaciones
}

class detalle_adquisicion {
    int id PK
    int adquisicion_id FK
    int articulo_id FK
    decimal cantidad
    decimal costo_unitario
    string observaciones
}

class documento_adquisicion {
    int id PK
    int adquisicion_id FK
    string tipo
    string nombre_archivo
    string archivo
    string mime_type
    int tamano
    datetime fecha_carga
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


%% =====================================================
%% CODIGO QR
%% =====================================================

class codigo_qr {
    int id PK
    int activo_id FK
    string codigo
    datetime fecha_generacion
    datetime fecha_desactivacion
    boolean activo
}


%% =====================================================
%% TRAZABILIDAD
%% =====================================================

class movimiento_ubicacion {
    int id PK
    int activo_id FK
    int ubicacion_origen_id FK
    int ubicacion_destino_id FK
    int usuario_id FK
    datetime fecha
    string motivo
    string observaciones
}

class asignacion_responsable {
    int id PK
    int activo_id FK
    int responsable_anterior_id FK
    int responsable_nuevo_id FK
    int usuario_id FK
    datetime fecha
    string motivo
    string observaciones
}

class historial_estado {
    int id PK
    int activo_id FK
    int estado_anterior_id FK
    int estado_nuevo_id FK
    int usuario_id FK
    datetime fecha
    string motivo
    string observaciones
}


%% =====================================================
%% COMPONENTES
%% =====================================================

class instalacion_componente {
    int id PK
    int componente_activo_id FK
    int activo_hospedador_id FK
    int usuario_id FK
    datetime fecha_instalacion
    datetime fecha_retiro
    string motivo_retiro
    string observaciones
}


%% =====================================================
%% EXISTENCIAS, CONSUMIBLES Y REFACCIONES
%% =====================================================

class movimiento_existencia {
    int id PK
    int articulo_id FK
    int ubicacion_origen_id FK
    int ubicacion_destino_id FK
    int detalle_adquisicion_id FK
    int usuario_id FK
    string tipo
    decimal cantidad
    datetime fecha
    string motivo
    string observaciones
}


%% =====================================================
%% TICKETS E INCIDENCIAS
%% =====================================================

class ticket {
    int id PK
    string codigo
    int activo_id FK
    int responsable_id FK
    int usuario_creador_id FK
    string tipo
    string prioridad
    string estado
    string asunto
    string descripcion
    datetime fecha_apertura
    datetime fecha_cierre
}

class incidencia {
    int id PK
    int ticket_id FK
    string categoria
    string impacto
    string causa
    string solucion
}

class historial_ticket {
    int id PK
    int ticket_id FK
    int usuario_id FK
    string estado_anterior
    string estado_nuevo
    datetime fecha
    string comentario
}

class archivo_ticket {
    int id PK
    int ticket_id FK
    string nombre_archivo
    string archivo
    string tipo
    datetime fecha_carga
}


%% =====================================================
%% REPARACIONES
%% =====================================================

class reparacion {
    int id PK
    int activo_id FK
    int incidencia_id FK
    int proveedor_id FK
    int usuario_tecnico_id FK
    datetime fecha_inicio
    datetime fecha_fin
    string diagnostico
    string trabajo_realizado
    string resultado
    string estado
    decimal costo
    string observaciones
}

class documento_reparacion {
    int id PK
    int reparacion_id FK
    string tipo
    string archivo
    datetime fecha_carga
}


%% =====================================================
%% GARANTIAS
%% =====================================================

class garantia {
    int id PK
    int activo_id FK
    int proveedor_id FK
    date fecha_inicio
    date fecha_fin
    string tipo
    string condiciones
    string estado
}

class reclamacion_garantia {
    int id PK
    int garantia_id FK
    int incidencia_id FK
    date fecha_reclamacion
    string folio
    string estado
    string resultado
    decimal monto_cubierto
    string observaciones
}

class documento_garantia {
    int id PK
    int garantia_id FK
    string tipo
    string archivo
    datetime fecha_carga
}


%% =====================================================
%% MANTENIMIENTO
%% =====================================================

class plan_mantenimiento {
    int id PK
    string nombre
    string descripcion
    string tipo
    int frecuencia_dias
    int tipo_bien_id FK
    int articulo_id FK
    boolean activo
}

class mantenimiento_programado {
    int id PK
    int plan_id FK
    int activo_id FK
    datetime fecha_programada
    string estado
    int dias_alerta
}

class mantenimiento_ejecucion {
    int id PK
    int mantenimiento_programado_id FK
    int usuario_id FK
    int proveedor_id FK
    datetime fecha_inicio
    datetime fecha_fin
    string trabajo_realizado
    string resultado
    decimal costo
    string observaciones
}

class documento_mantenimiento {
    int id PK
    int mantenimiento_ejecucion_id FK
    string tipo
    string archivo
    datetime fecha_carga
}


%% =====================================================
%% ALERTAS
%% =====================================================

class alerta {
    int id PK
    int activo_id FK
    int mantenimiento_programado_id FK
    int garantia_id FK
    int usuario_destino_id FK
    string tipo
    string mensaje
    datetime fecha_programada
    datetime fecha_envio
    string estado
}


%% =====================================================
%% RESERVAS Y PRESTAMOS
%% =====================================================

class reserva {
    int id PK
    int activo_id FK
    int responsable_id FK
    int usuario_registro_id FK
    datetime fecha_solicitud
    datetime fecha_inicio
    datetime fecha_fin
    string estado
    string observaciones
}

class prestamo {
    int id PK
    int activo_id FK
    int responsable_id FK
    int reserva_id FK
    int usuario_entrega_id FK
    datetime fecha_entrega
    datetime fecha_devolucion_prevista
    datetime fecha_devolucion_real
    string estado
    string observaciones
}

class firma_prestamo {
    int id PK
    int prestamo_id FK
    string tipo
    string nombre_firmante
    string archivo_firma
    datetime fecha
}


%% =====================================================
%% BAJAS Y DISPOSICION FINAL
%% =====================================================

class baja_activo {
    int id PK
    int activo_id FK
    int usuario_id FK
    date fecha_baja
    string motivo
    string estado
    string observaciones
}

class disposicion_final {
    int id PK
    int baja_id FK
    int proveedor_id FK
    string tipo
    date fecha
    string destino
    string observaciones
}

class documento_baja {
    int id PK
    int baja_id FK
    string tipo
    string archivo
    datetime fecha_carga
}


%% =====================================================
%% AUDITORIA
%% =====================================================

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


%% =====================================================
%% INTEGRACIONES E IMPORTACIONES
%% =====================================================

class sistema_externo {
    int id PK
    string nombre
    string tipo
    string descripcion
    boolean activo
}

class sincronizacion_externa {
    int id PK
    int sistema_externo_id FK
    int usuario_id FK
    string direccion
    datetime fecha_inicio
    datetime fecha_fin
    string estado
    int registros_procesados
    int registros_error
}

class sincronizacion_detalle {
    int id PK
    int sincronizacion_id FK
    string entidad
    string identificador_externo
    string resultado
    string mensaje
}

class referencia_externa {
    int id PK
    int sistema_externo_id FK
    string entidad
    int entidad_id
    string identificador_externo
}


%% =====================================================
%% RELACIONES DE INVENTARIO
%% =====================================================

tipo_bien "1" --> "0..*" articulo : clasifica
articulo "1" --> "0..*" activo : posee
articulo "1" --> "0..*" existencia : controla

ubicacion "1" --> "0..*" activo : alberga
estado_activo "1" --> "0..*" activo : estado_actual
responsable "0..1" --> "0..*" activo : resguarda

ubicacion "0..1" --> "0..*" ubicacion : contiene

estado_activo "1" --> "0..*" transicion_estado : origen
estado_activo "1" --> "0..*" transicion_estado : destino


%% =====================================================
%% RELACIONES DE USUARIOS Y PERMISOS
%% =====================================================

responsable "0..1" --> "0..1" usuario_sistema : cuenta

usuario_sistema "1" --> "0..*" usuario_rol : posee
rol "1" --> "0..*" usuario_rol : asigna

rol "1" --> "0..*" rol_permiso : posee
permiso "1" --> "0..*" rol_permiso : incluye


%% =====================================================
%% RELACIONES DE ADQUISICIONES
%% =====================================================

proveedor "1" --> "0..*" adquisicion : suministra

adquisicion "1" --> "1..*" detalle_adquisicion : contiene
articulo "1" --> "0..*" detalle_adquisicion : adquirido

detalle_adquisicion "1" --> "0..*" activo : origina

adquisicion "1" --> "0..*" documento_adquisicion : documentos
activo "1" --> "0..*" archivo_activo : archivos


%% =====================================================
%% RELACIONES DE QR
%% =====================================================

activo "1" --> "0..*" codigo_qr : identifica


%% =====================================================
%% RELACIONES DE MOVIMIENTOS DE UBICACION
%% =====================================================

activo "1" --> "0..*" movimiento_ubicacion : movimientos

ubicacion "1" --> "0..*" movimiento_ubicacion : origen
ubicacion "1" --> "0..*" movimiento_ubicacion : destino

usuario_sistema "1" --> "0..*" movimiento_ubicacion : registra


%% =====================================================
%% RELACIONES DE RESPONSABLES
%% =====================================================

activo "1" --> "0..*" asignacion_responsable : asignaciones

responsable "0..1" --> "0..*" asignacion_responsable : anterior
responsable "1" --> "0..*" asignacion_responsable : nuevo

usuario_sistema "1" --> "0..*" asignacion_responsable : registra


%% =====================================================
%% RELACIONES DEL HISTORIAL DE ESTADOS
%% =====================================================

activo "1" --> "0..*" historial_estado : historial

estado_activo "0..1" --> "0..*" historial_estado : anterior
estado_activo "1" --> "0..*" historial_estado : nuevo

usuario_sistema "1" --> "0..*" historial_estado : registra


%% =====================================================
%% RELACIONES DE COMPONENTES
%% =====================================================

activo "1" --> "0..*" instalacion_componente : componente
activo "1" --> "0..*" instalacion_componente : hospedador

usuario_sistema "1" --> "0..*" instalacion_componente : registra


%% =====================================================
%% RELACIONES DE EXISTENCIAS
%% =====================================================

articulo "1" --> "0..*" movimiento_existencia : movimientos

ubicacion "0..1" --> "0..*" movimiento_existencia : origen
ubicacion "0..1" --> "0..*" movimiento_existencia : destino

detalle_adquisicion "0..1" --> "0..*" movimiento_existencia : compra

usuario_sistema "1" --> "0..*" movimiento_existencia : registra


%% =====================================================
%% RELACIONES DE TICKETS E INCIDENCIAS
%% =====================================================

activo "0..1" --> "0..*" ticket : relacionado
responsable "0..1" --> "0..*" ticket : reporta
usuario_sistema "1" --> "0..*" ticket : crea

ticket "1" --> "0..1" incidencia : describe

ticket "1" --> "0..*" historial_ticket : historial
usuario_sistema "1" --> "0..*" historial_ticket : registra

ticket "1" --> "0..*" archivo_ticket : evidencias


%% =====================================================
%% RELACIONES DE REPARACIONES
%% =====================================================

activo "1" --> "0..*" reparacion : recibe

incidencia "0..1" --> "0..*" reparacion : origina
proveedor "0..1" --> "0..*" reparacion : realiza
usuario_sistema "0..1" --> "0..*" reparacion : tecnico

reparacion "1" --> "0..*" documento_reparacion : evidencias


%% =====================================================
%% RELACIONES DE GARANTIAS
%% =====================================================

activo "1" --> "0..*" garantia : posee
proveedor "0..1" --> "0..*" garantia : respalda

garantia "1" --> "0..*" reclamacion_garantia : reclamaciones

incidencia "0..1" --> "0..*" reclamacion_garantia : motiva

garantia "1" --> "0..*" documento_garantia : documentos


%% =====================================================
%% RELACIONES DE MANTENIMIENTO
%% =====================================================

tipo_bien "0..1" --> "0..*" plan_mantenimiento : aplica
articulo "0..1" --> "0..*" plan_mantenimiento : aplica

plan_mantenimiento "1" --> "0..*" mantenimiento_programado : genera
activo "1" --> "0..*" mantenimiento_programado : recibe

mantenimiento_programado "1" --> "0..1" mantenimiento_ejecucion : ejecucion

usuario_sistema "0..1" --> "0..*" mantenimiento_ejecucion : tecnico
proveedor "0..1" --> "0..*" mantenimiento_ejecucion : proveedor

mantenimiento_ejecucion "1" --> "0..*" documento_mantenimiento : evidencias


%% =====================================================
%% RELACIONES DE ALERTAS
%% =====================================================

activo "0..1" --> "0..*" alerta : genera

mantenimiento_programado "0..1" --> "0..*" alerta : mantenimiento
garantia "0..1" --> "0..*" alerta : garantia

usuario_sistema "1" --> "0..*" alerta : recibe


%% =====================================================
%% RELACIONES DE RESERVAS Y PRESTAMOS
%% =====================================================

activo "1" --> "0..*" reserva : reservado
responsable "1" --> "0..*" reserva : solicita
usuario_sistema "1" --> "0..*" reserva : registra

activo "1" --> "0..*" prestamo : prestado
responsable "1" --> "0..*" prestamo : recibe

reserva "0..1" --> "0..1" prestamo : origina

usuario_sistema "1" --> "0..*" prestamo : entrega

prestamo "1" --> "0..*" firma_prestamo : firmas


%% =====================================================
%% RELACIONES DE BAJAS
%% =====================================================

activo "1" --> "0..1" baja_activo : baja

usuario_sistema "1" --> "0..*" baja_activo : registra

baja_activo "1" --> "0..1" disposicion_final : disposicion

proveedor "0..1" --> "0..*" disposicion_final : participa

baja_activo "1" --> "0..*" documento_baja : documentos


%% =====================================================
%% RELACIONES DE AUDITORIA
%% =====================================================

usuario_sistema "1" --> "0..*" auditoria_operacion : realiza


%% =====================================================
%% RELACIONES DE INTEGRACIONES
%% =====================================================

sistema_externo "1" --> "0..*" sincronizacion_externa : sincroniza

usuario_sistema "1" --> "0..*" sincronizacion_externa : ejecuta

sincronizacion_externa "1" --> "0..*" sincronizacion_detalle : detalles

sistema_externo "1" --> "0..*" referencia_externa : referencias
```