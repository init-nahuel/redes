# Tabla de rutas con BGP

- [Tabla de rutas con BGP](#tabla-de-rutas-con-bgp)

En nuestro mini-Internet original las tablas de rutas tenían la siguiente estructura.

```bash
[Red destino (CIDR)] [Puerto_Inicial] [Puerto_final] [IP_siguiente_salto] [Puerto_siguiente_salto] [MTU]
```

Sin embargo, al agregar BGP es necesario hacer que la tabla de ruta contenga la ruta completa [ruta ASN] de forma inversa. Es decir una [ruta ASN] contenida en la tabla de rutas tendrá el siguiente formato:

```bash
[ASN de destino] [ASN intermedio] (...) [ASN de origen]
```

De esta forma, si tenemos: `[ruta ASN] = 8885 8883 8882 8881`, para llegar de 8881 a 8885 podemos seguir la ruta:

```bash
8881 -> 8882 -> 8883 -> 8885
```

En caso de que 2 nodos sean vecinos, veremos rutas del estilo [ruta ASN] = 8882 8881 , pues para llegar de 8881 a 8882 basta con tomar la ruta 8881 -> 8882.

Esto significa que ahora cada entrada en la tabla de rutas no tiene un largo fijo, si no que tiene un largo variable. Para la actividad usaremos el siguiente formato:

```bash
[Red destino (CIDR)] [ruta ASN] [IP_siguiente_salto] [Puerto_siguiente_salto] [MTU]
```

Es decir, cambiamos el rango de puertos por la ruta ASN. En este caso reemplazamos el área " [Puerto_Inicial] [Puerto_final] " por la ruta [ruta ASN]. Con esto obtenemos la siguiente estructura:

```bash
[Red destino (CIDR)] [ruta ASN] [IP_siguiente_salto] [Puerto_siguiente_salto] [MTU]
```

Sabemos que `[ruta ASN] = [ASN de destino] [ASN intermedio] (...) [ASN de origen]` , es decir, cada línea de la tabla de rutas se vería como:

```bash
[Red destino (CIDR)] [ASN de destino] [ASN intermedio] (...) [ASN de origen] [IP_siguiente_salto] [Puerto_siguiente_salto] [MTU]
```

Luego los primeros 2 elementos de la línea nos indican la IP y puerto de destino. Mientras que los últimos 3 elementos de la línea nos indican la IP y puerto del siguiente salto y el MTU del enlace.
