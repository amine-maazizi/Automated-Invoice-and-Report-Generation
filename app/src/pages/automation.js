const fs = require('fs');
const path = require('path');

const settingsPath = path.join(__dirname, '../../settings.json');

function initializeAutomationPage() {
    // Event listener for Generate Invoices button
    document.getElementById('generate-invoices-btn').addEventListener('click', () => {
        fetchSettings().then(settings => {
            fetch('http://127.0.0.1:5000/generate-invoices', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(settings),
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    alert(data.message);
                } else {
                    alert('Error generating invoices: ' + data.message);
                }
            })
            .catch(error => console.error('Error generating invoices:', error));
        });
    });

    // Event listener for Generate Reports button
    document.getElementById('generate-reports-btn').addEventListener('click', () => {
        fetchSettings().then(settings => {
            fetch('http://127.0.0.1:5000/generate-reports', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(settings),
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    alert(data.message);
                } else {
                    alert('Error generating reports: ' + data.message);
                }
            })
            .catch(error => console.error('Error generating reports:', error));
        });
    });

    // Event listener for Send Invoices to Clients button
    document.getElementById('send-invoices-btn').addEventListener('click', () => {
        fetchSettings().then(settings => {
            fetch('http://127.0.0.1:5000/send-invoices', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(settings),
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    alert(data.message);
                } else {
                    alert('Error sending invoices to clients: ' + data.message);
                }
            })
            .catch(error => console.error('Error sending invoices to clients:', error));
        });
    });

    // Event listener for Send Report to Managers button
    document.getElementById('send-report-btn').addEventListener('click', () => {
        fetchSettings().then(settings => {
            fetch('http://127.0.0.1:5000/send-report', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(settings),
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    alert(data.message);
                } else {
                    alert('Error sending report to managers: ' + data.message);
                }
            })
            .catch(error => console.error('Error sending report to managers:', error));
        });
    });
}

// Utility function to fetch settings
function fetchSettings() {
    return new Promise((resolve, reject) => {
        if (fs.existsSync(settingsPath)) {
            const settings = JSON.parse(fs.readFileSync(settingsPath, 'utf8'));
            resolve(settings);
        } else {
            reject('Settings file not found.');
        }
    });
}

module.exports = { initializeAutomationPage };
