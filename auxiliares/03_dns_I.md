# DNS (Domain Name System)

## P1. Conexiones a DNS

**Que es anycast? Que ventajas tiene su uso en DNS?**

Anycast escoge algun equipo para hablar dentro de un conjunto de equipos de acuerdo a algun parametro. Muchas veces este parametro es ubicacion geografica. Como los DNS tienen servidores por todo el mundo, usando anycast pueden elegir el que les quede mas cerca, reduciendo el tiempo de respuesta.

**Que problemas de seguridad pueden surgir de conectarse a ISPs y/o DNS?**

A parte de temas de hackeos, estas entidades tienen acceso a todo lo que hacemos. Aca ISPs y DNSs pueden terminar actuando como entidades maliciosas.

## P2. TTL (Time To Live)

**Las entradas DNS tienen un tiempo de vida conocido como TTL. Que significa el TTL cuando una respuesta viene de un server autoritativo? Y cuando vienen de uno no autoritativo?**

El TTL corresponde al Time To Live. El TTL en un servidor DNS Autoritativo corresponde a la cantidad de tiempo que mantengo una respuesta guardada en cache (memoria de rapido acceso). En el caso de un servidor DNS No Autoritativo el TTL nos indica por cuanto tiempo la informacion de dicho servidor esta respaldad por el servidor Autoritativo.

## P3. Verdadero o False

**1. Un DNS resolver siempre recorre el arbol de dominio desde la raiz.** *R: Falso. Gracias al cache, muy pocas veces termina recorriendo todo el arbol desde la raiz.*

**2. La delegacion de responsabilidades va hacia arriba en el arbol de dominio, esto es, por ejemplo: `uchile.cl` delega en `.cl` la resolucion de esos nombres.** *R: Falso. Se recorre desde la raiz del arbol hacia la izquierda.*

**3. Al recorrer el arbol de dominio de forma iterativa, luego de hacer una consulta DNS, recibimos la respuesta final a la consulta, o bien un mensaje de error.** *R: Falso. Cuando se realiza de forma iterativa, cada server entrega la mejor respuesta que tiene para la consulta. Luego el resolver sigue preguntando hasta encontrar la respuesta final.*

**4. Existen servidores primarios que se encargan de actualizar la informacion de secundarios.** *R: Verdadero. Los servidores primarios son los que se encargan de manejar la informacion e ir actualizandola acordemente. Los secundarios solo pueden leer informacion.*

**5. Una vez guardo informacion DNS en cache puedo seguir usandola de forma indefinida.** *R: Falso. La informacion de un dominio puede cambiar, por lo que es necesario ir actualizandola cada cierto tiempo.*

**6. El tipo de registro DNS indica que clase de informacion contiene el campo `Record Data`.** *R: Verdadero. Existen diversos tipos de registro DNS, los cuales os dicen como es la informacion contenida en `Record Data`.*

**7. Recibir un registro del tipo SOA indica que hemos recibido un alias apuntando a otro dominio.** *R: Falso. SOA es Start Of (a zone of) Authority. Especifica informacion autoritativa sobre una zona DNS, dentro de la cual se puede encontrar especificados diversos datos, tales como el servidor de nombre primario, mail administrador de la zone, TTL y otros.*

**8. Similar a los headers en HTTP, en DNS los headers se escriben en texto plano.** *R: Falso. Los headers DNS estan escritos en bits, los cuales se codifican en lineas de 16 bits, o 2 bytes, cada una.*

**9. El puerto por default para servidores DNS es el 53 y este es un puerto reservado.** *R: Verdadero. Asi como para HTTP el puerto era 80, o HTTPS es 443, en el caso de DNS el puerto reservado es el numero 53.*

**10. El ID de una respuesta es el mismo que el ID de la consulta.** *R: Verdadero. Estos ID  deben ser el mismmo, para asi poder identificar que respuesta corresponde a que pregunta.*

**11. Cuando un servidor DNS responde una pregunta (Question), este reutiliza el mensaje DNS que recibio y anhade la respuesta en la seccion "Answer" del mismo.** *R: Verdadero. El servidor no crea un nuevo mensaje, solo anhade su respuesta en la seccion Answer, modifica algunos pocos headers, y luego envia esa respuesta al resolver.*
