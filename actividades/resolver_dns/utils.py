from dnslib import DNSRecord, QTYPE, RR, A
import dnslib
import dnslib
import socket

IP_ADDRESS = '192.33.4.12'
PORT = 53
CACHE = {}  ## Diccionario de la forma qname, ip (key, value)
QUERYS_20 = [] # Lista con tuplas de la forma (qname, [count, ip])

# -------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------

# Funciones de parsing del query y 'getters'

def parse_dns_msg(dns_msg: bytes) -> dict[str, str | int | dict]:
    """Transforma el mensaje dns a un diccionario con todos los campos de este, ademas
    considera los casos para los tipos de authority o additional record. Para las secciones de
    Answer, Authority y Additional se guarda toda la seccion y ademas los campos del primer 
    elemento de cada una en un diccionario con el nombre de la seccion como llave respectivamente.
    """

    query_parsed = DNSRecord.parse(dns_msg)

    # Obtenemos QNAME, ANCOUNT, NSCOUNT, ARCOUNT
    first_query = query_parsed.get_q() # objeto tipo DNSQuestion

    dns_dict = {}
    qname = first_query.get_qname() # Nombre del dominio a preguntar
    dns_dict['qname'] = qname
    ancount = query_parsed.header.a # Answer count
    dns_dict['ancount'] = ancount
    nscount = query_parsed.header.auth # Authority count
    dns_dict['nscount'] = nscount
    arcount = query_parsed.header.ar # Additional information count
    dns_dict['arcount'] = arcount
    
    answer = {}
    answer['resource_records_list'] = []
    if ancount > 0:
        # Guardamos en el diccionario answer la seccion Answer completa y tambien los campos
        # de la primera respuesta (si queremos las sigs basta con aplicar los metodos get_rname
        # sobre los demas elementos de la lista all_resource_records)
        resource_records_list = query_parsed.rr
        answer['resource_records_list'] = resource_records_list
    
    dns_dict['answer'] = answer

    authority = {}
    authority['authority_section_list'] = []
    if nscount > 0:
        # Guardamos en el diccionario authority la seccion Authority completa
        authority_section_list = query_parsed.auth
        authority['authority_section_list'] = authority_section_list
    
    dns_dict['authority'] = authority

    additional = {}
    additional['additional_records_list'] = []
    if arcount > 0:
        # Guardamos en el diccionario additional la seccion Adittional completa, con los campos
        # del primer DNS record adicional
        additional_records_list = query_parsed.ar
        additional['additional_records_list'] = additional_records_list

    dns_dict['additional'] = additional

    return dns_dict

def has_typeA(rr_list: list[RR]) -> tuple[bool, int]:
    """"Dada la lista de RRs retorna una tupla con el valor de verdad True y el indice
    del RR con la respuesta de tipo A en caso de existir y (False, -1) en caso contrario.
    """

    for rr in rr_list:
        if QTYPE.get(rr.rtype) == 'A':
            return (True, rr_list.index(rr))
    
    return (False, -1)

def has_typeNS(rr_list: list[RR]) -> tuple[bool, int]:
    """Dada una lista de RRs retorna una tupla con el valor de verdad False y el indice del RR
    donde el tipo de la respuesta es distinto a NS en la seccion Authority, o (True, 0) en caso
    contrario.
    """

    for rr in rr_list:
        if not isinstance(rr.rdata, dnslib.dns.NS):
            return (False, rr_list.index(rr))
    
    return (True, 0)

# -------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------

# Resolver

def resolver(query_msg: bytes, new_socket: socket.socket, ip: str = IP_ADDRESS, ns = '.') -> bytes:
    """Toma una query y la envia a la ip dada mediante el socket entregado como parametro,
    retorna la query con la respuesta entregada por la ip de consulta.
    """

    response = '' # Por default la respuesta sera vacia

    # Preguntamos en cache
    qname = str(parse_dns_msg(query_msg)['qname'])
    if qname in CACHE:
        ip = CACHE[qname]
        response = modify_query(query_msg,qname ,ip)
        update_cache(qname, ip)
        print("<<----------------------------->>")
        print(f"(debug) Utilizando cache para dominio '{qname}' con direccion IP asociada {ip}")
        print("<<----------------------------->>")
        return response


    new_socket.sendto(query_msg, (ip, PORT))
    answer, _ = new_socket.recvfrom(4096)
    parsed_answer = parse_dns_msg(answer)

    domain_name = str(parsed_answer['qname'])
    print("<<----------------------------->>")
    print(f"(debug) Consultando '{domain_name}' a '{ns}' con direccion IP '{ip}'")
    print("<<----------------------------->>")

    if (has_typeA(parsed_answer['answer']['resource_records_list'])[0]):
        # Caso answer tiene respuesta tipo A en seccion Answer respondemo
        
        if ns == '.': # Solo actualizamos cache en la primera consulta no en las consultas recurivas para busqueda
            rr = parsed_answer['answer']['resource_records_list']
            update_cache(qname, str(rr[0].rdata))
        
        return answer
    
    # En caso de no obtener una respuesta de tipo A, para no ejecutar la funcion dos veces guardo el valor
    possible_ns = has_typeNS(parsed_answer['authority']['authority_section_list'])
    if (possible_ns[0]): # Si en cambio vienen delegacion a otro NS en Authority revisamos Additional

        possible_ip = has_typeA(parsed_answer['additional']['additional_records_list'])
        if (possible_ip[0]): # Si encontramos resp tipo A en Additional, enviamos la query a este nueva IP (recursivo nuevamente)
            index_ip = possible_ip[1]
            rr_with_ip = parsed_answer['additional']['additional_records_list'][index_ip]
            new_ip = rr_with_ip.rdata
            response = resolver(query_msg, new_socket, ip=str(new_ip), ns=rr_with_ip.rname)

        else: # Si no encontramos IP en Additional, tomamos un NS de Authority y usamos recursivamente resolver
            ns_index = possible_ns[1]
            ns_rr = parsed_answer['authority']['authority_section_list'][ns_index]
            ns_domain = ns_rr.rdata
            new_query = DNSRecord.question(str(ns_domain))
            response_with_ip = resolver(bytes(new_query.pack()), new_socket, ns=ns_domain)
            parsed_response = parse_dns_msg(response_with_ip)
            ns_ip = parsed_response['answer']['resource_records_list'][0].rdata
            new_socket.sendto(query_msg, (str(ns_ip), PORT))
            response, _ = new_socket.recvfrom(4096)
        
    # Actualizamos cache
        if ns == '.': # Solo actualizamos cache en la primera consulta no en las consultas recurivas para busqueda
            rr = parse_dns_msg(response)['answer']['resource_records_list'][0]
            update_cache(qname, str(rr.rdata))

    return response

# -------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------

# Funciones relacionadas con el manejo de cache

def modify_query(query_msg: bytes, qname: str, ip_answer: str) -> bytes:
    """Modifica la query agregando a la seccion Answer una lista con el resource record rr,
    retorna una tupla con la nueva query y la ip del resource record rr.
    """

    new_query = DNSRecord.parse(query_msg)
    print(f"qname: {qname}, rdata: {ip_answer}")
    new_query.add_answer(RR(qname, QTYPE.A, rdata=A(ip_answer)))
    return bytes(new_query.pack())

def count_sort(t: tuple[str, tuple[int, str]]) -> int:
    """Helper para ordenar QUERYS_20 por la cantidad de consultas al dominio.
    """
    
    return t[1][0]

def update_cache(qname: str, ip: str) -> None:
    """Dado el qname y el RR asociado, realiza un update de la cache (CACHE) acorde a la cantidad de consultas
    realizadas (limite 20), si el qname se encuentra entre las ultimas 20 querys aumentamos en 1 su respectivo contador,
    en caso contrario si ya se han realizado mas de 20 consultas se resetea el cache, sino se agrega el qname con su contador
    y RR a la cache.
    """

    global QUERYS_20
    global CACHE
    dict_querys_20 = dict(QUERYS_20)
    if qname in dict_querys_20: # Si la consulta se encuentra entre las ultimas 20 consultas recibidas aumentamos su respectivo contador
        QUERYS_20[QUERYS_20.index((qname, [dict_querys_20[qname][0], dict_querys_20[qname][1]]))][1][0] += 1 # Aumentamos la cantidad de veces que se repite
        QUERYS_20.sort(reverse=True, key=count_sort)
    else: # Si no se encuentra existe un caso de interes
        if len(QUERYS_20) >= 20: # Si llegamos al limite de las 20 ultimas consultas vaciamos la lista con estas consultas para empezar de nuevo a crear la cache
            QUERYS_20 = []
        QUERYS_20.append((qname, [1, ip]))
    
    # Actualizamos la cache
    CACHE = {}
    for i in range(len(QUERYS_20)):
        if i>=5:
            return
        
        qname, t = QUERYS_20[i]
        CACHE[qname] = t[1]