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

    if (!scanTypes || scanTypes.length === 0) {
        showError('No scan types specified');
        return;
    }

    const scanTypesArray = scanTypes.split(',');

    function checkEnumerationStatus() {
        const urlParams = new URLSearchParams(window.location.search);
        const domain = urlParams.get('domain');
        const scanTypes = urlParams.getAll('scan_types');

        //fetch(`/enumeration_status/${encodeURIComponent(domain)}?${scanTypes.map(t => `scan_types=${encodeURIComponent(t)}`).join('&')}`)
        //.then(response => response.json())
        const encodedDomain = encodeURIComponent(domain);
        const scanTypesParam = scanTypes.map(t => `scan_types=${encodeURIComponent(t)}`).join('&');
        const url = `/enumeration_status/${encodedDomain}?${scanTypesParam}`;

        console.log('Requesting enumeration status:', url);  // Add this line for debugging

        fetch(url)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
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
                html += `<button class="subtab-button" onclick="openSubTab(event, '${scanType}Shodan')">Shodan</button>`;
            } else if (scanType === 'active') {
                html += `<button class="subtab-button" onclick="openSubTab(event, '${scanType}DNSRecon')">DNS Recon</button>`;
                html += `<button class="subtab-button" onclick="openSubTab(event, '${scanType}Dig')">Dig</button>`;
                html += `<button class="subtab-button" onclick="openSubTab(event, '${scanType}Subzy')">Subzy</button>`;
            } else if (scanType === 'osint') {
                html += `<button class="subtab-button" onclick="openSubTab(event, '${scanType}Harvester')">Harvester</button>`;
                html += `<button class="subtab-button" onclick="openSubTab(event, '${scanType}SpiderFoot')">SpiderFoot</button>`;
                html += `<button class="subtab-button" onclick="openSubTab(event, '${scanType}TruffleHog')">TruffleHog</button>`;
            } else if (scanType === 'cloud_enum') {
                html += `<button class="subtab-button" onclick="openSubTab(event, '${scanType}CloudFail')">CloudFail</button>`;
                html += `<button class="subtab-button" onclick="openSubTab(event, '${scanType}AWSBucketDump')">AWSBucketDump</button>`;
                html += `<button class="subtab-button" onclick="openSubTab(event, '${scanType}GCPBucketBrute')">GCPBucketBrute</button>`;
                html += `<button class="subtab-button" onclick="openSubTab(event, '${scanType}MicroBurst')">MicroBurst</button>`;
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

                html += `<div id="${scanType}Shodan" class="subtab-content" style="display: none">`;
                html += createShodanContent(results.shodan);
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
            } else if (scanType === 'osint') {
                html += `<div id="${scanType}Harvester" class="subtab-content" style="display: none">`;
                html += createHarvesterContent(results.harvester);
                html += '</div>';

                html += `<div id="${scanType}SpiderFoot" class="subtab-content" style="display: none">`;
                html += createSpiderFootContent(results.spiderfoot);
                html += '</div>';

                html += `<div id="${scanType}TruffleHog" class="subtab-content" style="display: none">`;
                html += createTruffleHogContent(results.trufflehog);
                html += '</div>';
            } else if (scanType === 'cloud_enum') {
                html += `<div id="${scanType}CloudFail" class="subtab-content" style="display: none">`;
                html += createCloudFailContent(results.cloudfail);
                html += '</div>';

                html += `<div id="${scanType}AWSBucketDump" class="subtab-content" style="display: none">`;
                html += createAWSBucketDumpContent(results.aws_bucket_dump);
                html += '</div>';

                html += `<div id="${scanType}GCPBucketBrute" class="subtab-content" style="display: none">`;
                html += createGCPBucketBruteContent(results.gcp_bucket_brute);
                html += '</div>';

                html += `<div id="${scanType}MicroBurst" class="subtab-content" style="display: none">`;
                html += createMicroBurstContent(results.microburst);
                html += '</div>';
            }
    
            html += '</div>'; // Close tab-content div
        });
    
        resultsDiv.innerHTML = html;
        try {
            initializeTables();
        } catch (error) {
            console.error("Error initializing tables:", error);
        }
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
        if (dnsdumpster && dnsdumpster.error) {
            return `<h3>DNSDumpster Error</h3><p>${dnsdumpster.error}</p>`;
        }
        let html = '<h4>Subdomains</h4>';
        if (dnsdumpster && dnsdumpster.subdomains && Array.isArray(dnsdumpster.subdomains)) {
            html += '<ul>';
            for (const subdomain of dnsdumpster.subdomains) {
                html += `<li>${subdomain.domain || 'N/A'} (IP: ${subdomain.ip || 'N/A'}, ASN: ${JSON.stringify(subdomain.asn) || 'N/A'}, Server: ${subdomain.server || 'N/A'})</li>`;
            }
            html += '</ul>';
        } else {
            html += '<p>No subdomains found or invalid data structure.</p>';
        }
    
        html += '<h4>MX Records</h4>';
        if (dnsdumpster && dnsdumpster.mx_records && Array.isArray(dnsdumpster.mx_records)) {
            html += '<ul>';
            for (const mx of dnsdumpster.mx_records) {
                html += `<li>${mx.exchange || 'N/A'} (Preference: ${mx.preference || 'N/A'}, IP: ${mx.ip || 'N/A'})</li>`;
            }
            html += '</ul>';
        } else {
            html += '<p>No MX records found or invalid data structure.</p>';
        }
    
        html += '<h4>TXT Records</h4>';
        if (dnsdumpster && dnsdumpster.txt_records && Array.isArray(dnsdumpster.txt_records)) {
            html += '<ul>';
            for (const txt of dnsdumpster.txt_records) {
                html += `<li>${txt}</li>`;
            }
            html += '</ul>';
        } else {
            html += '<p>No TXT records found or invalid data structure.</p>';
        }
    
        return html;
    }

    function createShodanContent(shodanResults) {
        let html = '<h3>Shodan Results</h3>';

        if (!shodanResults || typeof shodanResults !== 'object') {
            return html + '<p>No Shodan results available or invalid data structure.</p>';
        }
        
        if (shodanResults.error) {
            html += `<p class="error">Error: ${shodanResults.error}</p>`;
        } else {
            html += '<h4>IP Addresses</h4>';
            html += createShodanTable(shodanResults.ip_addresses, ['IP Address']);
            
            html += '<h4>Open Ports</h4>';
            html += createShodanTable(shodanResults.open_ports, ['Port']);
            
            html += '<h4>Vulnerabilities</h4>';
            html += createShodanTable(shodanResults.vulnerabilities, ['Vulnerability']);
            
            html += '<h4>Technologies</h4>';
            html += createShodanTable(shodanResults.technologies, ['Technology']);
            
            html += '<h4>Hostnames</h4>';
            html += createShodanTable(shodanResults.hostnames, ['Hostname']);
            
            html += '<h4>Operating Systems</h4>';
            html += createShodanTable(shodanResults.operating_systems, ['OS']);
        }
        
        return html;
    }

    function createShodanTable(items, headers) {
        if (!Array.isArray(items) || items.length === 0) {
            return '<table class="display"><thead><tr><th>No Data</th></tr></thead><tbody><tr><td>No results found.</td></tr></tbody></table>';
        }

        let html = '<table class="display"><thead><tr>';
        headers.forEach(header => {
            html += `<th>${header}</th>`;
        });
        html += '</tr></thead><tbody>';
        items.forEach(item => {
            html += '<tr>';
            if (typeof item === 'object' && item !== null) {
                headers.forEach(header => {
                    html += `<td>${item[header] || 'N/A'}</td>`;
                });
            } else {
                html += `<td>${item || 'N/A'}</td>`;
            }
            html += '</tr>';
        });
        html += '</tbody></table>';
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

    function createHarvesterContent(harvesterResults) {
        let html = '<h3>Harvester Results</h3>';
        
        if (harvesterResults.employee_information) {
            html += '<h4>Employee Information</h4>';
            html += '<table class="display"><thead><tr><th>Type</th><th>Information</th></tr></thead><tbody>';
            for (const [key, value] of Object.entries(harvesterResults.employee_information)) {
                html += `<tr><td>${key}</td><td>${Array.isArray(value) ? value.join(', ') : value}</td></tr>`;
            }
            html += '</tbody></table>';
        }
        
        if (harvesterResults.potential_social_engineering) {
            html += '<h4>Potential Social Engineering Information</h4>';
            html += '<table class="display"><thead><tr><th>Type</th><th>Information</th></tr></thead><tbody>';
            for (const [key, value] of Object.entries(harvesterResults.potential_social_engineering)) {
                html += `<tr><td>${key}</td><td>${Array.isArray(value) ? value.join(', ') : value}</td></tr>`;
            }
            html += '</tbody></table>';
        }
        
        return html;
    }

    function createSpiderFootContent(spiderFootResults) {
        let html = '<h3>SpiderFoot Results</h3>';
        
        if (spiderFootResults.employee_information) {
            html += '<h4>Employee Information</h4>';
            html += '<table class="display"><thead><tr><th>Type</th><th>Value</th></tr></thead><tbody>';
            spiderFootResults.employee_information.forEach(item => {
                html += `<tr><td>${item.type}</td><td>${item.value}</td></tr>`;
            });
            html += '</tbody></table>';
        }
        
        if (spiderFootResults.potential_social_engineering) {
            html += '<h4>Potential Social Engineering Information</h4>';
            html += '<table class="display"><thead><tr><th>Type</th><th>Value</th></tr></thead><tbody>';
            spiderFootResults.potential_social_engineering.forEach(item => {
                html += `<tr><td>${item.type}</td><td>${item.value}</td></tr>`;
            });
            html += '</tbody></table>';
        }
        
        if (spiderFootResults.github_repos) {
            html += '<h4>Publicly Accessible GitHub Repositories</h4>';
            html += '<ul>';
            spiderFootResults.github_repos.forEach(repo => {
                html += `<li><a href="${repo}" target="_blank">${repo}</a></li>`;
            });
            html += '</ul>';
        }
        
        return html;
    }

    function createTruffleHogContent(truffleHogResults) {
        let html = '<h3>TruffleHog Results</h3>';
        
        if (!truffleHogResults) {
            return html + '<p>No TruffleHog results available.</p>';
        }
    
        if (truffleHogResults.error) {
            return html + `<p class="error">Error: ${truffleHogResults.error}</p>`;
        }
    
        html += '<h4>Exposed Secrets</h4>';
        html += createTruffleHogTable(truffleHogResults.exposed_secrets);
        
        html += '<h4>Sensitive Information</h4>';
        html += createTruffleHogTable(truffleHogResults.sensitive_information);
        
        return html;
    }
    
    function createTruffleHogTable(items) {
        if (!items || items.length === 0) {
            return '<p>No results found.</p>';
        }
    
        let html = '<table class="display"><thead><tr><th>Type</th><th>File</th><th>Commit</th><th>Detector</th><th>Raw</th></tr></thead><tbody>';
        for (const item of items) {
            html += `<tr>
                <td>${item.type || 'N/A'}</td>
                <td>${item.file || 'N/A'}</td>
                <td>${item.commit || 'N/A'}</td>
                <td>${item.detector || 'N/A'}</td>
                <td>${item.raw || 'N/A'}</td>
            </tr>`;
        }
        html += '</tbody></table>';
        return html;
    }

    function createCloudFailContent(cloudFailResults) {
        let html = '<h3>CloudFail Results</h3>';

        if (!cloudFailResults) {
            return html + '<p>No CloudFail results available.</p>';
        }

        html += `<p><strong>Cloud Provider:</strong> ${cloudFailResults.cloud_provider}</p>`;

        html += '<h4>DNS Records</h4>';
        html += '<table class="display"><thead><tr><th>Type</th><th>Records</th></tr></thead><tbody>';
        for (const [recordType, records] of Object.entries(cloudFailResults.dns_records)) {
            html += `<tr><td>${recordType}</td><td>${records.join(', ')}</td></tr>`;
        }
        html += '</tbody></table>';

        return html;
    }

    function createAWSBucketDumpContent(awsResults) {
        let html = '<h3>AWS S3 Bucket Results</h3>';

        if (!awsResults || awsResults.error) {
            return html + `<p>Error: ${awsResults.error || 'No results available.'}</p>`;
        }

        html += '<h4>Open Buckets</h4>';
        html += createTable(awsResults.open_buckets, ['Bucket Name']);

        html += '<h4>Accessible Files</h4>';
        html += createTable(awsResults.accessible_files, ['File Path']);

        return html;
    }

    function createGCPBucketBruteContent(gcpResults) {
        let html = '<h3>GCP Bucket Results</h3>';

        if (!gcpResults || gcpResults.error) {
            return html + `<p>Error: ${gcpResults.error || 'No results available.'}</p>`;
        }

        html += '<h4>Public Buckets</h4>';
        html += createTable(gcpResults.public_buckets, ['Bucket Name']);

        html += '<h4>Accessible Files</h4>';
        html += createTable(gcpResults.accessible_files, ['File Path']);

        return html;
    }

    function createMicroBurstContent(azureResults) {
        let html = '<h3>Azure Blob Storage Results</h3>';

        if (!azureResults || azureResults.error) {
            return html + `<p>Error: ${azureResults.error || 'No results available.'}</p>`;
        }

        html += '<h4>Open Blobs</h4>';
        html += createTable(azureResults.open_blobs, ['Blob URL']);

        html += '<h4>Containers</h4>';
        html += createTable(azureResults.containers, ['Container Name']);

        html += '<h4>Files</h4>';
        html += createTable(azureResults.files, ['File URL']);

        return html;
    }

    function createTable(items, headers) {
        if (!items || items.length === 0) {
            return '<p>No items found.</p>';
        }

        let html = '<table class="display"><thead><tr>';
        headers.forEach(header => {
            html += `<th>${header}</th>`;
        });
        html += '</tr></thead><tbody>';
        items.forEach(item => {
            html += '<tr>';
            if (typeof item === 'object' && item !== null) {
                headers.forEach(header => {
                    html += `<td>${item[header] || 'N/A'}</td>`;
                });
            } else {
                html += `<td>${item || 'N/A'}</td>`;
            }
            html += '</tr>';
        });
        html += '</tbody></table>';

        return html;
    }

    function initializeTables() {
        $('.display').each(function() {
            try {
                if ($.fn.DataTable.isDataTable(this)) {
                    $(this).DataTable().destroy();
                }
                
                // Check if the table has any rows
                if ($(this).find('tbody tr').length > 0) {
                    $(this).DataTable({
                        "pageLength": 25,
                        "lengthMenu": [[10, 25, 50, -1], [10, 25, 50, "All"]],
                        "order": [],
                        "columnDefs": [
                            { "targets": '_all', "defaultContent": "N/A" }
                        ],
                        "initComplete": function(settings, json) {
                            console.log("DataTable initialized successfully");
                        }
                    });
                } else {
                    console.log("Table is empty, not initializing DataTable");
                    $(this).after('<p>No data available in table</p>');
                }
            } catch (error) {
                console.error("Error initializing DataTable:", error);
                $(this).after('<p>Error loading table data</p>');
            }
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

    function exportResults() {
        const domain = new URLSearchParams(window.location.search).get('domain');
        if (!domain) {
            showError('No domain found for export.');
            return;
        }
        
        fetch('/export', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ domain: domain }),
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.blob();
        })
        .then(blob => {
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.style.display = 'none';
            a.href = url;
            a.download = `${domain}_enumeration_results.xlsx`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
        })
        .catch(error => {
            console.error('Error:', error);
            showError('An error occurred while exporting results. Please try again.');
        });
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