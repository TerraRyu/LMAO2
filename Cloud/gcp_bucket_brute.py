import subprocess
import json
import os
from typing import Dict, Any

def run_gcp_bucket_brute(domain: str) -> Dict[str, Any]:
    gcp_bucket_brute_path = os.path.join("repos", "GCPBucketBrute", "gcpbucketbrute.py")
    if not os.path.exists(gcp_bucket_brute_path):
        return {"error": "GCPBucketBrute script not found"}

    output_file = "gcp_bucket_brute_output.txt"
    cmd = [
        "python3",
        gcp_bucket_brute_path,
        "-k", domain,
        "-u",
        "-o", output_file
    ]

    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        
        with open(output_file, "r") as f:
            output = f.read()

        os.remove(output_file)

        return process_gcp_bucket_brute_output(output)
    except subprocess.CalledProcessError as e:
        return {"error": f"GCPBucketBrute failed: {e.stderr}"}
    except Exception as e:
        return {"error": f"Unexpected error in GCPBucketBrute: {str(e)}"}

def process_gcp_bucket_brute_output(output: str) -> Dict[str, Any]:
    results = {
        "public_buckets": [],
        "accessible_files": []
    }

    for line in output.split('\n'):
        if "is publicly accessible" in line:
            results["public_buckets"].append(line.split(":")[0].strip())
        elif "File found:" in line:
            results["accessible_files"].append(line.split("File found:")[1].strip())

    return results

if __name__ == "__main__":
    domain = input("Enter a domain to scan for GCP buckets: ")
    results = run_gcp_bucket_brute(domain)
    print(json.dumps(results, indent=2))