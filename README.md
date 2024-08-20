```
 _     __  __    _    ___  
| |   |  \/  |  / \  / _ \ 
| |   | |\/| | / _ \| | | |
| |___| |  | |/ ___ \ |_| |
|_____|_|  |_/_/   \_\___/ 
```
# LMAO (Large-scale Mapping & Attack Operations)

## Table of Contents
- [Introduction](#introduction)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

## Introduction
LMAO (Large-scale Mapping & Attack Operations) is a comprehensive web reconnaissance tool designed for penetration testing. It is intended for use by red teamers to conduct cybersecurity assessments by gathering critical information about a target company. The tool automates the collection of data from multiple sources, including public domains, social media, and cloud infrastructures.

## Features
- Domain enumeration
- OSINT (Open Source Intelligence) gathering
- Cloud enumeration
- SSL certificate inspection
- Integration with Netcraft, VirusTotal, ThreatCrowd, and more
- Passive and active reconnaissance capabilities
- Multi-threaded subdomain enumeration
- DNS record analysis
- Nuclei vulnerability scanning

## Installation
To get started with LMAO, follow these steps:

1. Clone the repository:
   ```sh
   git clone https://github.com/yourusername/LMAO.git
   cd LMAO
   ```

2. Run the post-installation script:
   ```sh
   python post_install.py
   ```
   This script will install all required dependencies and set up the necessary components.

3. Ensure that the `bin` directory contains the appropriate Nuclei binary for your operating system:
   - Windows: `nuclei_windows.exe`
   - macOS: `nuclei_macos`
   - Linux: `nuclei_linux`

   If the binary for your system is missing, download it from the [Nuclei GitHub releases page](https://github.com/projectdiscovery/nuclei/releases) and place it in the `bin` directory.

4. Make sure GoLang is installed on your computer and is in your Environment PATH. You can download it from https://go.dev/dl/

## Usage
To run LMAO, use the following command:

```sh
python SearchInterface.py
```

This will launch the graphical user interface where you can:

1. Select search engines
2. Enter a domain for subdomain enumeration
3. Specify the number of results to fetch
4. View and analyze the results

## Project Structure
- `SearchInterface.py`: Main GUI for the application
- `SearchFunctionality.py`: Handles search engine queries
- `SubdomainEnum.py`: Manages subdomain enumeration processes
- `DNSDumpEnum.py`: DNS enumeration using DNSDumpster
- `VTEnum.py`: VirusTotal API integration for subdomain discovery
- `nucleirecon.py`: Nuclei scanner integration for vulnerability detection

## Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contact
For any queries or suggestions, please open an issue in the GitHub repository.

## Disclaimer
This tool is for educational purposes only. Ensure you have permission before scanning any domains you don't own or have explicit permission to test.
