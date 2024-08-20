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

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Ensure the path to dnsdumpster.py is correct
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
dnsdumpster_dir = os.path.join(parent_dir, 'dnsdumpster')
sys.path.append(dnsdumpster_dir)

def update_dnsdumpster_repo() -> None:
    logger.info("Checking for DNSDumpster updates...")
    repo_url = "https://github.com/nmmapper/dnsdumpster.git"
    
    if not os.path.exists(dnsdumpster_dir):
        logger.info("DNSDumpster repository not found. Cloning...")
        try:
            git.Repo.clone_from(repo_url, dnsdumpster_dir)
            logger.info("DNSDumpster repository cloned successfully.")
        except git.exc.GitCommandError as e:
            logger.error(f"Error cloning repository: {e}")
            logger.info("Attempting to pull from the repository...")
            try:
                repo = git.Repo.init(dnsdumpster_dir)
                origin = repo.create_remote('origin', repo_url)
                origin.fetch()
                origin.pull(origin.refs[0].remote_head)
                logger.info("Successfully pulled DNSDumpster repository.")
            except git.exc.GitCommandError as pull_error:
                logger.error(f"Error pulling repository: {pull_error}")
                logger.warning("Please manually clone the repository from https://github.com/nmmapper/dnsdumpster.git")
    else:
        try:
            repo = git.Repo(dnsdumpster_dir)
            origin = repo.remotes.origin
            origin.fetch()
            if repo.head.commit != origin.refs.master.commit:
                logger.info("Updates available. Pulling latest changes...")
                origin.pull()
                logger.info("DNSDumpster repository updated successfully.")
            else:
                logger.info("DNSDumpster repository is up to date.")
        except git.exc.GitCommandError as e:
            logger.error(f"An error occurred while updating DNSDumpster: {e}")

update_dnsdumpster_repo()

from dnsdumpster.dnsdumpster import main as dnsdumpster_main

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
    if not domain:
        logger.error("Invalid domain provided to DNSDumpster")
        return {}

    logger.info(f"Starting DNSDumpster enumeration for {domain}")
    try:
        dnsrecords = dnsdumpster_main(domain)
        results = parse_results(dnsrecords)
        
        # Add dig MX records
        dig_mx = dig_mx_records(domain)
        results['mx_records'].extend(dig_mx)
        
        logger.debug("DNSDumpster raw results: %s", dnsrecords)
        logger.debug("DNSDumpster parsed results: %s", results)
        return results
    except Exception as e:
        logger.exception(f"Error in DNSDumpsterEnum: {str(e)}")
        return {}

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