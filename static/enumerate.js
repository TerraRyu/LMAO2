document.addEventListener('DOMContentLoaded', function() {
    checkEnumerationStatus();
    const queryInput = document.getElementById('queryInput');
    const submitBtn = document.getElementById('submitBtn');
    const scanButtons = document.querySelectorAll('.scan-btn');
    let selectedScanType = null;

    scanButtons.forEach(button => {
        button.addEventListener('click', function() {
            scanButtons.forEach(btn => btn.classList.remove('active'));
            this.classList.add('active');
            selectedScanType = this.id;
            submitBtn.disabled = false;
        });
    });

    submitBtn.addEventListener('click', function() {
        const query = queryInput.value.trim();
        if (!query) {
            alert('Please enter a search query or URL.');
            return;
        }

        if (selectedScanType === 'passiveScanBtn') {
            performPassiveScan(query);
        } else {
            alert('This scan type is not implemented yet.');
        }
    });
});

function checkEnumerationStatus() {
    const domain = new URLSearchParams(window.location.search).get('domain');
    if (!domain) {
        showError('No domain specified');
        return;
    }

    fetch(`/enumeration_status/${domain}`)
        .then(response => response.json())
        .then(data => {
            if (data.status === 'complete') {
                $('#loading').hide();
                $('#results').show();
                populateResults(data.results);
            } else if (data.status === 'error') {
                showError(`An error occurred: ${data.error}`);
            } else {
                setTimeout(checkEnumerationStatus, 5000); // Check again in 5 seconds
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showError('An error occurred while checking enumeration status');
        });
}

function populateResults(results) {
    populateSubdomains(results.subdomains);
    populateVirusTotal(results.virustotal);
    populateDNSDumpster(results.dnsdumpster);
    initializeTables();
}

function populateSubdomains(subdomains) {
    const tbody = document.getElementById('subdomains-body');
    tbody.innerHTML = '';
    for (const [subdomain, info] of Object.entries(subdomains)) {
        const row = tbody.insertRow();
        row.innerHTML = `
            <td>${subdomain}</td>
            <td>${info.ip || 'N/A'}</td>
            <td>${info.status || 'N/A'}</td>
            <td>${info.sources.join(', ')}</td>
        `;
    }
}

function populateVirusTotal(virustotal) {
    const tbody = document.getElementById('virustotal-body');
    tbody.innerHTML = '';
    for (const [subdomain, ips] of Object.entries(virustotal)) {
        const row = tbody.insertRow();
        row.innerHTML = `
            <td>${subdomain}</td>
            <td>${ips.join(', ')}</td>
        `;
    }
}

function populateDNSDumpster(dnsdumpster) {
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

    document.getElementById('dnsdumpster-content').innerHTML = html;
}

function initializeTables() {
    $('#subdomains-table').DataTable({
        "pageLength": 25,
        "lengthMenu": [[10, 25, 50, -1], [10, 25, 50, "All"]],
        "order": []
    });
    $('#virustotal-table').DataTable({
        "pageLength": 25,
        "lengthMenu": [[10, 25, 50, -1], [10, 25, 50, "All"]],
        "order": []
    });
}

function openTab(evt, tabName) {
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
}

function openSubTab(evt, tabName) {
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

function performPassiveScan(domain) {
    fetch('/passive_scan', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ domain: domain }),
    })
    .then(response => response.json())
    .then(data => {
        displayResults(data);
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred during the passive scan. Please try again.');
    });
}

function displayResults(results) {
    const resultsBox = document.getElementById('resultsBox');
    resultsBox.innerHTML = '<h2>Passive Scan Results</h2>';

    if (results.virustotal) {
        resultsBox.innerHTML += '<h3>VirusTotal Results</h3>';
        for (const [subdomain, ips] of Object.entries(results.virustotal)) {
            resultsBox.innerHTML += `<p>${subdomain}: ${ips.join(', ')}</p>`;
        }
    }

    if (results.dnsdumpster) {
        resultsBox.innerHTML += '<h3>DNSDumpster Results</h3>';
        for (const [key, value] of Object.entries(results.dnsdumpster)) {
            resultsBox.innerHTML += `<p>${key}: ${JSON.stringify(value)}</p>`;
        }
    }
}

function showError(message) {
    const statusMessage = document.getElementById('status-message');
    statusMessage.innerHTML = `<div class="alert alert-error">${message}</div>`;
    $('#loading').hide();
}