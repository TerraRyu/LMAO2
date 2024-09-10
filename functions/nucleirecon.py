# import os
# import subprocess
# import json
# from datetime import datetime
# import platform
# import shutil

# class NucleiRecon:
#     def __init__(self, target_domain, subdomains):
#         self.target_domain = target_domain
#         self.subdomains = subdomains
#         self.templates_dir = "nuclei-templates"
#         self.results_dir = "nuclei_results"
#         self.bin_dir = "bin"
#         self.ensure_directories()

#     def ensure_directories(self):
#         for dir in [self.templates_dir, self.results_dir, self.bin_dir]:
#             os.makedirs(dir, exist_ok=True)

#     def get_nuclei_path(self):
#         system = platform.system().lower()
#         if system == "windows":
#             return os.path.join(self.bin_dir, "nuclei_windows.exe")
#         elif system == "darwin":
#             return os.path.join(self.bin_dir, "nuclei_macos")
#         elif system == "linux":
#             return os.path.join(self.bin_dir, "nuclei_linux")
#         else:
#             raise OSError(f"Unsupported operating system: {system}")

#     def check_templates(self):
#         if not os.listdir(self.templates_dir):
#             print("No templates found. Please download Nuclei templates manually.")
#             print("You can download them from: https://github.com/projectdiscovery/nuclei-templates")
#             print(f"Extract the templates to: {os.path.abspath(self.templates_dir)}")
#             user_input = input("Have you downloaded and extracted the templates? (yes/no): ").lower()
#             if user_input != 'yes':
#                 return False
#         return True

#     def run_nuclei_scan(self):
#         nuclei_path = self.get_nuclei_path()
#         if not os.path.exists(nuclei_path):
#             print(f"Error: Nuclei binary not found at {nuclei_path}")
#             return None

#         if not self.check_templates():
#             print("Templates not available. Skipping Nuclei scan.")
#             return None

#         targets_file = "targets.txt"
#         with open(targets_file, "w") as f:
#             for subdomain in self.subdomains:
#                 f.write(f"http://{subdomain}\n")
#                 f.write(f"https://{subdomain}\n")

#         timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
#         output_file = os.path.join(self.results_dir, f"nuclei_scan_{self.target_domain}_{timestamp}.json")

#         print("Running Nuclei scan...")
        
#         try:
#             command = [
#                 nuclei_path,
#                 "-l", targets_file,
#                 "-t", self.templates_dir,
#                 "-o", output_file,
#                 "-j",  # Use -j for JSON output
#                 "-silent"
#             ]
            
#             process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
#             stdout, stderr = process.communicate()

#             if process.returncode != 0:
#                 print(f"Error running Nuclei: {stderr}")
#                 return None

#             print("Nuclei scan completed successfully.")
#         except subprocess.CalledProcessError as e:
#             print(f"Error running Nuclei: {e}")
#             return None
#         except FileNotFoundError:
#             print(f"Error: Nuclei executable not found at {nuclei_path}")
#             return None

#         os.remove(targets_file)
#         return output_file

#     def check_nuclei_installation(self):
#         nuclei_path = self.get_nuclei_path()
#         if not os.path.exists(nuclei_path):
#             print("Error: Nuclei is not installed or not in the expected location.")
#             print(f"Expected path: {nuclei_path}")
#             print("Please ensure Nuclei is installed and in the correct location.")
#             return False
#         return True

#     def run_recon(self):
#         if not self.check_nuclei_installation():
#             print("Skipping Nuclei scan due to installation issues.")
#             return []

#         output_file = self.run_nuclei_scan()
#         if output_file:
#             return self.parse_results(output_file)
#         return []

#     def parse_results(self, output_file):
#         vulnerabilities = []
#         if output_file and os.path.exists(output_file):
#             with open(output_file, "r") as f:
#                 for line in f:
#                     try:
#                         result = json.loads(line)
#                         vulnerabilities.append({
#                             "template": result["template-id"],
#                             "host": result["host"],
#                             "matched": result["matched-at"],
#                             "severity": result["info"]["severity"],
#                             "name": result["info"]["name"],
#                             "description": result["info"].get("description", "N/A")
#                         })
#                     except json.JSONDecodeError:
#                         print(f"Error parsing line: {line}")
#         return vulnerabilities

# if __name__ == "__main__":
#     domain = input("Enter a domain to scan: ")
#     subdomains = input("Enter subdomains (comma-separated): ").split(",")
#     nuclei_recon = NucleiRecon(domain, subdomains)
#     results = nuclei_recon.run_recon()
#     print(f"Found {len(results)} vulnerabilities.")
#     for vuln in results:
#         print(f"Template: {vuln['template']}")
#         print(f"Host: {vuln['host']}")
#         print(f"Severity: {vuln['severity']}")
#         print(f"Name: {vuln['name']}")
#         print(f"Description: {vuln['description']}")
#         print("---")


import subprocess
import json
import os
from typing import Dict, Any
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def nuclei_enum(domain: str) -> Dict[str, Any]:
    # Ensure Nuclei is installed
    try:
        version_output = subprocess.run(["nuclei", "-version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        logger.info(f"Nuclei version: {version_output.stdout.strip()}")
    except subprocess.CalledProcessError:
        logger.error("Nuclei is not installed or not in PATH. Please install Nuclei and ensure it's in your system PATH.")
        return {"error": "Nuclei not installed"}
    except FileNotFoundError:
        logger.error("Nuclei executable not found. Please install Nuclei and ensure it's in your system PATH.")
        return {"error": "Nuclei not found"}

    # Run Nuclei scan
    output_file = "nuclei_output.json"
    cmd = ["nuclei", "-u", domain, "-no-mhe", "-o", output_file]
    
    try:
        process = subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        logger.debug(f"Nuclei stdout: {process.stdout}")
        logger.debug(f"Nuclei stderr: {process.stderr}")
    except subprocess.CalledProcessError as e:
        logger.error(f"Nuclei scan failed: {e.stderr}")
        return {"error": f"Nuclei scan failed: {e.stderr}"}

    # Read the output file
    try:
        with open(output_file, 'r') as f:
            output = f.read()
        logger.debug(f"Nuclei raw output: {output}")
    except FileNotFoundError:
        logger.error(f"Nuclei output file not found: {output_file}")
        return {"error": "Nuclei output file not found"}
    finally:
        # Clean up the output file
        if os.path.exists(output_file):
            os.remove(output_file)

    return process_nuclei_results(output)

def process_nuclei_results(output: str) -> Dict[str, Any]:
    processed_results = {
        "vulnerabilities": [],
        "information": []
    }

    for line in output.strip().split('\n'):
        try:
            result = json.loads(line)
            entry = {
                "name": result.get("info", {}).get("name"),
                "severity": result.get("info", {}).get("severity"),
                "description": result.get("info", {}).get("description"),
                "matched_at": result.get("matched-at")
            }
            if result.get("info", {}).get("severity") in ["critical", "high", "medium", "low"]:
                processed_results["vulnerabilities"].append(entry)
            else:
                processed_results["information"].append(entry)
        except json.JSONDecodeError:
            logger.warning(f"Failed to parse Nuclei output line as JSON: {line}")
            processed_results["information"].append({"raw_output": line})

    return processed_results

if __name__ == "__main__":
    domain = input("Enter a domain to scan with Nuclei: ")
    results = nuclei_enum(domain)
    print(json.dumps(results, indent=2))