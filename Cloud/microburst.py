import subprocess
import json
import os
from typing import Dict, Any

def run_microburst(domain: str) -> Dict[str, Any]:
    microburst_path = os.path.join("repos", "MicroBurst", "Misc", "Invoke-EnumerateAzureBlobs.ps1")
    if not os.path.exists(microburst_path):
        return {"error": "MicroBurst script not found"}

    output_file = "microburst_output.json"
    cmd = [
        "powershell",
        "-ExecutionPolicy", "Bypass",
        "-File", microburst_path,
        "-Base", domain,
        "-OutputFile", output_file
    ]

    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        
        with open(output_file, "r") as f:
            output = json.load(f)

        os.remove(output_file)

        return process_microburst_output(output)
    except subprocess.CalledProcessError as e:
        return {"error": f"MicroBurst failed: {e.stderr}"}
    except Exception as e:
        return {"error": f"Unexpected error in MicroBurst: {str(e)}"}

def process_microburst_output(output: Dict[str, Any]) -> Dict[str, Any]:
    results = {
        "open_blobs": [],
        "containers": [],
        "files": []
    }

    for blob in output.get("Blobs", []):
        results["open_blobs"].append(blob["URL"])
        for container in blob.get("Containers", []):
            results["containers"].append(container["Name"])
            for file in container.get("Files", []):
                results["files"].append(file["URL"])

    return results

if __name__ == "__main__":
    domain = input("Enter a domain to scan for Azure Blob storage: ")
    results = run_microburst(domain)
    print(json.dumps(results, indent=2))