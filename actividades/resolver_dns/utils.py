from dnslib import DNSRecord, CLASS, QTYPE


# Parsear qname, ancount, nscount, arcount, answer, authority y additional
def parse_dns_msg(dns_msg: DNSRecord) -> dict[str, str]:
    query_parsed = DNSRecord.parse(dns_msg)
    print(query_parsed)
    first_query = query_parsed.get_q()
    domain_name_in_query = first_query.get_qname()
    ancount = dns_msg.header.a
