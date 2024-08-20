import os
import sys
import subprocess
from typing import Dict, Any
import json

def clone_dnsrecon():
    if not os.path.exists("dnsrecon"):
        print("Cloning DNSRecon repository...")
        subprocess.run(["git", "clone", "https://github.com/darkoperator/dnsrecon.git", "dnsrecon"], check=True)
    else:
        print("DNSRecon repository already exists. Updating...")
        subprocess.run(["git", "-C", "dnsrecon", "pull"], check=True)

def run_dnsrecon(domain: str) -> Dict[str, Any]:
    dnsrecon_path = os.path.join("dnsrecon", "dnsrecon.py")
    if not os.path.exists(dnsrecon_path):
        raise FileNotFoundError(f"DNSRecon script not found at {dnsrecon_path}")

    cmd = [sys.executable, dnsrecon_path, "-d", domain, "-j", "dnsrecon_output.json"]
    subprocess.run(cmd, check=True)

    with open("dnsrecon_output.json", "r") as f:
        results = json.load(f)

    os.remove("dnsrecon_output.json")
    return results

def dnsrecon_enum(domain: str) -> Dict[str, Any]:
    try:
        clone_dnsrecon()
        results = run_dnsrecon(domain)
        processed_results = process_dnsrecon_results(results)
        return processed_results
    except Exception as e:
        print(f"An error occurred during DNSRecon enumeration: {str(e)}")
        return {}

def process_dnsrecon_results(results: list) -> Dict[str, Any]:
    processed_results = {
        "subdomains": [],
        "dns_records": [],
        "mx_records": []
    }

    for item in results:
        if item["type"] == "A":
            processed_results["subdomains"].append({
                "domain": item["name"],
                "ip": item["address"]
            })
        elif item["type"] in ["NS", "SOA"]:
            processed_results["dns_records"].append({
                "type": item["type"],
                "name": item["name"],
                "address": item["address"]
            })
        elif item["type"] == "MX":
            processed_results["mx_records"].append({
                "name": item["name"],
                "address": item["address"],
                "priority": item["exchange"]
            })

    return processed_results