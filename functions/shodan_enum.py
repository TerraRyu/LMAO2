import shodan
from typing import Dict, Any
import logging
import requests

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SHODAN_API_KEY = "ZkrzCqYh6cH5ubsiMmtFHoedt3HvbTiM"

def shodan_enum(domain: str) -> Dict[str, Any]:
    api = shodan.Shodan(SHODAN_API_KEY)
    results = {
        "ip_addresses": [],
        "open_ports": set(),
        "vulnerabilities": [],
        "technologies": set(),
        "hostnames": set(),
        "operating_systems": set(),
    }

    try:
        # Check API info
        api_info = api.info()
        logger.info(f"Shodan API Info: {api_info}")

        if api_info['plan'] == 'oss' and api_info['query_credits'] == 0:
            logger.warning("Free plan detected with no query credits. Using alternative method.")
            return free_plan_enum(domain)

        # If we have credits, proceed with the original search
        search_results = api.search(f"hostname:{domain}")
        
        logger.info(f"Shodan search completed. Total results: {search_results['total']}")
        
        for result in search_results['matches']:
            results["ip_addresses"].append(result['ip_str'])
            results["open_ports"].update(result.get('ports', []))
            results["vulnerabilities"].extend(result.get('vulns', []))
            if 'http' in result:
                results["technologies"].update(result['http'].get('components', {}).keys())
            results["hostnames"].update(result.get('hostnames', []))
            if 'os' in result:
                results["operating_systems"].add(result['os'])

        # Convert sets to lists for JSON serialization
        results["open_ports"] = list(results["open_ports"])
        results["technologies"] = list(results["technologies"])
        results["hostnames"] = list(results["hostnames"])
        results["operating_systems"] = list(results["operating_systems"])

        # Remove duplicates from lists
        results["ip_addresses"] = list(set(results["ip_addresses"]))
        results["vulnerabilities"] = list(set(results["vulnerabilities"]))

        logger.info(f"Shodan scan completed for {domain}")
        return results

    except shodan.APIError as e:
        logger.error(f"Shodan API Error: {e}")
        return {"error": f"Shodan API Error: {e}. API Info: {api_info}"}
    except Exception as e:
        logger.exception(f"Unexpected error in Shodan enumeration: {e}")
        return {"error": f"Unexpected error: {e}"}

def free_plan_enum(domain: str) -> Dict[str, Any]:
    """Alternative enumeration method for free plan users"""
    results = {
        "ip_addresses": [],
        "message": "Limited results due to free plan constraints."
    }

    try:
        # Use Shodan's host lookup API, which is often available on free plans
        api = shodan.Shodan(SHODAN_API_KEY)
        host_info = api.host(domain)
        
        results["ip_addresses"].append(host_info.get('ip_str', 'N/A'))
        results["open_ports"] = host_info.get('ports', [])
        results["hostnames"] = host_info.get('hostnames', [])
        results["operating_system"] = host_info.get('os', 'N/A')

        logger.info(f"Basic Shodan lookup completed for {domain}")
        return results

    except shodan.APIError as e:
        logger.error(f"Shodan API Error in free plan enumeration: {e}")
        return {"error": f"Shodan API Error in free plan enumeration: {e}"}
    except Exception as e:
        logger.exception(f"Unexpected error in free plan Shodan enumeration: {e}")
        return {"error": f"Unexpected error in free plan enumeration: {e}"}

if __name__ == "__main__":
    domain = input("Enter a domain to scan with Shodan: ")
    results = shodan_enum(domain)
    print(results)