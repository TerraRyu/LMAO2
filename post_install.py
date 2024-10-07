import os
import subprocess
import sys
import platform
import venv

def run_command(command):
    try:
        result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        print(result.stdout)
        return result.stdout, result.stderr
    except subprocess.CalledProcessError as e:
        print(f"Command failed with exit code {e.returncode}")
        print(f"stdout: {e.stdout}")
        print(f"stderr: {e.stderr}")
        raise

def check_venv(venv_dir):
    if os.path.exists(venv_dir):
        if os.path.exists(os.path.join(venv_dir, "pyvenv.cfg")):
            return True
    return False

def create_or_update_venv(venv_dir):
    if check_venv(venv_dir):
        print(f"Existing virtual environment found in {venv_dir}")
        print("Updating virtual environment...")
        if platform.system() == "Windows":
            python = os.path.join(venv_dir, "Scripts", "python.exe")
        else:
            python = os.path.join(venv_dir, "bin", "python")
        run_command(f'"{python}" -m pip install --upgrade pip')
    else:
        print(f"Creating new virtual environment in {venv_dir}")
        venv.create(venv_dir, with_pip=True)
    return venv_dir

def get_venv_python(venv_dir):
    if platform.system() == "Windows":
        return os.path.join(venv_dir, "Scripts", "python.exe")
    return os.path.join(venv_dir, "bin", "python")

def is_tool_installed(tool_name):
    try:
        subprocess.run([tool_name, "--version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
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

# def clone_or_update_repo(repo_url, folder_name):
#     if not os.path.exists("repos"):
#         os.makedirs("repos")
#     source_folder = os.path.join(os.getcwd(), "repos", folder_name)
#     print(os.path.exists(source_folder))
#     if not os.path.exists(source_folder):
#         os.chdir("repos")
#         print(os.path)
#         print(f"Cloning {repo_url}...")
#         run_command(f"git clone {repo_url}")
#         print(f"Repository cloned successfully to {source_folder}")
#     else:
#         print(f"Updating existing repository at {source_folder}...")
#         os.chdir(folder_name)
#         run_command("git pull")
#         os.chdir("..")
#         print(f"Repository updated successfully")

def clone_or_update_repo(repo_url, folder_name):
    # Check if the "repos" folder exists, create it if not
    repos_folder = os.path.join(os.getcwd(), "repos")
    if not os.path.exists(repos_folder):
        os.makedirs(repos_folder)
    
    # Set the folder path for the repository
    source_folder = os.path.join(repos_folder, folder_name)
    
    os.chdir(repos_folder)
    
    if not os.path.exists(source_folder):
        print(f"Cloning {repo_url} into {source_folder}...")
        run_command(f"git clone {repo_url}")
        print(f"Repository cloned successfully to {source_folder}")
    else:
        print(f"Updating existing repository at {source_folder}...")
        os.chdir(folder_name)
        run_command("git pull")
        print(f"Repository updated successfully")
    
    os.chdir(os.path.dirname(repos_folder))  # Go back to the main directory

def install_requirements(requirements_file):
    print(f"Installing requirements from {requirements_file}...")
    try:
        run_command(f"{sys.executable} -m pip install -r {requirements_file}")
        print("Requirements installed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to install requirements: {e}")
        print("Please try installing the requirements manually.")

def main():
    venv_dir = os.path.join(os.getcwd(), "venv")
    venv_dir = create_or_update_venv(venv_dir)
    venv_python = get_venv_python(venv_dir)

    # Install requirements
    print("Installing requirements...")
    with open('requirements.txt', 'r') as f:
        requirements = f.read().splitlines()
    
    for requirement in requirements:
        if requirement.strip() and not requirement.startswith('#'):
            try:
                print(f"Installing {requirement}")
                run_command(f'"{venv_python}" -m pip install {requirement}')
            except subprocess.CalledProcessError:
                print(f"Failed to install {requirement}")
                continue

    cache_dir = os.path.join(os.getcwd(), "cache")
    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir)
        print(f"Created cache directory: {cache_dir}")

    # Clone or update repositories
    repos = [
        "https://github.com/nmmapper/dnsdumpster.git",
        "https://github.com/darkoperator/dnsrecon.git",
        "https://github.com/laramies/theHarvester.git",
        "https://github.com/smicallef/spiderfoot.git",
        "https://github.com/trufflesecurity/trufflehog.git",
        "https://github.com/m0rtem/CloudFail.git"
    ]

    for repo_url in repos:
        folder_name = repo_url.split("/")[-1].replace(".git", "")
        clone_or_update_repo(repo_url, folder_name)

    # Install additional requirements for cloned repositories
    additional_requirements = [
        "repos/dnsdumpster/requirements.txt",
        "repos/dnsrecon/requirements.txt",
        "repos/theHarvester/requirements.txt",
        "repos/spiderfoot/requirements.txt",
        "repos/CloudFail/requirements.txt"
    ]

    for req_file in additional_requirements:
        if os.path.exists(req_file):
            print(f"Installing requirements from {req_file}...")
            run_command(f'"{venv_python}" -m pip install -r {req_file}')

    # Install TruffleHog
    print("Installing TruffleHog...")
    os.chdir("repos/trufflehog")
    run_command("go build")
    os.chdir("../..")

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

if __name__ == "__main__":
    main()