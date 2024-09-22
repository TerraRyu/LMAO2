import subprocess
import json
from pathlib import Path
import sys
import os

def run_osint(company_url):
    harvester_path = os.path.join("theHarvester", "theHarvester.py")
    output_file = "harvester_output.json"
    
    command = [
        sys.executable,
        str(harvester_path),
        "-d",
        company_url,
        "-b",
        "all",
        "-f",
        output_file
    ]
    
    try:
        subprocess.run(command, check=True, capture_output=True, text=True)
        
        with open(output_file, "r") as f:
            harvester_data = json.load(f)
        
        employee_info = extract_employee_info(harvester_data)
        social_engineering_info = extract_social_engineering_info(harvester_data)
        
        return {
            "employee_information": employee_info,
            "potential_social_engineering": social_engineering_info
        }
    except subprocess.CalledProcessError as e:
        print(f"Error running theHarvester: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"Error parsing theHarvester output: {e}")
        return None
    finally:
        if os.path.exists(output_file):
            os.remove(output_file)

def extract_employee_info(harvester_data):
    employee_info = {
        "emails": harvester_data.get("emails", []),
        "linkedin": harvester_data.get("linkedin", []),
        "people": harvester_data.get("people", [])
    }
    return employee_info

def extract_social_engineering_info(harvester_data):
    social_engineering_info = {
        "hosts": harvester_data.get("hosts", []),
        "interesting_urls": harvester_data.get("interesting_urls", []),
        "twitter": harvester_data.get("twitter", []),
        "trello": harvester_data.get("trello", [])
    }
    return social_engineering_info

if __name__ == "__main__":
    company_url = input("Enter the company URL to perform OSINT: ")
    results = run_osint(company_url)
    if results:
        print(json.dumps(results, indent=2))
    else:
        print("Failed to retrieve OSINT information.")