# Actividad: Construir un proxy

- [Actividad: Construir un proxy](#actividad-construir-un-proxy)
  - [Que es un proxy?](#que-es-un-proxy)
  - [Antes de comenzar](#antes-de-comenzar)
  - [Actividad parte 1](#actividad-parte-1)
  - [Actividad parte 2](#actividad-parte-2)
  - [Pruebas](#pruebas)
  - [Material e indicaciones para la actividad](#material-e-indicaciones-para-la-actividad)

En esta actividad vamos a construir un proxy para filtrar contenido web. Esta actividad se divide en 2 partes para mantener el orden, sin embargo la parte 1 es más corta que la parte 2.

A continuación veremos algunos de los conceptos que necesitaremos saber para realizar esta actividad. Para esta actividad además necesitará del material provisto en el video: HTTP  y el material de la sección Mensajes HTTP.

## Que es un proxy?

Un proxy es cualquier dispositivo intermedio entre un cliente y servidor, comúnmente utilizado para realizar las consultas a nombre del cliente y luego reenviárselas. Un proxy necesita ser capaz de recibir consultas como lo haría un servidor y luego (re)enviarlas como lo haría un cliente. Un ejemplo de uso de proxy es acceder desde sus casas a artículos científicos usando el proxy del DCC. Artículos a los que ustedes no tienen acceso, pero la Universidad sí. Esto funciona pues al utilizar el proxy del DCC para solicitar un artículo a una biblioteca a la cual la Universidad tiene acceso, el proxy del DCC reenvía su petición desde la red del DCC la cual es parte de la red de la Universidad. Luego desde la biblioteca ven que la Universidad está solicitando un artículo y como esta tiene acceso a la biblioteca, le entregan el artículo sin problemas. Finalmente el artículo es recibido por el proxy del DCC quien reenvía el artículo a ustedes en sus casas.

## Antes de comenzar

- **Tipo de socket usado por HTTP:** El protocolo HTTP utiliza sockets orientados a conexión, por lo que los clientes deben invocar a la función `connect` para conectarse al servidor, mientras que los servidores deben llamar a `accept` para aceptar peticiones de clientes.
- **Comando:** El comando `curl` funciona como cliente HTTP para texto permitiéndonos crear de forma fácil y rápida clientes para probar servidores HTTP.  Para esta actividad utilizaremos `curl` con la opción `-I` , la que sirve para traer sólo los headers. También les puede servir la opción `-L` la cual entrega información siguiendo las redirecciones. El detalle de las opciones posibles lo pueden encontrar usando la linea de comando `curl -h`. La opción `-x [dirección]:[puerto]` le permite indicarle a `curl` que use el proxy ubicado en la dirección y puerto especificados.
- **Mensajes HTTP:** Los mensajes HTTP se caracterizan por tener headers HTTP bastante amigables con el humano. La sección de headers se puede ver como un gran string que contiene la información necesaria para establecer la comunicación mediante HTTP. La primera línea de esta sección indica el protocolo HTTP en uso, el estado de la comunicación y el tipo de request si es que hay alguna (GET, POST), mientras que el resto de las líneas contiene un header cada una. Cada header tiene el formato "Nombre-del-header: contenido del header". Cada una de las líneas dentro de la sección de headers está separada por un salto de línea del tipo `\r\n`, y con un doble salto de línea `\r\n\r\n` se marca el fin de la sección de headers y el inicio de la sección de datos.

    Para comunicarse con un browser es necesario que los headers indiquen el `Content-Type` que indica el tipo de datos que lleva el paquete y el `Content-Length` que indica el largo de los datos que lleva el paquete. Para enviar texto plano puede usar `Content-Type: text/html`. Para más información puede visitar [HTTP Headers](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers.)

- **Puerto default HTTP:** En conexiones HTTP, salvo que se indique lo contrario, nos vamos a conectar al puerto 80. De esta forma si un mensaje HTTP no especifica el puerto al que se desea conectar y sólo indica el nombre del host, se asume que la conexión debe hacerse a la dirección `(host, 80)`. Si en cambio el mensaje especifica tanto el nombre del host como un puerto con el formato `host:puerto`, se asume que la conexión debe hacerse a la dirección `(host, puerto)`.  El puerto 80 se encuentra dentro de los llamados puertos reservados, los cuales se reservan para uso del sistema operativo o para protocolos conocidos como lo es el protocolo HTTP.
- **Archivo JSON:** Los archivos JSON nos permiten almacenar e intercambiar datos usando un formato legible para el humano. La sintaxis de archivos JSON es relativamente similar a la sintaxis de diccionarios en Python. Estos archivos nos permiten almacenar datos en archivos .json y consultarlos a través de nuestro código. En la sección [Material e indicaciones para la actividad](#material-e-indicaciones-para-la-actividad) puede encontrar un ejemplo de uso.

## Actividad parte 1

Partiremos creando y probando un servidor HTTP. Para construir su servidor puede usar como código base el ejemplo de comunicación orientada a conexión [server.py](/ejemplos_por_materia/sockets/server_co.py). Recuerde que para que un servidor sea en efecto un servidor HTTP, debe ser capaz de recibir mensajes HTTP, es decir, debe ser capaz de leer e interpretar headers HTTP. Veamos los pasos:

1. Primero encárguese de que su servidor pueda leer, interpretar y crear mensajes HTTP. Para ello cree una función que tome un mensaje HTTP y lo transfiera a una estructura de datos (la que prefiera), y una función que sea capaz de tomar dicha estructura de datos y la convierta en un mensaje HTTP.

    **Test**: Cree un socket servidor en el puerto 8000. Utilice su navegador para obtener un 'request' y use dicho request para probar que las funciones que acaba de programar funcionen como corresponde. Para obtener la request intente acceder a  `http://localhost:[puerto_server_http]` y haga que su código imprima en pantalla el mensaje recibido. Note que si no le entrega una respuesta a su navegador este no va a mostrar nada.

2. Use lo anterior para construir un servidor HTTP que responda peticiones `GET` y córralo localmente en el puerto 8000. Para responder la petición cree un pequeño HTML de prueba. Cuando usted abra el browser con la URI `http://localhost:8000` éste debe mostrar un mensaje de bienvenida.

    **Test**: Utilice su navegador para ver que su mensaje de respuesta se muestra bien. Para crear el HEAD y BODY de su respuesta puede utilizar como ejemplo lo entregado por otras páginas. Puede serle util usar `curl` con el dominio `example.com` como se muestra a continuación.

    ```bash
    $ curl example.com -i
    ```

3. Modifique su servidor para que al momento de responder le agregue el header `X-ElQuePregunta` con su nombre como valor.

    **Test**: pruebe que se agrega de forma correcta el header utilizando `curl` como se muestra a continuación.

    ```bash
    $ curl localhost:[puerto_server_http] -i
    ```

4. Modifique su servidor para que pueda leer archivos JSON o archivos de configuración. Haga que el nombre y ubicación del archivo JSON pueda ser recibido como argumento al ejecutar su código. Estos archivos serán necesarios más adelante para darle ciertas instrucciones a nuestro servidor. Por mientras úselo para dejar en una variable su nombre, así el servidor quedará con usuario parametrizable. Puede encontrar un ejemplo de uso de JSON en la sección [Material e indicaciones para la actividad](#material-e-indicaciones-para-la-actividad).

    **Test**: Pruebe que su servidor puede tomar su nombre desde su archivo JSON y lo puede utilizar para añadir el header `X-ElQuePregunta`.

## Actividad parte 2

Ahora que ya tenemos listo nuestro servidor HTTP vamos a modificarlo para convertirlo en un proxy. Nuestro proxy tendrá dos funcionalidades principales:

- **Bloquear tráfico hacia páginas no permitidas** (como un control parental)
- **Reemplazar contenido inadecuado** (reemplazo el  string A  con el  string B)

Para ello siga los siguientes pasos:

1. Modifique su servidor para que sea un proxy que esté entre un cliente y un servidor, pero que no modifique el mensaje, esto es: recibe un requerimiento, se lo envía al servidor, recibe la respuesta y se la envía al cliente. Note que para lograr esto necesitará poder comunicarse con el cliente y el servidor al mismo tiempo.

    **Test**: Use `curl` para ver que su proxy logra transferir mensajes de forma exitosa. Para ello verifique que pedir la página `example.com` con `curl` sin usar proxy, entrega lo mismo que al usar `curl` con su código como proxy.

    ```bash
    %%% peticion sin proxy:
    $ curl example.com
    %%% peticion con proxy:
    $ curl example.com -x localhost:8000
    ```

2. Modifique su proxy para que al recibir la URI (protocolo + dirección; por ejemplo `http://www.example.com)`  del servidor, chequee si la dirección está bloqueada. De ser así devuelva el código de error 403 y el mensaje de error de su preferencia (por ejemplo: “Forbidden”, o “El proxy no te lo permite”, o “Nope”). Para saber qué direcciones están bloqueadas utilice el archivo JSON de la sección [Material e indicaciones para la actividad](#material-e-indicaciones-para-la-actividad).

    **Test:** Utilizando su proxy con `curl` intente acceder a una página prohibida y verifique que este retorna error 403. Verifique que al ingresar a páginas que no están prohibidas, como `cc4303.bachmann.cl`, su código sigue funcionando como antes.

3. En caso de que la dirección del servidor final no sea una dirección prohibida, agregue a la request que va desde el proxy al servidor el header `X-ElQuePregunta` con su nombre.

    **Test**: Utilizando `curl`, pruebe acceder al dominio cc4303.bachmann.cl a través de su proxy y verifique que el mensaje de bienvenida mostrado por la página cambia al pasar por su proxy, versus el mensaje mostrado al usar curl sin pasar por su proxy.

4. Configure su proxy para que reemplace contenido inadecuado. Para esto busque las palabras prohibidas (marcado como `forbidden_words` en el JSON mostrado en la sección [Material e indicaciones para la actividad](#material-e-indicaciones-para-la-actividad)) y reemplace dichas palabras (reemplazo el string A con el string B).

    **Test**: Utilizando `curl` pruebe acceder a `cc4303.bachmann.cl/replace` a través de su proxy y verifique que las palabras son reemplazadas y que no hay errores en el contenido.

5. Finalmente modifique su código para que pueda recibir mensajes utilizando sockets cuyo buffer de recepción sea más pequeño que el tamaño del mensaje a recibir. Para ello puede usar/modificar las funciones provistas en los códigos de ejemplo de la semana 1 ([sockets](/ejemplos_por_materia/sockets/)). Para implementar esta parte deberá responder las siguientes preguntas ¿Cómo sé si llegó el mensaje completo? ¿Qué pasa si los headers no caben en mi buffer? ¿Cómo sé que el HEAD llegó completo?¿Y el BODY?

    **Test**: Pruebe que su proxy sigue funcionando cuando el tamaño del buffer de recepción es pequeño (ejemplo: `recv_buffer = 50`)

## Pruebas

Para probar el proxy recién implementado utilizaremos `http://localhost:8000` como proxy del sistema de forma de que podamos probarlo utilizando un browser. Antes de configurar el proxy verifique que puede ver correctamente los siguientes sitios a través de su browser:

- Usted puede ver el sitio [http://cc4303.bachmann.cl/](http://cc4303.bachmann.cl/)
- Usted puede ver el sitio [http://cc4303.bachmann.cl/replace](http://cc4303.bachmann.cl/replace)
- Usted puede ver el sitio [http://cc4303.bachmann.cl/secret](http://cc4303.bachmann.cl/secret)

Una vez haya confirmado que dichos sitios se muestran sin problemas configure su proxy para utilizarlo a través de su browser y proceda a hacer las pruebas. Para configurar el proxy puede seguir estas instrucciones [https://es.ccm.net/faq/25993-como-configurar-un-proxy-en-tu-navegador-web](https://es.ccm.net/faq/25993-como-configurar-un-proxy-en-tu-navegador-web)

Pruebe que su código es capaz de hacer lo siguiente al probarlo con el browser:

- Verifique que ya NO puede ver el sitio [http://cc4303.bachmann.cl/secret](http://cc4303.bachmann.cl/secret), si no que recibe un error 403.
- Verifique que al acceder al sitio [http://cc4303.bachmann.cl/](http://cc4303.bachmann.cl/) el contenido de este se modifica según los cambios introducidos al área de headers.
- Verifique que puede ver los sitios [http://cc4303.bachmann.cl/](http://cc4303.bachmann.cl/) y [http://cc4303.bachmann.cl/replace](http://cc4303.bachmann.cl/replace), pero las palabras prohibidas han sido modificadas. Verifique que el texto mostrado sea el mismo solo que con las palabras prohibidas censuradas.
- Cree una función que le permita manejar el caso en que el tamaño del mensaje es menor que el tamaño del buffer. Luego cambie el tamaño de buffer de recepción de su código para que este sea más pequeño (puede utilizar `buff_size = 40`) y verifique que su código puede recibir correctamente mensajes HTTP incluso si el mensaje es de un tamaño mayor al tamaño del buffer.

## Material e indicaciones para la actividad

- **Ejemplo JSON**: En el siguiente ejemplo vemos cómo calcular la cantidad total de artículos de oficina en un inventario. Para ello tenemos el archivo `inventario.json`:

```json
{
"oficina": [
    {
    "nombre": "lapiz_pasta",
    "cantidad_total": 10,
    "colores": ["rojo","negro","azul"],
    "rojo": 2,
    "azul": 5,
    "negro": 3

    },
    {
    "nombre": "lapiz_mina",
    "cantidad_total": 5,
    "colores": ["grafito"],
    "grafito": 5
    }
]
}
```

Usando el archivo `inventario.json` podemos calcular la cantidad total de artículos de oficina usando el siguiente código en Python ¿Cómo modificarían este código para que entregue sólo la cantidad de lápices de colores?

```python
import json

# abrimos el archivo del inventario
with open("inventario.json") as file:
    # usamos json para manejar los datos
    data = json.load(file)
    # calculamos la cantidad total de artículos de oficina en el inventario
    total_articulos_de_oficina = 0
    for articulo in data['oficina']:
        cantidad_articulo = articulo['cantidad_total']
        total_articulos_de_oficina += cantidad_articulo

# imprimimos un mensaje indicando la cantidad total de artículos de oficina
print("Hay un total de " + str(total_articulos_de_oficina) + " de artículos de oficina")
```

- **Probar proxy con `curl`**: Puede realizar las pruebas iniciales de su proxy usando el comando `curl` con el flag `-x` para indicar el uso de proxy de la siguiente manera:

```bash
$ curl [domain] -x localhost:8000
```

- **JSON páginas bloqueadas y palabras prohibidas**: Las páginas bloqueadas y las palabras prohibidas puede encontrarlas en el siguiente JSON:

```json
{ 
  "user": "--su email--",
  "blocked": ["http://www.dcc.uchile.cl/", "http://cc4303.bachmann.cl/secret"],
  "forbidden_words": [{"proxy": "[REDACTED]"}, {"DCC": "[FORBIDDEN]"}, {"biblioteca": "[???]"}]
}
```

- Note que su proxy debe funcionar con páginas HTTP, pero es perfectamente posible que no funcione para HTTPS (http secure). Las páginas [http://www.example.cl](http://www.example.cl) y [http://cc4303.bachmann.cl](http://cc4303.bachmann.cl) se comunican a través de http y puede usarlas para probar su proxy.
