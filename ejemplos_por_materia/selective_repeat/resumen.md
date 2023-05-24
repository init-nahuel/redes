# Clases TimerList y SlidingWindow

Para simplificar la actividad Selective Repeat se provee las clases `SlidingWindow` y `TimerList` para manejar ventanas deslizantes y multiples timeouts respectivamente.

## `SlidingWindow`

Esta clase le permite crear ventanas deslizantes usando una lista de datos, el numero de secuencia inicial y el tamanho de la ventana.

* `SlidingWindow(window_size, data_list, initial_seq)`: Construye una ventana de tamanho `window_size`, usando los datos de `data_list` y numero de secuencia inicial `initial_seq` (Y = `initial_seq`).
* `move_window(steps_to_move)`: Avanza la ventana en `steps_to_move` espacios y actualiza los numeros de secuencia segun corresponda. No puede avanzar mas espacios que el tamanho de la ventana. Si se acaban los datos en `data_list` rellena con `None`.
* `get_sequence_number(window_index)`: Entrega el numero de secuencia del elemento almacenado en la posicion `window_index` de la ventana.
* `pull_data(data, seq, window_index)`: Anhade un elemento a la ventana en la posicion `window_index` con los datos `data`, numero de secuencia `seq`. Note que si la ventana no es vacia tiene que asegurarse que el numero de secuencia sea valido dentro de la ventana. Puede crear una ventana vacia con `SlidingWindow(window_size, [], initial_seq)`.

### Ejemplo uso de `SlidingWindow`

```python
import slidingWindow as sw # para poder llamar así a la clase, guárdela en un archivo llamado slidingWindow.py

window_size = 3
initial_seq = 3
message = "Esta es una prueba de sliding window"
message_length = len(message.encode())

# mensaje "Esta es una prueba de sliding window." separado en grupos de 4 caracteres.
data_list = [message_length, "Esta", " es ", "una ", "prue", "ba", "e sl", "idin", "g wi", "ndow"]

# creamos un objeto SlidingWindow
data_window = sw.SlidingWindow(window_size, data_list, initial_seq)

# Podemos imprimir la ventana inicial
print(data_window)
# y nos muestra lo siguiente:
# +------+---------+---------+---------+
# | Data | 37      | Esta    |  es     |
# +------+---------+---------+---------+
# | Seq  | Y+0 = 3 | Y+1 = 4 | Y+2 = 5 |
# +------+---------+---------+---------+

# Avanzamos la ventana en 2 espacios y luego otros 3
data_window.move_window(2)
data_window.move_window(3)
print(data_window)

# si avanzamos lo suficiente la ventana se acaban los datos
data_window.move_window(1)
data_window.move_window(3)
if data_window.get_sequence_number(2) == None and data_window.get_data(2) == None:
    print("el último elemento de la ventana es igual a None")
    print(data_window) 

# También podemos crear ventanas vacías de la siguiente forma:
empty_window = sw.SlidingWindow(window_size, [], initial_seq)
print(empty_window)

# y podemos añadir datos a esta ventana
add_data = "Hola"
seq = initial_seq + 2
window_index = 2
empty_window.put_data(add_data, seq, window_index)
print(empty_window)
```

## `TimerList`

Esta clase permite crear una lista de timers con un timeout fijo. Este timeout es el mismo para todos los timers. Para usar estos timers junto con la clase `SlidingWindow` vease el ejemplo de mas bajo en esta seccion. Estos timers no usan threads ni levantan errores cuando se cumple el timeout, por lo que debemos checkear de forma manual si algun timer ya cumplio su timeout. Usamos un timeout personalizado y no el timeout de la clase socket porque este ultimo le pertenece al socket, no al mensaje enviado, y se reinicia cada vez que llamamos una funcion bloqueante (como `recvfrom`), si queremos asociar un timeout a cada segmento enviado como en el caso de selective repeat, vamos a necesitar un timer para cada segmento.

* `TimerList(timeout, number_of_timers)`: Construye una lista de timers de tamanho `number_of_timers` con un timeout de `timeout` segundos.
* `start_timer(timer_index)`: Inicia el timer en la posicion `timer_index`.
* `get_timed_out_timers()`: Retorna una lista con los indices de los timers que ya cumplieron su timeout.
* `stop_timer(timer_index)`: Detiene el timer en la posicion `timer_index`. El timer detenido no aparecera al llamar `get_timed_out_timers()`.

### Como usar `TimerList` con `SlidingWindow`

En el siguiente codigo puede ver como usar las clase `TimerList` y `SlidingWindow` para implementar Stop & Wait. En este ejemplo vemos como usar sockets en forma o bloqueante junto a objetos `timerList` para poder manejar multiples timeouts sin usar threads. El flujo general se puede resumir en los siguientes pasos:

* Inicializamos lo necesario para enviar datos, hacemos que el socket sea no bloqueante, enviamos el primer segmento e inciamos un timer usando `TimerList`.
* Dentro de un `while True` esperamos la respuesta dentro de un bloque `Try-Except-Else`. Un socket no bloqueante levanta un `BlockingIOError` cada vez que no le llega un mensaje (lo cual es la mayoria del timepo). Si nos llega este error entramos al bloque `Except` y simplemente continuamos esperando a que llegue algo. Si entramos al bloque `Else` significa que recibimos algo y lo manejamos segun corresponda. Cuanto checkeo el timeout? Cada vez que entramos del bloque `Try`.
* Si terminamos de enviar todo el mensaje salimos del `while True` y se detiene la ejecucion.

```python
import timerList as tm
import slidingWindow as sw
import socket

    # (...) acá está el resto de la clase SocketTCP

    def send_using_stop_and_wait(self, message):
        message_length = len(message.encode())
        # dividimos el mensaje en trozos de 64 bytes
        data_list = self.chop_message(message, 64)

        # usamos una ventana para que vean como se usa
        initial_seq = self.seq
        data_to_send = sw.SlidingWindow(1, [message_length] + data_list, initial_seq)
        wnd_index = 0

        # creamos un timer usando TimerList, en stop and wait mandamos de a un elemento y necesitamos sólo un timer
        # asi que hacemos que nuestro timer_list sea de tamaño 1 y usamos el timeout de SocketTCP
        timer_list = tm.TimerList(self.timeout, 1)
        t_index = 0

        # partimos armando y enviando el primer segmento
        current_data = data_to_send.get_data(wnd_index)
        current_seq = data_to_send.get_sequence_number(wnd_index)
        current_segment = self.wrap_data_as_segment(current_data, current_seq)
        self.socket_udp.sendto(current_segment.encode(), self.destination_address)

        # y ponemos a correr el timer
        timer_list.start_timer(t_index)

        # para poder usar este timer vamos poner nuestro socket como no bloqueante
        self.socket_udp.setblocking(False)

        # y para manejar esto vamos a necesitar un while True
        while True:
            try:
                # en cada iteración vemos si nuestro timer hizo timeout
                timeouts = timer_list.get_timed_out_timers()
                # si hizo timeout reenviamos el último segmento
                if len(timeouts) > 0:
                    self.socket_udp.sendto(current_segment.encode(), self.destination_address)
                    # reiniciamos el timer
                    timer_list.start_timer(t_index)

                # si no hubo timeout esperamos el ack del receptor
                answer, address = self.socket_udp.recvfrom(self.buff_size)

            except BlockingIOError:
                # como nuestro socket no es bloqueante, si no llega nada entramos aquí y continuamos (hacemos esto en vez de usar threads)
                continue

            else:
                # si no entramos al except (y no hubo otro error) significa que llegó algo!
                # si la respuesta es un ack válido
                if self.is_valid_ack_stop_and_wait(current_segment, answer.decode()):
                    # detenemos el timer
                    timer_list.stop_timer(t_index)

                    # actualizamos el segmento
                    data_to_send.move_window(1)
                    current_data = data_to_send.get_data(wnd_index)
                    
                    # si ya mandamos el mensaje completo tenemos current_data == None
                    if current_data == None:
                        return

                    # si no, actualizamos el número de secuencia y mandamos el nuevo segmento
                    else:     
                        current_seq = data_to_send.get_sequence_number(wnd_index)
                        self.seq = current_seq
                        current_segment = self.wrap_data_as_segment(current_data, current_seq)

                        self.socket_udp.sendto(current_segment.encode(), self.destination_address)
            
                        # y ponemos a correr de nuevo el timer
                        timer_list.start_timer(t_index)
```
