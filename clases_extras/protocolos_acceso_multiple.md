# Protocolos de acceso multiple

- [Protocolos de acceso multiple](#protocolos-de-acceso-multiple)
  - [Uso eficiente del enlace](#uso-eficiente-del-enlace)
  - [Tipos de protocolos de acceso multiple](#tipos-de-protocolos-de-acceso-multiple)
  - [Random Access Protocols](#random-access-protocols)
    - [ALOHA](#aloha)
    - [Slotted ALOHA](#slotted-aloha)
    - [Carrier Sense Multiple Access (CSMA)](#carrier-sense-multiple-access-csma)
    - [CSMA Collision Detection (CSMA/CD)](#csma-collision-detection-csmacd)
    - [CSMA Collision Avoidance (CSMA/CA)](#csma-collision-avoidance-csmaca)

En la presente seccion hablaremos de los tipos de protocolos que pueden ser utilizados para manejar el **problema de acceso multiple.**

## Uso eficiente del enlace

Existen varias formas de coordinar la utilizacion de un enlace compartido por varios nodos. Sin embargo, si se quiere usar el canal de forma eficiente, el protocolo debera tener las siguientes caracteristicas:

- **Usar toda la capacidad del enlace:** Si hay un **unico nodo** con informacion por enviar, este deberia poder usar toda la capacidad del enlace. Si hay **multiples nodos** queriendo enviar informacion, la suma de los datos enviados por todos los nodos deberia usar toda la capacidad del canal.
- **Uso equitativo del enlace:** Si hay multiples nodos queriendo enviar informacion, entonces el **uso promedio** del enlace deberia ser **repartido de forma equitativa**. Esto no necesariamente implica que cada nodo siempre use lo mismo del enlace, si no que el uso promedio es el mismo. Es decir, podria ocurrir que un nodo A utilice la mayoria del enlace en un instante 1, pero en instancias subsecuentes use una pequenha fraccion del enlace de tal manera que en promedio utilizo el enlace tanto como el resto de los nodos.
- **Descentralizado:** El protocolo debe ser descentralizado, es decir, **no existe un unico nodo a cargo de manejar el uso del enlace.** Tener un nodo central a cargo de organizar el uso del enlace significaria tener un punto unico de error, cuyo fallo resultaria en una red local incapaz de coordinar el uso del enlace.
- **Bajo costo:** Un protocolo eficiente debe ser capaz de correr utilizando pocos recursos de la red. Su funcionamiento no debe entorpecer la transmision de informacion.

## Tipos de protocolos de acceso multiple

Los protocolos de acceso multiple pueden agruparse en 3 categorias:

- **Random Access Protocols:** En este tipo de protocolos todos los nodos tienen la misma prioridad al momento de usar el enlace. Cada nodo intenta transmitir usando toda la capacidad del enlace y en caso de detectar colision el nodo se detiene y espera una cantidad de tiempo aleatorio antes de volverlo a intentar.
- **Particion de canal o channelization protocols:** Los protocolos de *particion de canal*, como su nombre sugiere, dividen o particionan el canal para coordinar su uso. Esta division puede ser a nivel de tiempo (dandole un trozo de tiempo a cada nodo para usar el canal), a nivel de frecuencias (a cada nodo se le asigna una banda de frecuencia para usar), etc.
- **Controlled Access Protocols:** Este tipo de protocolos organiza a sus nodos otorgandole turnos a los nodos. El proceso de entrega de turnos se hace de manera descentralizada, por lo que los turnos son decididos entre los mismos nodos.

## Random Access Protocols

A continuacion nos enfocaremos en **Random Access Protocols** pues estos son utilizados por los medios que nos interesan: **Ethernet** y **Wireless**. Estos protocolos son:

- **ALOHA**
- **Slotted ALOHA**
- **Carrier Sense Multiple Access (CSMA)**

### ALOHA

La **version original de ALOHA** (tambien conocido como **Pure ALOHA**) fue desarrollado originalmente en la Universidad de Hawaii y su nombre responde al acronimo: **Additive Links On-Line Hawaii Area**. En su version original ALOHA se comporta siguiendo las siguientes directrices.

- Si un nodo tiene frames para enviar, simplemente los envia. Es decir, el nodo no verifica el estado del enlace antes de usarlo.
- Si durante la transmision de frames el nodo recibe datos de algun otro nodo, entonces hubo colision. En caso de colision, todos los nodos que hayan detectado la colision (aquellos que estaban tratando de enviar frames) deberan reintentar enviar sus frames en un **momento posterior.**
- El tiempo que debera esperar un nodo para la retransmision de frames en caso de colision, es determinado de manera aleatoria por cada nodo. La idea detras de esto es evitar que aquellos nodos que participaron en la colision intenten retransmitir al mismo tiempo.

La version original de ALOHA no es muy eficiente en cuanto a su uso del canal, por lo que resulta en perdida de datos y tiempo.

### Slotted ALOHA

Una mejora a ALOHA correspnde a Slotted ALOHA. Esta version del protocolo ALOHA utiliza trozos o **slots** de tiempo para manejar la transmision y retransmision de frames:

- Un nodo puede transmitir frames solo al incio del slot de tiempo.
- En caso de colision, el nodo detecta la colision antes del final de slot e intentara retransmitir el frame con una cierta probabilidad hasta que logre enviar el frame sin detectar colision.

Si bien **Slotted ALOHA** es una mejora a ALOHA, este sigue siendo un protocolo poco eficiente. Parte de esta ineficiencia es causada por hacer uso del canal sin primero observar su estado o por **"no escuchar antes de hablar"**.

### Carrier Sense Multiple Access (CSMA)

Existen multiples protocolos **"Carrier Sense"**. Los **protocolos Carrier Sense** corresponden a aquellos que **verifican** que el medio de comunicacion **no esta siendo ocupado antes de intentar transmitir frames**. Es decir, son protocolos que **"escuchan antes de hablar"**.

Al asegurarse de que el canal no esta siendo ocupado antes de transmitir, este tipo de protocolos logra **evitar colisiones en la mayoria de los casos**. Sin embargo, aun pueden ocurrir colisiones. Esto puede parecer contraintuitivo considerando que cada nodo va a enviar frames unicamente si esta seguro de que el canal no esta siendo utilizado. Entonces **por que ocurren estas colisiones?**. Estas colisiones ocurren por el tiempo de **delay en la propagacion del mensaje**. Cuando un nodo A hace uso del canal, los datos enviados no aparecen de forma instantanea en todas partes, si no que se demoran un tiempo en viajar a traves del mismo. Esto significa que si un nodo B observa el estado del enlace inmediatamente despues de que el nodo A envio un frame, el nodo B va a ver que el enlace no esta siendo usado pues los datos enviados por A aun no han llegado al sector del enlace al que tiene acceso B. Luego el nodo B envia sus datos (pensando que el canal no esta siendo usado), resultando en colision.

A continuacion vamos a hablar de **CSMA Collision Detecton (CSMA/CD)** y **CSMA Collision Avoidance (CSMA/CA).**

### CSMA Collision Detection (CSMA/CD)

Este protocolo es un **Carrier Sense Protocol** que incorpora **detección de colisiones** o **Collision Detection**. En **CSMA/CD**, si un nodo detecta que otro nodo se encuentra transmitiendo frames al mismo tiempo que él, entonces este detiene su transmisión y espera una cantidad de tiempo antes de intentar retransmitir. La cantidad de tiempo que el nodo deberá esperar es determinado de forma aleatoria para evitar nuevas colisiones. La cantidad de tiempo que un nodo espera para retransmitir va a afectar qué tan bien se está usando el canal. Si el tiempo es muy largo y hay pocos nodos, el canal no va a ser utilizado tanto como es posible. Mientras que si el tiempo de espera es corto y hay muchos nodos, se aumenta la probabilidad de colisiones.

CSMA/CD fue utilizado por redes **Ethernet antiguas**. Actualmente, **las redes Ethernet modernas no utilizan CSMA/CD** pues estas solucionan el problema de colisiones haciendo que los cables no sean compartidos (conectan un par de nodos A y B), y utilizando cables ethernet *full-duplex*. En este contexto un **cable full-duplex** es un cable que permite transmitir información de origen a destino y viceversa al mismo tiempo, sin que estas señales interfieran entre sí.

### CSMA Collision Avoidance (CSMA/CA)

Este protocolo es un **Carrier Sense Protocol** que incorpora **prevención de colisiones** o **Collision Avoidance**. En **CSMA/CA**, se enfoca en **evitar las colisiones** en vez de detectarlas. Esto es particularmente útil en redes inalámbricas o Wireless como **Wi-Fi**. En el caso de redes inalámbricas, la fuerza de la señal de salida es mucho mayor que la de llegada, por lo que detectar que alguien está enviando frames mientras se están enviando datos es bastante difícil. Además, las redes Wi-Fi son propensas a otros problemas que hacen que detectar colisiones no sea suficiente.

Para prevenir las colisiones **CSMA/CA** sigue los siguientes pasos:

1. Si el canal no esta siendo ocupado, el nodo transmite luego de un tiempo (cortito) conocido como *Distributed Inter-Frame Space* (DIFS).
2. Si el canal esta siendo ocupado, espera un tiempo aleatorio y se vuelve a intentar.
3. Una vez se logra transmitir el frame se espera un ACK. Si este llega con exito se continua enviado frames. En caso de no llegar el ACK se pasa al paso 2.
