import socket
import ssl
import dns.resolver
import whois
import requests
from bs4 import BeautifulSoup
from typing import Dict, Any, List
from concurrent.futures import ThreadPoolExecutor, as_completed
import re
import hashlib
from urllib.parse import urlparse
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def comprehensive_passive_recon(domain: str) -> Dict[str, Any]:
    results = {
        "related_domains": [],
        "subdomains": {},
        "ssl_info": {},
        "file_hashes": [],
        "dns_records": {},
        "dns_servers": [],
        "mx_records": [],
        "whois_info": {}
    }

    # 1. Related Domains and Subdomains
    results["related_domains"], results["subdomains"] = find_related_domains_and_subdomains(domain)

    # 2. SSL Certificate Information
    results["ssl_info"] = get_ssl_info(domain)

    # 3. File Hashes and Associated Artifacts
    results["file_hashes"] = get_file_hashes(domain)

    # 4. DNS Records
    results["dns_records"] = get_dns_records(domain)

    # 5. DNS Servers
    results["dns_servers"] = get_dns_servers(domain)

    # 6. MX Records
    results["mx_records"] = get_mx_records(domain)

    # 7. WHOIS Information
    results["whois_info"] = get_whois_info(domain)

    return results

def find_related_domains_and_subdomains(domain: str) -> tuple:
    related_domains = []
    subdomains = {}

    # Use search engines to find related domains and subdomains
    search_engines = [
        f"https://www.google.com/search?q=site%3A{domain}",
        f"https://www.bing.com/search?q=site%3A{domain}",
        f"https://search.yahoo.com/search?p=site%3A{domain}"
    ]

    for engine in search_engines:
        try:
            response = requests.get(engine, headers={"User-Agent": "Mozilla/5.0"})
            soup = BeautifulSoup(response.text, 'html.parser')
            links = soup.find_all('a')
            for link in links:
                href = link.get('href')
                if href and domain in href:
                    parsed_url = urlparse(href)
                    if parsed_url.netloc:
                        if parsed_url.netloc == domain:
                            subdomain = parsed_url.hostname
                            if subdomain not in subdomains:
                                subdomains[subdomain] = []
                        else:
                            related_domains.append(parsed_url.netloc)

        except Exception as e:
            logger.error(f"Error searching {engine}: {str(e)}")

    # Resolve IP addresses for subdomains
    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_subdomain = {executor.submit(resolve_ip, subdomain): subdomain for subdomain in subdomains}
        for future in as_completed(future_to_subdomain):
            subdomain = future_to_subdomain[future]
            try:
                ip = future.result()
                if ip:
                    subdomains[subdomain].append(ip)
            except Exception as e:
                logger.error(f"Error resolving {subdomain}: {str(e)}")

    return list(set(related_domains)), subdomains

def resolve_ip(domain: str) -> str:
    try:
        return socket.gethostbyname(domain)
    except socket.gaierror:
        return ""

def get_ssl_info(domain: str) -> Dict[str, Any]:
    try:
        context = ssl.create_default_context()
        with socket.create_connection((domain, 443)) as sock:
            with context.wrap_socket(sock, server_hostname=domain) as secure_sock:
                cert = secure_sock.getpeercert()
                return {
                    "subject": dict(x[0] for x in cert['subject']),
                    "issuer": dict(x[0] for x in cert['issuer']),
                    "version": cert['version'],
                    "serialNumber": cert['serialNumber'],
                    "notBefore": cert['notBefore'],
                    "notAfter": cert['notAfter'],
                    "subjectAltName": cert.get('subjectAltName', [])
                }
    except Exception as e:
        logger.error(f"Error getting SSL info for {domain}: {str(e)}")
        return {}

def get_file_hashes(domain: str) -> List[Dict[str, str]]:
    file_hashes = []
    try:
        response = requests.get(f"https://{domain}", headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(response.text, 'html.parser')
        for script in soup.find_all('script', src=True):
            script_url = script['src']
            if not script_url.startswith(('http://', 'https://')):
                script_url = f"https://{domain}/{script_url.lstrip('/')}"
            try:
                script_content = requests.get(script_url).content
                file_hash = hashlib.sha256(script_content).hexdigest()
                file_hashes.append({"url": script_url, "sha256": file_hash})
            except Exception as e:
                logger.error(f"Error hashing script {script_url}: {str(e)}")
    except Exception as e:
        logger.error(f"Error fetching page content for {domain}: {str(e)}")
    return file_hashes

def get_dns_records(domain: str) -> Dict[str, List[str]]:
    record_types = ['A', 'AAAA', 'CNAME', 'MX', 'NS', 'TXT', 'SOA']
    dns_records = {}

    for record_type in record_types:
        try:
            answers = dns.resolver.resolve(domain, record_type)
            dns_records[record_type] = [str(rdata) for rdata in answers]
        except dns.exception.DNSException:
            dns_records[record_type] = []

    return dns_records

def get_dns_servers(domain: str) -> List[str]:
    try:
        answers = dns.resolver.resolve(domain, 'NS')
        return [str(rdata) for rdata in answers]
    except dns.exception.DNSException:
        return []

def get_mx_records(domain: str) -> List[Dict[str, Any]]:
    try:
        answers = dns.resolver.resolve(domain, 'MX')
        return [{"preference": rdata.preference, "exchange": str(rdata.exchange)} for rdata in answers]
    except dns.exception.DNSException:
        return []

def get_whois_info(domain: str) -> Dict[str, Any]:
    try:
        w = whois.whois(domain)
        return {
            "domain_name": w.domain_name,
            "registrar": w.registrar,
            "creation_date": w.creation_date,
            "expiration_date": w.expiration_date,
            "name_servers": w.name_servers,
            "registrant": w.registrant,
            "admin": w.admin,
            "tech": w.tech,
            "billing": w.billing
        }
    except Exception as e:
        logger.error(f"Error getting WHOIS info for {domain}: {str(e)}")
        return {}

if __name__ == "__main__":
    import json
    domain = input("Enter a domain for comprehensive passive reconnaissance: ")
    results = comprehensive_passive_recon(domain)
    print(json.dumps(results, indent=2, default=str))