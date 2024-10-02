import sys
import os
import time
import git
import requests
from bs4 import BeautifulSoup
import re
import dns.resolver
import socket
from typing import Dict, List, Any
import logging
import importlib

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Ensure the path to dnsdumpster.py is correct
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
dnsdumpster_dir = os.path.join(parent_dir, 'repos', 'dnsdumpster')
print(dnsdumpster_dir)
sys.path.append(dnsdumpster_dir)

# from repos.dnsdumpster.dnsdumpster import main as dnsdumpster_main

def safe_import_dnsdumpster():
    # Temporarily remove the problematic geolocator from sys.modules
    geolocator_module = sys.modules.pop('geolocator', None)

    try:
        # Add the repos directory to the Python path
        repo_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'repos')
        sys.path.insert(0, repo_path)

        # Import dnsdumpster directly
        from repos.dnsdumpster import dnsdumpster
        return dnsdumpster.main
    except ImportError as e:
        logger.error(f"Failed to import dnsdumpster: {e}")
        return None
    finally:
        # Restore the geolocator module and remove the added path
        if geolocator_module:
            sys.modules['geolocator'] = geolocator_module
        if repo_path in sys.path:
            sys.path.remove(repo_path)

def get_dnsdumpster_main():
    # try:
    #     dnsdumpster_module = importlib.import_module('repos.dnsdumpster.dnsdumpster')
    #     return dnsdumpster_module.main
    # except ImportError as e:
    #     logger.error(f"Failed to import dnsdumpster module: {e}")
    #     return None
    return safe_import_dnsdumpster()

def get_ip_address(hostname: str) -> str:
    try:
        return socket.gethostbyname(hostname)
    except socket.gaierror:
        return "Unable to resolve"
    
def dig_mx_records(domain: str) -> List[Dict[str, Any]]:
    try:
        mx_records = dns.resolver.resolve(domain, 'MX')
        results = []
        for mx in mx_records:
            exchange = str(mx.exchange).rstrip('.')
            ip_address = get_ip_address(exchange)
            results.append({
                'exchange': exchange,
                'preference': mx.preference,
                'ip': ip_address,
                'source': 'dig'
            })
        logger.debug(f"Dig MX records: {results}")
        return results
    except dns.resolver.NoAnswer:
        logger.warning(f"No MX records found for {domain}")
        return []
    except dns.resolver.NXDOMAIN:
        logger.warning(f"Domain {domain} does not exist")
        return []
    except dns.exception.DNSException as e:
        logger.error(f"DNS query failed: {str(e)}")
        return []

def dnsdumpster_enum(domain: str) -> Dict[str, Any]:
    # if not domain:
    #     logger.error("Invalid domain provided to DNSDumpster")
    #     return {}

    # logger.info(f"Starting DNSDumpster enumeration for {domain}")
    # try:
    #     dnsrecords = get_dnsdumpster_main()(domain)
    #     results = parse_results(dnsrecords)
        
    #     # Add dig MX records
    #     dig_mx = dig_mx_records(domain)
    #     results['mx_records'].extend(dig_mx)
        
    #     logger.debug("DNSDumpster raw results: %s", dnsrecords)
    #     logger.debug("DNSDumpster parsed results: %s", results)
    #     return results
    # except Exception as e:
    #     logger.exception(f"Error in DNSDumpsterEnum: {str(e)}")
    #     return {}
    if not domain:
        logger.error("Invalid domain provided to DNSDumpster")
        return {"error": "Invalid domain provided"}

    logger.info(f"Starting DNSDumpster enumeration for {domain}")
    try:
        dnsdumpster_main = safe_import_dnsdumpster()
        if dnsdumpster_main is None:
            return {"error": "Failed to import DNSDumpster module"}
        
        dnsrecords = dnsdumpster_main(domain)
        if not dnsrecords:
            return {"error": "DNSDumpster returned no data"}
        
        results = parse_results(dnsrecords)
        
        logger.debug("DNSDumpster raw results: %s", dnsrecords)
        logger.debug("DNSDumpster parsed results: %s", results)
        return results
    except Exception as e:
        logger.exception(f"Error in DNSDumpsterEnum: {str(e)}")
        return {"error": str(e)}

def parse_results(dnsrecords: Dict[str, Any]) -> Dict[str, Any]:
    results = {
        'subdomains': [],
        'mx_records': [],
        'txt_records': [],
        'dns_records': []
    }
    
    if isinstance(dnsrecords, dict):
        results['dns_records'] = dnsrecords.get('ns', [])
        results['mx_records'] = [
            {**record, 'source': 'DNSDumpster'}
            for record in dnsrecords.get('mx', [])
        ]
        results['txt_records'] = dnsrecords.get('txt', [])
        
        for subdomain in dnsrecords.get('subdomains', []):
            results['subdomains'].append({
                'domain': subdomain.get('subdomain'),
                'ip': subdomain.get('subdomain_ip', 'N/A'),
                'asn': subdomain.get('asn', {}),
                'server': subdomain.get('server', 'N/A')
            })
    else:
        logger.warning("DNSDumpster returned unexpected data structure")
        results['error'] = "Unexpected data structure from DNSDumpster"
    
    logger.debug(f"Parsed MX records: {results['mx_records']}")
    return results

if __name__ == "__main__":
    domain = input("Enter a domain to enumerate: ")
    results = dnsdumpster_enum(domain)
    print("\nDNSDumpster Results:")
    for record_type, records in results.items():
        print(f"\n{record_type.replace('_', ' ').title()}:")
        for record in records:
            print(record)