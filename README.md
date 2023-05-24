# Redes

La materia se divide por temas, cada uno de estos temas tiene una parte de ejemplo en donde se muestra el funcionamiento aplicado del respectivo tema:

* **[DNS programado con sockets](./ejemplos_por_materia/dns_sockets/resumen.md)**
* [**Selective Repeat**](./ejemplos_por_materia/selective_repeat/resumen.md)

Gran parte de la materia que se encuentra que resumida en los ejemplos aplicados fue extraida del material perteneciente al curso de Redes, todos los creditos pertinentes van para el equipo docente :D.

Aca se encuentran las auxiliares realizadas durante el semestre de Otonho 2023:

* **[HTTP](./auxiliares/01_http.md)**
* **[Proxies y Conexiones Persistentes](./auxiliares/02_proxies_conexiones_persistentes.md)**
* **[DNS Parte 1](./auxiliares/03_dns_I.md)**
* **[DNS Parte 2](./auxiliares/04_dns_II.md)**
* **[Capa de Transporte](./auxiliares/05_capa_de_transporte.md)**
* **[Comunicacion Confiable](./auxiliares/06_comunicacion_confiable.md)**

## Comandos utiles

### `netcat`

Para enviar mensajes por internet se usa **netcat** de la siguiente forma:

* Si es orientado a conexion:

    ```bash
    nc host puerto
    ```

* Si no es orientado a conexion:

    ```bash
    nc -u host puerto
    ```

### `netem`

Con **netem** podemos simular (y controlar) la perdida de mensajes en nuestra red de comunicacion. Al usarlo sobre localhost, usamos el comando `tc` que pertenece a `netem`. Si queremos generar un 20% de perdida de mensajes y un delay de 0.5 segundos sobre localhost (`lo`) ejecutamos:

```bash
tc qdisc add dev lo root netem loss 20.0% delay 0.5s
```

Si una vez ejecutado `netem` deseamos modificar alguno de los valores debemos usar `change`. Luego si queremos cambiar el porcentaje de perdida a 30% debemos ejecutar:

```bash
tc qdisc change dev lo root netem loss 30.0% delay 0.5s
```

Para detener el efecto de perdida y/o de delay de mensajes se ejecuta:

```bash
tc qdisc del dev lo root netem
```

### `curl` (HTTP)

El comando `curl` funciona como cliente HTTP para texto permitiendonos crear de forma facil y rapida clientes para probar servidores HTTP, `curl` puede ser ocupado de la siguiente forma:

```bash
% curl [domain] -flag
```

* Donde `flag` son las flags que podemos utilizar, las mas comunes son `I` para traer solo los headers, `L` que entrega informacion siguiendo las redirecciones y `x` que le permite ocupar un proxy para la consulta, en este caso el uso es de la siguiente manera:

```bash
% curl [domain] -x [direccion]:[puerto]
```

### `dig` (DNS)

El comando `dig` (**Domain Information Groper**) nos permite hacer consultas DNS y nos muestra la respuesta de la consulta, por lo que es especialmente util para probar el funcionamiento de un resolver. Para hacer consultas DNS con `dig` a un resolver corriendo en una IP y puerto especificos se puede usar el siguiente comando:

```bash
% dig -[puerto] @[ip] [domain]
```

Ejemplo:

```bash
% dig -p8000 @localhost example.com
% dig @8.8.8.8 www.uchile.cl
```

* En el caso en que no se especifica puerto es porque se esta preguntando al resolver de Google.
