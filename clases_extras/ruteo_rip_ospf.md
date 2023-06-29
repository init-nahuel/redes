# Protocolos de ruteo interno: RIP y OSPF

- [Protocolos de ruteo interno: RIP y OSPF](#protocolos-de-ruteo-interno-rip-y-ospf)
  - [Tipos de protocolos de ruteo](#tipos-de-protocolos-de-ruteo)
  - [Routing Information Protocolo (RIP)](#routing-information-protocolo-rip)
    - [Generacion de tablas de ruta](#generacion-de-tablas-de-ruta)
    - [Versiones de RIP](#versiones-de-rip)
  - [Open Shortest Path First (OSPF)](#open-shortest-path-first-ospf)
    - [Areas](#areas)
    - [Funcionamiento de OSPF](#funcionamiento-de-ospf)
  - [Split Horizon y Poison Reverse](#split-horizon-y-poison-reverse)
  - [Route Poisoning y holddown](#route-poisoning-y-holddown)

En la siguiente seccion veremos como funcionan los protocolos de ruteo interno open source mas utilizados: **Routing Information Protocol (RIP)** y **Open Shortest Path First (OSPF)**.

## Tipos de protocolos de ruteo

Los protocolos de ruteo se pueden agrupar de varias maneras segun su funcionamiento, los mas importantes son:

- **Protocolo de vector de distancia:** Estos protocolos apuntan a minimizar la distancia entre routers. Aqui la distancia se mide utilizando una *metrica de ruteo*. Usualmente la distancia es medida en saltos o *hops*. Es decir, la distancia suele ser medida de acuerdo al numero de routers por el cual se debe pasar al recorrer el camino desde el router de origen al de destino. Para calcular las mejores rutas, estos protocolos usan el algoritmo de *Bellman-Ford*.
- **Protocolo de vector de camino:** Los protocolos de vector de camino almacenan o mantienen el camino completo que debe recorrer un datagrama desde el origen al destino. De esta manera, la tabla de rutas almacena el destino, el siguiente salto y el camino para llegar al destino. BGP es un ejemplo de protocolo de vector de camino.
- **Protocolo de estado de enlace:** En este tipo de protocolos, los routers consideran la estructura completa de la red para realizar el ruteo. Cada router intercambia informacion sobre el estado de sus enlaces (no sus tablas). Con esta informacion cada router crea su propio mapa o grafo de conectividad de la red, determina los mejores caminos y con esta informacion crea su tabla de rutas.

## Routing Information Protocolo (RIP)

RIP es el protocolo de ruteo de **vector de distancia** mas antiguo. Este protocolo utiliza como metrica de ruteo el numero de *hops* que da un paquete, donde cada hop corresponde a un router dentro del camino.

Al ser un protocolo de vector de diastancia, RIP no tiene como saber si una ruta tiene un loop o no. Para aminorar el efecto de loops, RIP establece el maximo numero de saltos que puede dar un paquete como 16. De  esta forma, el maximo numero de hops permitido en una ruta es de 15. Ademas, RIP implementa otros mecanismos como *split horizon* y *route poisoning*.

Las tablas de rutas de RIP almacenan cual enlace deben utilizar para enviar un paquete a su destino (next hop) y la mejor distancia conocida hacia cada destino (distancia en numero de hops).

### Generacion de tablas de ruta

1. Primero, un router envia a otros routers un **mensaje de request** solicitando las tablas de rutas de otros routers. El manejo de este envio va a depender de la version de RIP.
2. Luego, **los routers que hayan recibido este request le envian sus tablas de rutas** al router que envio el mensaje original de request.
3. Una vez el router inicial recibe las tablas de rutas que le enviaron los otros routers, este las revisa y **actualiza su tabla de rutas en los siguientes casos**: Si recibe una ruta para **un destino que no estaba previamente en su tabla de rutas**, o si recibe una ruta para **un destino que si estaba previamente en su tabla de rutas pero cuyo largo es menor** que la ruta que tenia. En caso de que se reciban **2 rutas que van a un mismo destino**, tienen **igual numero de hops** pero cuyo **siguiente salto es distinto**, entonces **RIP mantiene ambas rutas** y luego las usa procurando **balancear la carga entre ambas rutas**.
4. Al **actualizar su tabla de rutas**, el router anhade la **red de destino**, el **numero de saltos**, y el **siguiente salto** o *next hop*. El **next hop** en este caso corresponde al router a traves del caul recibio la tabla de rutas.
5. El **mensaje de request**, junto al proceso recien descrito, **se repite cada 30 segundos** para mantener actualizadas las tablas de rutas.

### Versiones de RIP

Existen 3 versiones de RIP: **RIPv1, RIPv2** y **RIPng (next generation)**.

- **RIPv1:** Corresponde a la version original de RIP publicada en 1988. Esta version envia los mensajes de request a traves de un **broadcast** a `255.255.255.255`. Esta version fue desarrollada para ser utilizada con *Classfull networks*, y no es compatible con CIDR.
- **RIPv2:** Corresponde a la siguiente version de RIP. Esta fue publicada en 1994. En esta version los mensajes de request se envian usando **multicast** a la direccion `224.0.0.9`. La idea de no usar *broadcast* es evitar sobrecargar tanto a la red. Esta version de RIP puede manejar **Classless Interdomain Routing (CIDR).**
- **(next generation):** Esta version es una extension de **RIPv2**, disenhada para manejar IPv6.

Las ventajas del uso de RIP son:

- No es necesario configurarlo. Basta con poner RIP a correr y este va a generar de forma automatica las tablas de rutas.
- Al ser de los protocolos de ruteo mas antiguos, practicamente todos los equipos soportan RIP.

Desventajas:

- Envia mensajes de request y tablas de rutas cada 30 segundos.
- En redes grande se vuelve muy lento.
- La unica metrica de ruteo que utiliza es el numero de hops, sin incorporar otras variables.

## Open Shortest Path First (OSPF)

OSPF es un protocolo de ruteo de **estado de enlace**, por lo que en este protocolo los routers crean **un mapa de la topologia de la red**. Una vez que un router tiene un mapa de la topologia de la red, este **calcula las rutas mas cortas** utilizando el algoritmo de dijkstra.

### Areas

Este protocolo maneja los routers en base a areas. Estas areas pueden ser mas pequenhas que un *sistema autonomo*, y en general **un sistema autonomo tendra varias areas**. La idea es tener una instancia de OSPF por cada area, de forma de evitar que el numero de routers considerado a la hora de calcular dijkstra sea demasiado grande.

Cada una de **estas areas tiene asociado un ID que se escribe como si fuera una direccion IP**. Por ejemplo, el area 27 tiene **ID=0.0.0.27**. Las **distintas areas** dentro de una red **se unen a traves del area 0** (**ID=0.0.0.0**) llamada **backbone area**.

Usando las areas, el **trafico se puede clasificar** como **intra-area o dentro de una misma area**, e **inter-area o entre areas distintas**. Aqui, similar al caso de sistemas autonomos, podemos distinguir entre areas que permiten pasar trafico inter-area o **transit-area**, y areas que no permiten trafico inter-area o **stub area**.

### Funcionamiento de OSPF

Dentro de cada area se usara OSPF para que cada router pueda crear un mapa de la topologia de la red. Usando este mapa, cada router **calcula las rutas mas cortas** utilizando el algoritmo de dijkstra, y a partir de ellas crea su tabla de rutas.

Para que cada router pueda crear su propio mapa, OSPF funciona de la siguiente manera:

- Primero, los routers se saludan a traves de un **mensaje hello**. Los mensajes hello son mensajes muy pequenhos que permiten establecer relaciones de *adyacencia* entre routers, esto es equivalente a que cada router sepa cuales son sus vecinos. Si dos routers intercambian mensajes *hello* entre ellos, entonces se establece una adyacencia.
- Luego, los routers adyacentes intercambian su **Link State Database (LSDB)** a traves de **mensajes Database Description**. Las LSDB contienen informacion sobre los vecinos delrouter y sus redes accesibles en forma de **Link State Advertisements (LSAs).**
- A partir de la LSDB, el router puede generar un mapa de la topoogia de la red.
- **Una vez las topologias se estabilizan**, los routers unicamente enviaran mensajes en caso que ocurran **cambios en el estado de algun enlace**. Para ello enviaran **mensajes Link State Update** a traves de *multicast*. Ademas enviaran mensajes hello para verificar que los enlaces se encuentren operativos.
- Usando el mapa generado, el router genera su tabla de rutas usando las rutas mas cortas. Para calcular las rutas mas cortas se utiliza dijkstra. Al calcular dijkstra OSPF considera varias metricas de ruteo (capacidad del enlace, numero de hops, etc.).

Las ventajas de OSPF son:

- Gracias al uso de areas es facil de escalar a redes grandes.
- El uso de mensajes *hello* permite verificar el funcionamiento de los enlaces usando mensajes muy pequenhos.
- Soporta CIDR.

Desventajas:

- Requiere mas poder de procesamiento y memoria que otros protocolos de ruteo como RIP.

## Split Horizon y Poison Reverse

**Split horizon** es un **mecanismo para evitar loops en las rutas**. Si bien RIP intenta mitigar la formacion de loops estableciendo un numero maximo de *hops*, esto no es suficiente para evitar todos los casos. Aqui es donde entra **split horizon**.

Para evitar la formacion de *loops*, **split horizon evita enviar actualizaciones de sus rutas a traves de la interfaz por la cual se aprendieron**.

Para entenderlo mejor veamos un ejemplo. Suponga que tiene la siguiente configuracion:

```txt
R1 <--------> R2 <--------> R3
```

Si no tenemos implementado *split horizon*, el router R1 puede avisarle a R2 que tiene una ruta hacia R3 de largo 2. Esta ruta de largo 2 pasa por R2. Sin embargo, como RIP es un protocolo de vector de distancia, R2 no tiene como saber que el camino de R1 a R3 de largo 2, es de hecho el camino que pasa a traves de R2. En general esto no supondra un problema, pues R2 tiene una ruta de largo 1 a R3 y preferira dicha ruta.

El problema aparece cuando **el enlace entre R2 y R3 deja de funcionar**.

```txt
R1 <--------> R2 <----X---> R3
```

Si el enlace entre R2 y R3 deja de funcionar, es posible que R1 le informe a R2 que tiene una ruta hacia R3 de largo 2. Como ahora R2 no tiene una ruta hacia R3, al recibir las rutas de R1, R2 va a anhadir esta ruta a su tabla. Al anhadirla, esta ruta en R2 indicara:

```txt
destino=R3, número de saltos=3, next hop=R1
```

Sin embargo, la misma ruta en R1 se ve como:

```txt
destino=R3, número de saltos=2, next hop=R2
```

Es decir, **se crea un loop**. Pero eso no es todo. Luego de que R2 actualice su tabla, este se la enviara a R1. Como la ruta de R1 a R3 para a traves de R2, y la informacion que acaba de recibir de R2 indica:

```txt
destino=R3, número de saltos=3, next hop=R1
```

Vamos a observar que R1 actualiza su tabla de rutas y queda con una ruta que ahora tiene un **numero de saltos igual a 3+1=4**.

```txt
destino=R3, número de saltos=4, next hop=R2
```

Luego, cuando R1 envie su tabla de rutas a R2, este va a recibir una ruta hacia R3 que pasa por R1 y tiene un numero de saltos igual a 4, por lo que anhade una ruta hacia R3 de largo 4+1=5. Este proceso se repite hasta que finalmente el largo de las rutas llega a *"infinito"* (que en este caso es 16) donde finalmente se determina que R3 es inalcanzable. Este problema es conocido como el **count-to-infinity problem**.

Si en este caso implementamos **split horizon**, tendremos que R1 no enviara sus rutas a R2, y se evita el loop. Tipicamente vamos a encontrar *split horizon* siendo utilizado en conjunto con **poison reverse**.

- **Poison reverse:** Considere la configuracion de routers **R1-R2-R3** que acabamos de utilizar. Con *poison reverse*, cuando R1 le envie sus rutas a R2, R1 le va a indicar a R2 que su ruta para llegar a R3 es de *largo infinito*. De esta forma, R2 no va a intentar llegar a R3 a traves de R1.

Debemos notar que si bien *split horizon* con *poison reverse* logra evitar los loops en configuraciones simples. Configuraciones mas complejas aun pueden sufrir de loops. Para prevenir los loops en estos casos, RIP utiliza **route poisoning** y **holddown**.

## Route Poisoning y holddown

A diferencia de *split horizon* con *poison reverse*, **route poisoning** le informa a **toda la red** si un router se vuelve inalcanzable. Para ello le envia un mensaje a todos los routers indicando que la ruta al router que ahora es **inalcanzable es de largo infinito**.

Sin embargo, aun es posible tener problemas. **Si se pierden estos mensajes** puede ocurrir que **un router no reciba la informacion sobre el router inalcanzable** y crea que aun puede llegar a el. El router que cree que de hecho puede llegar al router inalcanzable **va a avisarle a otros routers** de esto, lo cual puede generar nuevamente la aparicion de **loops**. **Aqui es donde se utiliza holddown**.

Con **holddown** cada vez que un router recibe un mensaje indicando que un router A es inalcanzable, este inicia un timer. Mientras dure el *timer*, el router **descartara todos los mensajes que contengan una ruta que indique que se puede alcanzar el router A**. De esta manera, inclusi si un router B no recibe el mensaje incial con *router poisoning* y B comienza a avisar que el router A es alcanzable, los routers que si saber que A es inalcanzable **ignoraran las rutas de B hacia A hasta que la red se estabilice.**
