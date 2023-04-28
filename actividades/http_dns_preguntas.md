# Preguntas Actividades HTTP y DNS

## HTTP

**Su proxy maneja correctamente los tests pedidos. Pero cuando se intenta acceder a info.cern.ch/, su código se cae (la página utiliza http, no https) ¿Por qué cree que ocurre? Justifique basándose en su código.**

En este caso testeando el proxy vemos que el error se produce debido a que el nombre de dominio no existe y por tanto al conectarse con el socket lanza una excepcion. La funcion encargada de extraer el nombre de dominio de la request, `get_host()`, retorna, segun el codigo entregado en la tarea, el string `"a"` y como no existe tal nombre de dominio simplemente lanza la excepcion. Antes de dar una solucion al problema es necesario mencionar que la funcion `get_host()` posee un error de tipeo, el retorno en caso de no obtener el nombre de dominio no es el string `"a"` sino que debiese ser el string vacio `""`. Dada esta explicacion podemos observar que el dominio al cual intenta conectarse a traves de nuestro proxy es `info.cern.ch/`, el cual posee como subdominio `.ch`, este es el top-level domain para Suiza, sin embargo nuestra funcion `get_host()` al realizar el parse a traves de una expresion regular donde solo se busca el patron `.cl` o `.com` lanza la excepcion, pues no la encuentra, y al atraparla, entrega el string `"a"`, la forma de solucionar este problema es agregando este dominio al conjunto de coincidencias de la expresion regular de nuestra funcion, adicionalmente se podria implementar una lista con los top-level domain mas importantes para disminuir la posibilidad de que un error como este vuelva a ocurrir al momento de ingresar un dominio cualquiera.

## DNS

**Su resolver no utiliza el caché para los pasos intermedios (i.e. luego de haber resuelto eol.uchile.cl, al preguntar por www.uchile.cl no se tiene guardado uchile.cl) ¿Qué cambio le haría a su implementación para que funcionara de esa forma?**

En este caso bastaria con eliminar la condicion de guardado en cache solo al inicio en la funcion `resolver()`, esta funcion fue diseñada para guardar en cache solo la consulta inicial, es decir, en el caso del ejemplo guarda `eol.uchile.cl`, si queremos que exista cache sobre los pasos intermedios para guardar los subdominios basta con eliminar esta condicion (`if ns == '.':`).
