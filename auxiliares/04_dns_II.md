# DNS

## P1. Servidores DNS y cache

**1. Imaginen, estan en la universidad y saben que el DCC tiene instalado un server DNS para todos los equipos dentro de la red, Como puedo saber si un sitio externo ha sido accesado por algun dcciano?**

Comparando el tiempo de preguntar la direccion dos veces: si la primera vez es mucho mayor que la siguiente, no se habia accesado. Esto, pues los DNS mantienen un cache de los sitios ya preguntados.

**2. Que consecuencias tendria para el DNS que no se guarden cosas en cache?**

Sin cache, los resolvers siempre partirian preguntando desde la raiz en el arbol de dominio. Si multiplicamos este efecto por muchos usuarios, esto colapsaria los servidores de nombre.

**3. Suponga que todos los servidores DNS del mundo dejan de funcionar y que todas las caches expiran. Como puede usted acceder a U-Cursos en ese caso?**

Sabiendose de memoria la IP.

## P2. Tipos de resolver

**1. Suponga que usted tiene varios resolvers DNS a quien hacerle consultas. Como podria saber usted cuales de los resolvers son iterativos y cuales recursivos? Suponga que los resolvers no tienen cache.**

Como suponemos que los resolvers no tienen cache, entonces tendran que siempre acceder a la raiz. La forma de saber cuales son iterativos y recursivos, es hacer una consulta cualquiera por alguna IP, si el resolver nos devuelve la respuesta, entonces es recursivo, por otro lado, si nos devuelve una delegacion, entonces es iterativo.

**2. Cual es la diferencia entre un servidor de nombre primario, uno secundario y uno cache?**

Un servidor de nombre primario puede manejar, editar, agregar o borrar registros (zone files) y ademas pueden responder consultas. Los servidores secundarios tambien pueden responder consultas, pero reciben registros DNS del servidor primario y no pueden modificarlos. Por ultimo, los servidores cache consultaron en algun momento a un servidore de dominio y guardaron la informacion recibida, con la cual pueden resolver queries, a la respuesta deben agreagar que no estan a cargo del dominio, para que asi los clientes decidan si utilizar esa informacion o no.

## P3. Red de servidores de contenido

**Se le pide crear una red de servidores de contenido con el objetivo de garantizar una distribucion rapida y efectiva de la informacion a los clientes. Es importante asegurar que, en caso de que la red se divida en dos, la distribucion de contenido pueda continuar sin interrupciones para todos los usuarios. Asimismo, si uno de los nodos de la red falla, es fundamental que la informacion alojada en ese servidor siga siendo accesible para los usuarios. Con los conocimientos que posee actualmente sobre redes, Como lo haria? Puede aprovechar alguno de los protocolos vistos en clase?**

Efectivamente, se pueden aprovechar los protocolos vistos. Se puede realizar con HTTP, pero por lo que se esta pidiendo es mejor con DNS. Esto debido a que se puede copiar la idea, o derechamente utilizar una version modificada del protocolo, donde las direcciones IP de los servidores de contenido seria lo que encontramos con nuestros resolvers, para asi aprovechar anycast. La ventaja de usar este flujo, es aprovechar la rapidez que tiene para contactarse con diversos clientes. Ademas, la idea es que el sistema sea redundante, para que asi, si se cae algun nodo, no se pieda el acceso.

## P4. Servidores DNS con ansiedad por tanta consulta :(

**Si un servidor DNS recibe una cantidad excesiva de consultas, puede provocar una sobrecarga y un rendimiento lento o incluso errores en la resolucion de DNS, Como se puede prevenir o mitigar la sobrecarga de consultas DNS y mantener un rendimiento optimo del servidor?**

Primero, lo mas importante es utilizar la memoria cache, para disminuir el tiempo de respuesta y tambien la cantidad de consultas que debe realizarse al servidor. Tambien se puede implementar un sistema distribuido, con servidores DNS forwarders, los cuales reenvian la consulta a otro servidor para que haga la recursion y asi no esten tan cargados ellos mismos. Se puede configurar el servidor para limitar la cantidad de consultas que puede recibir, y simplemente bloquear nuevas solicitudes si es que esta lleno. Finalmente, se puede monitorear la actividad en el servidor, e intentar identificar patrones de consulta inusuales (o maliciosos), para poder tomar medidas preventivas.
