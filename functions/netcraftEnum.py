import requests
from bs4 import BeautifulSoup
import re

def netcraft_enum(domain):
    subdomains = set()
    url = f"https://searchdns.netcraft.com/?restriction=site+contains&host={domain}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        for link in soup.find_all('a'):
            href = link.get('href')
            if href and 'host' in href:
                subdomain = re.search(f'(?:https?://)?(?:www\.)?([^/]*\.{domain})', href)
                if subdomain:
                    subdomains.add(subdomain.group(1))
    except Exception as e:
        print(f"An error occurred during Netcraft enumeration: {e}")
    return subdomains

if __name__ == "__main__":
    domain = input("Enter a domain to enumerate subdomains: ")
    results = netcraft_enum(domain)
    print(f"Found {len(results)} subdomains:")
    for subdomain in results:
        print(subdomain)