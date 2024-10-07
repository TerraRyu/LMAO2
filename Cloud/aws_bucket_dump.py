import subprocess
import json
import os
from typing import Dict, Any

def run_aws_bucket_dump(domain: str) -> Dict[str, Any]:
    aws_bucket_dump_path = os.path.join("repos", "AWSBucketDump", "AWSBucketDump.py")
    if not os.path.exists(aws_bucket_dump_path):
        return {"error": "AWSBucketDump script not found"}

    output_file = "aws_bucket_dump_output.txt"
    cmd = [
        "python3",
        aws_bucket_dump_path,
        "-l", domain,
        "-g", "interesting_Keywords.txt",
        "-o", output_file
    ]

    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        
        with open(output_file, "r") as f:
            output = f.read()

        os.remove(output_file)

        return process_aws_bucket_dump_output(output)
    except subprocess.CalledProcessError as e:
        return {"error": f"AWSBucketDump failed: {e.stderr}"}
    except Exception as e:
        return {"error": f"Unexpected error in AWSBucketDump: {str(e)}"}

def process_aws_bucket_dump_output(output: str) -> Dict[str, Any]:
    results = {
        "open_buckets": [],
        "accessible_files": []
    }

    for line in output.split('\n'):
        if line.startswith("[+]"):
            results["open_buckets"].append(line.split("[+]")[1].strip())
        elif line.startswith("[!]"):
            results["accessible_files"].append(line.split("[!]")[1].strip())

    return results

if __name__ == "__main__":
    domain = input("Enter a domain to scan for AWS S3 buckets: ")
    results = run_aws_bucket_dump(domain)
    print(json.dumps(results, indent=2))