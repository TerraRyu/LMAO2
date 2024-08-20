import os
import subprocess
import sys

def run_command(command):
    result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return result.stdout.decode(), result.stderr.decode()

def is_go_installed():
    try:
        subprocess.run("go version", shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except subprocess.CalledProcessError:
        return False

try:
    # Install main project requirements
    print("Installing main project requirements...")
    stdout, stderr = run_command(f"{sys.executable} -m pip install -r requirements.txt")
    print(stdout)
    if stderr:
        print(stderr)

    # Clone the Git repository if not already cloned
    if not os.path.exists("dnsdumpster"):
        print("Cloning dnsdumpster repository...")
        stdout, stderr = run_command("git clone https://github.com/nmmapper/dnsdumpster.git dnsdumpster")
        print(stdout)
        if stderr:
            print(stderr)

    if not os.path.exists("dnsrecon"):
        print("Cloning DNSRecon repository...")
        stdout, stderr = run_command("git clone https://github.com/darkoperator/dnsrecon.git dnsrecon")
        print(stdout)
        if stderr:
            print(stderr)

    # Install the cloned repository's dependencies if a requirements.txt exists
    if os.path.exists("src/dnsdumpster/requirements.txt"):
        print("Installing dnsdumpster requirements...")
        stdout, stderr = run_command(f"{sys.executable} -m pip install -r src/dnsdumpster/requirements.txt")
        print(stdout)
        if stderr:
            print(stderr)

    # Check if Go is installed
    if not is_go_installed():
        print("Go is not installed. Please install Go from https://golang.org/dl/ and ensure it's in your PATH.")
        sys.exit(1)

    # Install nuclei using go install
    print("Installing nuclei tool...")
    stdout, stderr = run_command("go install -v github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest")
    print(stdout)
    if stderr:
        print(stderr)

    print("Setup completed successfully.")

except subprocess.CalledProcessError as e:
    print(f"An error occurred: {e}")
    print(f"Command output: {e.stdout.decode()}")
    print(f"Command error: {e.stderr.decode()}")
