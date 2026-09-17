Lunes 14/09/2026, 12:00 – 14:00

# Preguntas orientadoras

## 1. ¿Qué diferencias existen entre un activo individual, una componente instalada, un accesorio, una refacción y un consumible?

La diferencia principal está en la manera en la que se controla cada uno de los elementos dentro del inventario.

a. **Activo individual:** es un bien que se identifica y controla de manera independiente, como una computadora, impresora o monitor. Tiene un identificador propio y un historial asociado.

b. **Componente instalado:** es una pieza que forma parte de un activo y que puede cambiarse, como una memoria RAM, un disco SSD o una fuente de poder. Debe poder relacionarse con el equipo en el que está instalado.

c. **Accesorio:** elemento complementario que se utiliza junto con un activo, como el teclado, el mouse, el cargador o los adaptadores.

d. **Refacción:** pieza destinada a reparar o sustituir un componente, como una batería, un ventilador o una fuente de poder almacenada para mantenimiento.

e. **Consumible:** material que se utiliza y se agota con el uso, como tóneres, cartuchos, etiquetas, cables o materiales de limpieza.

Se considera una regla importante que no todos deben manejarse de la misma manera: un activo individual requiere trazabilidad individual, mientras que un consumible se controla mediante entradas, salidas y existencias.

Dentro de los consumibles conviene distinguir dos casos:

- **Consumibles serializados** (tóneres y cartuchos): pueden rastrearse de manera individual, porque interesa saber en qué impresora se instaló cada uno.
- **Consumibles no serializados** (cables, etiquetas, material de limpieza): se controlan únicamente por cantidad disponible, sin identificador individual.

Esta distinción se retoma más adelante, en la Regla 4, al definir los estados aplicables a cada caso.

## 2. ¿Qué información es indispensable para identificar un equipo sin crear formularios innecesariamente extensos?

Se debe capturar solo la información indispensable que permita identificar, localizar y controlar el equipo.

Como mínimo:

- Tipo de equipo
- Marca
- Modelo
- Número de serie (en caso de existir)
- Identificador interno (número de inventario)
- Estado
- Ubicación o área
- Responsable o usuario asignado
- Fecha de adquisición

Dependiendo del modelado y del alcance podría capturarse información técnica adicional, la cual debería mantenerse separada de los datos obligatorios, a fin de que el registro inicial sea rápido.

## 3. ¿Cómo se conserva un historial confiable y, al mismo tiempo, se consulta rápidamente el estado actual?

Separando el estado actual del historial de movimientos.

```
PC-001 -> Alta        -> Almacén
PC-001 -> Asignación  -> Administración
PC-001 -> Traslado    -> Sistemas
PC-001 -> Devolución  -> Almacén
```

Queda entonces una estructura de consulta rápida:

```
Equipo:      PC-001
Estado:      En uso
Ubicación:   Administración
Responsable: Usuario A
```

y una estructura separada que almacena sus eventos.

Esto genera un menor consumo de recursos, ya que no es necesario reconstruir todos los movimientos del equipo para conocer su situación actual, y al mismo tiempo se conserva el historial en caso de auditoría.

Por lo anterior, cada movimiento debe registrar fecha, usuario que realiza la operación, origen, destino, motivo y resultado.

## 4. ¿Qué sucede cuando un componente cambia de un equipo a otro o cuando una compra incluye varios activos?

El componente no debe eliminarse ni duplicarse. El comportamiento esperado es:

```
SSD-001 -> Instalado en PC-001
SSD-001 -> Retirado de PC-001
SSD-001 -> Instalado en PC-002
```

Esto permite conocer tanto su ubicación actual como su historial de instalaciones.

En el caso de una compra, el documento de adquisición funciona como registro general y cada bien incluido genera su propio registro individual dentro del inventario.

## 5. ¿Qué reglas deben cumplirse al asignar, trasladar, devolver o dar de baja un bien?

Estas operaciones deben controlarse mediante reglas de negocio:

**Asignación**
- El activo debe existir en el inventario.
- El activo debe estar disponible.
- Su estado debe permitir el cambio de asignación.
- Debe registrarse el responsable asignado.
- Debe registrarse la fecha del cambio de estado.

**Traslado**
- El activo debe encontrarse actualmente en la ubicación de origen.
- Debe especificarse la ubicación de destino.
- Debe registrarse quién realiza el traslado.
- Deben conservarse los movimientos anteriores (historial).

**Devolución**
- El activo debe estar asignado a un responsable o ubicación.
- Debe registrarse quién devuelve el bien.
- Deben actualizarse su estado y su ubicación.
- En caso de presentar algún daño o falla, debe documentarse en el mismo registro.

**Baja**
- El activo no se elimina de la base de datos.
- Se conservan todos sus registros históricos.
- Su estado cambia a "Dado de baja".
- El registro debe almacenar fecha, responsable que autoriza y motivo.

Cada uno de estos registros se conserva con la finalidad de mantener la trazabilidad de los activos.

## 6. ¿Qué información debería estar disponible al escanear un QR sin iniciar sesión y cuál debe permanecer protegida?

El QR debe mostrar únicamente información general y limitada, suficiente para identificar el activo sin exponer información sensible.

**Visible sin iniciar sesión**
- Número de inventario
- Tipo de activo
- Estado general
- Fecha de la última actualización
- Opción para reportar una incidencia

**Protegida**
- Marca y modelo
- Nombre del responsable
- Historial completo de movimientos
- Datos de contacto
- Información de adquisición
- Facturas y documentos
- Información técnica del activo
- Registros de auditoría
- Usuarios que realizaron modificaciones

Cabe señalar que mostrar marca y modelo sin autenticación permitiría que cualquier persona con acceso físico a las instalaciones levante un mapa del inventario escaneando etiquetas. Por esa razón se propone dejar esos datos dentro de la información protegida y limitar la vista pública a la identificación mínima del activo y al reporte de incidencias.

## 7. ¿Cómo se comprueba que un endpoint no genera N+1 y qué volumen de datos sería representativo para probarlo?

El problema N+1 se presenta cuando el número de consultas crece de manera proporcional a la cantidad de elementos recuperados: con 10 elementos se ejecutan 11 consultas y con 1000 elementos se ejecutan 1001. Esto hace que el sistema se vuelva más lento conforme crece el inventario.

La comprobación puede realizarse de la siguiente manera:

- Contar el número de consultas que se ejecutan para satisfacer una misma petición.
- Repetir la medición con distintos volúmenes de datos. Se propone probar con 10, 100 y 1000 activos, ya que ese último valor es representativo del tamaño esperado del inventario del área.
- Si el número de consultas se mantiene constante al aumentar la cantidad de elementos, el comportamiento es el esperado.
- Si el número de consultas aumenta en proporción directa a la cantidad de elementos, existe un problema de tipo N+1.
- Observar el tráfico hacia la base de datos mientras el sistema está en uso. La presencia de patrones repetidos de la misma consulta, variando únicamente el identificador, es una característica del problema N+1.

La corrección consiste en recuperar los datos relacionados en una sola operación, ya sea mediante carga anticipada de relaciones o mediante una consulta con unión de tablas, en lugar de consultar cada elemento por separado.

## 8. ¿Qué índices mejoran consultas reales y qué costos pueden introducir en las operaciones de escritura?

Deben crearse índices únicamente sobre los campos que realmente se utilizan para:

- Buscar
- Filtrar
- Ordenar
- Relacionar registros

Los campos candidatos identificados son:

- numero_inventario
- estado
- ubicacion_id
- responsable_id
- Campos de fecha utilizados en consultas por periodo

Es importante considerar que las claves primarias y los campos declarados como únicos ya cuentan con un índice creado automáticamente por el gestor de base de datos como parte de la restricción de unicidad, por lo que no requieren un índice adicional. Lo mismo aplica a las claves foráneas en varios gestores.

El costo de los índices se presenta en las operaciones de escritura: cada índice ocupa espacio en disco y debe actualizarse cada vez que se inserta, modifica o elimina un registro. Por esa razón no conviene indexar todos los campos de manera indiscriminada, sino únicamente aquellos que se utilizan de forma frecuente en las consultas del sistema.

## 9. ¿Cómo se validan y protegen PDF, XML e imágenes cargados por usuarios?

Los archivos deben validarse por tipo, tamaño y contenido:

- Establecer un tamaño máximo por archivo.
- Permitir únicamente las extensiones necesarias.
- Validar el tipo MIME y no confiar únicamente en la extensión.
- Verificar que el archivo realmente corresponda al tipo declarado.
- Generar nombres de archivo seguros, evitando utilizar directamente el nombre proporcionado por el usuario.
- Almacenar los archivos fuera de directorios donde puedan ejecutarse como código.
- Aplicar permisos adecuados de lectura y escritura.
- Registrar qué usuario realizó la carga y en qué fecha.
- Considerar el análisis antivirus cuando sea posible.

## 10. ¿Qué pruebas aportan mayor confianza en las reglas del inventario, la trazabilidad y los permisos?

Para determinar que el sistema funciona de manera confiable es necesario realizar pruebas que comprueben tanto las reglas de los datos como el seguimiento de los cambios y el acceso de los usuarios.

### Pruebas de reglas del inventario

Deben comprobar que los activos cumplan con las reglas definidas para su registro y administración:

- **Identificador único:** intentar registrar dos activos con el mismo identificador para comprobar que el sistema impida duplicados.
- **Campos obligatorios:** intentar registrar un activo sin información indispensable, como identificador o tipo de activo.
- **Datos inválidos:** introducir valores incorrectos para comprobar que sean rechazados.
- **Estados del activo:** cambiar un equipo entre los diferentes estados permitidos y verificar que solo se acepten los valores establecidos.
- **Componentes:** comprobar que un componente pueda asignarse a un equipo y que el sistema evite relaciones incorrectas, como que un mismo componente aparezca instalado en dos equipos al mismo tiempo.
- **Bajas de activos:** verificar qué sucede cuando un activo deja de utilizarse y asegurar que su información histórica no se pierda.

Con esto se busca que la base de datos mantenga información consistente y que se eviten registros duplicados.

### Pruebas de trazabilidad

Deben comprobar que los cambios realizados sobre un activo puedan consultarse posteriormente.

Secuencia propuesta para las pruebas:

```
Equipo registrado -> Asignación a un usuario -> Cambio de ubicación ->
Cambio de componente -> Mantenimiento -> Nueva asignación
```

Después se comprueba que el sistema conserve el historial correspondiente:

- Registrar un activo y comprobar que quede almacenada la fecha de registro.
- Cambiar el responsable y verificar que se conserve el responsable anterior.
- Cambiar la ubicación y comprobar que pueda consultarse la ubicación anterior.
- Sustituir un componente y verificar que queden registrados el componente retirado y el nuevo.
- Registrar un mantenimiento y comprobar que quede asociado al activo correspondiente.
- Registrar una incidencia y verificar que pueda consultarse posteriormente.

Debe realizarse una prueba en la que se compruebe que el estado actual del activo puede obtenerse a partir de la información registrada y que los cambios anteriores permanecen disponibles para consulta.

### Pruebas de permisos

Deben verificar que cada usuario solamente pueda realizar las operaciones correspondientes a su función dentro del sistema.

| Prueba | Resultado esperado |
|---|---|
| Usuario autorizado consulta un activo | Puede visualizar la información permitida |
| Usuario autorizado modifica un activo | El cambio se registra correctamente |
| Usuario sin permiso intenta modificar un activo | La operación es rechazada |
| Usuario intenta eliminar información histórica | La operación es restringida |
| Usuario consulta información fuera de su función | El sistema limita el acceso |
| Administrador modifica permisos | El cambio solo puede realizarlo un usuario autorizado |

Debe comprobarse que las restricciones funcionen tanto en la interfaz del sistema como en las operaciones que se realicen directamente contra los servicios o módulos de la aplicación.

La prueba final de permisos, consultas y modificaciones debe verificar que:

1. El equipo existe una sola vez.
2. Su estado actual es el correcto.
3. Su responsable actual es el correcto.
4. Su ubicación actual es la correcta.
5. Sus componentes actuales son los correctos.
6. Los cambios anteriores permanecen registrados.
7. Los usuarios solamente hayan podido realizar las operaciones autorizadas.

## 11. ¿Qué alternativas de lectura e impresión de QR ofrecen la mejor relación entre costo, durabilidad y facilidad de uso para el área?

El uso de códigos QR facilita la identificación de activos tecnológicos, ya que permite asociar físicamente un equipo con su registro dentro del sistema.

Para seleccionar las alternativas más adecuadas se consideran los siguientes aspectos:

- **Costo:** precio de impresión y materiales necesarios.
- **Durabilidad:** capacidad de conservar el código legible durante la vida útil del activo.
- **Facilidad de uso:** rapidez para imprimir, colocar y leer los códigos.

### Alternativas de impresión

| Alternativa | Costo | Durabilidad | Facilidad de uso | Aplicación |
|---|---|---|---|---|
| Etiqueta adhesiva de papel | Bajo | Baja | Alta | Equipos de uso interno y temporal |
| Etiqueta adhesiva sintética | Bajo-medio | Media-alta | Alta | Computadoras y periféricos |
| Etiqueta de poliéster | Medio | Alta | Alta | Equipos de uso frecuente |
| Etiqueta industrial | Medio-alto | Muy alta | Media | Equipos expuestos a condiciones exigentes |
| Impresión en hoja y recorte | Muy bajo | Baja | Media | Pruebas o prototipos |

### Alternativas de lectura

Para la lectura de códigos QR no es necesario adquirir dispositivos especializados desde el inicio.

**Teléfono inteligente.** La cámara de los dispositivos móviles identifica los códigos QR y permite acceder a los registros correspondientes dentro del sistema.

Ventajas:
- No requiere adquirir lectores especializados.
- Es fácil de utilizar.
- Permite realizar consultas directamente donde se encuentra el activo.
- Puede utilizarse mediante una aplicación o desde el navegador.

**Lector QR dedicado.** Dispositivo especializado para realizar lecturas de código.

Ventajas:
- Facilita las lecturas repetitivas.
- Resulta conveniente cuando se realizan inventarios de manera constante.
- Puede conectarse a una computadora, según el modelo.

Representa un costo adicional de adquisición y mantenimiento.

**Computadora con cámara.** Puede utilizarse, aunque resulta menos práctica cuando se realizan recorridos físicos por las instalaciones.

### Mejor opción considerada

Etiquetas QR más teléfonos inteligentes para la lectura, debido a su practicidad: evita la compra de lectores especializados y permite que el personal consulte la información del activo desde el lugar donde se encuentra.

El QR contendrá un identificador único del activo o una referencia que permita al sistema localizar su registro. De esta manera el código no almacena toda la información del equipo: la información permanece en la base de datos y el QR funciona principalmente como mecanismo de identificación.

---

Miércoles 16 de septiembre de 2026

# Avances de prácticas

**Proyecto:** Diseño y desarrollo de un sistema web para la gestión de activos tecnológicos y mesa de ayuda de TI
**Etapa:** Análisis y diseño preliminar
**Fecha:** 16 de septiembre de 2026
**Horario correspondiente:** 9:00 – 16:00

## Introducción

Como parte de las actividades iniciales del proyecto de prácticas se inicia el análisis de los requerimientos relacionados con la gestión de los activos tecnológicos y con la futura estructura de información del sistema.

El proyecto contempla el desarrollo de una solución orientada a la gestión de activos tecnológicos, considerando aspectos como inventario de equipos, componentes, asignaciones, ubicaciones, movimientos, mantenimientos e incidencias.

Durante estos avances se busca identificar las necesidades que deberá cubrir el sistema para comenzar con la implementación de la base de datos. Para ello se analizan los aspectos relacionados con las reglas de inventario, la trazabilidad de activos, los permisos de los usuarios y las alternativas para utilizar códigos QR como mecanismo de identificación física.

El componente de mesa de ayuda se aborda en este avance únicamente a nivel de la entidad Incidencia. El análisis del flujo de atención, categorías, prioridades y tiempos de respuesta se contempla para el siguiente avance.

## Objetivo del avance

Identificar los principales requerimientos de información y de operación relacionados con la gestión de activos tecnológicos, con el propósito de establecer una propuesta preliminar para el inventario, la trazabilidad, el control de permisos y la identificación de los activos mediante códigos QR.

## Análisis de las reglas de inventario

Uno de los aspectos principales a considerar es la necesidad de establecer reglas que permitan mantener información consistente en el inventario.

**Regla 1. Identificación única**

Cada activo debe contar con un identificador único que permita distinguirlo de los demás activos registrados. El sistema debe evitar que dos o más activos tengan el mismo identificador.

**Regla 2. Información mínima obligatoria**

Para el registro de activos deben establecerse determinados datos indispensables, evitando la solicitud de información innecesaria. Entre los datos considerados de manera inicial están:

1. Identificador
2. Tipo de activo
3. Marca
4. Modelo
5. Número de serie (cuando exista)
6. Estado
7. Ubicación
8. Responsable o usuario asignado

**Regla 3. Estado del activo**

Todo activo debe mantener un estado actual que permita conocer su condición o situación dentro del inventario.

Para computadoras, impresoras y equipos de almacenamiento:

- **Activo / en uso:** el equipo está asignado a un usuario o departamento, o conectado a la red, cumpliendo funciones operativas.
- **Disponible / en stock:** el equipo está en almacén o inventario central, en buen estado y listo para ser asignado o instalado.
- **En mantenimiento / reparación:** el activo presenta una falla temporal y se encuentra en revisión técnica, interna o del proveedor.
- **En tránsito / préstamo:** el equipo fue trasladado temporalmente a otra sucursal o se entregó como préstamo temporal a un usuario.
- **Baja temporal:** el equipo está retenido por auditoría o por respaldo de información pendiente.
- **Dado de baja:** el activo cumplió su vida útil o está dañado y ha sido retirado del inventario.

**Regla 4. Control de consumibles**

Los consumibles no se controlan de la misma forma que los activos individuales. Se distinguen dos casos:

*Consumibles serializados* (tóneres y cartuchos). Se registran individualmente y mantienen un estado propio:

- **Nuevo / en stock:** el consumible está sellado en su empaque original, almacenado y listo para su uso.
- **En uso / instalado:** el tóner o cartucho fue colocado en una impresora y se encuentra operando.
- **Agotado / vacío:** el consumible llegó al fin de su vida útil y está pendiente de reemplazo o de recolección para reciclaje.
- **Dañado / defectuoso:** el consumible llegó con fallas de fábrica, se derramó o se rompió el sello antes de instalarse.
- **Caducado:** el consumible superó la fecha recomendada por el fabricante, lo que podría afectar la calidad de impresión o dañar el equipo.

*Consumibles no serializados* (cables, etiquetas, material de limpieza). Se controlan únicamente mediante entradas, salidas y existencias, sin identificador individual ni historial por unidad.

**Regla 5. Relación entre activos y componentes**

Los componentes instalados deben poder relacionarse con el equipo al que pertenecen. La estructura debe considerar que un componente puede ser retirado de un equipo y posteriormente instalarse en otro. Un mismo componente no puede figurar como instalado en dos equipos al mismo tiempo.

**Regla 6. Conservación de la información**

Los cambios realizados sobre un activo no deben provocar la pérdida de la información anterior cuando esta sea necesaria para fines de trazabilidad.

**Regla 7. Inventario relacionado con el documento de origen**

Todo activo registrado debe contar con una referencia al documento mediante el cual ingresó al inventario. En la mayoría de los casos este documento será la factura de adquisición, pero también deben contemplarse otros orígenes:

- Factura de compra
- Contrato de arrendamiento o comodato
- Acta de donación
- Acta de transferencia desde otra área o dependencia

Cuando un activo se incorpore al inventario sin que su documento de origen esté disponible, el registro se marca como **pendiente de documentación**, en lugar de rechazarse. Esto evita que equipos heredados o sin factura localizable queden fuera del inventario.

Mostrando las reglas de forma resumida:

| Situación | Resultado esperado |
|---|---|
| Registrar activo con documento de origen | Registro permitido |
| Registrar activo sin documento de origen | Registro permitido, marcado como pendiente de documentación |
| Registrar varios activos con un mismo documento | Permitido |
| Registrar varios componentes con un mismo documento | Permitido |
| Consultar el documento desde un activo | Debe mostrar el documento relacionado |
| Consultar los activos desde un documento | Debe mostrar los activos relacionados |

## Análisis de la trazabilidad

La trazabilidad se considera un elemento importante, debido a que los activos tecnológicos pueden experimentar diferentes cambios durante su vida útil.

Un equipo puede cambiar de:

- Usuario
- Responsable
- Ubicación
- Estado
- Componentes
- Condición de mantenimiento

Por lo anterior se propone el manejo de dos tipos de información.

**Información actual.** Permite conocer la condición y situación actual del activo:

```
Equipo:      PC-001
Ubicación:   Oficina de TI
Responsable: Usuario A
Estado:      En operación
```

**Información histórica.** Permite conocer los cambios anteriores:

```
PC-001      -> Oficina A -> Oficina B
PC-001      -> Usuario A -> Usuario B
SSD 256 GB  -> Retirado
SSD 1 TB    -> Instalado
```

De esta manera la base de datos no solo permite conocer el estado actual, sino también reconstruir los cambios importantes que haya experimentado el activo.

## Análisis de los permisos

*(Pendiente de definir los usuarios con acceso al sistema.)*

Se considera establecer diferentes niveles de acceso. No todos los usuarios deben tener la posibilidad de realizar las mismas operaciones sobre la información del inventario.

Como propuesta general de permisos se contempla:

| Operación | Posible restricción |
|---|---|
| Consultar activos | Según el tipo de usuario |
| Registrar activos | Personal autorizado |
| Modificar activos | Personal autorizado |
| Registrar movimientos | Personal autorizado |
| Registrar mantenimientos | Personal de TI |
| Registrar incidencias | Usuarios autorizados |
| Modificar permisos | Administrador |
| Eliminar registros | Operación restringida |

## Análisis de la identificación mediante códigos QR

Como parte de lo identificado se contempla la utilización de códigos QR para facilitar la identificación física de los activos.

El objetivo es colocar una etiqueta en cada equipo para que el personal pueda escanearla y acceder rápidamente al registro correspondiente dentro del sistema. Se analizan dos elementos principales.

**Lectura.** Como alternativa inicial se considera el uso de teléfonos inteligentes, debido a que permite realizar la lectura sin adquirir dispositivos especializados. También se contempla la posibilidad de utilizar lectores QR dedicados en caso de que posteriormente se determine que el volumen del inventario o la frecuencia de revisiones lo requieran.

**Impresión.** Se identificaron diferentes alternativas de etiquetas:

- Papel adhesivo
- Material sintético
- Poliéster
- Etiquetas industriales

Para una primera evaluación se considera conveniente comparar principalmente el costo, la resistencia, la adherencia y la facilidad de lectura.

**Funcionamiento (propuesta).** El código QR no almacenará la información completa del activo. Se propone la siguiente secuencia:

```
Código QR -> Identificador del activo -> Sistema web -> Registro del activo
```

De esta manera, en caso de cambio de ubicación, responsable, estado o componentes del equipo, la información puede actualizarse directamente en la base de datos sin necesidad de generar un nuevo código QR.

## Información preliminar del activo

A partir del análisis anterior se identifica que el registro de un activo podría requerir inicialmente la siguiente información:

| Campo | Propósito |
|---|---|
| Identificador | Identificar de manera única el activo |
| Tipo | Clasificar el activo |
| Marca | Identificar el fabricante |
| Modelo | Identificar el modelo |
| Número de serie | Identificación proporcionada por el fabricante |
| Estado | Conocer la situación actual |
| Ubicación | Conocer dónde se encuentra |
| Responsable | Conocer quién tiene asignado el activo |
| Fecha de registro | Identificar cuándo fue registrado |
| Observaciones | Registrar información adicional |

## Entidades propuestas para la base de datos

A partir de las necesidades identificadas se propone considerar inicialmente las siguientes entidades:

- Factura (o documento de origen)
- Activo
- TipoActivo
- Usuario
- Ubicación
- Asignación
- Movimiento
- Componente
- ComponenteInstalado
- Mantenimiento
- Incidencia
- EtiquetaQR

Respecto a la entidad **EtiquetaQR**: dado que el código contiene únicamente el identificador del activo, esta entidad solo se justifica si se requiere llevar control de las etiquetas físicas impresas (fecha de impresión, material utilizado, reimpresiones). En caso contrario, el QR puede generarse a partir del identificador del activo sin necesidad de una entidad propia. Esta decisión queda pendiente de confirmación.

Respecto a las entidades **Asignación** y **Movimiento**: ambas registran eventos sobre el activo y podrían solaparse. Se propone tratar la asignación como un tipo de movimiento dentro de una misma bitácora, diferenciándolo mediante un campo de tipo de evento (alta, asignación, traslado, devolución, mantenimiento, baja). De esta forma se evita registrar el mismo hecho en dos lugares distintos. Esta decisión también queda pendiente de confirmación durante el diseño de la base de datos.

## Relaciones (propuesta)

Se identifican las siguientes relaciones:

- Un TipoActivo puede estar relacionado con varios Activos.
- Un Activo puede tener diferentes asignaciones a lo largo del tiempo.
- Un Activo puede registrar diferentes movimientos.
- Un Activo puede tener diferentes registros de mantenimiento.
- Un Activo puede presentar diferentes incidencias.
- Un Componente puede ser retirado de un activo y posteriormente relacionarse con otro.
- Una Ubicación puede contener múltiples activos.
- Un Activo puede tener asociado un código QR para facilitar su identificación.

### Relación entre facturas y activos

Se establece una relación de uno a muchos entre las entidades Factura y Activo:

- Una factura puede contener uno o varios activos.
- Cada activo debe estar asociado a un documento de origen, o bien quedar marcado como pendiente de documentación.
- Una misma factura puede estar relacionada con diferentes tipos de activos.

La relación se representa como:

```
Factura (1) ---------------------- (N) Activo
```

Ejemplo de una factura:

```
Factura F-00125
    Laptop Dell Latitude 5420
    Monitor Dell P2422H
    Impresora HP LaserJet
```

Los tres elementos pertenecen a la misma factura, pero cada uno mantiene su propio registro dentro del inventario.

### Relación entre facturas y componentes

Se identifica también el caso de que una factura puede incluir componentes tecnológicos que no necesariamente representan un equipo completo. Por ejemplo:

- 5 memorias RAM
- 3 unidades SSD
- 2 fuentes de alimentación
- 1 computadora portátil

De la misma manera, cada uno de los componentes debe poder relacionarse con la factura correspondiente:

```
Factura (1) ---------------------- (N) Componente
```

### Información de la factura necesaria (propuesta)

La entidad Factura debe analizarse para determinar los datos necesarios. Se consideran los siguientes elementos:

- Identificador de la factura
- Folio o número de factura
- Fecha de emisión
- Proveedor
- RFC del proveedor
- Importe total
- Moneda
- Archivo o documento digital de la factura (si se requiere almacenar)
- Observaciones
