# Mini-Internet + BGP

- [Mini-Internet + BGP](#mini-internet--bgp)
  - [Sistemas autónomos y números de sistema autónomo](#sistemas-autónomos-y-números-de-sistema-autónomo)
  - [Mensajes BGP](#mensajes-bgp)
  - [Estructura \[ruta ASN\]](#estructura-ruta-asn)

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