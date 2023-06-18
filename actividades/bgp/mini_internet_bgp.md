# Mini-Internet + BGP

- [Mini-Internet + BGP](#mini-internet--bgp)
  - [Sistemas autónomos y números de sistema autónomo](#sistemas-autónomos-y-números-de-sistema-autónomo)
  - [Mensajes BGP](#mensajes-bgp)
  - [Estructura \[ruta ASN\]](#estructura-ruta-asn)
  - [Algoritmo BGP](#algoritmo-bgp)
  - [Ejemplo](#ejemplo)

## Sistemas autónomos y números de sistema autónomo

Como se vio en el video de BGP, un sistema autónomo (AS por sus siglas en inglés) corresponde a una red que tiene su propio sistema de ruteo interno. Cada sistema autónomo se identifica según un Autonomous System Number (ASN).

Para efectos de nuestro mini-Internet, vamos a suponer que todos los routers son routers de borde, es decir, todos los routers participan de BGP externo. Por simplicidad asumiremos que el número de sistema autónomo al que pertenece cada router es el mismo que el número de puerto en el cual dicho router se encuentra escuchando. Así si R1 está corriendo en el puerto 8881, diremos que R1 pertenece al sistema autónomo ASN 8881.

## Mensajes BGP

Para poder correr BGP vamos a necesitar mensajes para indicar el inicio de BGP, y mensajes que permitan que un router le comunique a otros las rutas que conoce. Para ello encapsularemos los mensajes BGP en el área de [mensaje] de nuestro datagrama IP. Recuerde que el formato de datagrama en este punto es:

```bash
[Dirección IP],[Puerto],[TTL],[ID],[Offset],[Tamaño],[FLAG],[mensaje]
```

De esta forma tendremos los siguientes mensajes BGP:

- **Mensaje de inicio o START_BGP**: Este mensaje simplemente contiene el string `START_BGP` en el área de [mensaje] del datagrama IP. El mensaje `START_BGP` le anuncia al router que el algoritmo de BGP va a comenzar.
- **Mensajes de rutas BGP o `BGP_routes`:** Estos mensajes contienen todas las rutas que conoce un router en particular. Al iniciar BGP, cada router solo conoce las rutas que van desde sí mismo hacia sus vecinos. Conforme cada router va recibiendo mensajes con las rutas de sus vecinos, este va actualizando sus rutas. Los mensajes de rutas BGP se encuentran dentro del área de [mensaje] del datagrama IP, y tienen el siguiente formato:

    ```bash
    BGP_ROUTES
    888X
    [ruta ASN]
    (... más rutas)
    [ruta ASN]
    END_BGP_ROUTES
    ```

  - En la primera línea anunciamos que éste es un mensaje BGP de rutas.
  - En la segunda línea comunicamos el ASN asociado al router que envío este mensaje. En el caso del ejemplo, este es un router que pertenece al AS cuyo ASN es 888X.
  - A partir de la tercera línea listamos todas las rutas que el router emisor conoce. Cada [ruta ASN] corresponde a una lista de ASNs que corresponden al camino completo entre el ASN de destino y el ASN de origen.
  - La última línea marca el fin del mensaje.

## Estructura [ruta ASN]

En la sección anterior se explicó cómo enviar mensajes de rutas BGP o BGP_routes. Aquí vimos que cada [ruta ASN] es una lista de ASNs que corresponden al camino completo entre el ASN de destino y el ASN de origen. Para que esto quede más claro veamos de forma más detallada cómo se podría ver una [ruta ASN].

Una [ruta ASN] contiene el camino completo para llegar desde el ASN de origen al de destino en orden inverso, de la siguiente manera:

```bash
[ASN de destino] [ASN intermedio] (...) [ASN de origen]
```

De esta forma, si tenemos: `[ruta ASN] = 8885 8883 8882 8881`

Entonces se está indicando que para llegar de 8881 a 8885 podemos seguir la ruta:

```bash
8881 -> 8882 -> 8883 -> 8885
```

En caso de que 2 nodos sean vecinos, veremos rutas del estilo [ruta ASN] = 8882 8881 , pues para llegar de 8881 a 8882 basta con tomar la ruta 8881 -> 8882.

## Algoritmo BGP

Para nuestro mini-Internet seguiremos el siguiente algoritmo:

1. Primero enviamos a cada router el mensaje `START_BGP` para que estos comiencen a ejecutar el algoritmo BGP.
2. Luego, cada router debe enviar todas las rutas que este conozca a sus vecinos. Al correr BGP por primera vez, el router solo conoce la ruta hacia sus vecinos.
3. Cuando un router recibe un mensaje `BGP_routes` desde un vecino este revisa todas las rutas contenidas en él.
4. Al revisar las rutas: si en la ruta aparece el ASN del router de recepción, se descarta la ruta pues mantener dicha ruta podría generar ciclos.
5. Al revisar las rutas: si no conozco el ASN de destino (el primer ASN en la ruta) entonces el router lo agrega a su tabla de rutas. Como la ruta original no contiene el ASN del router de recepción, este debe agregarse al final de la ruta. Ej: si el router asociado a 8881 recibe la ruta `[ruta ASN] = 8885 8883 8882` desde el router asociado a 8882 y no tenía una ruta hacia 8885, entonces añade a su tabla de rutas la ruta `[ruta ASN] = 8885 8883 8882 8881`.
6. Al revisar las rutas: si el router ya tiene una ruta para el ASN de destino, deberá revisar cuál es la ruta más corta y quedarse con esa. Si son de igual largo puede simplemente quedarse con la que ya tenía.
7. Si luego de revisar las rutas que le han llegado al router este actualiza o cambia su tabla de rutas, entonces debe volver a enviar sus rutas a sus vecinos con un mensaje `BGP_routes`.
8. Este proceso se repite hasta que las tablas de rutas dejen de cambiar.

## Ejemplo

Veamos cómo funcionaría BGP en nuestro mini-Internet. Suponga que tiene la siguiente configuración donde R1 está asociado a 8881, R2 a 8882, y R3 a 8883.

```bash
R1 <--------> R2 <--------> R3 
```

Inicialmente cada router solo conoce el camino a sus vecinos. Luego, una vez cada router haya recibido el mensaje `START_BGP`, vamos a ver que:

- El router R1 le envía el siguiente mensaje BGP_routes a sus vecinos. En este caso, su único vecino es R2.

  ```bash
  BGP_ROUTES
  8881
  8882 8881
  END_ROUTES
  ```

- El router R2 le envía el siguiente mensaje BGP_routes a sus vecinos. En este caso sus vecinos son R1 y R3.

  ```bash
  BGP_ROUTES
  8882
  8881 8882 
  8883 8882
  END_ROUTES
  ```

- El router R3 le envía el siguiente mensaje BGP_routes a sus vecinos. En este caso, su único vecino es R2.

  ```bash
  BGP_ROUTES
  8883
  8882 8883
  END_ROUTES
  ```

Con esto R2 va a recibir mensajes desde R1 y R3. Como ambos mensajes solo tienen rutas que contienen a R2, este los ignora y no hace cambios a su tabla de rutas.

En el caso de R1, este va a recibir el mensaje de R2 y va a ver que este contiene una ruta hacia R3, para quien no tiene ruta, por lo que va a incorporar esta nueva ruta a su tabla. Al incorporar la nueva ruta, R1 cambia su tabla de rutas por lo que le comunica a sus vecinos el cambio con el siguiente mensaje. Aquí, su único vecino es R2.

```bash
BGP_ROUTES
8881
8882 8881
8883 8882 8881
END_ROUTES
```

El caso de R3 es análogo al de R1. Luego este va actualizar su ruta y enviarle a su único vecino (R2) el siguiente mensaje.

```bash
BGP_ROUTES
8883
8882 8883
8881 8882 8883
END_ROUTES
```

Finalmente R2 va a recibir los nuevos mensajes de R1 y R3. Nuevamente observa que todas las rutas que le llegan lo contienen, por lo que no realiza ningún cambio a su tabla de rutas.

De esta forma observamos que las tablas de ruta han dejado de cambiar y por lo tanto se finaliza el algoritmo.
