1.Levantamiento y comprensión del proyecto 
1.1 Descripción del problema 
El área de tecnología de TI necesita contar con un sistema que permita administrar de manera organizada los bienes relacionados con TI. Actualmente se requiere conocer que bienes existen, donde se encuentran, quien los tiene bajo responsabilidad, cuál es el estado y cuál ha sido su recorrido dentro de la organización.
El sistema deberá permitir registrar y consultar los bienes, relacionados con la información de su adquisición, conservar documentar y fotografías, y facilitar su identificación mediante códigos QR.
Además, deberás conservar un historial de los cambios importantes relacionados sobre los bienes, principalmente los relacionados con su ubicación, responsable y estado 

1.2 Alcance inicial 
En esta primera etapa se desarrollará únicamente el backend del sistema. El backend será construido utilizando Django y Django REST Framework y proporciona una API REST que posteriormente podrá ser utilizada por una interfaz desarrollada en Rest.
El sistema contemplará la administración del inventario, ubicaciones, responsables, estados, adquisiciones, archivos, códigos QR e historial de cambios, además de mecanismos de autenticación, autorización, pruebas y documentación.
La interfaz final en Rest y otros módulos como tickets, incidencias, reparaciones y mantenimientos no forman parte de esta primera etapa


1.3 Actores del sistema 
Para el funcionamiento del sistema del inventario se considera tres tipos de usuarios: 
Administrador 
Es el usuario encargado de administrar el sistema y sus configuraciones principales. Tendrá permisos para registrar, modificar y consultar la información del inventario, así como administrar usuarios y permisos cuando corresponda. 
Operador
Es el usuario encargado de realizar las operaciones cotidianas del inventario. Podrá registrar y actualizar bienes, ubicaciones, responsables y estados, además de consultar la información necesaria para realizar sus actividades. 
Usuario de consulta 
Es el usuario que únicamente necesita consultar información del inventario. Tendrá permisos limitados y no podrá modificar los registros. 

1.4 Permisos y acciones de usuarios
Acción 	                    Administrador 	Operador 	Usuario de consulta 
Iniciar sesión 	                  ✓             ✓                ✓
Consultar bienes 	              ✓             ✓                ✓    
Buscar y filtrar bienes 	      ✓             ✓                ✓
Registrar bienes 	              ✓             ✓                ✕
Modificar bienes 	              ✓             ✓                ✕
Registrar ubicaciones 	          ✓             ✓                ✕
Modificar ubicaciones 	          ✓             ✓                ✕
Registrar responsables	          ✓             ✓                ✕
Modificar responsables 	          ✓             ✓                ✕
Cambiar estado de un bien 	      ✓             ✓                ✕
Registrar adquisiciones 	      ✓             ✓                ✕
Cargar documentos y fotografías   ✓             ✓                ✕
Asociar código QR                 ✓             ✓                ✕ 	
Consultar historial 	          ✓             ✓                ✕
Consultar información mediante QR ✓             ✓                ✕	
Administrar usuarios y permisos   ✓             ✓                ✕	



