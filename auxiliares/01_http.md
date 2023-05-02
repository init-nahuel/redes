# HTTP

## Conceptos

* **Conexiones Persistentes:** Se reutiliza un socket de conexion para enviar varios datos entre el origen y el destino.
* **Conexion No Persistente:** Se cierra una vez finalizada.
* **`connection`:** Header para indicar que tipo de conexion a utilizar. Sus valores son `keep-alive` para persisente, `closed` para no persistente.
* **Round-Trip Timer (RTT):** Tiempo en milisegundos de cuanto se demora una solicitud en ir de origen a destino, y luego de vuelta al origen.

## P1. Servidores HTTP

**1. Suponga que un web server corre en el host C en el puerto 80, este server usa conexiones persistentes y esta recibiendo request de dos hosts diferentes A y B. Se procesan todas las request en el mismo socket de C? Si se pasan a sockets distintos, tienen ambos sockets el puerto 80? Explique.**

Los sockets se definen de acuerdo a la siguiente tupla: `(IP origen, Puerto origen, IP destino, Puerto destino)`. Por cada conexion persistente, el web server crea un socket de conexion distinto pues esta tupla es distinta. De acuerdo a esto se tiene que tanto A como B se comunican con C a traves de distintos sockets (IP de origen distinta), **pero ambos tienen como puerto de destino el puerto 80**.

## P2. Conexion Persistente

**1. Considere que establecer conexion en un socket orientado a conexion se demora 3RTT y cerrar dicha conexion se demora 2RTT. Suponga una pagina HTML referencia 8 pequenhos objetos en el mismo server. Asumiendo que el tiempo de descarga de los objetos es despreciable y que no se pueden establecer conexiones paralelas. ¿Cuanto tiempo toma descargar la pagina si:**

* **se usan conexiones no persistentes?**

    Suponiendo que cada objeto hace una conexion TCP y la cierra, tenemos 3+2RTT por objeto.

* **se usan conexiones persistentes?**

    Si la conexion es persistente, solo hay que abrirla una vez por tanto 3RTT del handshake inicial.

## P3. Sockets

**1. Que datos basicos necesita un socket orientado a conexion y cuales necesita uno no orientado a conexion para mandar cosas?**

Orientado a conexion: necesita saber entre que direcciones (origen y destino) ocurre la comunicacion. No orientado a conexion: necesita saber la direccion de destino.

**2. Cual es la gran diferencia entre un socket orientado a conexion y uno no orientado a conexion?**

Un socket orientado a conexion establece un canal de comunicacion, mientras que un socket no orientado a conexion no.

**3. Como funcionan los sockets no orientados a conexion? Por que alguien los preferiria?**

Los sockets no orientados a conexion mandan los datos a su direccion sin verificar si llegaron o no (no se asegura en el envio completo de los mensajes). Son preferibles en situaciones donde la rapidez con que llega la informacion es mas relevante que perder un poco de informacion (como en zoom por ejemplo).

## P4. HTTP

**1. De que forma viene la informacion en un mensaje HTTP?**

Viene en texto plano. Primero viene el HEAD que tiene como primera linea el `start-line` y luego los headers. El fin de los headers se marca con un doble salto de linea debajo del cual se encuentra el BODY.

**2. Si un agente malicioso bloquea el puerto 80 de su PC, podra visitar paginas web?**

Si, porque el puerto 80 esta reservado para servidores HTTP (no clientes).

**3. Que ocurre si envio un mensaje HTTP sin el doble salto de linea `\r\n\r\n` que separa el HEAD del BODY?**

En ese caso, quien recibe el mensaje cree que todo lo que le llego son headers y puede quedarse pegado esperando el fin del area de headers.

## P5. Verdadero y Falso

**1. HTTP es un lenguaje de marcado y HTML es un protocolo de comunicacion.** *R: Falso, es al reves*.

**2. El HTTP response (la respuesta) se compone de headers o datos, no ambos.** *R: Falso, la respuesta contiene tanto headers, que contiene los metadatos e informacion necesaria sobre el mensaje, y los datos o BODY, que son los datos que se quieren enviar.*

**3. El protocolo HTTP no guarda informacion de la conexion, para eso se usan los headers/cookies.** *R: Verdadero, el protocolo no tiene forma de guardar ningun tipo de informacion, por lo que se le solicita al cliente que lo haga, en forma de cookies.*

**4. El protocolo HTTP utiliza comunicacion no orientada a conexion, para evitar delays innecesarions.** *R: Falso, HTTP utiliza comunicacion orientada a conexion. Es importante que llegue toda la informacion y que llegue ordenada, para que asi el cliente la pueda procesar correctamente.*

**5. Un servidor HTTP puede recibir una request y antes de responder, puede hacer consultas a otros servidores, formando una cadena de preguntas y respuestas.** *R: Verdadero, puede que un servidor no tenga todos los elementos solicitados, por ejemplo una imagen, un css, un javascript, etc, teniendo que solicitarlos a otros servidores.*

**6. Los headers siguen un orden determinado, por ejemplo `Content-Type` siempre viene antes que `Content-Length`.** *R: Falso, pueden estar en cualquier orden y es tarea del cliente el saber leerlos.*

**7. El header `Content-Length` indica el largo del mensaje HTTP, incluyendo los headers.** *R: Falso, indica el largo del area BODY de la respuesta.*

**8. En caso de recibir de forma incompleta el BODY, puedo volver a hacer `receive()`.** *R: Verdadero, en caso de que el largo del BODY leido sea menor que el indicado por `Content-Length` se hace un nuevo request hasta obtener todo el mensaje.*

**9. Usando mensajes HTTP puedo recibir tanto texto plano como imagenes.** *R: Verdadero, el protocolo sirve para enviar diversos tipos de contenido.*
