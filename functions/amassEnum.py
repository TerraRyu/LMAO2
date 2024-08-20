import subprocess
import json

class AmassEnum:
    def __init__(self, domain):
        self.domain = domain

    def run_amass(self):
        try:
            result = subprocess.run(
                ['amass', 'enum', '-d', self.domain, '-json', '-'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            if result.returncode != 0:
                raise Exception(f"Amass error: {result.stderr}")
            
            return json.loads(result.stdout)
        except Exception as e:
            print(f"Error running Amass: {e}")
            return None

    def parse_results(self, results):
        # Assuming you want to extract certain fields from the Amass results
        parsed_results = []
        if results:
            for entry in results:
                parsed_results.append({
                    "name": entry.get("name"),
                    "domain": entry.get("domain"),
                    "addresses": entry.get("addresses"),
                })
        return parsed_results

if __name__ == "__main__":
    domain = "example.com"  # Replace with the target domain
    amass_enum = AmassEnum(domain)
    results = amass_enum.run_amass()
    parsed_results = amass_enum.parse_results(results)
    print(parsed_results)
