import time
import requests
from urllib.parse import urlparse
from typing import Dict, List
import logging
from apikeys import VIRUSTOTAL_API_KEY

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def extract_domain(url: str) -> str:
    parsed_url = urlparse(url)
    domain = parsed_url.netloc or parsed_url.path
    domain = domain.split(':')[0]  # Remove port if present
    domain_parts = domain.split('.')
    # Keep only the last two parts of the domain
    if len(domain_parts) > 2:
        return '.'.join(domain_parts[-2:])
    return '.'.join(domain_parts)

def virustotal_enum(domain: str) -> Dict[str, List[str]]:
    base_domain = extract_domain(domain)
    if not base_domain:
        logger.error("Invalid domain provided to VirusTotal API")
        return {}
    
    subdomains: Dict[str, List[str]] = {}
    url = f"https://www.virustotal.com/api/v3/domains/{base_domain}/subdomains?limit=1000"
    
    headers = {
        "accept": "application/json",
        "x-apikey": VIRUSTOTAL_API_KEY
    }

    logger.info(f"Querying VirusTotal for domain: {base_domain}")
    logger.debug(f"Using API URL: {url}")
    logger.debug(f"API Key (first 5 chars): {VIRUSTOTAL_API_KEY[:5]}...")

    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        logger.info(f"VirusTotal API response status code: {response.status_code}")
        
        if 'data' in result:
            for item in result['data']:
                subdomain = item['id']
                ip_addresses = item.get('attributes', {}).get('last_dns_records', [])
                ips = [record['value'] for record in ip_addresses if record['type'] in ['A', 'AAAA']]
                subdomains[subdomain] = ips
            logger.info(f"Processed {len(result['data'])} items from VirusTotal response")
        else:
            logger.warning("No 'data' field found in VirusTotal response")
            logger.debug(f"Response content: {result}")
    
    except requests.exceptions.RequestException as e:
        logger.error(f"An error occurred while querying VirusTotal: {e}")
        if hasattr(e, 'response') and e.response is not None:
            logger.error(f"Response status code: {e.response.status_code}")
            logger.error(f"Response content: {e.response.text}")
    except KeyError as e:
        logger.error(f"Unexpected response format from VirusTotal API: {e}")
    except Exception as e:
        logger.exception(f"An unexpected error occurred: {e}")
    
    logger.info(f"Total subdomains found by VirusTotal: {len(subdomains)}")
    return subdomains

if __name__ == "__main__":
    domain = input("Enter a domain to enumerate subdomains: ")
    results = virustotal_enum(domain)
    print("\nResults:")
    for subdomain, ips in results.items():
        print(f"Subdomain: {subdomain}")
        print(f"IP Addresses: {', '.join(ips) if ips else 'No IP found'}")