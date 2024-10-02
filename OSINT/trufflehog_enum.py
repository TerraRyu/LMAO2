import subprocess
import json
import os
from typing import Dict, Any

def run_trufflehog(repo_url: str) -> Dict[str, Any]:
    trufflehog_path = os.path.join("repos", "trufflehog", "trufflehog")
    output_file = "trufflehog_output.json"

    # Run TruffleHog
    cmd = [
        trufflehog_path,
        "git",
        repo_url,
        "--json",
        "--only-verified",
        "--no-update",
        "--fail"
    ]

    print(f"Running TruffleHog command: {' '.join(cmd)}")

    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        
        # TruffleHog outputs results to stdout, so we need to parse it
        trufflehog_data = [json.loads(line) for line in result.stdout.splitlines() if line.strip()]

        results = process_trufflehog_results(trufflehog_data)
        print("TruffleHog Results:")
        print(json.dumps(results, indent=2))
        return results
    except subprocess.CalledProcessError as e:
        error_message = f"Error running TruffleHog: {e}\n"
        error_message += f"Command: {' '.join(cmd)}\n"
        error_message += f"Exit code: {e.returncode}\n"
        error_message += f"stdout: {e.stdout}\n"
        error_message += f"stderr: {e.stderr}\n"
        print(error_message)
        return {
            "error": error_message,
            "exposed_secrets": [],
            "sensitive_information": []
        }
    except Exception as e:
        error_message = f"Unexpected error: {str(e)}"
        print(error_message)
        return {
            "error": error_message,
            "exposed_secrets": [],
            "sensitive_information": []
        }

def process_trufflehog_results(trufflehog_data: list) -> Dict[str, Any]:
    results = {
        "exposed_secrets": [],
        "sensitive_information": []
    }

    for item in trufflehog_data:
        secret_type = item.get("DetectorType")
        file_path = item.get("SourceMetadata", {}).get("Data", {}).get("Git", {}).get("file")
        commit = item.get("SourceMetadata", {}).get("Data", {}).get("Git", {}).get("commit")
        
        result = {
            "type": secret_type,
            "file": file_path,
            "commit": commit,
            "detector": item.get("DetectorName"),
            "raw": item.get("Raw")
        }

        if item.get("Verified"):
            results["exposed_secrets"].append(result)
        else:
            results["sensitive_information"].append(result)

    return results

if __name__ == "__main__":
    repo_url = input("Enter a GitHub repository URL to scan with TruffleHog: ")
    results = run_trufflehog(repo_url)
    print(json.dumps(results, indent=2))