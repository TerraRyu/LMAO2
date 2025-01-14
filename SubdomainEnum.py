import requests
from urllib.parse import urlparse
import re
from typing import Set, Dict, Any, Tuple, List
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import json
from cache_manager import save_to_cache, load_from_cache

from SearchFunctionality import is_valid_domain, extract_domain
from functions.VTEnum import virustotal_enum
from functions.DNSDumpEnum import dnsdumpster_enum
from activescans.dnsrecon import dnsrecon_enum
from functions.nucleirecon import nuclei_enum
from activescans.dig_enum import dig_enum 
from activescans.subzy_enum import subzy_enum
from OSINT.harvester import run_osint
from OSINT.spiderfoot_enum import run_spiderfoot
from OSINT.trufflehog_enum import run_trufflehog
from functions.shodan_enum import shodan_enum 
from Cloud.cloudfail_enum import cloudfail_enum
from Cloud.aws_bucket_dump import run_aws_bucket_dump
from Cloud.gcp_bucket_brute import run_gcp_bucket_brute
from Cloud.microburst import run_microburst
# Import other enumeration functions as needed

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def extract_base_domain(url: str) -> str:
    parsed_url = urlparse(url)
    domain = parsed_url.netloc if parsed_url.netloc else parsed_url.path
    # domain_parts = domain.split('.')
    # return '.'.join(domain_parts[-2:]) if len(domain_parts) > 2 else domain
    return domain

def check_subdomain_status(subdomain: str) -> Tuple[str, str]:
    for protocol in ['http', 'https']:
        try:
            response = requests.get(f"{protocol}://{subdomain}", timeout=5)
            return subdomain, str(response.status_code)
        except requests.RequestException:
            pass
    return subdomain, "Unreachable"

def enumerate_subdomains(domain: str, scan_types: List[str], progress_callback=None) -> Tuple[Set[str], Dict[str, Any]]:
    clean_domain = extract_base_domain(domain)

    if not is_valid_domain(clean_domain):
        logger.error(f"Invalid domain: {clean_domain}")
        return set(), {"error": "Invalid domain"}
    
    # Check cache first
    cached_results = load_from_cache(clean_domain, scan_types)
    if cached_results:
        logger.info(f"Using cached results for {clean_domain}")
        return set(cached_results['subdomains'].keys()), cached_results
    
    all_subdomains: Set[str] = set()
    results = {
        'subdomains': {},
        'virustotal': {},
        'dnsdumpster': {},
        'dnsrecon': {},
        'nuclei': {},
        'subzy': {},
        'harvester': {},
        'spiderfoot': {},
        'trufflehog': {},
        'shodan': {},
        'cloudfail': {},
        'aws_bucket_dump': {},
        'gcp_bucket_brute': {},
        'microburst': {}
        # Add other result categories as needed
    }
    
    results_lock = threading.Lock()
    
    with ThreadPoolExecutor(max_workers=len(scan_types)) as executor:
        future_to_scan = {executor.submit(run_scan, clean_domain, scan_type, all_subdomains, results, results_lock, progress_callback): scan_type for scan_type in scan_types}
        
        for future in as_completed(future_to_scan):
            scan_type = future_to_scan[future]
            try:
                future.result()
            except Exception as exc:
                logger.exception(f'{scan_type} scan generated an exception: {exc}')

    # Check status of all subdomains
    # with ThreadPoolExecutor(max_workers=20) as executor:
    #     future_to_subdomain = {executor.submit(check_subdomain_status, subdomain): subdomain for subdomain in all_subdomains}
    #     for future in as_completed(future_to_subdomain):
    #         subdomain = future_to_subdomain[future]
    #         try:
    #             subdomain, status = future.result()
    #             with results_lock:
    #                 results['subdomains'][subdomain]['status'] = status
    #         except Exception as exc:
    #             logger.exception(f'{subdomain} generated an exception: {exc}')
    with ThreadPoolExecutor(max_workers=20) as executor:
        future_to_subdomain = {executor.submit(check_subdomain_status, subdomain): subdomain for subdomain in all_subdomains}
        for future in as_completed(future_to_subdomain):
            subdomain = future_to_subdomain[future]
            try:
                subdomain, status = future.result()
                with results_lock:
                    if subdomain not in results['subdomains']:
                        results['subdomains'][subdomain] = {'ip': subdomain, 'sources': ['IP Address']}
                    results['subdomains'][subdomain]['status'] = status
            except Exception as exc:
                logger.exception(f'{subdomain} generated an exception: {exc}')
    
    logger.info(f"Total unique subdomains found across all methods: {len(all_subdomains)}")
    
    # Save results to cache
    save_to_cache(clean_domain, scan_types, results)
    
    return all_subdomains, results

def run_scan(domain: str, scan_type: str, all_subdomains: Set[str], results: Dict[str, Any], lock: threading.Lock, progress_callback=None):
    if scan_type == 'passive':
        process_passive_scan(domain, all_subdomains, results, lock, progress_callback)
    elif scan_type == 'active':
        process_active_scan(domain, all_subdomains, results, lock, progress_callback)
    elif scan_type == 'osint':
        process_osint_scan(domain, all_subdomains, results, lock, progress_callback)
    elif scan_type == 'cloud':
        process_cloud_enum_scan(domain, all_subdomains, results, lock, progress_callback)

def process_passive_scan(domain: str, all_subdomains: Set[str], results: Dict[str, Any], lock: threading.Lock, progress_callback=None):
    if progress_callback:
        progress_callback('passive', 0)
    
    vt_results = virustotal_enum(domain)
    if progress_callback:
        progress_callback('passive', 20)
    
    dns_results = dnsdumpster_enum(domain)
    if progress_callback:
        progress_callback('passive', 40)
    
    nuclei_results = nuclei_enum(domain)
    if progress_callback:
        progress_callback('passive', 60)
    
    shodan_results = shodan_enum(domain)  # Use the new shodan_enum function
    if progress_callback:
        progress_callback('passive', 80)
    
    with lock:
        process_virustotal_results(vt_results, all_subdomains, results)
        if 'error' not in dns_results:
            process_dnsdumpster_results(dns_results, all_subdomains, results)
        else:
            results['dnsdumpster'] = dns_results
        process_nuclei_results(nuclei_results, results)
        process_shodan_results(shodan_results, results)
    
    if progress_callback:
        progress_callback('passive', 100)

def process_shodan_results(shodan_results: Dict[str, Any], results: Dict[str, Any]) -> None:
    results['shodan'] = shodan_results
    logger.info(f"Shodan found {len(shodan_results.get('ip_addresses', []))} IP addresses")

def process_active_scan(domain: str, all_subdomains: Set[str], results: Dict[str, Any], lock: threading.Lock, progress_callback=None):
    if progress_callback:
        progress_callback('active', 0)
    
    dnsrecon_results = dnsrecon_enum(domain)
    if progress_callback:
        progress_callback('active', 25)
    
    dig_results = dig_enum(domain)
    if progress_callback:
        progress_callback('active', 50)
    
    subzy_results = subzy_enum(domain)  # Add this line
    if progress_callback:
        progress_callback('active', 75)
    
    with lock:
        process_dnsrecon_results(dnsrecon_results, all_subdomains, results)
        process_dig_results(dig_results, all_subdomains, results)
        process_subzy_results(subzy_results, results)  # Add this line
    
    if progress_callback:
        progress_callback('active', 100)

def process_osint_scan(domain: str, all_subdomains: Set[str], results: Dict[str, Any], lock: threading.Lock, progress_callback=None):
    if progress_callback:
        progress_callback('osint', 0)
    
    print(f"\nRunning OSINT scan for domain: {domain}")
    
    spiderfoot_results = run_spiderfoot(domain)
    print("\nSpiderFoot Results:")
    print(json.dumps(spiderfoot_results, indent=2))
    
    # Construct GitHub repo URL (this is a simple assumption, adjust as needed)
    github_repo_url = f"https://github.com/{domain.split('.')[0]}/{domain.split('.')[0]}.git"
    trufflehog_results = run_trufflehog(github_repo_url)
    print("\nTruffleHog Results:")
    print(json.dumps(trufflehog_results, indent=2))
    
    with lock:
        results['spiderfoot'] = spiderfoot_results
        results['trufflehog'] = trufflehog_results
    
    if progress_callback:
        progress_callback('osint', 100)
        
def process_cloud_enum_scan(domain: str, all_subdomains: Set[str], results: Dict[str, Any], lock: threading.Lock, progress_callback=None):
    if progress_callback:
        progress_callback('cloud_enum', 0)
    
    cloud_results = cloudfail_enum(domain)
    aws_results = run_aws_bucket_dump(domain)
    gcp_results = run_gcp_bucket_brute(domain)
    azure_results = run_microburst(domain)
    
    with lock:
        results['cloudfail'] = cloud_results
        results['aws_bucket_dump'] = aws_results
        results['gcp_bucket_brute'] = gcp_results
        results['microburst'] = azure_results

        # Add discovered subdomains to all_subdomains set
        if 'dns_records' in cloud_results:
            for record_type, records in cloud_results['dns_records'].items():
                for record in records:
                    if record_type in ['A', 'AAAA', 'CNAME']:
                        all_subdomains.add(record)
        
        # Add discovered buckets and blobs to all_subdomains set
        all_subdomains.update(aws_results.get('open_buckets', []))
        all_subdomains.update(gcp_results.get('public_buckets', []))
        all_subdomains.update(azure_results.get('open_blobs', []))
    
    if progress_callback:
        progress_callback('cloud_enum', 100)
        
def process_virustotal_results(result: Dict[str, Any], all_subdomains: Set[str], results: Dict[str, Any]) -> None:
    results['virustotal'] = result
    for subdomain, ips in result.items():
        all_subdomains.add(subdomain)
        if subdomain not in results['subdomains']:
            results['subdomains'][subdomain] = {'ip': ', '.join(ips), 'sources': ['VirusTotal']}
        else:
            results['subdomains'][subdomain]['ip'] = ', '.join(ips)
            if 'VirusTotal' not in results['subdomains'][subdomain]['sources']:
                results['subdomains'][subdomain]['sources'].append('VirusTotal')

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

def process_subzy_results(subzy_results: Dict[str, Any], results: Dict[str, Any]) -> None:
    if "error" in subzy_results:
        results['subzy'] = {"error": subzy_results["error"]}
        logger.error(f"Subzy scan error: {subzy_results['error']}")
    elif "raw_output" in subzy_results:
        results['subzy'] = {"raw_output": subzy_results["raw_output"]}
        logger.warning("Subzy returned non-JSON output")
        # Try to extract subdomains from raw output
        subdomains = extract_subdomains_from_raw(subzy_results["raw_output"])
        if subdomains:
            for subdomain in subdomains:
                if subdomain not in results['subdomains']:
                    results['subdomains'][subdomain] = {'ip': 'N/A', 'sources': ['Subzy']}
                elif 'Subzy' not in results['subdomains'][subdomain]['sources']:
                    results['subdomains'][subdomain]['sources'].append('Subzy')
    else:
        results['subzy'] = subzy_results
        logger.info(f"Subzy found {len(subzy_results.get('vulnerable', []))} vulnerable subdomains")

def extract_subdomains_from_raw(raw_output: str) -> List[str]:
    # This is a basic extraction. Adjust the regex pattern if needed based on Subzy's actual output format
    subdomain_pattern = r'\b(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}\b'
    return list(set(re.findall(subdomain_pattern, raw_output)))


def process_nuclei_results(nuclei_results: Dict[str, Any], results: Dict[str, Any]) -> None:
    if "error" in nuclei_results:
        results['nuclei'] = {"error": nuclei_results["error"]}
    else:
        results['nuclei'] = nuclei_results
        logger.info(f"Nuclei found {len(nuclei_results.get('vulnerabilities', []))} vulnerabilities and {len(nuclei_results.get('information', []))} informational items.")

# def process_dnsrecon_results(result: Dict[str, Any], all_subdomains: Set[str], results: Dict[str, Any]) -> None:
#     results['dnsrecon'] = result
#     for record in result.get('dns_records', []) + result.get('mx_records', []):
#         domain = record.get('name')
#         if domain:
#             all_subdomains.add(domain)
#             if domain not in results['subdomains']:
#                 results['subdomains'][domain] = {'ip': record.get('address', 'N/A'), 'sources': ['DNSRecon']}
#             else:
#                 if results['subdomains'][domain]['ip'] == 'N/A':
#                     results['subdomains'][domain]['ip'] = record.get('address', 'N/A')
#                 if 'DNSRecon' not in results['subdomains'][domain]['sources']:
#                     results['subdomains'][domain]['sources'].append('DNSRecon')

def process_dnsrecon_results(result: Dict[str, Any], all_subdomains: Set[str], results: Dict[str, Any]) -> None:
    structured_results = {
        'a_records': [],
        'mx_records': [],
        'ns_records': [],
        'soa_records': [],
        'srv_records': [],
        'txt_records': []
    }

    # Check if result is a string (JSON)
    if isinstance(result, str):
        try:
            result = json.loads(result)
        except json.JSONDecodeError:
            logger.error("Failed to parse DNSRecon results JSON")
            return

    # Ensure result is a dictionary
    if not isinstance(result, dict):
        logger.error(f"Unexpected DNSRecon result type: {type(result)}")
        return

    # Process each record type
    for record_type, records in result.items():
        if not isinstance(records, list):
            logger.warning(f"Skipping non-list record type: {record_type}")
            continue

        for record in records:
            if record_type == 'A':
                structured_results['a_records'].append({
                    'name': record.get('name'),
                    'address': record.get('address')
                })
            elif record_type == 'MX':
                structured_results['mx_records'].append({
                    'name': record.get('name'),
                    'address': record.get('address'),
                    'priority': record.get('preference')  # Note: changed from 'exchange' to 'preference'
                })
            elif record_type == 'NS':
                structured_results['ns_records'].append({
                    'name': record.get('name'),
                    'target': record.get('target')
                })
            elif record_type == 'SOA':
                structured_results['soa_records'].append({
                    'name': record.get('mname'),
                    'target': record.get('rname')
                })
            elif record_type == 'SRV':
                structured_results['srv_records'].append({
                    'name': record.get('name'),
                    'target': record.get('target'),
                    'port': record.get('port'),
                    'priority': record.get('priority'),
                    'weight': record.get('weight')
                })
            elif record_type == 'TXT':
                structured_results['txt_records'].append({
                    'name': record.get('name'),
                    'text': record.get('strings')
                })

            # Add to all_subdomains and results['subdomains']
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

    results['dnsrecon'] = structured_results
    logger.info(f"DNSRecon found {len(all_subdomains)} subdomains")

# Add other processing functions as needed

def process_osint_scan(domain: str, all_subdomains: Set[str], results: Dict[str, Any], lock: threading.Lock, progress_callback=None):
    if progress_callback:
        progress_callback('osint', 0)
    
    harvester_results = run_osint(domain)
    
    with lock:
        results['harvester'] = harvester_results
    
    if progress_callback:
        progress_callback('osint', 100)

def process_dig_results(dig_results: Dict[str, Any], all_subdomains: Set[str], results: Dict[str, Any]) -> None:
    results['dig'] = dig_results
    for record_type, records in dig_results.items():
        if isinstance(records, list):
            for record in records:
                if record_type in ['A', 'AAAA', 'CNAME', 'MX', 'NS']:
                    domain = record.split()[-1].rstrip('.')
                    all_subdomains.add(domain)
                    if domain not in results['subdomains']:
                        results['subdomains'][domain] = {'ip': 'N/A', 'sources': ['dig']}
                    else:
                        if 'dig' not in results['subdomains'][domain]['sources']:
                            results['subdomains'][domain]['sources'].append('dig')

    logger.info(f"Dig found {len(all_subdomains)} subdomains")

if __name__ == "__main__":
    domain = input("Enter a domain to enumerate subdomains: ")
    scan_types = input("Enter scan types (comma-separated, e.g., passive,active,osint): ").split(',')
    
    def print_progress(scan_type, progress):
        print(f"{scan_type.capitalize()} scan progress: {progress}%")
    
    all_subdomains, results = enumerate_subdomains(domain, scan_types, print_progress)
    
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

        print("\nNuclei Results:")
        print("Vulnerabilities:")
        for vuln in results['nuclei']['vulnerabilities']:
            print(f"  - {vuln['name']} ({vuln['severity']}): {vuln['description']}")
        print("\nInformation:")
        for info in results['nuclei']['information']:
            print(f"  - {info['name']}: {info['description']}")
    
    if 'active' in scan_types:
        print("\nDNSRecon Results:")
        for record_type, records in results['dnsrecon'].items():
            print(f"\n{record_type.upper()}:")
            for record in records:
                print(record)
        
        print("\nDig Results:")
        for record_type, records in results['dig'].items():
            if record_type in ['DNS_SERVER', 'RESPONSE_TIME', 'DNSSEC']:
                continue
            print(f"\n{record_type} Records:")
            for record in records:
                print(record)
        
        print("\nDNS Server Information:")
        print(f"Name: {results['dig']['DNS_SERVER'].get('name', 'N/A')}")
        print(f"Version: {results['dig']['DNS_SERVER'].get('version', 'N/A')}")
        
        print(f"\nDNSSEC: {results['dig']['DNSSEC']}")
        print(f"\nResponse Time: {results['dig']['RESPONSE_TIME']}")
    # Print other results as needed