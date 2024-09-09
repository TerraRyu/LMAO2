import dns.resolver
import dns.reversename
from dns.exception import DNSException
from typing import Dict, Any
import time

def dig_enum(domain: str) -> Dict[str, Any]:
    results = {
        'A': [],
        'AAAA': [],
        'NS': [],
        'MX': [],
        'TXT': [],
        'CNAME': [],
        'SOA': [],
        'PTR': [],
        'SRV': [],
        'ANY': [],
        'DNS_SERVER': {},
        'RESPONSE_TIME': None
    }

    resolver = dns.resolver.Resolver()

    record_types = ['A', 'AAAA', 'NS', 'MX', 'TXT', 'CNAME', 'SOA', 'PTR', 'SRV']

    for record_type in record_types:
        try:
            start_time = time.time()
            answers = resolver.resolve(domain, record_type)
            end_time = time.time()
            
            if results['RESPONSE_TIME'] is None:
                results['RESPONSE_TIME'] = f"{(end_time - start_time) * 1000:.2f} ms"

            for rdata in answers:
                if record_type == 'MX':
                    results[record_type].append(f"{rdata.exchange} {rdata.preference}")
                elif record_type == 'SOA':
                    results[record_type].append(f"{rdata.mname} {rdata.rname} {rdata.serial} {rdata.refresh} {rdata.retry} {rdata.expire} {rdata.minimum}")
                else:
                    results[record_type].append(str(rdata))
        except dns.resolver.NoAnswer:
            results[record_type] = ["No records found"]
        except DNSException as e:
            results[record_type] = [f"Error: {str(e)}"]

    # Check for DNSSEC
    try:
        answers = resolver.resolve(domain, 'DNSKEY')
        results['DNSSEC'] = "DNSSEC is enabled"
    except dns.resolver.NoAnswer:
        results['DNSSEC'] = "DNSSEC is not enabled"
    except DNSException as e:
        results['DNSSEC'] = f"Error checking DNSSEC: {str(e)}"

    # Get DNS server information
    try:
        ns_records = resolver.resolve(domain, 'NS')
        if ns_records:
            ns = str(ns_records[0])
            results['DNS_SERVER']['name'] = ns
            try:
                # Create a new resolver instance for the specific nameserver
                ns_resolver = dns.resolver.Resolver()
                ns_resolver.nameservers = [dns.resolver.resolve(ns).rrset[0].to_text()]
                version = ns_resolver.resolve('version.bind', 'TXT', raise_on_no_answer=False)
                results['DNS_SERVER']['version'] = str(version[0]) if version else "Unknown"
            except DNSException:
                results['DNS_SERVER']['version'] = "Unable to retrieve version"
    except DNSException as e:
        results['DNS_SERVER']['name'] = f"Error: {str(e)}"
        results['DNS_SERVER']['version'] = "Unknown"

    return results

if __name__ == "__main__":
    domain = input("Enter a domain to enumerate: ")
    results = dig_enum(domain)
    import json
    print(json.dumps(results, indent=2))