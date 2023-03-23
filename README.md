# Comandos utiles para redes

## `netcat`

Para enviar mensajes por internet se usa **netcat** de la siguiente forma:

* Si es orientado a conexion:

    ```bash
    nc host puerto
    ```

* Si no es orientado a conexion:

    ```bash
    nc -u host puerto
    ```

## `netem`

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
