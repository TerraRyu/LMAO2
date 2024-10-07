import dns.resolver
import requests
from typing import Dict, Any
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def cloudfail_enum(domain: str) -> Dict[str, Any]:
    results = {
        "cloud_provider": identify_cloud_provider(domain),
        "dns_records": get_dns_records(domain),
    }
    return results

def identify_cloud_provider(domain: str) -> str:
    # Check for common cloud providers
    providers = {
        "cloudflare": ["cloudflare.com", "cloudflare.net"],
        "aws": ["amazonaws.com", "cloudfront.net"],
        "google": ["googleusercontent.com", "googleapis.com"],
        "azure": ["azurewebsites.net", "cloudapp.azure.com"],
    }

    try:
        ip = dns.resolver.resolve(domain, 'A')[0].to_text()
        for provider, domains in providers.items():
            for domain in domains:
                try:
                    if dns.resolver.resolve(domain, 'A')[0].to_text() == ip:
                        return provider
                except:
                    continue
    except:
        pass

    return "Unknown"

def get_dns_records(domain: str) -> Dict[str, list]:
    record_types = ['A', 'AAAA', 'CNAME', 'MX', 'NS', 'TXT']
    dns_records = {}

    for record_type in record_types:
        try:
            answers = dns.resolver.resolve(domain, record_type)
            dns_records[record_type] = [str(rdata) for rdata in answers]
        except:
            dns_records[record_type] = []

    return dns_records

if __name__ == "__main__":
    domain = input("Enter a domain to enumerate: ")
    results = cloudfail_enum(domain)
    print(results)