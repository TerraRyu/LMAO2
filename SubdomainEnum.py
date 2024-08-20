import requests
from urllib.parse import urlparse
import re
from typing import Set, Dict, Any, Tuple, List
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

from functions.VTEnum import virustotal_enum
from functions.DNSDumpEnum import dnsdumpster_enum
from activescans.dnsrecon import dnsrecon_enum

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def extract_base_domain(url: str) -> str:
    parsed_url = urlparse(url)
    domain = parsed_url.netloc if parsed_url.netloc else parsed_url.path
    domain_parts = domain.split('.')
    return '.'.join(domain_parts[-2:]) if len(domain_parts) > 2 else domain

def check_subdomain_status(subdomain: str) -> Tuple[str, str]:
    for protocol in ['http', 'https']:
        try:
            response = requests.get(f"{protocol}://{subdomain}", timeout=5)
            return subdomain, str(response.status_code)
        except requests.RequestException:
            pass
    return subdomain, "Unreachable"

def enumerate_subdomains(domain: str, scan_types: List[str]) -> Tuple[Set[str], Dict[str, Any]]:
    clean_domain = extract_base_domain(domain)
    
    all_subdomains: Set[str] = set()
    results = {
        'subdomains': {},
        'virustotal': {},
        'dnsdumpster': {},
        'dnsrecon': {}
    }
    
    enumeration_functions = []
    if 'passive' in scan_types:
        enumeration_functions.extend([virustotal_enum, dnsdumpster_enum])
    if 'active' in scan_types:
        enumeration_functions.append(dnsrecon_enum)
    
    for func in enumeration_functions:
        enum_name = func.__name__
        try:
            logger.info(f"Starting enumeration with {enum_name}")
            result = func(clean_domain)
            logger.info(f"Finished enumeration with {enum_name}. Result type: {type(result)}")
            
            if enum_name == 'virustotal_enum':
                process_virustotal_results(result, all_subdomains, results)
            elif enum_name == 'dnsdumpster_enum':
                process_dnsdumpster_results(result, all_subdomains, results)
            elif enum_name == 'dnsrecon_enum':
                process_dnsrecon_results(result, all_subdomains, results)
            
            logger.info(f"{enum_name} total subdomains found: {len(all_subdomains)}")
        except Exception as exc:
            logger.exception(f"{enum_name} generated an exception: {exc}")

    # Check status of all subdomains
    with ThreadPoolExecutor(max_workers=20) as executor:
        future_to_subdomain = {executor.submit(check_subdomain_status, subdomain): subdomain for subdomain in all_subdomains}
        for future in as_completed(future_to_subdomain):
            subdomain = future_to_subdomain[future]
            try:
                subdomain, status = future.result()
                results['subdomains'][subdomain]['status'] = status
            except Exception as exc:
                logger.exception(f'{subdomain} generated an exception: {exc}')
    
    logger.info(f"Total unique subdomains found across all methods: {len(all_subdomains)}")
    return all_subdomains, results

def process_virustotal_results(result: Dict[str, Any], all_subdomains: Set[str], results: Dict[str, Any]) -> None:
    if isinstance(result, dict):
        for subdomain, ips in result.items():
            all_subdomains.add(subdomain)
            results['virustotal'][subdomain] = ips
            if subdomain not in results['subdomains']:
                results['subdomains'][subdomain] = {'ip': 'N/A', 'sources': []}
            results['subdomains'][subdomain]['ip'] = ', '.join(ips)
            results['subdomains'][subdomain]['sources'].append('VirusTotal')
        logger.info(f"VirusTotal found {len(result)} subdomains")
    else:
        logger.warning(f"Unexpected result type from VirusTotal: {type(result)}")

def process_dnsdumpster_results(result: Dict[str, Any], all_subdomains: Set[str], results: Dict[str, Any]) -> None:
    results['dnsdumpster'] = result
    for subdomain in result.get('subdomains', []):
        domain = subdomain.get('domain')
        if domain:
            all_subdomains.add(domain)
            if domain not in results['subdomains']:
                results['subdomains'][domain] = {'ip': subdomain.get('ip', 'N/A'), 'sources': ['DNSDumpster']}
            else:
                if results['subdomains'][domain]['ip'] == 'N/A':
                    results['subdomains'][domain]['ip'] = subdomain.get('ip', 'N/A')
                if 'DNSDumpster' not in results['subdomains'][domain]['sources']:
                    results['subdomains'][domain]['sources'].append('DNSDumpster')
    logger.info(f"DNSDumpster found {len(result.get('subdomains', []))} subdomains")

def process_dnsrecon_results(result: Dict[str, Any], all_subdomains: Set[str], results: Dict[str, Any]) -> None:
    results['dnsrecon'] = result
    for record_type, records in result.items():
        if record_type == 'subdomains':
            for subdomain in records:
                domain = subdomain.get('domain')
                ip = subdomain.get('ip')
                if domain:
                    all_subdomains.add(domain)
                    if domain not in results['subdomains']:
                        results['subdomains'][domain] = {'ip': ip or 'N/A', 'sources': ['DNSRecon']}
                    else:
                        if results['subdomains'][domain]['ip'] == 'N/A':
                            results['subdomains'][domain]['ip'] = ip or 'N/A'
                        if 'DNSRecon' not in results['subdomains'][domain]['sources']:
                            results['subdomains'][domain]['sources'].append('DNSRecon')
        elif record_type in ['dns_records', 'mx_records']:
            for record in records:
                domain = record.get('name')
                if domain:
                    all_subdomains.add(domain)
                    if domain not in results['subdomains']:
                        results['subdomains'][domain] = {'ip': record.get('address', 'N/A'), 'sources': ['DNSRecon']}
                    else:
                        if results['subdomains'][domain]['ip'] == 'N/A':
                            results['subdomains'][domain]['ip'] = record.get('address', 'N/A')
                        if 'DNSRecon' not in results['subdomains'][domain]['sources']:
                            results['subdomains'][domain]['sources'].append('DNSRecon')

    logger.info(f"DNSRecon found {len(result.get('subdomains', []))} subdomains")

if __name__ == "__main__":
    domain = input("Enter a domain to enumerate subdomains: ")
    scan_types = input("Enter scan types (comma-separated, e.g., passive,active): ").split(',')
    all_subdomains, results = enumerate_subdomains(domain, scan_types)
    
    print("\nAll Subdomains:")
    for subdomain in sorted(all_subdomains):
        status = results['subdomains'][subdomain].get('status', 'Unknown')
        print(f"{subdomain}: Status {status}")
    
    if 'passive' in scan_types:
        print("\nVirusTotal Results:")
        for subdomain, ips in results['virustotal'].items():
            print(f"{subdomain}: {', '.join(ips)}")
    
        print("\nDNSDumpster Results:")
        for record_type, records in results['dnsdumpster'].items():
            print(f"\n{record_type.upper()}:")
            for record in records:
                print(record)
    
    if 'active' in scan_types:
        print("\nDNSRecon Results:")
        for record_type, records in results['dnsrecon'].items():
            print(f"\n{record_type.upper()}:")
            for record in records:
                print(record)