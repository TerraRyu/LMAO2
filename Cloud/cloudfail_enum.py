# functions/cloud_enum.py

import sys
import os
from typing import Dict, Any

# Add CloudFail to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
cloudfail_path = os.path.join(project_root, 'repos', 'CloudFail')
sys.path.append(cloudfail_path)

# Import CloudFail components
try:
    from DNSDumpsterAPI import DNSDumpsterAPI
    from Host import Host
    from Breaker import CloudBreaker
except ImportError as e:
    print(f"Error importing CloudFail components: {e}")
    print(f"CloudFail path: {cloudfail_path}")
    print(f"Python path: {sys.path}")
    DNSDumpsterAPI = None
    Host = None
    CloudBreaker = None

def cloud_enum(domain: str) -> Dict[str, Any]:
    if DNSDumpsterAPI is None or Host is None or CloudBreaker is None:
        return {"error": "CloudFail components not found"}

    try:
        host = Host(domain)
        
        # Perform DNS enumeration
        dumper = DNSDumpsterAPI(host.name)
        host.dns_records = dumper.DNSdumpster()
        
        # Perform Crimeflare search
        breaker = CloudBreaker(host)
        breaker.run()
        
        results = {
            "cloud_provider": host.cloudflare_ip or "Unknown",
            "dns_records": host.dns_records,
            "subdomains": host.domains,
            "crimeflare_results": breaker.ipv4_results if hasattr(breaker, 'ipv4_results') else []
        }
        
        return results
    except Exception as e:
        return {"error": f"Error running CloudFail components: {str(e)}"}