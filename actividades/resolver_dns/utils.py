from dnslib import DNSRecord, CLASS, QTYPE
import dnslib
import socket

IP_ADDRESS = '192.33.4.12'
PORT = 53

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
    if ancount > 0:
        # Guardamos en el diccionario answer la seccion Answer completa y tambien los campos
        # de la primera respuesta (si queremos las sigs basta con aplicar los metodos get_rname
        # sobre los demas elementos de la lista all_resource_records)
        resource_records_list = query_parsed.rr
        answer['resource_records_list'] = resource_records_list
        # first_answer = query_parsed.get_a()
        # answer['domain_name'] = first_answer.get_rname()
        # answer['answer_class'] = CLASS.get(first_answer.rclass)
        # answer['answer_type'] = QTYPE.get(first_answer.rtype)
        # answer['answer_rdata'] = first_answer.rdata
    
    dns_dict['answer'] = answer

    authority = {}
    if nscount > 0:
        # Guardamos en el diccionario authority la seccion Authority completa
        authority_section_list = query_parsed.auth
        authority['authority_section_list'] = authority_section_list
        
        # if len(authority_section_list) > 0:
        #     authority_section_RR_0 = authority_section_list[0]
        #     authority['auth_type'] = QTYPE.get(authority_section_RR_0.rtype)
        #     authority['auth_class'] = CLASS.get(authority_section_RR_0.rclass)
        #     authority['auth_ttl'] = authority_section_RR_0.ttl
        #     authority_section_0_rdata = authority_section_RR_0.rdata

        #     # Clasificamos el tipo de authority
        #     if isinstance(authority_section_0_rdata, dnslib.dns.SOA):
        #         primary_name_server = authority_section_0_rdata.get_mname()
        #         authority['primary_name_server'] = primary_name_server
        #     elif isinstance(authority_section_0_rdata, dnslib.dns.NS):
        #         authority['name_server_domain'] = authority_section_0_rdata
    
    dns_dict['authority'] = authority

    additional = {}
    if arcount > 0:
        # Guardamos en el diccionario additional la seccion Adittional completa, con los campos
        # del primer DNS record adicional
        additional_records_list = query_parsed.ar
        additional['additional_records_list'] = additional_records_list
        # firs_additional_record = additional_records_list[0]
        # additional['ar_class'] = CLASS.get(firs_additional_record.rclass) # TODO: En el item 2 este valor en el dict es 1232 (?)
        # ar_type = QTYPE.get(firs_additional_record.rclass)
        # additional['ar_type'] = ar_type

        # if ar_type == 'A': # Tipo Address
        #     additional['first_additional_record_rname'] = firs_additional_record.rname # Nombre de dominio
        #     additional['first_additional_record_rdata'] = firs_additional_record.rdata # IP asociada

    dns_dict['additional'] = additional

    return dns_dict

def has_typeA_in_section(rr_list) -> bool:
    """"Dada la lista de resource records obtenida con el metodo parse de la clase DNSRecord
    retorna True si existe una respuesta de tipo A y False en caso contrario.
    """

    for rr in rr_list:
        if QTYPE.get(rr.rtype) == 'A':
            return True
    
    return False

def resolver(query_msg: bytes) -> str | bytes:
    response = '' # Por default la respuesta sera vacia

    new_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    new_socket.sendto(query_msg, (IP_ADDRESS, PORT))
    answer, _ = new_socket.recvfrom(4096)
    parsed_answer = parse_dns_msg(answer)

    if (has_typeA_in_section(parsed_answer['answer']['resource_records_list'])
        or has_typeA_in_section(parsed_answer['authority']['authority_section_list'])
        or has_typeA_in_section(parsed_answer['additional']['additional_records_list'])): # No necesito revisar si ancount pues la funcion tambien sirve para el caso en que ancount=0
        return answer
    
    # Sino tomar el nombre de un NS desde Authority y usar recursivamente resolver() 