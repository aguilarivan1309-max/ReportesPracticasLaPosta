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
