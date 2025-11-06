// Train Delay Notifier - Web UI JavaScript

let statusInterval = null;

// Load configuration on page load
document.addEventListener('DOMContentLoaded', function() {
    loadConfig();
    refreshStatus();

    // Auto-refresh status every 10 seconds when monitoring
    statusInterval = setInterval(refreshStatus, 10000);
});

// Load configuration from API
async function loadConfig() {
    try {
        const response = await fetch('/api/config');
        const config = await response.json();

        document.getElementById('trainUrl').value = config.train_url || '';
        document.getElementById('destination').value = config.destination_station || '';
        document.getElementById('notifyBefore').value = config.notify_minutes_before || 60;
        document.getElementById('checkInterval').value = config.check_interval_minutes || 5;
    } catch (error) {
        console.error('Error loading config:', error);
    }
}

// Save configuration
async function saveConfig(event) {
    event.preventDefault();

    const config = {
        train_url: document.getElementById('trainUrl').value,
        destination_station: document.getElementById('destination').value,
        notify_minutes_before: parseInt(document.getElementById('notifyBefore').value),
        check_interval_minutes: parseInt(document.getElementById('checkInterval').value)
    };

    try {
        const response = await fetch('/api/config', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(config)
        });

        const result = await response.json();

        if (result.success) {
            showMessage('Configuration saved successfully!', 'success');
        } else {
            showMessage('Error: ' + result.error, 'error');
        }
    } catch (error) {
        showMessage('Error saving configuration: ' + error.message, 'error');
    }
}

// Test connection
async function testConnection() {
    const trainUrl = document.getElementById('trainUrl').value;
    const destination = document.getElementById('destination').value;

    if (!trainUrl || !destination) {
        showMessage('Please fill in train URL and destination first', 'error');
        return;
    }

    showMessage('Testing connection... This may take a few seconds.', 'info');

    try {
        const response = await fetch('/api/train/info', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                train_url: trainUrl,
                destination_station: destination
            })
        });

        const result = await response.json();

        if (result.success) {
            const message = `
                ✅ Connection successful!<br><br>
                <strong>Train:</strong> ${result.train_number} ${result.train_name}<br>
                <strong>Destination:</strong> ${result.destination}<br>
                <strong>Scheduled Arrival:</strong> ${result.scheduled_arrival}<br>
                <strong>Current Delay:</strong> ${result.delay_minutes > 0 ? '+' : ''}${result.delay_minutes} minutes<br>
                <strong>Expected Arrival:</strong> ${result.actual_arrival}
            `;
            showMessage(message, 'success');
        } else {
            let errorMsg = 'Error: ' + result.error;
            if (result.available_stations) {
                errorMsg += '<br><br><strong>Available stations:</strong><br>' +
                            result.available_stations.slice(0, 10).join(', ');
            }
            showMessage(errorMsg, 'error');
        }
    } catch (error) {
        showMessage('Error testing connection: ' + error.message, 'error');
    }
}

// Start monitoring
async function startMonitoring() {
    try {
        const response = await fetch('/api/monitor/start', {
            method: 'POST'
        });

        const result = await response.json();

        if (result.success) {
            document.getElementById('startBtn').style.display = 'none';
            document.getElementById('stopBtn').style.display = 'inline-block';
            refreshStatus();
        } else {
            alert('Error starting monitoring: ' + result.error);
        }
    } catch (error) {
        alert('Error: ' + error.message);
    }
}

// Stop monitoring
async function stopMonitoring() {
    try {
        const response = await fetch('/api/monitor/stop', {
            method: 'POST'
        });

        const result = await response.json();

        if (result.success) {
            document.getElementById('startBtn').style.display = 'inline-block';
            document.getElementById('stopBtn').style.display = 'none';
            refreshStatus();
        } else {
            alert('Error stopping monitoring: ' + result.error);
        }
    } catch (error) {
        alert('Error: ' + error.message);
    }
}

// Refresh status
async function refreshStatus() {
    try {
        const response = await fetch('/api/status');
        const status = await response.json();

        // Update status indicator
        const statusDot = document.querySelector('.status-dot');
        const statusText = document.getElementById('statusText');

        if (status.active) {
            statusDot.classList.remove('inactive');
            statusDot.classList.add('active');
            statusText.textContent = 'Monitoring Active';
            document.getElementById('startBtn').style.display = 'none';
            document.getElementById('stopBtn').style.display = 'inline-block';
        } else {
            statusDot.classList.remove('active');
            statusDot.classList.add('inactive');
            statusText.textContent = 'Not monitoring';
            document.getElementById('startBtn').style.display = 'inline-block';
            document.getElementById('stopBtn').style.display = 'none';
        }

        // Update train info
        if (status.train_number) {
            document.getElementById('trainInfo').style.display = 'block';
            document.getElementById('trainNumber').textContent = status.train_number || '-';
            document.getElementById('trainName').textContent = status.train_name || '';
            document.getElementById('destination').textContent = status.destination || '-';
            document.getElementById('scheduledArrival').textContent = status.scheduled_arrival || '-';
            document.getElementById('actualArrival').textContent = status.actual_arrival || '-';
            document.getElementById('lastCheck').textContent = status.last_check || '-';

            // Update delay badge
            const delayBadge = document.getElementById('currentDelay');
            const delay = status.current_delay || 0;
            delayBadge.textContent = (delay > 0 ? '+' : '') + delay + ' min';

            if (delay > 15) {
                delayBadge.classList.add('high');
            } else {
                delayBadge.classList.remove('high');
            }
        } else {
            document.getElementById('trainInfo').style.display = 'none';
        }

    } catch (error) {
        console.error('Error refreshing status:', error);
    }
}

// Show message
function showMessage(message, type) {
    const testResult = document.getElementById('testResult');
    testResult.innerHTML = message;
    testResult.className = 'message ' + type;
    testResult.style.display = 'block';

    // Auto-hide after 10 seconds for non-error messages
    if (type !== 'error') {
        setTimeout(() => {
            testResult.style.display = 'none';
        }, 10000);
    }
}
