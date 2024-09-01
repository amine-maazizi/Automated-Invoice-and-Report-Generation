const fs = require('fs');
const path = require('path');

const settingsPath = path.join(__dirname, '../../settings.json'); // Path to settings.json

function initializeDashboard() {
    loadHeadData();
    displayTimeLeft();
}

function loadHeadData() {
    if (fs.existsSync(settingsPath)) {
        const settings = JSON.parse(fs.readFileSync(settingsPath, 'utf8'));
        if (settings.filePath) {
            fetch('http://127.0.0.1:5000/upload-excel', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ filePath: settings.filePath }),
            })
                .then(response => response.json())
                .then(data => {
                    renderHeadData(data.head);
                })
                .catch(error => {
                    console.error('Error fetching head data:', error);
                    alert('Failed to load data preview.');
                });
        }
    }
}

function renderHeadData(headData) {
    const dataTable = document.getElementById('data-table');
    dataTable.innerHTML = ''; // Clear existing content

    if (!headData || headData.length === 0) {
        dataTable.innerHTML = '<tr><td>No data available</td></tr>';
        return;
    }

    // Create header row
    const headerRow = document.createElement('tr');
    headData.columns.forEach(col => {
        const th = document.createElement('th');
        th.textContent = col;
        headerRow.appendChild(th);
    });
    dataTable.appendChild(headerRow);

    // Populate data rows
    headData.rows.forEach(row => {
        const rowElement = document.createElement('tr');
        row.forEach(cell => {
            const td = document.createElement('td');
            td.textContent = cell;
            rowElement.appendChild(td);
        });
        dataTable.appendChild(rowElement);
    });
}

function displayTimeLeft() {
    if (fs.existsSync(settingsPath)) {
        const settings = JSON.parse(fs.readFileSync(settingsPath, 'utf8'));
        const targetTime = settings.scheduleTime || '00:00'; // Default to midnight if no time set
        const targetDate = new Date();
        const [hours, minutes] = targetTime.split(':').map(Number);
        targetDate.setHours(hours, minutes, 0, 0);

        // Update time left every second
        const intervalId = setInterval(() => {
            const dashboard = document.querySelector('.dashboard');
            if (dashboard && dashboard.style.display !== 'none') { // Check if Dashboard is visible
                const now = new Date();
                let timeDifference = targetDate - now; // Difference in milliseconds

                // Adjust for next day's target if the time has already passed
                if (timeDifference < 0) {
                    targetDate.setDate(targetDate.getDate() + 1);
                    timeDifference = targetDate - now;
                }

                const timeLeftSpan = document.getElementById('time-left');

                if (timeLeftSpan) {
                    const hoursLeft = Math.floor(timeDifference / (1000 * 60 * 60));
                    const minutesLeft = Math.floor((timeDifference % (1000 * 60 * 60)) / (1000 * 60));
                    const secondsLeft = Math.floor((timeDifference % (1000 * 60)) / 1000);

                    // Format time left as HH:MM:SS
                    const formattedTimeLeft = `${String(hoursLeft).padStart(2, '0')}:${String(minutesLeft).padStart(2, '0')}:${String(secondsLeft).padStart(2, '0')}`;

                    // Update the span with the formatted time left
                    timeLeftSpan.textContent = formattedTimeLeft;
                } else {
                    console.error("Time left span not found");
                }
            } else {
                // Clear the interval if the dashboard is not visible
                clearInterval(intervalId);
            }
        }, 1000); // Update every second
    }
}

module.exports = { initializeDashboard };
