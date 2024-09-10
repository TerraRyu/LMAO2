import subprocess
import json
import logging
from typing import Dict, Any, List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def subzy_enum(domain: str, concurrency: int = 10, hide_fails: bool = False, use_https: bool = False, timeout: int = 10, verify_ssl: bool = False) -> Dict[str, Any]:
    output_file = "subzy_result.txt"
    cmd = ["subzy", "run", "--target", domain]
    
    cmd.extend(["--concurrency", str(concurrency)])
    if hide_fails:
        cmd.append("--hide_fails")
    if use_https:
        cmd.append("--https")
    cmd.extend(["--timeout", str(timeout)])
    if verify_ssl:
        cmd.append("--verify_ssl")
    
    cmd.extend(["--output", output_file])

    try:
        process = subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        output = process.stdout
        logger.debug(f"Subzy raw output: {output}")
    except subprocess.CalledProcessError as e:
        logger.error(f"Subzy scan failed: {e.stderr}")
        return {"error": f"Subzy scan failed: {e.stderr}"}

    try:
        results = json.loads(output)
        return process_subzy_results(results)
    except json.JSONDecodeError:
        logger.warning("Failed to parse Subzy output as JSON, returning raw output")
        return {"raw_output": output.strip()}

def process_subzy_results(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    processed_results = {
        "vulnerable": [],
        "not_vulnerable": [],
        "errors": []
    }

    if isinstance(results, list):
        for result in results:
            if isinstance(result, dict):
                if result.get("vulnerable"):
                    processed_results["vulnerable"].append(result)
                elif "error" in result:
                    processed_results["errors"].append(result)
                else:
                    processed_results["not_vulnerable"].append(result)
            else:
                logger.warning(f"Unexpected result type from Subzy: {type(result)}")
    else:
        logger.warning(f"Unexpected results type from Subzy: {type(results)}")
        processed_results["errors"].append({"error": "Unexpected results format"})

    return processed_results

if __name__ == "__main__":
    domain = input("Enter a domain to scan with Subzy: ")
    results = subzy_enum(domain)
    print(json.dumps(results, indent=2))