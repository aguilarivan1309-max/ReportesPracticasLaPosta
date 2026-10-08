
# 1. Levantamiento y comprensión del proyecto

## 1.1 Descripción del problema
### 14/09/2026 12:00 - 14:00
El área de tecnología de TI necesita contar con un sistema que permita administrar de manera organizada los bienes relacionados con TI. Actualmente se requiere conocer qué bienes existen, dónde se encuentran, quién los tiene bajo responsabilidad, cuál es el estado y cuál ha sido su recorrido dentro de la organización.

El sistema deberá permitir registrar y consultar los bienes, relacionados con la información de su adquisición, conservar documentos y fotografías, y facilitar su identificación mediante códigos QR.

Además, deberá conservar un historial de los cambios importantes relacionados sobre los bienes, principalmente los relacionados con su ubicación, responsable y estado.

## 1.2 Alcance inicial

En esta primera etapa se desarrollará únicamente el backend del sistema. El backend será construido utilizando Django y Django REST Framework y proporcionará una API REST que posteriormente podrá ser utilizada por una interfaz desarrollada en React.

El sistema contemplará la administración del inventario, ubicaciones, responsables, estados, adquisiciones, archivos, códigos QR e historial de cambios, además de mecanismos de autenticación, autorización, pruebas y documentación.

La interfaz final en React y otros módulos como tickets, incidencias, reparaciones y mantenimientos no forman parte de esta primera etapa.


# 1.3. Preguntas orientadoras para la investigacón 
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

# -------
### 16/09/2026 9:00 - 16:00 

# Continuacion de Preguntas
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

## 1.3 Actores del sistema

Para el funcionamiento del sistema del inventario se consideran tres tipos de usuarios:

**Administrador**

Es el usuario encargado de administrar el sistema y sus configuraciones principales. Tendrá permisos para registrar, modificar y consultar la información del inventario, así como administrar usuarios y permisos cuando corresponda.

**Operador**

Es el usuario encargado de realizar las operaciones cotidianas del inventario. Podrá registrar y actualizar bienes, ubicaciones, responsables y estados, además de consultar la información necesaria para realizar sus actividades.

**Usuario de consulta**

Es el usuario que únicamente necesita consultar información del inventario. Tendrá permisos limitados y no podrá modificar los registros.

## 1.4 Permisos y acciones de usuarios

| Acción | Administrador | Operador | Usuario de consulta |
|---|:---:|:---:|:---:|
| Iniciar sesión | ✓ | ✓ | ✓ |
| Consultar bienes | ✓ | ✓ | ✓ |
| Buscar y filtrar bienes | ✓ | ✓ | ✓ |
| Registrar bienes | ✓ | ✓ | ✕ |
| Modificar bienes | ✓ | ✓ | ✕ |
| Registrar ubicaciones | ✓ | ✓ | ✕ |
| Modificar ubicaciones | ✓ | ✓ | ✕ |
| Registrar responsables | ✓ | ✓ | ✕ |
| Modificar responsables | ✓ | ✓ | ✕ |
| Cambiar estado de un bien | ✓ | ✓ | ✕ |
| Registrar adquisiciones | ✓ | ✓ | ✕ |
| Cargar documentos y fotografías | ✓ | ✓ | ✕ |
| Asociar código QR | ✓ | ✓ | ✕ |
| Consultar historial | ✓ | ✓ | ✓ |
| Consultar información mediante QR | ✓ | ✓ | ✓ |
| Administrar usuarios y permisos | ✓ | ✕ | ✕ |

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
Respecto a las entidades **Asignación** y **Movimiento**: ambas registran eventos sobre el activo y podrían solaparse. Se propone tratar la asignación como un tipo de movimiento dentro de una misma bitácora, diferenciándolo mediante un campo de tipo de evento (alta, asignación, traslado, devolución, mantenimiento, baja). De esta forma se evita registrar el mismo hecho en dos lugares distintos. Esta decisión también queda pendiente de confirmación durante el diseño de la base de datos.


# ----
# 21/01/2026 12:00 - 14:00 
## 1.5 Información de los bienes

Para que el sistema pueda identificar y administrar correctamente los bienes de TI, cada registro deberá contener información suficiente para distinguirlo de otros bienes.

| Dato | Descripción |
|---|---|
| Identificador | Referencia única del bien cuando requiera seguimiento individual |
| Nombre | Nombre del bien |
| Descripción | Información adicional para describir el artículo |
| Categoría | Tipo de bien al que pertenece |
| Marca | Fabricante del bien |
| Modelo | Modelo correspondiente |
| Número de serie | Identificador proporcionado por el fabricante, cuando exista |
| Estado | Situación actual del bien |
| Ubicación | Lugar donde se encuentra actualmente |
| Responsable | Persona que tiene el bien asignado o bajo resguardo |
| Código QR | Identificador utilizado para localizar la ficha del bien |
| Fecha de registro | Fecha en que el bien fue incorporado al sistema |

## 1.6 Clasificación de bienes

El sistema deberá permitir registrar diferentes tipos de bienes relacionados con el área de Tecnologías de la Información. Debido a que no todos los artículos se administran de la misma manera, se propone clasificarlos en las siguientes categorías:

| Tipo de bien | Descripción | ¿Requiere identificación individual? | Ejemplos |
|---|---|:---:|---|
| Activo Individual | Bien que debe ser identificado y seguido de manera individual durante su permanencia en la organización | Sí | Laptop, servidor, monitor, impresora, teléfono |
| Componente | Elemento que puede formar parte de un equipo o estar instalado dentro de otro bien | Puede requerirla | Memoria RAM, disco duro, tarjeta de red |
| Accesorio | Artículo complementario utilizado junto con un equipo, pero que no necesariamente forma parte de él | Generalmente no | Teclado, mouse, adaptador |
| Refacción | Pieza destinada a sustituir un componente o pieza de un equipo | Generalmente no | Fuente de poder, ventilador, batería |
| Consumible | Artículo que se utiliza y se reemplaza periódicamente como parte de la operación | No | Tóner, papel, consumibles de impresión |

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



# --- 
# 23/09/2026 9:00 - 14:00 
## 1.7 Ubicación, responsable y estado

Para mantener un control adecuado de los bienes, el sistema deberá registrar su ubicación actual, la persona responsable y el estado en el que se encuentra cada bien.

**Ubicación**

La ubicación representa el lugar donde se encuentra actualmente un bien.
Por ejemplo:

| Ubicación | Ejemplo |
|---|---|
| Edificio | Edificio A |
| Área | Área de tecnologías de la información |
| Oficina | Oficina 3 |
| Almacén | Almacén de TI |

Una ubicación deberá poder asociarse con varios bienes y permitirá consultar qué bienes se encuentran actualmente en ella.

**Responsable**

El responsable representa a la persona que tiene un bien asignado o bajo su resguardo.
El sistema deberá permitir identificar al responsable de un bien y consultar los bienes relacionados con cada responsable.

**Estado**

El estado representa la condición administrativa u operativa actual de un bien.

Como parte del análisis inicial se consideran estados que permitirán distinguir la situación del bien, por ejemplo:

| Estado | Descripción |
|---|---|
| En uso | El bien se encuentra actualmente en funcionamiento o asignado |
| Almacenamiento | El bien se encuentra resguardado y no está asignado |
| En revisión | El bien se encuentra pendiente de revisión o verificación |
| Baja | El bien ha dejado de formar parte de los bienes disponibles para su uso |

Los estados deberán permitir representar de forma clara la condición actual del bien y posteriormente controlar las transiciones que sean válidas dentro del proceso.

## 1.8 Adquisiciones y documentos

Los bienes registrados en el inventario deberán poder relacionarse con la adquisición que les dio origen. De esta manera, el sistema podrá conservar información relacionada con la compra y mantener evidencia documental asociada a los bienes.

La información de una adquisición podrá incluir los datos necesarios para identificar la compra y relacionarla con uno o varios bienes registrados en el inventario.

Además, el sistema deberá permitir conservar diferentes tipos de archivos de respaldo, de acuerdo con la información disponible para cada adquisición o bien.

Entre los archivos que se contemplan se encuentran:

| Tipo de archivo | Uso dentro del sistema |
|---|---|
| Factura | Evidencia de la adquisición del bien |
| PDF | Documento de respaldo relacionado con la compra |
| XML | Archivo electrónico asociado a la factura |
| Fotografía | Evidencia visual para apoyar la identificación del bien |

Los archivos deberán almacenarse de manera organizada y deberán considerarse mecanismos para validar los tipos y tamaños permitidos. También deberán contemplarse aspectos de seguridad, recuperación y crecimiento del almacenamiento.

La relación entre adquisiciones y bienes deberá permitir que una misma compra pueda estar asociada con varios bienes cuando corresponda.

## 1.9 Código QR

Los bienes que requieran identificación individual podrán contar con un código QR asociado a su registro dentro del sistema. El objetivo del código será facilitar la identificación física del bien y permitir localizar rápidamente su ficha correspondiente.

El código QR no deberá contener directamente información sensible del activo. En su lugar, deberá utilizar un identificador que permita al sistema localizar el registro correspondiente y aplicar las reglas de acceso establecidas.

La información almacenada en el QR deberá mantenerse independiente de los datos que se muestran en la ficha del bien. De esta manera, si la información del activo cambia, por ejemplo su ubicación, responsable o estado, no será necesario modificar el código QR.

El sistema deberá contemplar también la posibilidad de asociar o generar nuevamente un código cuando un bien lo requiera, así como considerar qué procedimiento seguir cuando una etiqueta QR se dañe o deje de ser legible.

Como parte de una investigación posterior se compararán diferentes alternativas para la lectura e impresión de los códigos QR, considerando dispositivos, compatibilidad, costos aproximados, ventajas, limitaciones y materiales para las etiquetas.

## 1.10 Historial y trazabilidad
### Analisis de Trazabilidad
Los activos tecnológicos pueden experimentar diferentes cambios durante su vida útil.

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

## Trazabilidad 
El sistema deberá conservar un historial de los cambios relevantes realizados sobre los bienes del inventario, con el propósito de mantener la trazabilidad de cada activo durante su permanencia dentro de la organización.

El historial deberá permitir conocer, como mínimo, los cambios relacionados con:
- Ubicación.
- Responsable.
- Estado.

Cada registro del historial deberá conservar información que permita identificar cuándo ocurrió el cambio, qué modificación se realizó y qué usuario registró la operación.

El historial deberá mantenerse aunque la información actual del bien sea modificada. Por lo tanto, actualizar la ubicación, el responsable o el estado de un bien no deberá eliminar los datos correspondientes a sus situaciones anteriores.

Por ejemplo, si un equipo cambia de ubicación, el sistema deberá conservar tanto la ubicación anterior como la nueva:

| Fecha | Ubicación anterior | Ubicación nueva | Usuario |
|---|:---:|:---:|:---:|
| 10/09/2026 | Laboratorio 1 | Laboratorio 2 | Operador1 |

De esta manera, será posible consultar tanto la situación actual del bien como los movimientos que ha tenido anteriormente.

La trazabilidad permitirá reconstruir el recorrido de los bienes y proporcionará evidencia de las operaciones realizadas sobre ellos.

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

# Relaciones propuestas por activos 
Se identifican las siguientes relaciones:

- Un TipoActivo puede estar relacionado con varios Activos.
- Un Activo puede tener diferentes asignaciones a lo largo del tiempo.
- Un Activo puede registrar diferentes movimientos.
- Un Activo puede tener diferentes registros de mantenimiento.
- Un Activo puede presentar diferentes incidencias.
- Un Componente puede ser retirado de un activo y posteriormente relacionarse con otro.
- Una Ubicación puede contener múltiples activos.
- Un Activo puede tener asociado un código QR para facilitar su identificación.

## Relacion entre facturas y activos 
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

# Relacion entre Facturas y componentes
Se identifica también el caso de que una factura puede incluir componentes tecnológicos que no necesariamente representan un equipo completo. Por ejemplo:

- 5 memorias RAM
- 3 unidades SSD
- 2 fuentes de alimentación
- 1 computadora portátil

De la misma manera, cada uno de los componentes debe poder relacionarse con la factura correspondiente:

```
Factura (1) ---------------------- (N) Componente
```
### Informacion necesaria de la factura (Propuesta)
Se consideran los siguientes elementos:

- Identificador de la factura
- Folio o número de factura
- Fecha de emisión
- Proveedor
- RFC del proveedor
- Importe total
- Moneda
- Archivo o documento digital de la factura (si se requiere almacenar)
- Observaciones


# -------
### 25/09/2026 9:00 - 11:00

## 1.11 Consultas y búsquedas
El sistema deberá proporcinar mecanismos de consultas que permitan localizart de manera eficiente los bienes registrados en el inventario. 

Las consultas deberán permitir buscar y filtrar información relevante de los bienes, por ejemplo: 
- Identificador del bien. 
- Nombre. 
- Categoría. 
- Marca o modelo 
- Número de serie 
- Ubicación 
- Responsable 
- Estado 

Tambien deberá ser posible ordenas los resultados de acuerdo con los datos disponibles, con el objetivo de facilitar la consulta del inventario. 

Los resultados deberán mostrarse mediante listados con paginación para evitar que el sistema tenga que devolver todos los registros disponibles en una sola consulta. 

Además, las consultas deberán diseñarse de manera eficiente para evitar operaciones repetitivas e innecesarias sobre la base de datos, especialmente cuando existan relaciones sobre bienes, responsables, ubicaciones, y otros elementos del sistema. 

La información detallada de un bien podrá consultarse individualmente a partir de su identificador y, cuando responda, mediante el código QR asociado. 

## 1.12 Archivos  y seguridad 

El sistema deberá permitir la carga y conservación de documentos y fotografias relacionados con los bienes y sus adquisiciones. Debido a que estos archivos forman parte de la información del inventario, deberá establecerse condiciones adecuadas para su validación, almacenamiento y recuperación. 

Los archivos deberán ser validados antes de almacenarse, considerando principalmente:

- Tipos de archivos permitido.
- Tamaño maximo. 
- Condiciones de almacenamiento. 
- Seguridad de los archivos.
- Recuperación de la información. 
- Crecimeinto del espacio de almacenamiento. 

Entre los archivos que deberán contemplarse se encuentran documentos PDF, archivos XML y fotografías. 

El almacenamiento deberá diseñarse de forma que pueda mantenerse organizado y que permita administrar un mayor volumen de archivos conforme crezca el inventario. 

También deberán considerarse medidas para evitar que la carga de archivos permita incorporar información no autorizada o incompatible con las condiciones establecidas por el sistema. 

Las mismas consideraciones deberán mantenerse en los ambientes de desarrollo y producción, tomando en cuenta las necesidades se seguridad y almacenamiento de cada ambiente. 

Por ejemplo: 
Usuario
   ↓
Sube archivo
   ↓
Validar tipo
   ↓
Validar tamaño
   ↓
Validar condiciones
   ↓
Almacenar

## 1.13 Autenticación, autorización y registro de operaciones

El sistema deberá contar con mecanismos de autenticación que permitan identificar a los usuarios que accedan al backend. 

Además de identificar al usuario, el sistema deberá aplicar mecanismos de autorización para determinar qué operaciones puede realizar cada tipo de usuario de acuerdo con los permisos establecidos anteriormente. 

Las operaciones que requieran permisos deberán ser rechazadas cuiando sean realizadas por usuarios que no tengan autorización suficiente. Las respuestas de la API deberán informar de manera clara cuando una operación no pueda realizarse debido a restricciones de acceso. 

El sistema tambien deberá conservar un registro suficiente de las operaciones realizadas por los usuarios para facilitar la trazabilidad de las modificaciones efectuadas sobre la información del inventario. 

Este registro deberá permitir relacionar las operaciones relevantes con el usuario que las realizo y conservar la información necesaria para revisar posteriormente las acciones efectuadas en el sistema. 

La implementación especifica del mecanismo de autenticación, autorización y registro sera definido posteriormente durante el diseño del backend.

# 2. Casos de uso y escenarios principales 
Los casos de uso describen las principales operaciones que los usuarios podrán realizar dentro del sistema de inventario. Estos escenarios permiten definir el comportamiento esperado del backend antes de comenzar con la implementación técnica.

## 2.1 Registrar un bien 
Actor principal: Administrador u Operador 
Objetivo: Registrar un bien dentro del inventario. 

**Precondiciones:** 
- El usuario debe haber iniciado sesión.
- El usuario debe contar con permisos para registrar bienes. 

**Flujo principal** 
1. El usuario selecciona la operación para registrar un nuevo bien.
2. El sistema solicita la información correspondiente al bien. 
3. El usuario captura los datos disponibles.
4. El sistema valida la información proporcionada. 
5. El sistema verifica que los datos utilizados para identificar individualmente el bien no genera un registro duplicado. 
6. El sistema registra el bien. 
7. El sistema establece la información inicial correspondiente. 
8. El sistema confirma que el registro fue creado correctamente. 

**Resultado Esperado:** 
El nuevo bien queda registrado en el inventario y puede ser consultado posteriormente por los usuarios que tengan permisos para hacerlo. 

### 28/09/2026 12:00 - 14:00


## 2.2 Consultar un bien 
**Actor Principal**: Administrador, operador o Usuario de consultas
**Objetivo**: Consultar la información de un bien registrado en el inventario 
**Precondiciones**: 
- El usuario debe haber iniciado sesión.
- El usuario debe contar con permisos de consultas.
- El bien debe encontrarse registrado en el sistema. 

**Flujo principal**: 
1. El usuario accede a la consulta de los bienes.
2. El usuario busca o selecciona el bien que desea consultar.
3. El sistema localiza el registro correspondiente. 
4. El sistema verifica que el usuario tenga permisos para consultar la información. 
5. El sistema recupera la información disponible del bien.
6. El sistema muestra la ficha correspondiente. 

**Información que podrá mostrarse: 
- Identificación del bien.
- Nombre y descripción.
- Categoría.
- Marca y modelo.
- Número de serie, cuando corresponda. 
- Estado actual.
- Ubicación actual.
- Responsable actual. 
- Información relacionada con su adquisición 
- Código QR asociado, cuando corresponda 

**Flujo alternativo** 
Si el bien solicitado no existe, el sistema deberá informar que no se encontró ningún registro correspondiente. 

Si el usuario no cuenta con los permisos necesarios, el sistema deberá rechazar la consulta y devolver una respuesta clara 

**Resultado Esperado** 
El usuario puede consultar la información actual del bien sin modificar los datos almacenados en el inventario. 

## 2.3 Modificar un bien.

**Actor principal**: Administrador u Operador.

**Objetivo**: Actualizar la información de un bien que ya se encuentra registrado en el inventario.

**Precondiciones**: 
- El usuario debe haber iniciado sesión. 
- El usuario debe contar con permisos par modificar bienes. 
- El bien debe existir dentro del sistema. 

**Flujo principal**: 
1. El usuario localiza el bien que desea modificar. 
2. El sistema muestra la información actual del bien. 
3. El usuario modifica uno o varios datos permitidos. 
4. El sistema valida la nueva información.
5. El sistema verifica que la modificación no genera información inválida o duplicada.
6. El sistema actualiza los datos del bien. 
7. Si el cambio afecta la ubicación, el responsable o el estado, el sistema deberá conservar el registro anterior dentro del historial. 
8. El sistema registra al usuario que realizó la operación. 
9. El sistema confirma que la modificación fue relizado correctamente. 

**Flujos alternativos**

- Si el bien no existe, el sistema deberá informar que no se encontró el registro solicitado.
- Si el usuario no tiene permisos sificiente, la operación deberá ser rechazada.
- Si los nuevos datos no cumplen con las reglas establecidas, el sistema no deberá realizar la modificación y deberá indicar el error correspondiente. 

**Resultado esperado**
La información actual del bien queda actualizada correctamente. Cuando la modificación corresponde a la ubicación, responsable o estado, el cambio anterior permanece disponible dentro del historial del archivo. 

## 2.4 Cambiar ubicación de un bien 
**Actor principal**: Administrador u Operador. 

**Objetivo**: Registrar el traslado de un bien de una ubicación a otra dentro de la organización.

**Precondiciones**: 
- El usuario debe haber iniciado sesión. 
- El usuario debe contar con permisos para modificar la ubicación de bienes. 
- El bien debe encontrarse registrado en el sistema. 
- La nueva ubicación debe existir dentro del catálogo de ubicaciones. 

**Flujo Principal** 
1. El usuario selecciona el bien que será trasladado. 
2. El sistema muestra la ubicación actual del bien. 
3. El usuario selecciona la nueva ubicación. 
4. El usuario registra el motivo del cambio, cuando corresponda. 
5. El sistema valida que la nueva ubicación sea válida. 
6. El sistema actualiza la ubicación actual del bien. 
7. El sistema genera un registro en el historial de movimientos. 
8. El sistema almacena la ubicación anterior y la nueva ubicación. 
9. El sistema registra la fecha del cambio y el usuario que realizó la operación. 
10. El sistema confirma que el traslado fue realizado correctamente. 

**Flujos alternativos** 
- Si el bien no existe, el sistema deberá informar que no se encontró el registro. 
- Si la nueva ubicación no existe, el sistema deberá impedir el cambio. 
- Si el usuario no tiene permisos suficientes, la operación deberá ser rechazada. 

**Información registrada en el historial**: 

| Dato | Descripción |
|---|---|
| Bien | Activo que fue trasladado |
| Ubicación anterior | Lugar donde se encontraba el bien  |
| Nueva Ubicación | Lugar al que fue trasladado |
| Fecha del cambio | Momento en que ocurrió el movimiento |
| Usuario responsable | Persona que realizo la modificación |
| Motivo | Razón del traslado, cuando aplique |

**Resultado esperado** 
El bien queda asociado a su nueva ubicación y el sistema conserva evidencia del movimiento realizado para futuras consultas. 

### 30/09/2026 13:00 - 15:00
## 2.5 Asignación responsable a un bien 
**Actor Principal**: Administrador u Operador.
**Objetivo**: Asignar un bien a una persona responsable de su uso o resguardo 

**Precondiciones**: 
- El usuario debe haber iniciado sesión.
- El usuario debe contar con permisos para realizar asignaciones.
- El bien debe encontrarse registrado en el sistema. 
- La persona responsable debe registrar en el sistema. 

**Flujo principal**
1. El usuario selecciona el bien que desea asignar. 
2. EL sistema muestra la información actual del bien.
3. El usuario selecciona a la persona que quedará como responsable. 
4. El sistema verifica que el responsable seleccionado exista. 
5. El sistema actualiza el responsable actual del bien. 
6. El sistema genera un registro en el historial del activo. 
7. El sistema conserva la información del responsable anterior, cuando exista.
8. El sistema registra al nuevo responsable, la fecha del cambo y el usuario que realizó la operación.
9. El sistema confirma que la asignación fue realizada correctamente. 

**Flujos alternativos** 
- Si el bien ni existe, el sistema deberá informar que no se encontró el registro solicitado.
- Si el responsable seleccionado no existe, el sistema deberá impedir la asignación. 
- Si el usuario no tiene permisos suficientes, la operación deberá ser rechazada.
- Si el bien ya tiene asginado al mismo responsable, el sistema podrá informar que no existe ningún cambio que registrar. 

**Información registrada en el historial**: 
| Dato | Descripción |
|---|---|
| Bien | Activo al que se realizó la asignación |
| Responsable anterior | Persona que tenía anteriormente el bien, cuando exista |
| Nuevo Responsable | Persona que recibe el bien |
| Usuario que realizó la operación | Usuario del sistema que registró el cambio |
| Motivo | Razón de la asignación o cambio, cuando corresponda |

**Resultados esperados**:
El bien queda relacionado con su nuevo responsable y el sistema conserva el cambio dentro del historial para poder consiltar posteriormente quién tuvo el bien bajo su responsabilidad.

## 2.6 Cambiar el estado de un bien 

**Actor principal**: Administrador u Operador.

**Objetivo**: Modificar el estado actual de un bien de acuerdo con su situación dentro de la organización.

**Precondiciones**:
- El usuario debe haber iniciado sesión.
- El usuario debe contar con permisos para modificar el estado de los bienes. 
- El bien debe encontrarse registrado en el sistema. 
- El nuevo estado debe existir dentro de los estados permitidos. 

**Flujo principal** 
1. El usuario selecciona el bien cuyo estado desea modificar. 
2. El sistema muestra el estado actual del bien. 
3. El usuario selecciona el nuevo estado. 
4. El usuario registra el motivo del cambio, cuando corresponda. 
5. El sistema valida que el nuevo estado sea válido. 
6. El sistema verifica que la transición entre el estado actual y el nuevo estado éste permitida. 
7. El sistema actualiza el estado actual del bien. 
8. El sistema genera un registro dentro del historial
9. EL sistema conserva el estado anterior, el nuevo estado, la fecha del cambio y el usuario que realizó la operación. 
10. El sistema confirma que el cambio fue realizado correctamente. 

**Flujos alternativos** 
- Si el bien no existe, el sistema deberá informar que no se encontró el registro solicitado. 
- Si el nuevo estado no es válido, el sistema deberá rechazar la modificación.
- Si la transición entre estados no está permitida, el sistema deberá impedir el cambio e informar le motivo. 
- Si el usuario no cuenta con los permisos necesarios, la operación deberá ser rechazada. 
- Si el nuevo estado es igual al estado actual, el sistema podra indicar que no existe ningun cambio que registrar. 


**Información registrada enm el historial**

| Dato | Descripción |
|---|---|
| Bien | Activo cuyo estado fue modificado |
| Estado anterior | Estado que tenía antes del cambio |
| Nuevo estado| Estado asignado al bien |
| Fecha del cambio | Momento en que se realizó la modificación |
| Usuario que realizó la operación | Usuario que registr´po el cambio |
| Motivo | Razón del cambio, cuando corresponda |

**Resultado esperado** 
El bien queda asociado con su nuevo estado y el sustema conserva el cambio dentro de su historial para permitir la consulta de estados anteriores. 

## 2.7 Registrar una adquisición y relacionarla con bienes 

**Actor principal**: Administrador u Operador.
**Objetivo**: Registrar un adquisición u relacionarla con uno o varios bienes del inventario. 

**Precondiciones:** 
- El usuario debe haber iniciado sesión.
- El usuario debe contar con permisos para registrar adquisiciones. 
- Los bienes que serán relacionados deberán encontrarse registrados en el msistema o ser incorporados como parte del proceso definido posteriormente. 

**Flujo principal** 
1. El usuario seleccionado la opción para registrar una nueva adquisición.
2. El sistema solicita la información correspondiente a la compra. 
3. El usuario captura los datos disponibles de la adquisición.
4. El usuario adjunta los documentos relacionados, cuando correspondan. 
5. El sistema valida la información proporcionada. 
6. El sistema valida los archivos adjuntos de acuerdo con las reglas establecidas. 
7. El sistema registra la adquisición. 
8. El usuario selecciona uno o varios bienes que serán relacionados con la adquisición. 
9. El sistema crea la relación entre la adquisición y los bienes correspondientes.
10. El sistema confirma que la operación fue realizada correctamente. 

**Archivos que podrán relacionarse con la adquisición: 
- Factura.
- Documento PDF.
- Archivo XML. 
- Fotografias.

**Flujos alternativos**
- Si la información de la adquisición no es válida, el sistema deberá impedir el registro e indicar los datos que deben corregirse. 
- Si alguno de los archivos no cunple con las condiciones establecidas, el sistema deberá rechazar dichos archivos. 
- Si uno de los bienes seleccionados no existe, el sistema deberá informar el error correspondiente. 
- Si el usuario no cuenta con permisos suficientes, la operación deberá ser rechazada.

**Resultados esperados**: 
La adquisición queda registrada dentro del sistema y relacionada con los bienes correspondientes, permitiendo posteriormente consultar el origen de compra y la evidencia documental asociado. 


 ### 02/09/2026 9:00 - 14:00


## 2.8 Asociar o general un código QR para un bien. 
**Actor Principal**: Administrador u Operador.

**Objetivo**: Generar o asociar un código QR a un bien que requiera identificación individual.

**Precondiciones**: 
- El usuario debe haber iniciado sesión. 
- El usuario debe contar con permisos para administrar códigos QR.
- El bien debe encontrarse registrado en el sistema. 
- El bien debe ser de un tipo que requiere identificación individual. 

**Flujo principal**: 

1. El usuario selecciona el bien al que desea asignar un código QR. 
2. EL sistema verifica que el bien exista. 
3. El sistema obtiene el identificador único correspondiente al bien. 
4. El sistema genera o asocia un código QR utilizando dichos identificadores.
5. El sistema relaciona el código QR con el bien. 
6. El sistema verifica que el código generado permita localizar correctamente la ficha correspondiente.
7. El sistema guarda la relación entre el bien y el código QR. 
8. El sistema confirma que el QR fue asociado correctamente. 

**Flujo alternativo**: 

- Si el bien no existe, el sistema deberá informar que no se encontró el registro. 
- Si el bien no requiere identificación individual, el sistema podrá impedir la generación del código QR. 
- Si el usuario no cuenta con permisos suficientes, la operación deberá ser rechazada. 
- Si el bien ya cuenta con un código QR asociado, el sistema deberá evitar duplicados o permitor una regeneración controlada cuando sea necesario. 
- Si el código QE se encuentra dañado o deja de ser legible, deberá existir un mecanismo para general nuevamente la etiqueta sin perder la relación con el activo. 

**Consideraciones de seguridad**: 

EL código QR no deberá almacenar directamente la información sensible del bien. Su función principal será proporcionar una referencia que permita al sistema localizar la ficha correspondiente. 

La información visible después de escanear el código dependera de los permisos y reglas de acceso definidos para el sistema. 

**Resultado esperado**: 
El bien queda asociado con un código QR funcional que permite localizar su ficha correspondiente sin depender de que la información actual del activo permanezca sin cambios. 

## 2.9 Consultar un bien mediante código QR 

**Actor principal**: Administrador, Operador o Usuario de consulta. 

**Objetivo**: Localizar y consultar la ficha de un bien a partir de su código QR. 

**Precondiciones**: 

- El bien debe encontrarse registrado en el sistema. 
- El bien debe contar con un código QR asociado. 
- El código QR debe contener una referencia válida que permita localizar el registro correspondiente.

**Flujo principal**: 

1. El usuario escanea el código QR asociado al bien. 
2. El sistema recibe el identificador contenido en el código. 
3. El sistema busca el bien relacionado con dicho identificador. 
4. El sistema verifica que el registro exista. 
5. El sistema aplica las reglas de acceso correspondientes. 
6. El sistema recupera la información permitida del bien. 
7. El sistema muestra la ficha correspondiente al activo. 

**Información que podrá mostrarse**: 

- Identificador del bien. 
- Nombre. 
- Categoría. 
- Marca y modelo. 
- Estado actual. 
- Ubicación actual.
- Responsable actual, cuando los permisos lo permitan. 
- Otra información autorizada de acuerdo con el tipo de usuario. 

**Flujos alternativos** 

- Si el código QR no corresponde a ningún bien registrado, el sistema deberá informar que no se encontró un registro válido. 
- Si el código está dañado y no puede ser leído, deberá utilizarse otro mecanismo de búsqueda mediante el identificador del bien. 
- Si el usuario intenta acceder a información para la que no tiene permisos, el sistema deberá limitar o rechazar el acceso correspondiente. 
- Si el bien no se encuentra activo dentro del inventario, el sistema deberá mostrar su situación de acuerdo con las reglas establecidas. 

**Consideraciones de seguridad**: 
El código deberá utilizarse únicamente como medio de identificación. La lectura del código no deberá otorgar automáticamente acceso a información sensible. 

El sistema será responsable de determinar qué información puede consultar cada usuario de acuerdo con sus permisos. 

**Resultados esperados**

El usuario puede identificar físicamente un bien mediante su código QR y acceder a la ficha conrrespondiente con la información permitida por el sistema. 


### 08/10/2026 9:00 - 14:00

**Correcciones**
**Regla 7. Origen del bien y documentación pendiente**

El sistema deberá permitir registrar un bien aunque no se cuente con su factura o documento de origen. En ese caso, quedará marcado como pendiente de documentación, sin exigir uan relación con una compra o un detalle de adquisición.

Cuando se conozca el origen, se indicará, si corresponde a una compra, donación, transferencia, arrendamiento o préstamo recibido. Si se desconose, se dejará pendiente de identificar. No deberán inventarse compras. proveedores, importantes o documentos para permitir el registro.

Cuando se obtenga el documento, un usuario autorizado podrá incorporarlo y relacionarlo con el bien existente, sin crear otro registro ni modificar su idenficador o código QR. El sistema conservará su historial y registrará quién agregó el respaldo y en qué fecha. 

Por ejemplo, una laptop que ya pertenece al inventario y no tiene factura disponible podrá registrarse con sus datos conocidos. Posteriormente se podrá adjuntar el documento correspondiente al mismo registro. 

**2. Devolver un bien al almacén sin responsable**

**Devolución de un bien al almacén**

Un bien podrá permanecer en almacén sin una persona asignada como responsable. La persona que tiene el bien bajo resguardo es distinta del usuario que registra la operación.

**Flujo de devolución**
1. El usuario selecciona el bien que será devuelto.
2. El sistema muestra su ubicación, responsable y estado actuales.
3. El usuario selecciona el almacén de destino y registra el motivo de la devolución y la condición del bien.
4. El sistema verifica los permisos del usuario y valida la información.
5. El sistema actualiza la ubicación al almacén y deja vacío el responsable actual.
6. Si el bien está en condiciones de utilizarse, queda disponible. Si presenta una falla, queda en revisión.
7. El sistema conserva en el historial el responsable anterior, el nuevo responsable vacío, las ubicaciones y estados anteriores y nuevos, la fecha, el motivo y el usuario que registró la operación.
8. El sistema confirma la devolución cuando todos los cambios y su historial se hayan guardado correctamente.

**Resultados esperados**
El bien queda registrado en el almacén, sin responsable asignado y con el estado correspondiente a su condición. El historial conserva quién lo tenía anteriormente y quién registró la devolución.

Por ejemplo, si Ana devuelve una laptop en buen estado, el equipo queda disponible en almacén y sin responsable actual. Ana permanece registrada como responsable anterior.

**3. Guardar eñ cambio y su historial juntos**

**Consistencia entre la información actual y el historial**

Cada cambio de ubicación, responsable o estado deberá guardarse junto con su historial como una sola operación. Si falla el guardado de cualquiera de sus partes, se cancelará toda la operación y se conservará la información anterior del bien.

No deberá quedar un cambio aplicado sin su historial ni un registro histórico que indique una modificación que no se realizó. El sistema confirmará el éxito únicamente cuando ambas partes se hayan guardado correctamente.

Esta regla deberá cumplirse desde cualquier parte del backend que permita modificar el inventario.

**Modificaciones simultáneas**
Si dos operadores intentan modificar el mismo bien al mismo tiempo, el sistema deberá evitar que uno sobrescriba los cambios del otro sin advertencia.

Antes de guardar, se verificará que la información utilizada para realizar la modificación siga vigente. Si otro usuario ya cambió el bien, se rechazará la operación basada en la información anterior y se solicitará consultar los datos actualizados antes de intentarlo nuevamente.

**Comprobaciones esperadas**

- Una modificación correcta guarda tanto la situación actual como su historial. 
- Si falla el guardado del historial, la situación actual del bien pertenece sin cambios. 
- Si dos operadores modifican el mismo bien, no se pierde por una sobreescritura sin advertencia. 

## 2.10 Consultar el historial de un bien 
**Actor principal**: Administrador, Operador o Usuario de consulta.

**Objetivo**: Consultar los cambios registrados sobre un bien para conocer sus ubicaciones, responsables y estados anteriores. 

**Precondiciones**:
- El usuario debe haber iniciado sesión. 
- El usuario debe contar con permisos para consultar el historial. 
- El bien debe encontrarse registrado en el sistema. 

**Flujo principal**:
1. El usuario busca y selecciona el bien que desea consultar.
2. El sistema verifica que el bien exista y que el usuario tenga los permisos necesarios.
3. El usuario selecciona la consulta del historial.
4. El sistema recupera los cambios registrados sobre el bien.
5. El sistema presenta los movimientos ordenados del más reciente al más antiguo y distribuidos en páginas.
6. El usuario puede filtrar los registros por tipo de movimiento o periodo.
7. El usuario selecciona un movimiento para consultar su detalle.
8. El sistema muestra la información permitida de acuerdo con los permisos del usuario.

**Información que podrá mostrarse:**

| Dato | Descripción |
|---|---|
| Bien | Identificador del bien al que corresponde el movimiento |
| Tipo de movimiento | Cambio de ubicación, asignación, devolución o cambio de estado |
| Fecha y hora | Momento en que se registró la operación |
| Información anterior | Ubicación, responsable o estado previo, segun el movimiento |
|Ubicación nueva | Ubicación, responsable o estado resultante |
| Usuario que registró la operación | Usuario del sistema que realizó el cambio |
| Motivo | Razón registrada para realizar el movimiento, cuando corresponda |

En una devolución al almacén, el nuevo responsable podrá aparecer como “Sin responsable asignado”. Esto no deberá confundirse con el usuario que registró la devolución, cuya identidad deberá conservarse.

**Flujos alternativos**
- Si el bien no existe, el sistema deberá informar que no se encontró el registro solicitado.
- Si el usuario no cuenta con permisos suficientes, el sistema deberá rechazar la consulta.
- Si el bien no tiene movimientos registrados, el sistema deberá informarlo sin tratarlo como un error.
- Si los filtros no encuentran coincidencias, el sistema deberá mostrar un listado vacío e indicar que no existen movimientos con esos criterios.

**Reglas de consultas**: 

La consulta del historial no deberá permitir modificar ni eliminar los movimientos registrados.

Los cambios de ubicación, responsable o estado deberán conservarse aunque posteriormente se realicen nuevas modificaciones sobre el bien.

El historial permanecerá disponible para los usuarios autorizados cuando el bien esté dado de baja.

**Resultado esperado:**
El usuario puede consultar los cambios anteriores del bien y conocer cuándo ocurrieron, qué información cambió y quién registró cada operación, sin modificar la información histórica.

## 2.11 Buscar, filtrar y ordenar bienes.

**Actor principal:** Administrador, Operador o Usuario de consulta.

**Objetivo:** Localizar bienes dentro del inventario mediante búsquedas, filtros y ordenamiento, sin tener que consultar todos los registros al mismo tiempo.

**Precondiciones:**
- El usuario debe haber iniciado sesión.
- El usuario debe contar con permisos para consultar el inventario.

**Flujo principal:**

1. El usuario accede a la consulta del inventario.
2. El sistema verifica sus permisos.
3. El usuario introduce un término de búsqueda o selecciona uno o varios filtros.
4. El sistema valida los criterios proporcionados.
5. El sistema busca los bienes que coincidan con los criterios y que el usuario tenga autorización para consultar.
6. El sistema ordena los resultados según la opción seleccionada. Si no se indica una, utiliza un orden predeterminado y estable.
7. El sistema devuelve una página de resultados e indica cómo consultar las páginas restantes.
8. El usuario puede cambiar los criterios o seleccionar un bien para consultar su ficha.

| Criterio | Uso |
|---|---|
| Identificador del bien | Localizar un bien con seguimiento individual |
| Nombre | Buscar bienes por su nombre |
| Categoría o tipo del bien | Consultar bienes de una clasificación determinada |
| Marca o modelo | Localizar bienes con esas características |
| Numero de serie | Buscar un bien por su número de serie, cuando exista |
| Ubicación actual| Consultar los bienes que se encuentran en un lugar |
| Responsable actual  | Consultar los bienes asignados a una persona |
| Sin Responsable asignado  | Identificar bienes que no tienen una persona asignada |
| Estado Actual | Consultar bienes disponibles, en uso, en revisión o dados de baja |
| Documentación pendiente | Identificar bienes cuyo documento de origen todavía no se ha incorporado |

**Ordenamiento:**

Los resultados podrán ordenarse por identificador, nombre o fecha de registro, de manera ascendente o descendente.

Cuando varios bienes tengan el mismo valor en el campo seleccionado, el sistema utilizará un criterio adicional único para mantener un orden estable.

**Flujos alternativos:**

Si no existen bienes que coincidan con los criterios, el sistema devolverá un listado vacío e informará que no se encontraron resultados.

Si el usuario no proporciona criterios, el sistema devolverá la primera página de los bienes que tenga permiso para consultar.

Si un filtro, campo de ordenamiento o parámetro de paginación no es válido, el sistema rechazará la solicitud e indicará qué debe corregirse.

Si el usuario no cuenta con permisos de consulta, el sistema rechazará la operación.

**Reglas de consulta:**

Los filtros seleccionados deberán aplicarse de forma conjunta. Por ejemplo, al seleccionar una ubicación y un estado, se mostrarán únicamente los bienes que cumplan ambas condiciones.

Los campos que no correspondan a un tipo de bien podrán permanecer vacíos. Un artículo controlado por cantidad no deberá requerir un número de serie individual para aparecer en los resultados.

El sistema establecerá un tamaño predeterminado y un límite máximo de resultados por página. Sus valores se definirán durante el diseño técnico.

Las búsquedas y los filtros deberán respetar los permisos del usuario y no permitir el acceso a información restringida.

Las consultas no deberán modificar los bienes ni su historial.

**Resultado esperado:**

El usuario puede localizar los bienes que necesita mediante resultados ordenados y paginados, consultar su información autorizada y acceder a la ficha de un bien específico.

## 2.12 Incorporar documentos y fotografias a

**Actor principal:** Administrador u Operador

**Objetivo**: Incorporar documentos y fotografias un bien o a su adquisición u otro origen, incluyendo el respaldo que se encuentre pendiente de documentación 

**Precondiciones:**
- El usuario debe haber iniciado sesión.
- El usuario debe contar con permisos para cargar archivos.
- El bien o registro de origen al que se asociará el archivo debe existir.

**Flujo principal:**
1. El usuario selecciona el bien o registro de origen correspondiente.
2. El sistema verifica que el registro exista y que el usuario tenga permisos para incorporar archivos.
3. El usuario selecciona el archivo e indica qué tipo de evidencia representa.
4. El sistema valida su tamaño, extensión, tipo y contenido, de acuerdo con las condiciones permitidas.
5. El sistema genera un nombre interno seguro y almacena el archivo.
6. El sistema relaciona el archivo con el registro seleccionado.
7. El sistema registra el tipo de evidencia, la fecha de carga y el usuario que realizó la operación.
8. Si el archivo completa la documentación de origen pendiente, el sistema verifica que corresponda al bien y actualiza esa condición.
9. El sistema confirma que el archivo quedó almacenado y asociado correctamente.

**Archivos contemplados**
| Archivo | Uso |
|---|---|
| PDF | Facturas y otros documentos de respaldo |
| XML | Archivo electrónico asociado a una factura |
| Fotografía | Evidencia visual del bien o de su documentación |

Las extensiones de imagen permitidas y los tamaños máximos se definirán durante el diseño técnico.

**Flujos alternativos:**
- Si el registro seleccionado no existe, el sistema rechazará la operación.
- Si el usuario no tiene permisos suficientes, el sistema impedirá la carga.
- Si el archivo supera el tamaño permitido o su tipo o contenido no es válido, el sistema lo rechazará e indicará el motivo.
- Si ocurre un error al almacenar el archivo o asociarlo al registro, el sistema informará que la operación no se completó. No deberá conservar una asociación que apunte a un archivo inexistente; si quedó un archivo almacenado sin asociación, deberá eliminarlo o gestionar su limpieza.
- Si el archivo no completa el respaldo de origen requerido, el bien continuará marcado como pendiente de documentación.

**Reglas de seguridad y conservación:**

El sistema no deberá confiar únicamente en la extensión o en el nombre proporcionado por el usuario para aceptar un archivo.

Los documentos y fotografías deberán almacenarse de manera que su consulta respete los permisos del sistema. Conocer la dirección de un archivo o escanear el QR del bien no deberá permitir acceder automáticamente a documentos restringidos.

Agregar un archivo no deberá eliminar ni sobrescribir silenciosamente la evidencia existente.

Una fotografía del equipo no será suficiente por sí sola para retirar la condición de documentación de origen pendiente.

Cuando se incorpore posteriormente un documento de origen, se utilizará el mismo registro del bien y se conservarán su identificador, código QR e historial.

**Resultado esperado:**

El documento o fotografía queda almacenado y relacionado con el registro correspondiente, con información sobre quién lo incorporó y cuándo. Los usuarios autorizados pueden consultarlo y la condición de documentación pendiente se actualiza únicamente cuando se completa el respaldo correspondiente.

## 2.13 Registrar entradas y salidas por cantidad 

**Actor principal:** Administrador u Operador.

**Objetivo:** Registrar entradas y salidas de artículos que se administran por cantidad, manteniendo actualizadas sus existencias y conservando el historial de los movimientos.

**Precondiciones:**

- El usuario debe haber iniciado sesión.
- El usuario debe contar con permisos para registrar movimientos de existencias.
- El artículo debe estar registrado y definido como un artículo controlado por cantidad.
- La ubicación donde se realizará el movimiento debe existir.
- El artículo debe tener definida su unidad de medida.


**Flujo principal:**
1. El usuario selecciona el artículo y la ubicación correspondiente.
2. El sistema muestra la cantidad disponible y su unidad de medida.
3. El usuario selecciona si registrará una entrada o una salida.
4. El usuario captura la cantidad y el motivo del movimiento.
5. El sistema verifica los permisos y valida que la cantidad sea mayor que cero y compatible con la unidad de medida.
6. Si se trata de una salida, el sistema comprueba que exista cantidad suficiente en la ubicación seleccionada.
7. El sistema aumenta las existencias cuando se registra una entrada o las disminuye cuando se registra una salida.
8. En la misma operación, el sistema registra el movimiento con la cantidad anterior, la cantidad del movimiento, la cantidad resultante, la fecha y el usuario que lo realizó.
9. El sistema confirma la operación únicamente cuando las existencias y su historial se hayan guardado correctamente.

**Información registrada en el movimiento**: 
**Archivos contemplados**
| Dato | Descripción |
|---|---|
| Articulo | Bien controlado por cantidad |
| Ubicación | Lugar donde aumentan o disminuyen las existencias |
| Tipo de movimiento | Entrada o salida |
| Cantidad del movimiento | Cantidad que ingresa o se retira |
| Unidad de medida | Unidad utilizada para controlar el artículo |
| Cantidad anterior | Existencias antes de la operación |
| Cantidad resultante |Existencias después de la operación |
| Fecha y hora | Momento en que se registró el movimiento |
| Usuario | Persona que registró la operación en el sistema |
| Motivo | Razón de la entrada o salida |
| Documento de respaldo | Referencia al documento relacionado, cuando esté disponible |

**Flujos alternativos:**

- Si el artículo o la ubicación no existen, el sistema rechazará la operación.
- Si el artículo requiere seguimiento individual, el sistema impedirá utilizar este procedimiento e indicará que debe registrarse mediante el control individual correspondiente.
- Si la cantidad es cero, negativa o incompatible con la unidad de medida, el sistema rechazará el movimiento.
- Si la salida supera las existencias disponibles en la ubicación seleccionada, el sistema impedirá la operación.
- Si el usuario no cuenta con permisos suficientes, el sistema rechazará el movimiento.
- Si otro usuario modifica las existencias después de que fueron consultadas, el sistema rechazará la operación basada en información anterior y solicitará revisar la cantidad actualizada.
- Si falla el guardado de las existencias o del historial, el sistema cancelará toda la operación y conservará la cantidad anterior.

**Reglas de control:**

Las existencias deberán controlarse por artículo y ubicación. Una salida no podrá utilizar automáticamente cantidades disponibles en otra ubicación.

No se permitirán existencias negativas.

Los artículos administrados por unidades completas deberán utilizar cantidades enteras. Cuando se requieran cantidades fraccionarias, estas deberán corresponder a una unidad de medida definida para el artículo.

Cada entrada o salida deberá conservarse como un movimiento consultable. No se deberá modificar directamente la cantidad disponible sin registrar la operación que justifica el cambio.

El control por cantidad no requiere crear un registro ni un historial por cada unidad física. Sin embargo, deberá conservarse el historial de entradas y salidas del artículo.

Los consumibles definidos como serializados deberán seguir el procedimiento de control individual, aunque pertenezcan a una categoría de consumibles.

**Ejemplo:**

Si existen 20 cables en el almacén y un operador registra la salida de 3, el sistema deberá dejar 17 disponibles y conservar el movimiento con las cantidades anterior y resultante.

Si posteriormente se intenta registrar una salida de 18 cables, el sistema deberá rechazarla por falta de existencias.

**Resultado esperado:**

Las existencias del artículo quedan actualizadas en la ubicación correspondiente y cada entrada o salida permanece registrada, permitiendo conocer cuánto había, cuánto se movió, cuánto quedó y quién realizó la operación.

## 2.14 Instalar o retirar un componente

**Actor principal:** Administrador u Operador.

**Objetivo:** Registrar la instalación o el retiro de un componente con seguimiento individual, conservando su relación actual con un equipo y el historial de instalaciones anteriores.

**Precondiciones:**

- El usuario debe haber iniciado sesión.
- El usuario debe contar con permisos para registrar instalaciones y retiros.
- El componente y el equipo deben existir en el inventario.
- El componente debe estar definido para seguimiento individual.
- Para una instalación, el componente no debe encontrarse instalado en otro equipo.
- Para un retiro, debe existir una instalación vigente del componente en el equipo seleccionado.

**Flujo principal para instalar un componente:**
1. El usuario selecciona el componente que desea instalar.
2. El sistema muestra su estado, ubicación y relación actual con algún equipo, cuando exista.
3. El usuario selecciona el equipo de destino y registra el motivo de la instalación.
4. El sistema verifica los permisos y comprueba que el componente esté disponible para instalarse.
5. El sistema valida que el equipo de destino pueda recibir componentes y que los estados de ambos bienes permitan la operación.
6. El sistema registra la relación entre el componente y el equipo, junto con la fecha de instalación.
7. El sistema actualiza la situación del componente para indicar que está instalado y que su ubicación corresponde a la del equipo.
8. En la misma operación, el sistema registra el movimiento en el historial e identifica al usuario que lo realizó.
9. El sistema confirma la instalación cuando todos los cambios se hayan guardado correctamente.



**Flujo para retirar un componente:**

1. El usuario selecciona el equipo y el componente instalado que desea retirar.
2. El sistema verifica que la relación de instalación siga vigente.
3. El usuario registra el motivo del retiro, la ubicación de destino y la condición del componente.
4. El sistema valida los permisos y la información proporcionada.
5. El sistema registra la fecha de retiro y finaliza la relación de instalación, conservándola en el historial.
6. El sistema actualiza la ubicación y el estado del componente. Si puede utilizarse nuevamente, queda disponible; si presenta una falla, queda en revisión.
7. En la misma operación, el sistema registra los datos anteriores y nuevos, la fecha y el usuario que realizó el retiro.
8. El sistema confirma el retiro cuando todos los cambios se hayan guardado correctamente.

**Información registrada en el historial:**
| Dato | Descripción |
|---|---|
| Componente | Identificador del componente instalado o retirado |
| Equipo | Identificador del equipo relacionado |
| Tipo de movimiento | Instalación o retiro |
| Fecha y hora | Momento en que se registró la operación |
| Ubicación anterior y nueva | Ubicaciones del componente antes y después del movimiento |
| Estado anterior y nuevo | Situación del componente antes y después de la operación |
| Usuario | Usuario del sistema que registró el movimiento |
| Motivo | Razón de la instalación o del retiro |

**Flujos alternativos:**

- Si el componente o el equipo no existen, el sistema rechazará la operación.
- Si el componente ya está instalado en otro equipo, el sistema impedirá una nueva instalación hasta que se registre su retiro.
- Si el componente ya está instalado en el equipo seleccionado, el sistema informará que la relación ya existe y no generará otra instalación.
- Si se intenta retirar un componente que no está instalado en el equipo seleccionado, el sistema rechazará la operación.
- Si los estados del componente o del equipo no permiten la operación, el sistema informará el motivo del rechazo.
- Si la ubicación de destino del retiro no existe, el sistema impedirá la operación.
- Si el usuario no tiene permisos suficientes, el sistema rechazará el movimiento.
- Si otro usuario modificó la información después de su consulta, el sistema solicitará revisar los datos actualizados antes de continuar.
- Si falla el guardado de la relación, la situación actual o el historial, el sistema cancelará toda la operación y conservará la información anterior.

**Reglas de relación y trazabilidad:**

Un componente no podrá tener más de una instalación vigente al mismo tiempo.

El sistema deberá impedir que un bien se instale dentro de sí mismo o que se formen relaciones circulares entre bienes.

Retirar un componente no deberá eliminar su registro ni las instalaciones anteriores. Si posteriormente se instala en otro equipo, conservará su identificador y su historial.

Mientras permanezca instalado, la ubicación del componente deberá corresponder a la del equipo que lo contiene. Un traslado del equipo deberá mantener esa coherencia y permitir rastrear el cambio de ubicación del componente.

Este procedimiento corresponde a componentes con seguimiento individual. Las piezas controladas únicamente por cantidad se administrarán mediante sus movimientos de existencias.

El registro de una instalación o retiro no implica implementar un módulo completo de reparaciones o mantenimiento en esta etapa.

**Resultado esperado:**

El sistema permite conocer qué componentes están instalados actualmente en un equipo y consultar dónde estuvo instalado cada componente anteriormente, sin duplicar registros ni perder su historial.