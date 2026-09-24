# 1. Levantamiento y comprensión del proyecto

## 1.1 Descripción del problema

El área de tecnología de TI necesita contar con un sistema que permita administrar de manera organizada los bienes relacionados con TI. Actualmente se requiere conocer qué bienes existen, dónde se encuentran, quién los tiene bajo responsabilidad, cuál es el estado y cuál ha sido su recorrido dentro de la organización.

El sistema deberá permitir registrar y consultar los bienes, relacionados con la información de su adquisición, conservar documentos y fotografías, y facilitar su identificación mediante códigos QR.

Además, deberá conservar un historial de los cambios importantes relacionados sobre los bienes, principalmente los relacionados con su ubicación, responsable y estado.

## 1.2 Alcance inicial

En esta primera etapa se desarrollará únicamente el backend del sistema. El backend será construido utilizando Django y Django REST Framework y proporcionará una API REST que posteriormente podrá ser utilizada por una interfaz desarrollada en React.

El sistema contemplará la administración del inventario, ubicaciones, responsables, estados, adquisiciones, archivos, códigos QR e historial de cambios, además de mecanismos de autenticación, autorización, pruebas y documentación.

La interfaz final en React y otros módulos como tickets, incidencias, reparaciones y mantenimientos no forman parte de esta primera etapa.

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






# 13. Preguntas orientadoras para la investigacón 
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
