import os
import platform
import subprocess
import sys

def get_venv_python():
    venv_dir = os.path.join(os.getcwd(), "venv")
    if platform.system() == "Windows":
        return os.path.join(venv_dir, "Scripts", "python.exe")
    return os.path.join(venv_dir, "bin", "python")

def main():
    venv_python = get_venv_python()
    
    if not os.path.exists(venv_python):
        print("Virtual environment not found. Running post_install.py...")
        subprocess.run([sys.executable, "post_install.py"], check=True)
    
    print("Starting the application...")
    try:
        process = subprocess.Popen([venv_python, "app.py"])
        process.wait()
    except KeyboardInterrupt:
        print("\nStopping the application...")
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
        print("Application stopped.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nSetup interrupted by user.")
    except Exception as e:
        print(f"An unexpected error occurred during setup: {e}")