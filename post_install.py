import os
import subprocess
import sys
import platform

def run_command(command):
    result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return result.stdout.decode(), result.stderr.decode()

def is_tool_installed(tool_name):
    try:
        subprocess.run([tool_name, "--version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except subprocess.CalledProcessError:
        return False
    except FileNotFoundError:
        return False

def is_go_installed():
    try:
        subprocess.run("go version", shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except subprocess.CalledProcessError:
        return False
    
def install_go():
    system = platform.system().lower()
    if system == "linux":
        print("Please install Go manually on Linux. Visit https://golang.org/doc/install for instructions.")
    elif system == "darwin":
        try:
            run_command("brew install go")
        except subprocess.CalledProcessError:
            print("Failed to install Go. Please install it manually from https://golang.org/doc/install")
    elif system == "windows":
        print("Please install Go manually on Windows. Visit https://golang.org/doc/install for instructions.")
    else:
        print(f"Unsupported system: {system}. Please install Go manually from https://golang.org/doc/install")

def is_nuclei_installed():
    try:
        subprocess.run("nuclei -version", shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except subprocess.CalledProcessError:
        return False
    except FileNotFoundError:
        return False

def install_nuclei():
    print("Installing Nuclei...")
    try:
        run_command("go install -v github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest")
        print("Nuclei installed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to install Nuclei: {e}")
        print("Please try installing Nuclei manually.")

def install_subzy():
    print("Installing Subzy...")
    try:
        run_command("go install -v github.com/LukaSikic/subzy@latest")
        print("Subzy installed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to install Subzy: {e}")
        print("Please try installing Subzy manually.")

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
        print("Go is not installed. Attempting to install Go...")
        install_go()
        if not is_go_installed():
            print("Failed to install Go. Please install it manually from https://golang.org/dl/ and ensure it's in your PATH.")
            sys.exit(1)

    # Check if Nuclei is installed
    if not is_tool_installed("nuclei"):
        print("Nuclei is not installed. Installing Nuclei...")
        install_nuclei()
        if not is_tool_installed("nuclei"):
            print("Failed to install Nuclei. Please install it manually.")

    # Check if Subzy is installed
    if not is_tool_installed("subzy"):
        print("Subzy is not installed. Installing Subzy...")
        install_subzy()
        if not is_tool_installed("subzy"):
            print("Failed to install Subzy. Please install it manually.")

    print("Setup completed successfully.")

except subprocess.CalledProcessError as e:
    print(f"An error occurred: {e}")
    print(f"Command output: {e.stdout.decode()}")
    print(f"Command error: {e.stderr.decode()}")
