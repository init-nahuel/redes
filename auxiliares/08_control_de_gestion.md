# Control de Gestion

## Verdadero y Falso

**1. El control de congestion se encarga de no sobrecargar al receptor, mientras que el control de flujo se encarga de no sobrecargar la red.**

R: Falso. El control de congestion se encarga de no sobrecargar la red mientras que el control de flujo se encarga de no sobrecargar al receptor.

**2. La velocidad a la que el receptor puede procesar los segmentos que le llegan no influye en el nivel de congestion de la red.**

R: Falso. A pesar de que no es directo, igual afecta la carga total que puede tener la red, ya que si los procesa a una velocidad inferior a lo que se envian, los canales quedaran congestionados.

**3. Todas las implementaciones de TCP usan Fast Recovery.**

R: Falso. No siempre se implementa, ya que no es parte esencial de control de congestion.

**4. La idea bajo AIMD es que el flujo entre dos puntos aumente linealmente, pero disminuya de forma multiplicativa (por ejemplo a la mitad) en caso de deteccion de congestion.**

R: Verdadero. Para aumentar el flujo, se va sumando una fraccion de MSS, y al disminuir se divide a la mitad.

**5. Dos computadores que hablan a 1[Mb/s] igual pueden sufrir congestion aunque el canal sea de 100[Mb/s].**

R: Verdadero. Ese canal puede estar siendo utilizado por mas entidades, creando congestion en el.

**6. La congestion es detectada solo mediante el uso de segmentos que cuyo proposito es indicar el nivel de congestion.**

R: Falso. La congestion se detecta mediante la perdida de segmentos.

**7. TCP sin simplificar usa Go-Back-N.**

R: Falso. No se indica que utiliza, depende de quien lo implemente.

**8. TCP es full-duplex pues, dados un host A y un host B, podemos enviar datos de A a B y de B a A al mismo tiempo. Esto se puede lograr enviando datos en los ACKs.**

R: Verdadero. El canal se utiliza para ambos lados, teniendo una comunicacion mas fluida entre los puntos.

**9. Durante el envio de datos, si un segmento llega en desorden, este siempre se almacena en la ventana de recepcion.**

R: Falso. Esto depende de que mecanismo de manejo de perdidas se ocupe.

**10. Los ACKs en TCP son acumulativos, por lo que el numero de ACK indica que todos los bytes menores al ACK number llegaron con exito, similar a G0-Back-N.**

R: Verdadero. Esto esta estipulado que se haga de esta forma, independiente del metodo que se utiice para el envio.

**11. Una diferencia entre TCP simplificado y TCP real es que TCP simplificado es simplex y TCP es full-duplex.**

R: Falso. TCP simplificado es half-duplex, ya que se puede hablar de punto a punto, solo que no al mismo tiempo.

**12. En TCP simplificado manejamos los ACKs usando el numero de secuencia y el flag ACK, mientras que en TCP existe un numero de secuencia y un numero de ACK que son distintos entre si.**

R: Verdadero. La gracia es aprovechar los ACKs para enviar informacion y asi poder implementar la comunicacion full-duplex.

**13. El router se compone principalmente de: una cola con los paquetes que vienen llegando, las colas de salida para cada enlace o puerto, y una tabla de rutas para saber en cual cola dejar cada cosa segun la IP de destino.**

R: Verdadero. Puede tener mas elementos, pero no son esenciales.

**14. En la capa de red es importante saber el puerta al que va dirigida la informacion, ademas de la direccion.**

R: Falso. Solo es necesaria la direccion, del puerto se encarga la capa de transporte.

**15. En ruteo, la direccion del siguiente salto o *Next Hop* indica la direccion IP de la interfaz del router por donde se debe hacer forward.**

R: Falso. Eso es indicado por *Interface*, *next hop* es la direccion de la interfaz hacia la que se le forwardeara el paquete.

**16. Originalmente, las redes IP se reconocian por clases de tamanho fijo, pero luego CIDR permitio que fuesen redes de tamanho variable.**

R: Verdadero. Esto lo logro a traves del uso de mascaras. El parche fue tan popular, que IPv4 se sigue utilizando hasya el dia de hoy, en vez de migrar a IPv6.

**17. En la capa de transporte, los routers cooperan junto a los hosts para manejar la perdidade de datos y la congestion.**

R: Falso. Los routers hacen lo minimo posible. Los hosts son los que se llevan toda la carga.

**18. Una red con mascar de tamanho 29 puede contener hasta 8 direcciones.**

R: Verdadero. Tiene 3 bits para asignar IPs, por lo tanto, tiene 2^3 = 8 combinaciones posibles.

## Control de Congestion

**1. Usamos Fast Retransmit (al recibir 3 ACKs duplicados retransmitimos el paquete correspondiente) pero aun asi necesitamos timeouts (esto es un hecho), por que?**

R: Este acercamiento funciona cuando los ACKs llegan, el timeout es necesario para identificar casos en que los ACKs se pierdan, cuando la ventana de transmision es muy pequenha (no podras tener muchos ACKs duplicadoss) o cuando el paquete perdido esta cerca del final.

**2. Que ocurre si en lugar de AIMD (Additive Increase, Multiplicative Decrease) usaramos MIMD (Multiplicative Increase, Multiplicative Decrease)?, seria justo?**

R: La idea de AIMD es que TCP busca el punto optimo de operacion (tamanho de ventana), aquel justo antes de que la congestion haga perder muchos paquetes. La idea es que al detectar una perdida se disminuya a la mitad la ventana para dar tiempo de bajar la carga en la red y volver a buscar el equilibrio. En el caso de MIMD, una perdida haria que la ventana bajara a la mitad (lo que haria que bajara la congestion), pero al recibir el primer ACK volveria al mismo estado de perdida de hace poco, lo que hace que la red sea muy inestable, con oscilaciones en torno al punto de congestion. Como toda la gente estaria haciendo lo mismo una y otra vez, el sistema se volveria loco y seria muy injusto (aquel que pudiera mandar todo primero tendria mas posibilidades que aquel que, en las mismas condiciones, se atrasa un poco).

**3. Un problema de TCP son las ventanas tontas (o silly windows), por que ocurre esto? cuales son posibles soluciones?**

R: Es cuando se achica tanto la ventana que pasa a ser tonto, pudiendo ser tan chica que no pasan los headers. Por lo anterior, se deben enviar muchos paquetes pequenhitos, lo que termina congestionando la red.

Desde el lado del receptor, si es muy ineficiente para procesar los datos, envia senhal de que se achique el tamanho de la ventana emisora. Al hacer esto, se genera mayor flujo, lo que puede provocar que siga siendo muy ineficiente. Asi se repita, achicando cada vez mas la ventana, provocando mucha congestion. Para solucionarlo, el receptor no debe enviar un ACK apenas le llegue un segmento. Este espera a que tenga una cantidad decente de espacio para recibir, y luego informar sobre ese tamanho de ventana.

Desde el emisor, si no logra procesar los datos a ser enviados eficientemente, una solucion consiste en, luego de enviar el primer paquete, no transmitir el segundo inmediatamente. La idea es ir tomando los bytes a leer e ir guardandolos en un buffer, y cuando llegue el ACK del primer mensaje, enviar todo el buffer en un solo segmento TCP.

Ambas soluciones son complementarias, para asi evitar caer en ventanas tontas.

**4. Suponga que dos hosts abren una conexion TCP entre ellos y comienzan a mandar datos. Asuma que el tamanho de segmento es 3KB y ssthresh es de 64KB.**

* **Cuantos bytes son transmitidos despues de 3RTTs sin perdida?**

    En el instante inicial, cwnd=3KB (la ventana de congestion se setea de acuerdo al tamanho de segmento). Despues de 1RTT, se logran transferir 3KB y la ventana se duplica -> cwnd=6KB (2x3KB). Luego de 2RTT, se han transferido 9KB (3KB+6KB) y cwnd=12KB (4x3KB). Despues de 3RTT, se han transferido 21KB (3KB+6KB+12KB) y cwnd=24KB (8x3KB).

* **Ahora suponga que despues del 3er RTT ocurre una perdida y que el emisor super el timeout, que hace el control de congestion?**