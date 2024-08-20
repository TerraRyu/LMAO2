import requests
import urllib3

# Disable the InsecureRequestWarning
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def threatcrowd_enum(domain):
    subdomains = set()
    url = f"https://www.threatcrowd.org/searchApi/v2/domain/report/"
    params = {'domain': domain}
    
    try:
        response = requests.get(url, params=params, timeout=10, verify=False)
        response.raise_for_status()
        
        result = response.json()
        if 'subdomains' in result:
            subdomains.update(result['subdomains'])
    except requests.exceptions.RequestException as e:
        print(f"An error occurred while querying ThreatCrowd: {e}")
    
    return subdomains

if __name__ == "__main__":
    domain = input("Enter a domain to enumerate subdomains: ")
    results = threatcrowd_enum(domain)
    print(f"Found {len(results)} subdomains:")
    for subdomain in results:
        print(subdomain)