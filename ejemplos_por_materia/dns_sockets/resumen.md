# DNS programado con sockets

Antes de comenzar es importante mencionar que para comunicarse con servidores DNS se deben usar **sockets no orientados a conexion, adicionalmente mencionar que el flujo de trafico de DNS es anycast**.

Todos los mensajes de DNS utilizan el mismo formato:

```bash
+---------------------+
|        Header       |
+---------------------+
|       Question      | dominio a consultar
+---------------------+
|        Answer       | Resource Records (RRs) respondiendo la pregunta que haremos
+---------------------+
|      Authority      | RRs que corresponden a una respuesta autorizada
+---------------------+
|      Additional     | RRs con información adicional
+---------------------+
```

Debemos notar que el campo *Additional* no siempre se llena. Un ejemplo en que dicho campo es utilizado es en el caso en que la raiz que sabe cual es el NS de .cl y, aprovechando que lo conoce, nos dice cual es su nombre y su IP. **Sin embargo, como es un servidor que esta bajo .cl esta no es una respuesta autorizada**.

En los campos vemos que hay un area de *Question* y uno de *Answer*. Estos campos seran utilizados por los mensajes de pregunta o *Query* y de respuesta o *Response*, los cuales llenaran distintas partes del mensaje. En particular, **las preguntas o *Queries* son las encargadas de llenar el *Header*.**

## Query: Header

El encabezado o *Header* de un mensaje DNS tiene el formato que vemos a continuacion. **Aqui cada columna que se ve en el diagramma corresponde a un bit, por lo tando cada linea del *Header* puede contener 16 bits.**

```bash
 0  1  2  3  4  5  6  7  8  9  A  B  C  D  E  F
+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
|                      ID                       |
+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
|QR|   Opcode  |AA|TC|RD|RA|   Z    |   RCODE   |
+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
|                    QDCOUNT                    |
+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
|                    ANCOUNT                    |
+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
|                    NSCOUNT                    |
+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
|                    ARCOUNT                    |
+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
```

Esta division en 16 columnas esta hecha para facilitar la lectura humana del encabezado, sin embargo lo que se observa finalmente es una cadena de 16 bits por cada una de las lineas del diagrama. Los bits que no son relevantes a la consulta (pero si para la respuesta) se inicializan con el valor 0. Los campos que nos interesaran son:

* **ID:** Corresponde a un numero identificador aleatorio de 16 bits. Este mismo **ID** es usado en la respuesta para saber a que pregunta corresponde. Para el ejemplo de mas adelante se utiliza como **ID** el valor 0.
* **QR:** Este bit señala si el mensaje es una **pregunta (valor 0)** o una **respuesta (valor 1)**.
* **OPcode:** El **OPcode** corresponde a 4 bits que especifican el tipo de consulta. En nuestro caso solo haremos **consultas estandar, por lo que el OPcode sera 0000.**
* **TC:** Este bit nos señala si el mensaje esta truncado (i.r es parte de un mensaje mas largo). Nosotros enviaremos mensajes cortos, por lo que nuestro **TC** sera 0.
* **RD:** Este bit le indica al receptor si queremos usar o no recursion. Aqui recursion se refiere a que le pasamos la responsabilidad al receptor para que haga todas las consultas pertinentes. En nuestro caso **RD** sera 0.
* **QDCOUNT:** Corresponde a un **unsigned integer** de 16 bits que señala el numero de consultas que estamos enviando (se puede enviar mas de una). En nuestro caso usaremos una por lo que **QDCOUNT** tomara el valor 1.

**Como cada linea del encabezado contiene exactamente 16 bits, podemos expresar sus valores usando hexadecimal para facilitar su lectura.** Considerando los valores que acabamos de asignar, nuestro encabezado en hexadecimal se veria asi:

```bash
+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
|                    00 00                      | -> ID
+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
|                    00 00                      | -> QR|   Opcode  |AA|TC|RD|RA|   Z    |   RCODE  
+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
|                    00 01                      | -> QDCOUNT
+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
|                    00 00                      | -> ANCOUNT
+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
|                    00 00                      | -> NSCOUNT
+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
|                    00 00                      | -> ARCOUNT
+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
```

## Query data: Question

La seccion de consulta o *Question* tiene el siguiente formato:

```bash
 0  1  2  3  4  5  6  7  8  9  A  B  C  D  E  F
+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
|                                               |
/                     QNAME                     /
/                                               /
+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
|                     QTYPE                     |
+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
|                     QCLASS                    |
+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
```

* **QNAME:** Este campo contiene el dominio por el que pregunto, por ejemplo: `example.com.` (notar que siempre lleva un punto final por el arbol de dominio). Este campo puede tener las lineas que sean necesarias para escribir el dominio. En cada linea caben 16 bits, por lo tanto en cada linea podemos escribir 2 bytes. Luego **para codificar el dominio vamos a seguir los siguientes pasos:**
  * Pasamos cada palabra del dominio a minusculas. En este caso quedaria como `example.com.`
  * Agrupamos las cadenas de caracteres omitiendo los puntos y calculamos su largo. En este caso obtenemos las cadenas `example` de largo 7 y `com` de largo 3.
  * Pasamos cada letra o simbolo a su valor de byte en ASCII. Para el ejemplo tenemos que los valores ASCII en bytes de las letras son: a = 01100001, c = 01100011, e = 01100101, l = 01101100, m = 01101101, p = 01110000, o = 01101111 , x = 01111000 .
  * Escribimos cada cadena en lineas de 2 bytes indicando primero el largo de la cadena de simbolos. Repetimos esto para todas las cadenas. En este ejemplo usaremos una librearia para pasar de hexadecimal a binario, por lo que escribiremos cada elemento en hexadecimal. Para nuestro ejemplo obtenemos:
  
    ```bash
    +---+---+    +----------+----------+
    | 7 | e | -> | 00000111 | 01100101 | = 07 65 (hex)
    +---+---+    +----------+----------+
    | x | a | -> | 01111000 | 01100001 | = 78 61 (hex)
    +---+---+    +----------+----------+
    | m | p | -> | 01101101 | 01110000 | = 6D 70 (hex)
    +---+---+    +----------+----------+
    | l | e | -> | 01101100 | 01100101 | = 6C 65 (hex)
    +---+---+    +----------+----------+
    | 3 | c | -> | 00000011 | 01100011 | = 03 63 (hex)
    +---+---+    +----------+----------+
    | o | m | -> | 01101111 | 0110110  | = 6F 6D (hex)
    +---+---+    +----------+----------+
    ```

  * Finalmente indicamos el final de QNAME con el byte 0  (hexadecimal 00).

* **QTYPE:** Indica el tipo de consulta que estamos haciendo. Si consultamos direcciones IP el valor de QTYPE es 1. Si quisieramos preguntar solo por el NameServer (NS) entonces QTYPE es 2.
* **QCLASS:** Corresponde a la clase que buscamos. Generalmente la clase es tipo IN (Internet) por lo que su valor sera 1.

En nuestro caso, pasando todo nuevamente a hexadecimal, obtendriamos la siguiente seccion de consulta:

```bash
+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
|                     07 65                     | -> QNAME
/                     78 61                     /
/                     6D 70                     /
/                     6C 65                     /
/                     03 63                     /
/                     6F 6D                     /
/                     00                        /
+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
|                     00 01                     | -> QTYPE
+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
|                     00 01                     | -> QCLASS
+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
```

---

## Envio del mensaje

Al igual que los servidores HTTP, **los servidores DNS ocupan un puerto reservado, en este caso este corresponde al puerto 53**. Para enviar nuestro mensaje DNS podemos usar directamente hexadecimal, o utilizar librerias como `dnslib`. A continuacion veremos un ejemplo usando la libreria `binascii` de Python para pasar de hexadecimal a binario y viceversa, y un ejemplo utilizando `dnslib`.

### Libreria `binascii`

```python
import binascii
import socket

def send_dns_message(address, port):
    # Encabezado con ID 0 (00 00 en hexadecimal), preguntamos por example.com
    header = "00 00 00 00 00 01 00 00 00 00 00 00 ".replace(" ", "")
    data = "07 65 78 61 6D 70 6C 65 03 63 6F 6D 00 00 01 00 01".replace(" ","")
    message = header + data
    server_address = (address, port)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Usamos binascii para pasar el mensaje al formato apropiado
        binascii_msg = binascii.unhexlify(message)
        # y lo enviamos
        sock.sendto(binascii_msg, server_address)
        # En data quedara la respuesta a nuestra consulta
        data, _ = sock.recvfrom(4096)
    finally:
        sock.close()
    # OBS: Los datos de la respuesta van en hexadecimal, no en binario
    return binascii.hexlify(data).decode('utf-8')

print(send_dns_message('8.8.8.8', 53))
```

### Libreria `dnslib`

```python
import socket
from dnslib import DNSRecord

def send_dns_message(address, port):
    # Aca ya no tenemos que crear el encabezado porque dnslib lo hace por nosotros, por default pregunta por el tipo A
    qname = "example.com"
    q = DNSRecord.question(qname)
    server_address = (address, port)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Lo enviamos, hacemos cast a bytes de lo que resulte de la funcion pack() sobre el mensaje
        sock.sendto(bytes(q.pack()), server_address)
        # En data quedara la respuesta a nuestra consulta
        data, _ = sock.recvfrom(4096)
        # Le pedimos a dnslib que haga el trabjao de parsing por nosotros
        d = DNSRecord.parse(data)
    finally:
        sock.close()
    # OBS: Los datos de la respuesta van en una estructura de datos
    return d

# Es dnslib la que sabe como se debe imprimir la estructura, usa el mismo formato que dig, los datos
# NO vienen en un string gigante, sino en una estructura de datos
print(send_dns_message('8.8.8.8', 53))
```

**En ambos casos la direccion `8.8.8.8` corresponde al resolver de google.**

---

## Response: Header

La respuesta empieza con un Header similar al caso de la Query. En la respuesta algunos campos del Header pueden tener valores distintos a los que tenia el Header de pregunta. Para nuestro caso recibiriamos:

```bash
+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
|                    00 00                      | -> Mismo ID
+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
|                    80 80                      | -> Distintos bits (lo veremos más adelante)
+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
|                    00 01                      | -> 1 consulta
+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
|                    00 01                      | -> 1 respuesta
+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
|                    00 00                      | -> No authority records
+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
|                    00 00                      | -> No additional records
+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
```

Si pasamos `80 80` a binario obtenemos `10000000 10000000`. De esta forma vemos los siguientes valores en el header:

```bash
 0  1  2  3  4  5  6  7  8  9  A  B  C  D  E  F
+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
|QR|   Opcode  |AA|TC|RD|RA|   Z    |   RCODE   |
+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
                       ↓
 0  1  2  3  4  5  6  7  8  9  A  B  C  D  E  F
+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
| 1| 0  0  0  0| 0| 0| 0| 1| 0  0  0  0  0| 0  0|
+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
```

Nos queda:

* **QR = 1 :** Este mensaje es una respuesta.
* **AA = 0 :** Este servidor no es una autoridad para el dominio `example.com`
* **RD = 0 :** No pedimos recursions.
* **RA = 1 :** Quien nos responde indica que si acepta preguntas recursivas (aunque no le hayamos pedido recursion).
* **RCODE = 0 :** No hubo error.

## Response data: Question

En la respuesta esta seccion es la misma del mensaje enviado:

```bash
+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
|                     07 65                     | -> QNAME
/                     78 61                     /
/                     6D 70                     /
/                     6C 65                     /
/                     03 63                     /
/                     6F 6D                     /
/                     00                        /
+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
|                     00 01                     | -> QTYPE
+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
|                     00 01                     | -> QCLASS
+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
```

## Response data: Answer

La respuesta o *Answer* es una lista de *Resource Records* (RRs). Los RRs corresponden a las unidades de informacion con la que trabajan los DNS para resolver nombres de dominio. Veamos el formato de un RR:

```bash
 0  1  2  3  4  5  6  7  8  9  A  B  C  D  E  F
+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
|                                               |
/                                               /
/                      NAME                     /
|                                               |
+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
|                      TYPE                     |
+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
|                     CLASS                     |
+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
|                      TTL                      |
|                                               |
+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
|                   RDLENGTH                    |
+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--|
/                     RDATA                     /
/                                               /
+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
```

La respuesta que recibimos de nuestro ejemplo es:

```bash
+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
|                     C0 0C                     | -> NAME
+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
|                     00 01                     | -> TYPE
+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
|                     00 01                     | -> CLASS
+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
|                     00 00                     | -> TTL
|                     18 4C                     |
+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
|                     00 04                     | -> RDLENGTH (4 bytes)
+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--|
/                     5D B8                     / -> RDDTA
/                     D8 22                     /
+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
```

* **NAME:** Indica la URL que corresponde a la direccion IP que estamos respondiendo. Usa un formato comprimido para decirnos a quien nos referimos (recordar que se podian hacer varias consultas):

    ```bash
    0  1  2  3  4  5  6  7  8  9  A  B  C  D  E  F
    +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
    | 1  1|                OFFSET                   |
    +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
    ```

    En este caso, los primeros dos bits valen 1 y los siguientes 14 contienen un *unsigned integer* que indica los bytes de *offset* desde el principio del mensaje para encontrar el nombre. En nuestro caso ese valor es `c0 0c`, lo cual en binario corresponde a:

    ```bash
                        +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
    1100 0000 0000 1100 -> | 1  1| 0  0  0  0  0  0  0  0  0  0  1  1  0  0| 
                        +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+

                                    => OFFSET = 1100 = 12 (decimal)
    ```

    Eso significa que el offset es de 12 bytes. Si contamos 12 bytes desde el inicio del mensaje llegamos al byte 07 que es el primer de `example.com.` en QNAME.
* **TYPE & CLASS:** Mismo esquema que QTYPE y QCLASS. Son los mismos valores.
* **TTL:** Un *unsigned integer* de 32 bits que nos dice por cuantos segundos mas esta respuesta debiese considerarse valida (antes que el NameServer decida actualizarla). Si es valida se puede guardar en cache, sino no se debe guardar y debe ser descartada.
* **RDLENGTH:** Corresponde al largo en bytes de la seccion RDATA. En nuuestro caso es 4
* **RDATA:** Muestra los datos que buscamnos. En nuestro ejemplo `5D B8 D8 22` corresponden a los bytes de la direccion IP `93.184.216.34`.