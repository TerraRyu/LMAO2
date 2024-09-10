// document.addEventListener('DOMContentLoaded', function() {
//     checkEnumerationStatus();
//     const queryInput = document.getElementById('queryInput');
//     const submitBtn = document.getElementById('submitBtn');
//     const scanButtons = document.querySelectorAll('.scan-btn');
//     let selectedScanType = null;

//     scanButtons.forEach(button => {
//         button.addEventListener('click', function() {
//             scanButtons.forEach(btn => btn.classList.remove('active'));
//             this.classList.add('active');
//             selectedScanType = this.id;
//             submitBtn.disabled = false;
//         });
//     });

//     submitBtn.addEventListener('click', function() {
//         const query = queryInput.value.trim();
//         if (!query) {
//             alert('Please enter a search query or URL.');
//             return;
//         }

//         if (selectedScanType === 'passiveScanBtn') {
//             performPassiveScan(query);
//         } else {
//             alert('This scan type is not implemented yet.');
//         }
//     });
// });

// function checkEnumerationStatus() {
//     console.log('Checking enumeration status for domain:', domain);
//     const domain = new URLSearchParams(window.location.search).get('domain');
//     fetch(`/enumeration_status/${encodeURIComponent(domain)}`)
//         .then(response => {
//             if (!response.ok) {
//                 throw new Error(`HTTP error! status: ${response.status}`);
//             }
//             return response.json();
//         })
//         .then(data => {
//             console.log('Received data:', data);
//             if (data.status === 'complete') {
//                 document.getElementById('loading').style.display = 'none';
//                 document.getElementById('results').style.display = 'block';
//                 displayResults(data.results);
//             } else if (data.status === 'error') {
//                 showError(`An error occurred: ${data.error}`);
//             } else {
//                 setTimeout(checkEnumerationStatus, 5000); // Check again in 5 seconds
//             }
//         })
//         .catch(error => {
//             console.error('Error:', error);
//             showError('An error occurred while checking enumeration status');
//         });
// }

// function populateResults(results) {
//     populateSubdomains(results.subdomains);
//     populateVirusTotal(results.virustotal);
//     populateDNSDumpster(results.dnsdumpster);
//     initializeTables();
// }

// function populateSubdomains(subdomains) {
//     const tbody = document.getElementById('subdomains-body');
//     tbody.innerHTML = '';
//     for (const [subdomain, info] of Object.entries(subdomains)) {
//         const row = tbody.insertRow();
//         row.innerHTML = `
//             <td>${subdomain}</td>
//             <td>${info.ip || 'N/A'}</td>
//             <td>${info.status || 'N/A'}</td>
//             <td>${info.sources.join(', ')}</td>
//         `;
//     }
// }

// function populateVirusTotal(virustotal) {
//     const tbody = document.getElementById('virustotal-body');
//     tbody.innerHTML = '';
//     for (const [subdomain, ips] of Object.entries(virustotal)) {
//         const row = tbody.insertRow();
//         row.innerHTML = `
//             <td>${subdomain}</td>
//             <td>${ips.join(', ')}</td>
//         `;
//     }
// }

// function populateDNSDumpster(dnsdumpster) {
//     let html = '<h4>Subdomains</h4><ul>';
//     for (const subdomain of dnsdumpster.subdomains) {
//         html += `<li>${subdomain.domain} (IP: ${subdomain.ip}, ASN: ${subdomain.asn}, Server: ${subdomain.server})</li>`;
//     }
//     html += '</ul>';

//     html += '<h4>MX Records</h4><ul>';
//     for (const mx of dnsdumpster.mx_records) {
//         html += `<li>${mx.exchange} (Preference: ${mx.preference}, IP: ${mx.ip})</li>`;
//     }
//     html += '</ul>';

//     html += '<h4>TXT Records</h4><ul>';
//     for (const txt of dnsdumpster.txt_records) {
//         html += `<li>${txt}</li>`;
//     }
//     html += '</ul>';

//     document.getElementById('dnsdumpster-content').innerHTML = html;
// }

// function initializeTables() {
//     $('#subdomains-table').DataTable({
//         "pageLength": 25,
//         "lengthMenu": [[10, 25, 50, -1], [10, 25, 50, "All"]],
//         "order": []
//     });
//     $('#virustotal-table').DataTable({
//         "pageLength": 25,
//         "lengthMenu": [[10, 25, 50, -1], [10, 25, 50, "All"]],
//         "order": []
//     });
// }

// function openTab(evt, tabName) {
//     var i, tabContent, tabButtons;
//     tabContent = document.getElementsByClassName("tab-content");
//     for (i = 0; i < tabContent.length; i++) {
//         tabContent[i].style.display = "none";
//     }
//     tabButtons = document.getElementsByClassName("tab-button");
//     for (i = 0; i < tabButtons.length; i++) {
//         tabButtons[i].className = tabButtons[i].className.replace(" active", "");
//     }
//     document.getElementById(tabName).style.display = "block";
//     evt.currentTarget.className += " active";
// }

// function openSubTab(evt, tabName) {
//     var i, tabContent, tabButtons;
//     tabContent = document.getElementsByClassName("subtab-content");
//     for (i = 0; i < tabContent.length; i++) {
//         tabContent[i].style.display = "none";
//     }
//     tabButtons = document.getElementsByClassName("subtab-button");
//     for (i = 0; i < tabButtons.length; i++) {
//         tabButtons[i].className = tabButtons[i].className.replace(" active", "");
//     }
//     document.getElementById(tabName).style.display = "block";
//     evt.currentTarget.className += " active";
// }

// function exportResults() {
//     const domain = new URLSearchParams(window.location.search).get('domain');
//     if (!domain) {
//         showError('No domain found for export.');
//         return;
//     }

//     fetch('/export', {
//         method: 'POST',
//         headers: {
//             'Content-Type': 'application/json',
//         },
//         body: JSON.stringify({ domain: domain }),
//     })
//     .then(response => {
//         if (!response.ok) {
//             throw new Error('Network response was not ok');
//         }
//         return response.blob();
//     })
//     .then(blob => {
//         const url = window.URL.createObjectURL(blob);
//         const a = document.createElement('a');
//         a.style.display = 'none';
//         a.href = url;
//         a.download = `${domain}_enumeration_results.xlsx`;
//         document.body.appendChild(a);
//         a.click();
//         window.URL.revokeObjectURL(url);
//     })
//     .catch(error => {
//         console.error('Error:', error);
//         showError('An error occurred while exporting results. Please try again.');
//     });
// }

// function performPassiveScan(domain) {
//     fetch('/passive_scan', {
//         method: 'POST',
//         headers: {
//             'Content-Type': 'application/json',
//         },
//         body: JSON.stringify({ domain: domain }),
//     })
//     .then(response => response.json())
//     .then(data => {
//         displayResults(data);
//     })
//     .catch(error => {
//         console.error('Error:', error);
//         alert('An error occurred during the passive scan. Please try again.');
//     });
// }

// function displayResults(results) {
//     const resultsBox = document.getElementById('resultsBox');
//     if (!resultsDiv) {
//         console.error('Results div not found');
//         return;
//     }

//     let html = '<h2>Enumeration Results</h2>';
    
//     if (results.subdomains && Object.keys(results.subdomains).length > 0) {
//         html += '<h3>Subdomains</h3><ul>';
//         for (const [subdomain, info] of Object.entries(results.subdomains)) {
//             html += `<li>${subdomain} (IP: ${info.ip}, Sources: ${info.sources.join(', ')})</li>`;
//         }
//         html += '</ul>';
//     }

//     if (results.virustotal) {
//         resultsBox.innerHTML += '<h3>VirusTotal Results</h3>';
//         for (const [subdomain, ips] of Object.entries(results.virustotal)) {
//             resultsBox.innerHTML += `<p>${subdomain}: ${ips.join(', ')}</p>`;
//         }
//     }

//     if (results.dnsdumpster) {
//         resultsBox.innerHTML += '<h3>DNSDumpster Results</h3>';
//         for (const [key, value] of Object.entries(results.dnsdumpster)) {
//             resultsBox.innerHTML += `<p>${key}: ${JSON.stringify(value)}</p>`;
//         }
//     }
// }

// function showError(message) {
//     const statusMessage = document.getElementById('status-message');
//     if (statusMessage) {
//         statusMessage.innerHTML = `<div class="alert alert-error">${message}</div>`;
//     } else {
//         console.error('Status message div not found');
//     }
//     const loadingDiv = document.getElementById('loading');
//     if (loadingDiv) {
//         loadingDiv.style.display = 'none';
//     }
// }


document.addEventListener('DOMContentLoaded', function() {
    const urlParams = new URLSearchParams(window.location.search);
    const domain = urlParams.get('domain');
    const scanTypes = urlParams.get('scan_types');

    if (!domain) {
        showError('No domain specified');
        return;
    }

    const domainNameElement = document.getElementById('domain-name');
    if (domainNameElement) {
        domainNameElement.textContent = domain;
    }

    if (!scanTypes) {
        showError('No scan types specified');
        return;
    }

    const scanTypesArray = scanTypes.split(',');

    function checkEnumerationStatus() {
        fetch(`/enumeration_status/${encodeURIComponent(domain)}`)
            .then(response => response.json())
            .then(data => {
                if (data.status === 'complete') {
                    document.getElementById('loading').style.display = 'none';
                    document.getElementById('results').style.display = 'block';
                    displayResults(data.results, scanTypesArray);
                } else if (data.status === 'error') {
                    showError(`An error occurred: ${data.error}`);
                } else {
                    updateProgress(data.progress || {});
                    setTimeout(checkEnumerationStatus, 2000);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showError('An error occurred while checking enumeration status');
            });
    }

    function updateProgress(progress) {
        const loadingElement = document.getElementById('loading');
        if (loadingElement) {
            let progressHtml = '<p>Enumeration in progress...</p>';
            if (Object.keys(progress).length > 0) {
                for (const [scanType, percentage] of Object.entries(progress)) {
                    progressHtml += `<p>${scanType}: ${percentage}% complete</p>`;
                }
            } else {
                progressHtml += '<p>Initializing...</p>';
            }
            loadingElement.innerHTML = progressHtml;
        }
    }

    function createDigContent(digResults) {
        let html = '<h3>Dig Results</h3>';
        
        for (const [recordType, records] of Object.entries(digResults)) {
            if (recordType === 'DNS_SERVER' || recordType === 'RESPONSE_TIME' || recordType === 'DNSSEC') {
                continue;  // We'll handle these separately
            }
            
            html += `<h4>${recordType} Records</h4>`;
            if (Array.isArray(records) && records.length > 0) {
                html += '<ul>';
                records.forEach(record => {
                    html += `<li>${record}</li>`;
                });
                html += '</ul>';
            } else {
                html += '<p>No records found</p>';
            }
        }
        
        // DNS Server Information
        html += '<h4>DNS Server Information</h4>';
        html += `<p>Name: ${digResults.DNS_SERVER.name || 'N/A'}</p>`;
        html += `<p>Version: ${digResults.DNS_SERVER.version || 'N/A'}</p>`;
        
        // DNSSEC
        html += '<h4>DNSSEC</h4>';
        html += `<p>${digResults.DNSSEC || 'N/A'}</p>`;
        
        // Response Time
        html += '<h4>Response Time</h4>';
        html += `<p>${digResults.RESPONSE_TIME || 'N/A'}</p>`;
        
        return html;
    }

    function displayResults(results, scanTypes) {
        const resultsDiv = document.getElementById('results');
        let html = '<h2>Enumeration Results</h2>';
    
        // Create main tabs for each scan type
        html += '<div class="tabs">';
        scanTypes.forEach((scanType, index) => {
            html += `<button class="tab-button${index === 0 ? ' active' : ''}" onclick="openTab(event, '${scanType}Tab')">${scanType.charAt(0).toUpperCase() + scanType.slice(1)} Scan</button>`;
        });
        html += '</div>';
    
        // Create content for each main tab
        scanTypes.forEach((scanType, index) => {
            html += `<div id="${scanType}Tab" class="tab-content" style="display: ${index === 0 ? 'block' : 'none'}">`;
            
            // Create subtabs
            html += '<div class="subtabs">';
            html += `<button class="subtab-button active" onclick="openSubTab(event, '${scanType}CompiledResults')">Compiled Results</button>`;
            if (scanType === 'passive') {
                html += `<button class="subtab-button" onclick="openSubTab(event, '${scanType}VirusTotal')">VirusTotal</button>`;
                html += `<button class="subtab-button" onclick="openSubTab(event, '${scanType}DNSDumpster')">DNSDumpster</button>`;
                html += `<button class="subtab-button" onclick="openSubTab(event, '${scanType}Nuclei')">Nuclei</button>`;
            } else if (scanType === 'active') {
                html += `<button class="subtab-button" onclick="openSubTab(event, '${scanType}DNSRecon')">DNS Recon</button>`;
                html += `<button class="subtab-button" onclick="openSubTab(event, '${scanType}Dig')">Dig</button>`;
                html += `<button class="subtab-button" onclick="openSubTab(event, '${scanType}Subzy')">Subzy</button>`;
            }
            html += '</div>';
    
            // Create content for each subtab
            html += `<div id="${scanType}CompiledResults" class="subtab-content" style="display: block">`;
            html += createCompiledResultsTable(results, scanType);
            html += '</div>';
    
            if (scanType === 'passive') {
                html += `<div id="${scanType}VirusTotal" class="subtab-content" style="display: none">`;
                html += createVirusTotalTable(results.virustotal);
                html += '</div>';
    
                html += `<div id="${scanType}DNSDumpster" class="subtab-content" style="display: none">`;
                html += createDNSDumpsterContent(results.dnsdumpster);
                html += '</div>';
    
                html += `<div id="${scanType}Nuclei" class="subtab-content" style="display: none">`;
                html += createNucleiContent(results.nuclei);
                html += '</div>';
            } else if (scanType === 'active') {
                html += `<div id="${scanType}DNSRecon" class="subtab-content" style="display: none">`;
                html += createDNSReconContent(results.dnsrecon);
                html += '</div>';
    
                html += `<div id="${scanType}Dig" class="subtab-content" style="display: none">`;
                html += createDigContent(results.dig);
                html += '</div>';
    
                html += `<div id="${scanType}Subzy" class="subtab-content" style="display: none">`;
                html += createSubzyContent(results.subzy);
                html += '</div>';
            }
    
            html += '</div>'; // Close tab-content div
        });
    
        resultsDiv.innerHTML = html;
        initializeTables();
    }
    

    function createCompiledResultsTable(results, scanType) {
        let html = '<table class="display"><thead><tr><th>Subdomain</th><th>IP</th><th>Sources</th></tr></thead><tbody>';
        for (const [subdomain, info] of Object.entries(results.subdomains)) {
            if (info.sources.some(source => source.toLowerCase().includes(scanType.toLowerCase()))) {
                html += `<tr><td>${subdomain}</td><td>${info.ip || 'N/A'}</td><td>${info.sources.join(', ')}</td></tr>`;
            }
        }
        html += '</tbody></table>';
        return html;
    }

    function createVirusTotalTable(virustotal) {
        let html = '<table id="virusTotalTable" class="display"><thead><tr><th>Subdomain</th><th>IP Addresses</th></tr></thead><tbody>';
        for (const [subdomain, ips] of Object.entries(virustotal)) {
            html += `<tr><td>${subdomain}</td><td>${ips.join(', ')}</td></tr>`;
        }
        html += '</tbody></table>';
        return html;
    }

    function createDNSDumpsterContent(dnsdumpster) {
        let html = '<h4>Subdomains</h4><ul>';
        for (const subdomain of dnsdumpster.subdomains) {
            html += `<li>${subdomain.domain} (IP: ${subdomain.ip}, ASN: ${subdomain.asn}, Server: ${subdomain.server})</li>`;
        }
        html += '</ul>';

        html += '<h4>MX Records</h4><ul>';
        for (const mx of dnsdumpster.mx_records) {
            html += `<li>${mx.exchange} (Preference: ${mx.preference}, IP: ${mx.ip})</li>`;
        }
        html += '</ul>';

        html += '<h4>TXT Records</h4><ul>';
        for (const txt of dnsdumpster.txt_records) {
            html += `<li>${txt}</li>`;
        }
        html += '</ul>';

        return html;
    }

    function createDNSReconContent(dnsrecon) {
        let html = '';
    
        if (dnsrecon && typeof dnsrecon === 'object') {
            // A Records
            if (dnsrecon.a_records && dnsrecon.a_records.length > 0) {
                html += '<h4>A Records</h4>';
                html += '<table class="display"><thead><tr><th>Name</th><th>Address</th></tr></thead><tbody>';
                dnsrecon.a_records.forEach(record => {
                    html += `<tr><td>${record.name || 'N/A'}</td><td>${record.address || 'N/A'}</td></tr>`;
                });
                html += '</tbody></table>';
            }
    
            // MX Records
            if (dnsrecon.mx_records && dnsrecon.mx_records.length > 0) {
                html += '<h4>MX Records</h4>';
                html += '<table class="display"><thead><tr><th>Name</th><th>Address</th><th>Priority</th></tr></thead><tbody>';
                dnsrecon.mx_records.forEach(record => {
                    html += `<tr><td>${record.name || 'N/A'}</td><td>${record.address || 'N/A'}</td><td>${record.priority || 'N/A'}</td></tr>`;
                });
                html += '</tbody></table>';
            }
    
            // NS Records
            if (dnsrecon.ns_records && dnsrecon.ns_records.length > 0) {
                html += '<h4>NS Records</h4>';
                html += '<table class="display"><thead><tr><th>Name</th><th>Target</th></tr></thead><tbody>';
                dnsrecon.ns_records.forEach(record => {
                    html += `<tr><td>${record.name || 'N/A'}</td><td>${record.target || 'N/A'}</td></tr>`;
                });
                html += '</tbody></table>';
            }
    
            // SOA Records
            if (dnsrecon.soa_records && dnsrecon.soa_records.length > 0) {
                html += '<h4>SOA Records</h4>';
                html += '<table class="display"><thead><tr><th>Name</th><th>Target</th></tr></thead><tbody>';
                dnsrecon.soa_records.forEach(record => {
                    html += `<tr><td>${record.name || 'N/A'}</td><td>${record.target || 'N/A'}</td></tr>`;
                });
                html += '</tbody></table>';
            }
    
            // SRV Records
            if (dnsrecon.srv_records && dnsrecon.srv_records.length > 0) {
                html += '<h4>SRV Records</h4>';
                html += '<table class="display"><thead><tr><th>Name</th><th>Target</th><th>Port</th><th>Priority</th><th>Weight</th></tr></thead><tbody>';
                dnsrecon.srv_records.forEach(record => {
                    html += `<tr><td>${record.name || 'N/A'}</td><td>${record.target || 'N/A'}</td><td>${record.port || 'N/A'}</td><td>${record.priority || 'N/A'}</td><td>${record.weight || 'N/A'}</td></tr>`;
                });
                html += '</tbody></table>';
            }
    
            // TXT Records
            if (dnsrecon.txt_records && dnsrecon.txt_records.length > 0) {
                html += '<h4>TXT Records</h4>';
                html += '<table class="display"><thead><tr><th>Name</th><th>Text</th></tr></thead><tbody>';
                dnsrecon.txt_records.forEach(record => {
                    html += `<tr><td>${record.name || 'N/A'}</td><td>${record.text || 'N/A'}</td></tr>`;
                });
                html += '</tbody></table>';
            }
        }
    
        if (html === '') {
            html = '<p>No DNSRecon results available or unexpected format.</p>';
        }
    
        return html;
    }

    function createNucleiContent(nucleiResults) {
        let html = '<h3>Nuclei Results</h3>';
        
        if (nucleiResults.error) {
            html += `<p class="error">Error: ${nucleiResults.error}</p>`;
        } else {
            html += '<h4>Vulnerabilities</h4>';
            html += createNucleiTable(nucleiResults.vulnerabilities);
            
            html += '<h4>Information</h4>';
            html += createNucleiTable(nucleiResults.information);
        }
        
        return html;
    }
    
    function createNucleiTable(items) {
        if (items.length === 0) {
            return '<p>No results found.</p>';
        }
    
        let html = '<table class="display"><thead><tr><th>Name</th><th>Severity</th><th>Description</th><th>Matched At</th></tr></thead><tbody>';
        for (const item of items) {
            if (item.raw_output) {
                html += `<tr><td colspan="4">${item.raw_output}</td></tr>`;
            } else {
                html += `<tr><td>${item.name || 'N/A'}</td><td>${item.severity || 'N/A'}</td><td>${item.description || 'N/A'}</td><td>${item.matched_at || 'N/A'}</td></tr>`;
            }
        }
        html += '</tbody></table>';
        return html;
    }

    function createSubzyContent(subzyResults) {
        let html = '<h3>Subzy Results</h3>';
        
        if (subzyResults.error) {
            html += `<p class="error">Error: ${subzyResults.error}</p>`;
        } else if (subzyResults.raw_output) {
            html += '<h4>Raw Subzy Output</h4>';
            html += `<pre>${subzyResults.raw_output}</pre>`;
            
            // Attempt to extract and display subdomains from raw output
            const subdomains = extractSubdomainsFromRaw(subzyResults.raw_output);
            if (subdomains.length > 0) {
                html += '<h4>Extracted Subdomains</h4>';
                html += '<ul>';
                subdomains.forEach(subdomain => {
                    html += `<li>${subdomain}</li>`;
                });
                html += '</ul>';
            }
        } else {
            html += '<h4>Vulnerable Subdomains</h4>';
            html += createSubzyTable(subzyResults.vulnerable);
            
            html += '<h4>Not Vulnerable Subdomains</h4>';
            html += createSubzyTable(subzyResults.not_vulnerable);
            
            html += '<h4>Errors</h4>';
            html += createSubzyTable(subzyResults.errors);
        }
        
        return html;
    }
    
    function extractSubdomainsFromRaw(rawOutput) {
        const subdomainPattern = /\b(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}\b/g;
        return [...new Set(rawOutput.match(subdomainPattern) || [])];
    }
    
    function createSubzyTable(items) {
        if (!items || items.length === 0) {
            return '<p>No results found.</p>';
        }
    
        let html = '<table class="display"><thead><tr><th>Subdomain</th><th>Service</th><th>Status</th><th>Fingerprint</th></tr></thead><tbody>';
        for (const item of items) {
            html += `<tr>
                <td>${item.url || 'N/A'}</td>
                <td>${item.service || 'N/A'}</td>
                <td>${item.status || 'N/A'}</td>
                <td>${item.fingerprint || 'N/A'}</td>
            </tr>`;
        }
        html += '</tbody></table>';
        return html;
    }

    function initializeTables() {
        $('#compiledResultsTable').DataTable({
            "pageLength": 25,
            "lengthMenu": [[10, 25, 50, -1], [10, 25, 50, "All"]],
            "order": []
        });
        $('#virusTotalTable').DataTable({ 
            "pageLength": 25,
            "lengthMenu": [[10, 25, 50, -1], [10, 25, 50, "All"]],
            "order": []
        });
        $('.display').each(function() {
            if ($.fn.DataTable.isDataTable(this)) {
                $(this).DataTable().destroy();
            }
            $(this).DataTable({
                "pageLength": 25,
                "lengthMenu": [[10, 25, 50, -1], [10, 25, 50, "All"]],
                "order": []
            });
        });
    }

    function showError(message) {
        const statusMessage = document.getElementById('status-message');
        if (statusMessage) {
            statusMessage.innerHTML = `<div class="alert alert-error">${message}</div>`;
        }
        const loadingElement = document.getElementById('loading');
        if (loadingElement) {
            loadingElement.style.display = 'none';
        }
    }

    // Start the enumeration status check
    checkEnumerationStatus();
});

function createSubtabs(scanType) {
    let html = `<button class="subtab-button active" onclick="openSubTab(event, '${scanType}CompiledResults')">Compiled Results</button>`;
    if (scanType === 'passive') {
        html += `<button class="subtab-button" onclick="openSubTab(event, '${scanType}VirusTotal')">VirusTotal</button>`;
        html += `<button class="subtab-button" onclick="openSubTab(event, '${scanType}DNSDumpster')">DNSDumpster</button>`;
    } else if (scanType === 'active') {
        html += `<button class="subtab-button" onclick="openSubTab(event, '${scanType}DNSRecon')">DNS Recon</button>`;
        html += `<button class="subtab-button" onclick="openSubTab(event, '${scanType}Dig')">Dig</button>`; // Add this line
    }
    return html;
}

// Make these functions global so they can be called from inline onclick handlers
window.openTab = function(evt, tabName) {
    var i, tabContent, tabButtons;
    tabContent = document.getElementsByClassName("tab-content");
    for (i = 0; i < tabContent.length; i++) {
        tabContent[i].style.display = "none";
    }
    tabButtons = document.getElementsByClassName("tab-button");
    for (i = 0; i < tabButtons.length; i++) {
        tabButtons[i].className = tabButtons[i].className.replace(" active", "");
    }
    document.getElementById(tabName).style.display = "block";
    evt.currentTarget.className += " active";
};

window.openSubTab = function(evt, tabName) {
    var i, tabContent, tabButtons;
    tabContent = document.getElementsByClassName("subtab-content");
    for (i = 0; i < tabContent.length; i++) {
        tabContent[i].style.display = "none";
    }
    tabButtons = document.getElementsByClassName("subtab-button");
    for (i = 0; i < tabButtons.length; i++) {
        tabButtons[i].className = tabButtons[i].className.replace(" active", "");
    }
    document.getElementById(tabName).style.display = "block";
    evt.currentTarget.className += " active";
};
