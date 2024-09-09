import os
import sys
import subprocess
from typing import Dict, Any, List
import json
import logging
from prettytable import PrettyTable

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def clone_dnsrecon():
    if not os.path.exists("dnsrecon"):
        logger.info("Cloning DNSRecon repository...")
        subprocess.run(["git", "clone", "https://github.com/darkoperator/dnsrecon.git", "dnsrecon"], check=True)
    else:
        logger.info("DNSRecon repository already exists. Updating...")
        subprocess.run(["git", "-C", "dnsrecon", "pull"], check=True)

def run_dnsrecon(domain: str) -> List[Dict[str, Any]]:
    dnsrecon_path = os.path.join("dnsrecon", "dnsrecon.py")
    if not os.path.exists(dnsrecon_path):
        raise FileNotFoundError(f"DNSRecon script not found at {dnsrecon_path}")

    cmd = [sys.executable, dnsrecon_path, "-d", domain, "-j", "dnsrecon_output.json", "--iw", "-z"]
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
        display_results(processed_results)
        return processed_results
    except Exception as e:
        logger.error(f"An error occurred during DNSRecon enumeration: {str(e)}", exc_info=True)
        return {}

def process_dnsrecon_results(results: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    processed_results = {
        "A": [],
        "AAAA": [],
        "CNAME": [],
        "MX": [],
        "NS": [],
        "SOA": [],
        "SRV": [],
        "TXT": [],
        "PTR": [],
        "Wildcard": [],
        "Zone": []
    }

    for item in results:
        record_type = item.get("type")
        if record_type in processed_results:
            processed_results[record_type].append(item)
        elif record_type == "info":
            if "zone_transfer" in item.get("arguments", {}):
                processed_results["Zone"].append(item)
        elif record_type == "wildcard":
            processed_results["Wildcard"].append(item)

    return processed_results

def display_results(results: Dict[str, List[Dict[str, Any]]]):
    for record_type, records in results.items():
        if records:
            table = PrettyTable()
            table.title = f"{record_type} Records"
            
            if record_type in ["A", "AAAA", "CNAME", "PTR"]:
                table.field_names = ["Name", "Address"]
                for record in records:
                    table.add_row([record.get("name"), record.get("address")])
            elif record_type == "MX":
                table.field_names = ["Name", "Address", "Priority"]
                for record in records:
                    table.add_row([record.get("name"), record.get("address"), record.get("exchange")])
            elif record_type in ["NS", "SOA"]:
                table.field_names = ["Name", "Target"]
                for record in records:
                    table.add_row([record.get("name"), record.get("target")])
            elif record_type == "SRV":
                table.field_names = ["Name", "Target", "Port", "Priority", "Weight"]
                for record in records:
                    table.add_row([record.get("name"), record.get("target"), record.get("port"),
                                   record.get("priority"), record.get("weight")])
            elif record_type == "TXT":
                table.field_names = ["Name", "Text"]
                for record in records:
                    table.add_row([record.get("name"), record.get("strings")])
            elif record_type == "Wildcard":
                table.field_names = ["Name", "Type", "Content"]
                for record in records:
                    table.add_row([record.get("name"), record.get("type"), record.get("content")])
            elif record_type == "Zone":
                table.field_names = ["Type", "Name", "Content"]
                for record in records:
                    for zone_record in record.get("arguments", {}).get("zone_transfer", []):
                        table.add_row([zone_record.get("type"), zone_record.get("name"), zone_record.get("address")])
            
            print(table)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python dnsrecon.py <domain>")
        sys.exit(1)
    
    domain = sys.argv[1]
    dnsrecon_enum(domain)