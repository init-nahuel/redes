# Capa de enlace de datos

- [Capa de enlace de datos](#capa-de-enlace-de-datos)
  - [Capa de enlace de Datos o Data Link Layer](#capa-de-enlace-de-datos-o-data-link-layer)
  - [Colisiones](#colisiones)
  - [Enlaces](#enlaces)
  - [Elementos de la capa de enlace de datos](#elementos-de-la-capa-de-enlace-de-datos)
  - [Servicios y subcapas de la capa de enlace de datos](#servicios-y-subcapas-de-la-capa-de-enlace-de-datos)
  - [Problema de Acceso Multiple o Multiple Access Problem](#problema-de-acceso-multiple-o-multiple-access-problem)

## Capa de enlace de Datos o Data Link Layer

En la unidad de capa de red vimos que la informacion no va de forma directa de host a host, si no que esta debe pasar por varios routers y enlaces durante su camino. En la capa de red asumimos que la informacion simplemente logra viajar a traves de estos enlaces sin mayores problemas. Sin embargo, estos enlaces son **componentes fisicos** reales como **fibras opticas, ondas electromagneticas, cables de cobre, etc.** *Los componentes fisicos tienen limitaciones* y en el caso de enlaces fisicos, algo tan simple como enviar informacion de forma simultanea puede resultar en perdida de datos por colisision de las ondas enviadas a traves del medio fisico. La capa de enlace de datos es la encargada de manejar el envio de datos a traves de estos enlaces.

**La capa de enlace de datos (o capa de datos) tiene como objetivo manejar el envio de datos a traves de enlaces fisicos, considerando que los datos pueden dañarse o destruirse durante el envio debido a colisiones o problemas del medio de envio.**

## Colisiones

Decimos que ocurre **colision** cuando dos o mas entidades en la capa de datos intentan enviar informacion por un mismo enlace al mismo tiempo.

Al enviar informacion por un enlace fisico, tipicamente lo que se hace es enviar la informacion codificada como ondas (electricas o electromagneticas). Luego, si dos entidades envian informacion de forma simultanea a traves de un enlace, efectivamente tenemos ondas emitidas desde distintos origines viajando a traves del mismo medio, al mismo tiempo. Si estas ondas chocan (ocurre colision), la informacion codificada por estas ondas puede dañarse o destruirse, generando perdidas.

## Enlaces

Debemos notar que no todos los enlaces son compartidos por varias entidades y, por lo tanto, no todos los enlaces vana sufrir colisiones de la misma manera. En particular, hay enlaces que conectan dos puntos entre si y nada mas. De esta forma podemos distinguir los siguientes tipos de enlace.

- **Enlaces punto a punto:** Estos enlaces conectan dos entidades entre si. Un ejemplo de este tipo de enlace corresponde a los cables ethernet.
- **Enlaces de broadcast:** Los enlaces de broadcast pueden ser utilizados por varias entidades. Dentro de este tipo de enlaces encontramos las comunicaciones *wireless* como Wi-Fi o comunicaciones satelitales.

## Elementos de la capa de enlace de datos

Varios elementos participan en el funcionamiento de la capa de enlace de datos. A continuacion mencionaremos algunos de los elementos y terminos principales que participan en esta capa.

- **Frames:** Al enviar datos a traves de la capa de enlace de datos estos deben ser encapsulados usando los *headers* correspondientes.
- **Nodos:** Dentro de la capa de enlace de datos, los nodos se refieren a cualquier equipo que pueda manejar el funcionamiento de esta capa.
- **Enlaces:** Corresponde al medio de comunicacion que conecta nodos adyacentes.
- **Media Access Control Address o MAC Address:** Las MAC address corresponden a las direcciones manejadas dentro de la capa de enlace de datos. A diferencia de las direcciones IP, las MAC address no poseen una estructura jerarquica. Estas direcciones son asignadas directamente a las *tarjetas de red* o *Network Interface Card* (NIC) por su fabricante.
- **Local Area Network (LAN) o red local:** Grupo de equipos que comparte un mismo enlace de comunicaciones.
- **Switches:** Tal como en la capa de red los paquetes deben pasar por routers, en la capa de enlace de datos los frames deben pasar por switches. Los switches pueden recibir y hacer forward de frames a traves de la red local o LAN.

## Servicios y subcapas de la capa de enlace de datos

La capa de datos provee dos servicios principales: **asegurar la integridad de los frames** (en medios pocos confiables) y **manejar el acceso a enlace o Link Access**. Cada uno de estos servicios identifica una subcapa dentro de la capa de datos. La **subcapa de Logical Link Control** se encarga de manejar **asegurar la integridad de los frames**, mientras que la **subcapa de Media Access Control** se encarga del **link access.**

- **Subcapa de Logical Link Control (LLC):** Esta subcapa se encarga de controlar el funcionamiento del enlace y asegurar que los frames lleguen de forma integra. Esta capa se encarga de detectar y corregir errores. Ademas, puede proveer transmision confiable utilizando ACKs de forma similar a TCP. El servicio de transmision confiable se provee **unicamente en medios que lo requieran**, de lo contrario esta responsabilidad se le deja a la capa de transporte.
- **Subcapa de Media Access Control (MAC):** La funcion principal de esta subcapa es manejar el acceso al enlace o el *link access.* Es decir, se encarga de proveer las reglas que determinan el acceso o uso del enlace. En el caso de enlaces punto a punto el manejo del acceso al enlace es relativamente simple. En cambio, en el caso de enlaces o canales de broadcast, donde multiples nodos pueden usar un mismo enlace, el manejo es mas complejo.

## Problema de Acceso Multiple o Multiple Access Problem

La capa de datos se encarga de manejar el acceso al enlace de tal manera que este sea utilizado **sin inducir perdida por colisiones.** En *enlaces punto a punto* el manejo de colisiones es relativamente simple, pues estos enlaces comunican un unico par de nodos. Sin embargo, este problema se vuelve mas complejo cuando un mismo canal es compartido por varios nodos como es el caso de *enlaces de broadcast*. Cuando un enlace es compartido por varios nodos, todos los nodos pueden hacer uso del enlace en cualquier momento. Si los nodos utilizan dicho canal al mismo tiempo, ocurren colisiones. A su vez, estas colisiones resultan en perdida de informacion, **reduciendo la eficiencia de la transmision.**

El problema de cordinar el uso de un canal de comunicacion para enviar yu recibir informacion se conoce como el **problema de acceso multiple**. Para resolverlo es necesario contar con protocolos que regulen el uso del canal.
