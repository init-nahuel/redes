# BGP

- [BGP](#bgp)
  - [Antes de Empezar](#antes-de-empezar)
  - [Actividad](#actividad)
  - [Pruebas](#pruebas)

En esta actividad vamos a implementar BGP en nuestro mini-Internet. Para esta actividad necesitará el código implementado en la última actividad de la sección de IP.

## Antes de Empezar

- **Border Gateway Protocol (BGP):** Corresponde al protocolo de ruteo de paquetes entre distintas redes o sistemas autónomos. BGP considera los caminos a la hora de establecer las rutas entre sistemas autónomos pues es un path-vector protocol o protocolo de vector de camino. Además, BGP considera las políticas de ruteo de cada sistema autónomo. En esta actividad no consideraremos el factor político de BGP.
- **Sistema autónomo (Autonomous System o AS):** Un sistema autónomo corresponde a una red que tiene su propio sistema de ruteo interno. Cada sistema autónomo se identifica según un Autonomous System Number (ASN). Los ASN son asignados a cada AS por la Internet Assigned Numbers Authority (IANA).
- **Router de borde:** Un router de borde corresponde a un router que se comunica con el exterior del AS al que pertenece. Los routers de borde se rigen por BGP para comunicarse con otros routers de borde en otros AS.
- **Factor político en BGP:** Algo interesante que debemos tomar en cuenta a la hora de estudiar BGP es que las rutas que este establece no son necesariamente las mejores rutas en términos de 'saltos' entre routers pues BGP debe tomar en cuenta las políticas de cada AS. Estas políticas pueden significar que, por ejemplo, la mejor ruta entre un AS1 y un AS2 deba ser descartada pues dicha ruta pasa por un AS3 por el cual el AS1 no quiere rutear sus paquetes.

## Actividad

El objetivo de esta actividad es implementar BGP en nuestro mini-Internet. Para implementar BGP en nuestro mini-Internet deberá trabajar sobre una copia del código de manejo de routers utilizado en la actividad anterior. Usando dicha copia como base, siga los siguientes pasos:

1. Añada la función `create_BGP_message()` que le permita crear mensajes BGP según el formato indicado en la sección [Mini-Internet + BGP](./mini_internet_bgp.md). Recuerde que inicialmente cada router solo sabe llegar a sus vecinos.

    **Test:** Verifique que su función es capaz de generar un mensaje BGP de forma correcta.
2. Modifique su código para que revise si el contenido de un paquete IP corresponde a un mensaje `START_BGP`. En caso de que el mensaje del paquete IP corresponda a un mensaje `START_BGP` haga que su código invoque a la función `run_BGP()` (el funcionamiento de run_BGP() se describe en el siguiente paso).
3. Cree la función **run_BGP()**. Esta función se encargará de correr BGP. Su función `run_BGP()` primero deberá enviar un mensaje `START_BGP` a sus vecinos y luego deberá ejecutar BGP según lo explicado en la sección [Mini-Internet + BGP](./mini_internet_bgp.md). Si recibe un mensaje `START_BGP` dentro de su función `run_BGP()` simplemente debe ignorar dicho mensaje. Recuerde que dentro de BGP su router enviará sus rutas actualizadas a sus vecinos solo si su tabla de rutas cambió. Para saber cuándo se debe detener la función `run_BGP()`, ponga un timer dentro de su función que cuente el tiempo transcurrido desde el último envío de rutas. Su timer deberá ser reseteado cada vez que el router envíe mensajes `BGP_ROUTES`. Si su router no ha enviado mensajes `BGP_ROUTES` antes de que el timer termine, asumiremos que las tablas de rutas se han estabilizado por lo que deberá salir de la función `run_BGP()` y retornar el string de la tabla de rutas. Por ahora haga que su timer dure 10 segundos.

    **Test:** Pruebe que su BGP funciona utilizando la configuración de 3 routers. En particular, verifique que los routers R1 y R3 tienen caminos entre sí y que estos caminos pasan por R2.
4. Modifique su código para que imprima en pantalla la tabla de rutas obtenida de la función `run_BGP()` y luego las guarde en un archivo. Haga que su router use dicho archivo como tabla de rutas.

    **Test:** Pruebe generar las rutas para la configuración de 5 routers utilizada en la actividad de fragmentación (recuerde que deberá modificar estos archivos para que sigan la estructura de rutas BGP). Usando las rutas generadas por su código, pruebe que puede enviar mensajes entre 2 routers sin problemas. Verifique que estos mensajes siempre pasen por el mismo camino.

## Pruebas

Para esta actividad queremos probar que su código router es capaz de encontrar las rutas dado que solo sabe cómo llegar a sus vecinos. Para las pruebas considere la estructura de 5 routers de la actividad anterior con 2 routers extra R6 y R7 como se muestra en la figura. Asuma que cada enlace en esta nueva configuración tiene un MTU = 1000.

```bash
 R1 <--------> R2 <--------> R3                        

            ^             ^                      

            |             |                      

            v             v                      
R4 <--------> R5 <--------> R6 <--------> R7
```

- Primero ponga a correr su algoritmo BGP en cada router y verifique que sus tablas de ruta convergen. Observe las tablas de ruta impresas y compruebe que cada router tiene una ruta a cada uno de los otros 6 routers dentro de la configuración.
- Pruebe sus nuevas tablas de rutas usando `netcat`. Para ello pruebe enviando mensajes desde R7 a R1, de R7 a R4, y de R7 a R3. ¿Quién imprime el mensaje? Recuerde que puede usar `netcat` como se muestra a continuación. Añada sus observaciones al informe.

```bash
$ nc -u 127.0.0.1 8887 << EOF
127.0.0.1,8881,10,57,0,00000010,0
hola 8881!
EOF
```

- Ahora suponga que inicialmente solo tiene los primeros 6 routers (R1 a R6) tal que echa a correr BGP por primera vez considerando solo a estos 6 routers. Suponga que R7 se une a la red en un momento posterior a esta llamada inicial de BGP y que R7 quiere ser invisible para R4 ¿Cómo puede modificar la tabla de rutas inicial de R7 para que, luego de ejecutar `run_BGP()`, R4 no pueda alcanzar a R7? Pruebe que su respuesta funciona utilizando su código. Añada su respuesta y observaciones al informe.
