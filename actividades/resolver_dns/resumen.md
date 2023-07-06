# Actividad: construyamos un resolver

- [Actividad: construyamos un resolver](#actividad-construyamos-un-resolver)
  - [Antes de comenzar](#antes-de-comenzar)
  - [Actividad](#actividad)
  - [Pruebas](#pruebas)
    - [Pruebas de funcionalidad](#pruebas-de-funcionalidad)
    - [Experimentos](#experimentos)
  - [Material e indicaciones para la actividad](#material-e-indicaciones-para-la-actividad)

En esta actividad programaremos nuestro propio resolver.

## Antes de comenzar

- **Crear mensajes DNS:** En esta actividad deberá programar un resolver. Para ello es necesario que su resolver pueda comunicarse con servidores DNS, los cuales se comunican a través de mensajes DNS (tal como los servidores HTTP se comunican usando mensajes HTTP). Para ver en detalle cómo construir y leer mensajes DNS vaya a la sección [Programando DNS con sockets](/ejemplos_por_materia/dns_sockets/resumen.md). Importante: para esta actividad puede utilizar tanto hexadecimal como dnslib. Para ver más de cómo utilizar dnslib utilice el código provisto en [Material e indicaciones para la actividad](#material-e-indicaciones-para-la-actividad).
- **Comando dig**:  El comando `dig` (Domain Information Groper) nos permite hacer consultas DNS y nos muestra la respuesta de la consulta, por lo que es especialmente útil para probar el funcionamiento de un resolver. Para hacer consultas DNS con dig a un resolver corriendo en una IP y puerto específicos puede usar el siguiente comando:

    ```bash
    $ dig -p[puerto] @[IP] [domain]
    ```

    ¿Qué IP le entrega dig al preguntarle a `8.8.8.8` en el puerto 53 por [example.com](example.com? ¿Cómo se compara con la IP obtenida en la sección [Programando DNS con sockets](/ejemplos_por_materia/dns_sockets/resumen.md)?

- **Puerto default DNS**: Para comunicarnos con servidores DNS nos vamos a conectar al puerto 53, salvo que se indique lo contrario. Note que en el resolver que programaremos en esta actividad usaremos el puerto 8000. Haremos esto pues el puerto 53 se encuentra dentro de los llamados puertos reservados, los cuales se reservan para uso del sistema operativo o para protocolos conocidos como lo es el protocolo DNS.

## Actividad

En esta actividad programaremos un resolver DNS. Esta actividad está contemplada para ser realizada en el transcurso de las semanas 4 y 5. Por simplicidad asumiremos que el tipo de consultas que se harán desde el cliente a su Resolver serán siempre del tipo A, es decir, preguntarán por la dirección IPv4 del dominio consultado. Para crear su resolver siga los siguientes pasos:

1. Cree un archivo llamado `resolver.py`. En él construya un código que le permita obtener mensajes DNS. Para esto cree un socket apropiado que se encuentre asociado a la dirección `('localhost', 8000)` (¿Qué tipo de socket debe usar?). Luego haga que su socket pueda recibir mensajes en un loop, aquí puede utilizar un tamaño de buffer "grande" pues en esta actividad no nos preocuparemos de manejar mensajes más grandes que el tamaño del buffer. Finalmente haga que su código imprima en pantalla el mensaje recibido tal como se recibió, es decir, no utilice `decode()`.

    **Test**: Obtenga un mensaje DNS sin procesar utilizando su código. Para ello corra su código y utilice el comando `dig` en otra terminal.

    ```bash
    $ dig -p8000 @localhost example.com
    ```

    Note que en consola va a recibir una respuesta "connection timed out", esto es lo esperado pues su código en este punto es capaz de recibir un mensajes DNS, pero no de responder.

2. Programe una función para parsear mensajes DNS. Es decir, programe una función que sea capaz de tomar un mensaje DNS y transformarlo a alguna estructura de datos manejable. Para esta parte podrá usar tanto hexadecimal con binascii como dnslib. Sin embargo, por simplicidad de implementación se recomienda el uso de dnslib. Para crear sus funciones puede usar como guía la información y código presentado en la sección anterior Programando DNS con sockets. Si decide utilizar dnslib se recomienda revisar el material provisto más abajo en la sección Material e indicacciones para la actividad.

    **Nota**: Se recomienda guardar la siguiente información en su estructura: Qname, ANCOUNT, NSCOUNT, ARCOUNT, la sección Answer, la sección Authority y la sección Additional.

    **Test**: Obtenga un mensaje DNS (puede hacerlo de la misma forma que el Test del paso 1) y utilizando la función que acaba de programar verifique que puede transformar el mensaje DNS a la estructura de datos elegida.

3. Usando lo programado en los pasos anteriores, procederemos a crear nuestro resolver. Para ello cree una función llamada `resolver(mensaje_consulta)`, la cual recibe el mensaje de query en bytes obtenido desde el cliente. Dentro de esta función, siga el siguiente procedimiento para obtener la respuesta:

   a. Envíe el mensaje query al servidor raíz de DNS y espere su respuesta. Se recomienda dejar la IP del servidor raíz en una variable global de su programa. La dirección del servidor raíz es la siguiente: `192.33.4.12` y el puerto es el correspondiente a servidores DNS.

   b. Si el mensaje answer recibido tiene la respuesta a la consulta, es decir, viene alguna respuesta de tipo A en la sección Answer del mensaje, entonces simplemente haga que su función retorne el mensaje recibido.

   c. Si la respuesta recibida corresponde a una delegación a otro Name Server, es decir, vienen respuestas de tipo NS en la sección Authority, revise si viene alguna respuesta de tipo A en la sección Additional.

    - Si encuentra una respuesta tipo A, entonces envíe la query del paso a) a la primera dirección IP contenida en la sección Additional.

    - En caso de no encontrar alguna IP en la sección Additional, tome el nombre de un Name Server desde la sección Authority y use recursivamente su función para resolver la IP asociada al nombre de dominio del Name Server. Una vez obtenga la IP del Name Server, envíe la query obtenida en el paso a) a dicha IP. Una vez recibida la respuesta, vuelva al paso b).

    e. Si recibe algún otro tipo de respuesta simplemente ignórela.

    Finalmente utilice esta función en su programa principal para así resolver las consultas que usted recibe desde los clientes. Para ello entréguele directamente el mensaje recibido desde el cliente a su función `resolver()`. Luego, obtenga el resultado que retorna su función y si el resultado no es vacío, envíe la respuesta al cliente.

    **Test**: Consulte a través de dig la IP de [www.uchile.cl](www.uchile.cl) al resolver de google con el siguiente comando.

    ```bash
    $ dig @8.8.8.8 www.uchile.cl
    ```

    Repita la consulta con dig, pero esta vez haga la consulta a su resolver y compare las respuestas.

    ```bash
    dig -p8000 @localhost www.uchile.cl
    ```

4. Agregue un modo debug a su resolver, que vaya mostrando las consultas internas que esta va haciendo a los distintos Name Servers para obtener la respuesta. En él muestre el nombre del dominio que está consultando, el nombre del Name Server a quien le está consultando, y finalmente la dirección IP a la que está preguntando. A continuación se muestra un ejemplo de modo debug:

    ```bash
    (debug) Consultando 'www.uchile.cl' a '.' con dirección IP '192.33.4.12'
    ```

    **Test**: Repita el test del paso 3) y verifique que su modo debug funciona de acuerdo a las especificaciones.

5. Ahora agregaremos un "caché" a su resolver. Para ello su resolver guardará los 5 dominios que más se repiten dentro de las últimas 20 consultas que ha recibido. Para almacenar estos datos puede utilizar la estructura de datos que le parezca conveniente (no es necesario guardar el caché en un archivo). Cada consulta que reciba su resolver primero deberá ser buscada en el caché como se explicó en el video/clase. En caso que se tenga guardada la consulta en caché, su resolver responderá con la IP almacenada, en caso contrario su resolver deberá hacer consultas pertinentes como antes. Modifique su modo debug para que indique si su código está utilizando el caché.

    **Test**: Repita una consulta varias veces y verifique que su código utiliza el caché cuando corresponde.

## Pruebas

La sección de pruebas consta de dos partes. Una parte de pruebas de funcionalidad y una de experimentos. Las observaciones de sus experimentos deben ser anotadas en sus informes según lo que se pida.

### Pruebas de funcionalidad

- El comando `dig -p8000 @localhost eol.uchile.cl` responde `146.83.63.70`
- Si al iniciar su resolver hace una consulta a [eol.uchile.cl](eol.uchile.cl), la segunda consulta a [eol.uchile.cl](eol.uchile.cl) con `dig -p8000 @localhost` da la misma dirección IP, pero respondió el caché (lo puede ver en modo debug).
- El comando `dig -p8000 @localhost www.uchile.cl` resuelve a `200.89.76.36`
- El comando `dig -p8000 @localhost cc4303.bachmann.cl` resuelve a `104.248.65.245`

### Experimentos

- Intente resolver el siguiente dominio con su programa [www.webofscience.com](www.webofscience.com) ¿Resuelve su programa este dominio? ¿Qué sucede? ¿Por qué? ¿Cómo arreglaría usted este problema? Anote las respuestas a estas preguntas en su informe.
- Ejecute el comando `dig -p8000 @localhost www.cc4303.bachmann.cl` ¿Qué ocurre? ¿Qué habría esperado que ocurriera? Anote sus observaciones en su informe. Contraste sus observaciones con la respuesta de ejecutar `dig @8.8.8.8 www.cc4303.bachmann.cl` y utilice sus conocimientos sobre DNS para explicar por qué ocurre esto.
- Realice varias consultas a un mismo dominio y a través del modo debug vea a qué Name Servers y direcciones IP le pregunta su resolver en cada consulta. ¿Son siempre los mismos Name Servers? ¿Por qué cree usted que sucede esto? Anote las respuestas a estas preguntas en su informe.

## Material e indicaciones para la actividad

- **¿Cómo puede saber si su resolver funciona correctamente?** Para ver que su Resolver funciona, puede analizar el tráfico que hay en su red local usando tcpdump para que este le reporte el tráfico que entra y sale por el puerto en el que sirve su Resolver.

    ```bash
    $ sudo tcpdump -v -i lo port 5300
    ```

- **Añadir answer a dnslib:**

    ```python
    from dnslib.dns import RR, A
    from dnslib import DNSRecord, DNSHeader, DNSQuestion 

    # Modificar el mensaje de pregunta (opción 1) 
    dns_query.add_answer(RR(qname, QTYPE.A, rdata=A(ip_answer)))
    
    # Modificar el mensaje de pregunta (opción 2)
    dns_query.add_answer(*RR.fromZone("{} A {}".format(qname, ip_answer)))
    
    # Crear un nuevo mensaje que contenga la pregunta y la respuesta
    ```

- **Código de ejemplo dnslib:**

    ```python
    import socket
    from dnslib import DNSRecord
    from dnslib.dns import CLASS, QTYPE
    import dnslib


    def send_dns_message(query_name, address, port):
        # Acá ya no tenemos que crear el encabezado porque dnslib lo hace por nosotros, por default pregunta por el tipo A
        qname = query_name
        q = DNSRecord.question(qname)
        server_address = (address, port)
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            # lo enviamos, hacemos cast a bytes de lo que resulte de la función pack() sobre el mensaje
            sock.sendto(bytes(q.pack()), server_address)
            # En data quedará la respuesta a nuestra consulta
            data, _ = sock.recvfrom(4096)
            # le pedimos a dnslib que haga el trabajo de parsing por nosotros
            d = DNSRecord.parse(data)
        finally:
            sock.close()
        # Ojo que los datos de la respuesta van en en una estructura de datos
        return d

    def print_dns_reply_elements(dnslib_reply):
        # header section
        print(">>--------------- HEADER SECTION ---------------<<\n")
        print("----------- dnslib_reply.header -----------\n{}\n".format(dnslib_reply.header))

        qr_flag = dnslib_reply.header.get_qr()
        print("-> qr_flag = {}".format(qr_flag))

        number_of_query_elements = dnslib_reply.header.q
        print("-> number_of_query_elements = {}".format(number_of_query_elements))

        number_of_answer_elements = dnslib_reply.header.a
        print("-> number_of_answer_elements = {}".format(number_of_answer_elements))

        number_of_authority_elements = dnslib_reply.header.auth
        print("-> number_of_authority_elements = {}".format(number_of_authority_elements))

        number_of_additional_elements = dnslib_reply.header.ar
        print("-> number_of_additional_elements = {}".format(number_of_additional_elements))
        print(">>----------------------------------------------<<\n")

        print(">>---------------- QUERY SECTION ---------------<<\n")
        # query section
        all_querys = dnslib_reply.questions  # lista de objetos tipo dnslib.dns.DNSQuestion
        print("-> all_querys = {}".format(all_querys))

        first_query = dnslib_reply.get_q()  # primer objeto en la lista all_querys
        print("-> first_query = {}".format(first_query))

        domain_name_in_query = first_query.get_qname()  # nombre de dominio por el cual preguntamos
        print("-> domain_name_in_query = {}".format(domain_name_in_query))

        query_class = CLASS.get(first_query.qclass)
        print("-> query_class = {}".format(query_class))

        query_type = QTYPE.get(first_query.qtype)
        print("-> query_type = {}".format(query_type))

        print(">>----------------------------------------------<<\n")

        print(">>---------------- ANSWER SECTION --------------<<\n")
        # answer section
        if number_of_answer_elements > 0:
            all_resource_records = dnslib_reply.rr  # lista de objetos tipo dnslib.dns.RR
            print("-> all_resource_records = {}".format(all_resource_records))

            first_answer = dnslib_reply.get_a()  # primer objeto en la lista all_resource_records
            print("-> first_answer = {}".format(first_answer))

            domain_name_in_answer = first_answer.get_rname()  # nombre de dominio por el cual se está respondiendo
            print("-> domain_name_in_answer = {}".format(domain_name_in_answer))

            answer_class = CLASS.get(first_answer.rclass)
            print("-> answer_class = {}".format(answer_class))

            answer_type = QTYPE.get(first_answer.rtype)
            print("-> answer_type = {}".format(answer_type))

            answer_rdata = first_answer.rdata  # rdata asociada a la respuesta
            print("-> answer_rdata = {}".format(answer_rdata))
        else:
            print("-> number_of_answer_elements = {}".format(number_of_answer_elements))

        print(">>----------------------------------------------<<\n")

        print(">>-------------- AUTHORITY SECTION -------------<<\n")
        # authority section
        if number_of_authority_elements > 0:
            authority_section_list = dnslib_reply.auth  # contiene un total de number_of_authority_elements
            print("-> authority_section_list = {}".format(authority_section_list))

            if len(authority_section_list) > 0:
                authority_section_RR_0 = authority_section_list[0]  # objeto tipo dnslib.dns.RR
                print("-> authority_section_RR_0 = {}".format(authority_section_RR_0))

                auth_type = QTYPE.get(authority_section_RR_0.rtype)
                print("-> auth_type = {}".format(auth_type))

                auth_class = CLASS.get(authority_section_RR_0.rclass)
                print("-> auth_class = {}".format(auth_class))

                auth_time_to_live = authority_section_RR_0.ttl
                print("-> auth_time_to_live = {}".format(auth_time_to_live))

                authority_section_0_rdata = authority_section_RR_0.rdata
                print("-> authority_section_0_rdata = {}".format(authority_section_0_rdata))

                # si recibimos auth_type = 'SOA' este es un objeto tipo dnslib.dns.SOA
                if isinstance(authority_section_0_rdata, dnslib.dns.SOA):
                    primary_name_server = authority_section_0_rdata.get_mname()  # servidor de nombre primario
                    print("-> primary_name_server = {}".format(primary_name_server))

                elif isinstance(authority_section_0_rdata, dnslib.dns.NS): # si en vez de SOA recibimos un registro tipo NS
                    name_server_domain = authority_section_0_rdata  # entonces authority_section_0_rdata contiene el nombre de dominio del primer servidor de nombre de la lista
                    print("-> name_server_domain = {}".format(name_server_domain))
        else:
            print("-> number_of_authority_elements = {}".format(number_of_authority_elements))
        print(">>----------------------------------------------<<\n")

        print(">>------------- ADDITIONAL SECTION -------------<<\n")
        if number_of_additional_elements > 0:
            additional_records = dnslib_reply.ar  # lista que contiene un total de number_of_additional_elements DNS records
            print("-> additional_records = {}".format(additional_records))

            first_additional_record = additional_records[0]  # objeto tipo dnslib.dns.RR
            print("-> first_additional_record = {}".format(first_additional_record))

            # En caso de tener additional records, estos pueden contener la IP asociada a elementos del authority section
            ar_class = CLASS.get(first_additional_record.rclass)
            print("-> ar_class = {}".format(ar_class))

            ar_type = QTYPE.get(first_additional_record.rclass)  # para saber si esto es asi debemos revisar el tipo de record
            print("-> ar_type = {}".format(ar_type))

            if ar_type == 'A': # si el tipo es 'A' (Address)
                first_additional_record_rname = first_additional_record.rname  # nombre de dominio
                print("-> first_additional_record_rname = {}".format(first_additional_record_rname))

                first_additional_record_rdata = first_additional_record.rdata  # IP asociada
                print("-> first_additional_record_rdata = {}".format(first_additional_record_rdata))
        else:
            print("-> number_of_additional_elements = {}".format(number_of_additional_elements))
        print(">>----------------------------------------------<<\n")

    # Vamos a preguntar por cl. a un resolver existente
    dnslib_reply_1 = send_dns_message("cl.", "8.8.8.8", 53)
    # Como cl se encarga de un area entera, vamos a recibir un registro SOA que nos indica el primary_name_server = a.nic.cl.
    print_dns_reply_elements(dnslib_reply_1)

    print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
    # Si ahora queremos saber la IP, podemos volver a preguntarle al resolver. Esta vez preguntamos por el primary_name_server
    dnslib_reply_2 = send_dns_message("a.nic.cl.", "8.8.8.8", 53)
    # En las respuestas vamos a obtener la IP de este primary_name_server
    print_dns_reply_elements(dnslib_reply_2)

    # Propuesto: Utilizando la IP que puede ver en pantalla, ahora consulte por uchile.cl, pero consultele al NS de cl.
    # compare esta respuesta con la respuesta obteniida al preguntar por uchile.cl al resolver "8.8.8.8".
    # ¿Qué diferencias observa?
    ```
