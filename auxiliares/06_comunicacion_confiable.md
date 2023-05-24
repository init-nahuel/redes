# Comunicacion Confiable

## Verdadero o False

**1. En terminos de tiempo de transmision, Stop & Wait es menos eficiente que Go-Back-N y Selective Repeat.**

R: Verdadero. Debe esperar cada ACK para seguir avanzando con el envio.

**2. Tanto Go-Back-N como Selective Repeat se implementan con ventana de tamanho N (N>1) en el lado de emisor y el lado de receptor.**

R: Falso. Go-Back-N no utiliza ventanas en el lado del receptor.

**3. En promedio, Go-Back-N y Selective Repeat retransmiten la misma cantidad de paquetes en caso de igual tasa de perdida.**

R: Falso. Go-Back-N va a terminar reenviando muchos mas paquetes debido a que se retransmite toda la ventana en caso de perdida.

**4. Tanto en Go-Back-N como Selective Repeat es el timeout quien senhala el inicio de una retransmision de paquetes.**

R: Verdadero. Luego del timeout es que se decide iniciar el reenvio.

**5. En Go-Back-N si el emisor recibe unicamente el ACK asociado al ultimo segmento de su ventana, este no puede avanzar su ventana.**

R: Falso. Gracias al funcionamiento de Go-Back-N, el emisor se puede asegurar que todos los segmentos hasta ese ACK han llegado correctamente, por lo tanto, puede avanzar toda su ventana.

**6. En Selective Repeat si el emisor recibe unicamente el ACK asociado al ultimo segmento de su ventana, este no puede avanzar su ventana.**

R: Verdadero. Le deben llegar los ACKs de cada segmento antes de poder avanzar la ventana.

**7. Al usar ventanas deslizantes o Sliding Windows conforme entran elementos a la ventana, estos se van enviando.**

R: Verdadero. La idea es ser eficientes, entonces apenas avanza la ventana, se envian los paquetes.

**8. Un ACK perdido no necesariamente fuerza una retransmision. Verdadero o Falso? Justifique para el caso de Stop & Wait, Go-Back-N y Selective Repeat.**

R:

* **Stop & Wait:** Falso. Un ACK perdido siempre implica el reenvio del paquete en cuestion, ya que se verifica uno a uno antes de seguir con la transmision.
* **Go-Back-N:** Verdadero. En caso de que se pierda algun ACK, pero luego llegue un ACK para un N mayor, se puede asumir que el paquete anterior llego correctamente y no se necesita retransmitir.
* **Selective Repeat:** Falso. Para cada ACK perdido se va a reenviar el paquete asociado.

## Protocolos Capa de Transporte

**1. Considere un protocolo de ventana corredera o Sliding Window con un tamanho de ventana N, por que necesitamos que los numeros de secuencia vayan desde Y a (Y + 2N -1).**

En caso de que las ventanas queden corridas entre emisor y receptor, se debe tener un rango de numeros de secuencia lo suficiente para que no se mezclen entre el fin y el inicio de la ventana.

**2. En un protocolo Go-Back-N, vimos que el transmisor puede asumir que un ACK para la secuencia N implica un ACK para todos los segmentos con numero de secuencia previos a N. Frente a desorden de los paquetes, esto tambien es valido? Justifique.**

Si llegan en desorden, el receptor los descarta, pero luego se cumple el timeout de cada segmento y se reenvian, esto se va a repetir hasta que lleguen en orden los segmentos. Finalmente, se logra la transmision, luego de muchos reintentos. Por el funcionamiento anterior, se puede seguir asumiendo que un ACK implica un ACK para los segmentos previos, aunque es poco probable que ocurra.

**Proponga dos casos donde Go-Back-N tenga igual desempenho que Selective Repeat en terminos de numero de segmentos enviados.**

Cuando todo avanza sin problemas (no hay perdidas) y cuando el tamanho de la ventana es 1 (y pasa a ser Stop & Wait >.<). Como respondieron durante la clase, existen los casos de que haya 100% de perdidas, pero finalmente ahi ni siquiera hay envia de datos, y de que justo se pierdan todos los ACKs de la ventana en Selective Repeat, por lo que, al igual que en Go-Back-N, se reenviaria toda la ventana.
