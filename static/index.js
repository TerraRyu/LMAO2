document.addEventListener('DOMContentLoaded', function() {
    const searchModeBtn = document.getElementById('searchModeBtn');
    const urlModeBtn = document.getElementById('urlModeBtn');
    const queryInput = document.getElementById('queryInput');
    const numResultsGroup = document.getElementById('numResultsGroup');
    const numResults = document.getElementById('numResults');
    const submitBtn = document.getElementById('submitBtn');
    const resultsTable = document.getElementById('resultsTable');
    const resultsBody = document.getElementById('resultsBody');
    const resultsBox = document.getElementById('resultsBox');
    const messageArea = document.getElementById('messageArea');

    let isSearchMode = true;
    let selectedScanTypes = [];

    searchModeBtn.addEventListener('click', () => setMode(true));
    urlModeBtn.addEventListener('click', () => setMode(false));

    document.querySelectorAll('.scan-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const scanType = this.dataset.scanType;
            if (selectedScanTypes.includes(scanType)) {
                selectedScanTypes = selectedScanTypes.filter(type => type !== scanType);
                this.classList.remove('active');
                this.style.opacity = '0.5';
            } else {
                selectedScanTypes.push(scanType);
                this.classList.add('active');
                this.style.opacity = '1';
            }
        });
    });


    function setScanType(scanType) {
        selectedScanType = scanType;
        document.querySelectorAll('.scan-btn').forEach(btn => {
            btn.classList.remove('active');
            btn.style.opacity = '0.5';
        });
        document.getElementById(`${scanType}ScanBtn`).classList.add('active');
        document.getElementById(`${scanType}ScanBtn`).style.opacity = '1';
    }
    
    function setMode(searchMode) {
        isSearchMode = searchMode;
        searchModeBtn.classList.toggle('active', searchMode);
        urlModeBtn.classList.toggle('active', !searchMode);
        numResultsGroup.style.display = searchMode ? 'block' : 'none';
        resultsTable.style.display = 'none';
        resultsBox.innerHTML = '';
        messageArea.innerHTML = '';
        queryInput.placeholder = searchMode ? 'Enter search query' : 'Enter URL (e.g., https://example.com)';
    }

    submitBtn.addEventListener('click', function() {
        const query = queryInput.value.trim();
        if (!query) {
            showMessage('Please enter a search query or URL.', 'error');
            return;
        }

        if (isSearchMode) {
            const numResultsValue = parseInt(numResults.value);
            if (isNaN(numResultsValue) || numResultsValue > 50 || numResultsValue < 1) {
                showMessage('Number of results must be between 1 and 50.', 'error');
                return;
            }
            performSearch(query, numResultsValue);
        } else {
            const validUrl = isValidUrl(query);
            if (!validUrl) {
                showMessage('Please enter a valid URL (e.g., https://example.com)', 'error');
                return;
            }
            if (selectedScanTypes.length === 0) {
                showMessage('Please select at least one scan type.', 'error');
                return;
            }
            performEnumeration(validUrl, selectedScanTypes);
        }
    });

    function isValidUrl(input) {
        console.log("Validating URL:", input);
        let domain = input.replace(/^(https?:\/\/)?(www\.)?/, '');
        const domainRegex = /^[a-zA-Z0-9][a-zA-Z0-9-]{1,61}[a-zA-Z0-9]\.[a-zA-Z]{2,}$/;
        
        if (domainRegex.test(domain)) {
            console.log("Valid domain, returning:", 'https://' + domain);
            return 'https://' + domain;
        }
        console.log("Invalid domain");
        return null;
    }

    function performSearch(query, num_results) {
        showMessage('Searching...', 'info');
        fetch('/search', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ query, num_results }),
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            displayResults(data);
            showMessage('Search completed successfully.', 'success');
        })
        .catch(error => {
            console.error('Error:', error);
            showMessage('An error occurred while searching. Please try again.', 'error');
        });
    }

    function performEnumeration(url) {
        resultsTable.style.display = 'none';
        resultsBox.innerHTML = `<p>Enumerating '${url}'...</p>`;
        
        const params = new URLSearchParams();
        params.append('domain', url);
        selectedScanTypes.forEach(type => params.append('scan_types', type));
        
        window.location.href = `/enumerate?${params.toString()}`;
    }
    
    function displayResults(results) {
        resultsBody.innerHTML = '';
        results.forEach(result => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>
                    <strong>${result.title}</strong><br>
                    <a href="${result.link}" target="_blank" class="website-link">${result.link}</a>
                </td>
                <td>${result.engine}</td>
                <td><button onclick="performEnumeration('${result.link}')">Enumerate</button></td>
            `;
            resultsBody.appendChild(row);
        });
        resultsTable.style.display = 'table';
        resultsBox.style.display = 'block';
    }

    function performScan(scanType) {
        if (!currentDomain) {
            showMessage('Please enter a URL first.', 'error');
            return;
        }

        showMessage(`Performing ${scanType} scan on ${currentDomain}...`, 'info');
        const endpoint = `/${scanType}_scan`;
        fetch(endpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ domain: currentDomain }),
        })
        .then(response => {
            if (!response.ok) {
                if (response.status === 429) {
                    throw new Error('Rate limit exceeded. Please try again later.');
                }
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            displayScanResults(scanType, data);
            showMessage(`${scanType.charAt(0).toUpperCase() + scanType.slice(1)} scan completed successfully.`, 'success');
        })
        .catch(error => {
            console.error('Error:', error);
            showMessage(`An error occurred during ${scanType} scan: ${error.message}`, 'error');
        });
    }

    function displayScanResults(scanType, results) {
        let resultHtml = `<h2>${scanType.charAt(0).toUpperCase() + scanType.slice(1)} Scan Results</h2>`;

        if (scanType === 'passive') {
            resultHtml += '<h3>VirusTotal Results</h3>';
            resultHtml += '<ul>';
            for (const [subdomain, ips] of Object.entries(results.virustotal)) {
                resultHtml += `<li>${subdomain}: ${ips.join(', ')}</li>`;
            }
            resultHtml += '</ul>';

            resultHtml += '<h3>DNSDumpster Results</h3>';
            resultHtml += '<ul>';
            for (const [recordType, records] of Object.entries(results.dnsdumpster)) {
                resultHtml += `<li>${recordType}: ${JSON.stringify(records)}</li>`;
            }
            resultHtml += '</ul>';
        } else {
            resultHtml += `<p>Results for ${scanType} scan: ${JSON.stringify(results)}</p>`;
        }

        resultsBox.innerHTML = resultHtml;
        resultsBox.style.display = 'block';
    }

    function showMessage(message, type) {
        messageArea.innerHTML = `<div class="alert alert-${type}">${message}</div>`;
        messageArea.style.display = 'block';
        setTimeout(() => {
            messageArea.style.display = 'none';
        }, 5000);
    }

    window.performEnumeration = performEnumeration;
});


function exportResults() {
    const domain = new URLSearchParams(window.location.search).get('domain');
    if (!domain) {
        alert('No domain found for export.');
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
        alert('An error occurred while exporting results. Please try again.');
    });
}

// Initialize particles.js
particlesJS('network-background', {
    particles: {
        number: { value: 80, density: { enable: true, value_area: 800 } },
        color: { value: "#ffffff" },
        shape: { type: "circle", stroke: { width: 0, color: "#000000" }, },
        opacity: { value: 0.5, random: false, },
        size: { value: 3, random: true, },
        line_linked: { enable: true, distance: 150, color: "#ffffff", opacity: 0.4, width: 1 },
        move: { enable: true, speed: 6, direction: "none", random: false, straight: false, out_mode: "out", bounce: false, },
    },
    interactivity: {
        detect_on: "canvas",
        events: { onhover: { enable: true, mode: "repulse" }, onclick: { enable: true, mode: "push" }, resize: true },
        modes: { grab: { distance: 400, line_linked: { opacity: 1 } }, bubble: { distance: 400, size: 40, duration: 2, opacity: 8, speed: 3 }, repulse: { distance: 200, duration: 0.4 }, push: { particles_nb: 4 }, remove: { particles_nb: 2 } },
    },
    retina_detect: true

});

window.performEnumeration = performEnumeration;
window.exportResults = exportResults;