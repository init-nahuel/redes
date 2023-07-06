# DNS

- [DNS](#dns)
  - [¿Cómo saber a qué Name Server hablarle?](#cómo-saber-a-qué-name-server-hablarle)
    - [Tipos de flujos de trafico](#tipos-de-flujos-de-trafico)
  - [Registro DNS](#registro-dns)
    - [Campos de un RR](#campos-de-un-rr)
    - [Tipos de registro DNS](#tipos-de-registro-dns)

## ¿Cómo saber a qué Name Server hablarle?

Los servidores DNS suelen tener varias copias en distintas partes del planeta para disminuir los tiempos de respuesta. La idea es que un cliente intentando resolver un nombre de dominio siempre pueda preguntarle al servidor más cercano. Este tipo de comunicación es bastante diferente al que utiliza el protocolo HTTP, el cual se conecta punto a punto, comunicando a un cliente y un servidor particulares. Esto ocurre porque HTTP utiliza unicast para manejar los flujos de tráfico, mientras DNS utiliza anycast.

### Tipos de flujos de trafico

Lo principales tipos de flujo de tráfico son *unicast, multicast, broadcast y anycast*.

- **Unicast:** En unicast el tráfico es punto a punto, es decir, solo dos puntos se están comunicando entre sí. Si hay únicamente dos puntos que se pueden comunicar a la vez unicast es una buena alternativa, sin embargo en casos con más de dos opciones o participantes este sufre problemas de escalabilidad. El protocolo HTTP tiene un flujo de tráfico unicast.
- **Multicast**: Hablamos de que el tráfico es de tipo multicast cuando el flujo de información puede llegar a varios puntos simultáneamente, es decir, llega a un grupo de receptores dentro de la red. Un ejemplo de uso de multicast corresponde a la televisión IP donde la transmisión es enviada a aquellos clientes que estén suscritos.
- **Broadcast**: En el caso de broadcast tenemos que todos los elementos de la red reciben la información siendo enviada, independiente de si están interesados en dicha información o si les es útil. Esto puede generar envíos de datos innecesarios dentro de la red pues los receptores no interesados recibirán y procesarán la información solo para descubrir que no les interesa. Un ejemplo de uso de broadcast ocurre cuando un computador se conecta a una red, por ejemplo Wi-Fi, y necesita que se le asigne una dirección dentro de la red. Dado que el computador no sabe cuál es el dispositivo encargado de asignar las direcciones, este tendrá que comunicarle a toda la red que necesita que se le asigne una dirección.
- **Anycast**: En anycast se tiene que una misma dirección puede ser accesada a través de múltiples dispositivos, de los cuales se elige uno punto para comunicarse con el cliente. Típicamente anycast utiliza criterios de distancia en red para elegir el dispositivo más cercano al cliente para responder. Este tipo de flujo de tráfico es utilizado por los servidores DNS para disminuir el tiempo de respuesta.

## Registro DNS

Los **Resource Records** o **Registros de Recursos** (**RRs**) corresponden a las unidades de información con la que trabajan los DNS para resolver nombres de dominio. Cada registro contiene el nombre de dominio, dirección IP asociada, tipo, tiempo de vida o Time To Live (TTL), clase, entre otros.

Dentro de los servidores DNS, los RRs se encuentran organizados en **Zone Files** los cuales contienen los RRs asociados a la zona DNS manejada por el servidor. Aquí, una zona DNS corresponde a una porción dentro de la jerarquía del árbol de dominio (usualmente un nodo).

### Campos de un RR

Cada RR contiene la información necesaria para ser utilizada dentro de DNS. Esta información se encuentra almacenada en los siguientes campos:

- **`NAME`**: Nombre de dominio asociado.
- **`TYPE`**: Tipo de registro. Indica el tipo de información contenido en el registro, el cual puede ser una dirección IPv4, un servidor de nombre, una redirección, etc.
- **`CLASS`**: Clase del registro. Para DNS sobre Internet la clase corresponde a `IN` (Internet), sin embargo existen otras clases como `HS` (Hesiod) y `CH` (Chaos).
- **`TTL` (Time to Live)**: Número de segundos durante los cuales el registro es válido.
- **`RDLENGTH` (Record Data Length)**: Largo del segmento RDATA.
- **`RDATA` (Record Data)**: Contiene la información asociada al tipo de registro. Por ejemplo, para un registro tipo A (address), el RDATA contiene la dirección IPv4 asociada al nombre de dominio.

### Tipos de registro DNS

En esta sección vamos listar algunos de los posibles tipos que puede tener un RRs. Esta es una lista acotada y existen muchos otros [tipos de registro](https://en.wikipedia.org/wiki/List_of_DNS_record_types#[1]_Obsolete_record_types).

- **A (Address)**: Usualmente utilizado para mapear direcciones IP de 32 bits (IPv4) a nombres de dominio.
- **AAAA (IPv6 Adress)**: Similar al tipo de registro A, es usualmente utilizado para mapear direcciones IP de 128 bits (IPv6) a nombres de dominio.
- **CNAME (Canonical Name)**: Indica un alias que apunta a otro nombre de dominio o subdominio, pero nunca a una dirección IP.
- **NS (Name Server)**: Indica qué servidores de nombre son autoritativos para un dominio o subdominio.
- **SOA (Start Of [a zone of] Authority)**: Especifica información autoritativa sobre una zona DNS. Dentro de esta información se encuentra especificado cuál es el servidor de nombre primario.
