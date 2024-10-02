import subprocess
import json
import os
from typing import Dict, Any

def run_spiderfoot(domain: str) -> Dict[str, Any]:
    spiderfoot_path = os.path.join("repos","spiderfoot", "sf.py")
    output_file = "spiderfoot_output.json"

    if not os.path.exists(spiderfoot_path):
        print(f"SpiderFoot script not found at {spiderfoot_path}")
        return {"error": f"SpiderFoot script not found at {spiderfoot_path}"}

    # Define the modules we want to use
    modules = "sfp_names,sfp_email,sfp_social,sfp_github"

    # Run SpiderFoot
    cmd = [
        "python3",
        spiderfoot_path,
        "-m", modules,
        "-s", domain,
        "-f", "JSON",
        "-o", output_file,
        "-q"
    ]

    print(f"Running SpiderFoot command: {' '.join(cmd)}")

    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        
        if not os.path.exists(output_file):
            print(f"SpiderFoot did not create the output file: {output_file}")
            return {"error": f"SpiderFoot did not create the output file: {output_file}"}

        with open(output_file, "r") as f:
            spiderfoot_data = json.load(f)

        os.remove(output_file)  # Clean up the output file

        results = process_spiderfoot_results(spiderfoot_data)
        print("SpiderFoot Results:")
        print(json.dumps(results, indent=2))
        return results
    except subprocess.CalledProcessError as e:
        error_message = f"Error running SpiderFoot: {e}\n"
        error_message += f"Command: {' '.join(cmd)}\n"
        error_message += f"Exit code: {e.returncode}\n"
        error_message += f"stdout: {e.stdout}\n"
        error_message += f"stderr: {e.stderr}\n"
        print(error_message)
        return {"error": error_message}
    except json.JSONDecodeError as e:
        error_message = f"Error parsing SpiderFoot output: {e}"
        print(error_message)
        return {"error": error_message}
    except Exception as e:
        error_message = f"Unexpected error: {str(e)}"
        print(error_message)
        return {"error": error_message}

def process_spiderfoot_results(spiderfoot_data: list) -> Dict[str, Any]:
    results = {
        "employee_information": [],
        "potential_social_engineering": [],
        "github_repos": []
    }

    for item in spiderfoot_data:
        event_type = item.get("type")
        data = item.get("data")

        if event_type in ["HUMAN_NAME", "EMAIL_ADDRESS"]:
            results["employee_information"].append({
                "type": "name" if event_type == "HUMAN_NAME" else "email",
                "value": data
            })
        elif event_type in ["SOCIAL_MEDIA", "ACCOUNT_EXTERNAL_OWNED"]:
            results["potential_social_engineering"].append({
                "type": "social_media",
                "value": data
            })
        elif event_type == "GITHUB_REPO":
            results["github_repos"].append(data)

    return results

if __name__ == "__main__":
    domain = input("Enter a domain to scan with SpiderFoot: ")
    results = run_spiderfoot(domain)
    print(json.dumps(results, indent=2))