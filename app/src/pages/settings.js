const { ipcRenderer } = require('electron');
const fs = require('fs');
const path = require('path');

const settingsPath = path.join(__dirname, '../../settings.json');
let settings = {}; // Define settings as a global variable

function initializeSettingsPage() {
    // Load settings when the page is initialized
    loadSettings();

    // Add event listener to save settings button
    const saveButton = document.getElementById('save-settings-btn');
    if (saveButton) {
        saveButton.addEventListener('click', saveSettings);
    } else {
        console.error("Save settings button not found");
    }

    // Add event listeners to pagination buttons
    const pageButtons = document.querySelectorAll('.page-btn');
    if (pageButtons.length > 0) {
        pageButtons.forEach(button => {
            button.addEventListener('click', () => {
                const page = button.getAttribute('data-page');
                document.querySelectorAll('.settings-page').forEach(section => section.style.display = 'none');
                const targetPage = document.getElementById(`settings-page-${page}`);
                if (targetPage) {
                    targetPage.style.display = 'block';
                } else {
                    console.error(`Settings page ${page} not found`);
                }
            });
        });
    } else {
        console.error("Pagination buttons not found");
    }

    // Add event listeners for browse buttons for folders
    setupFolderSelection('invoices-folder-btn', 'invoices-folder', 'invoicesFolder');
    setupFolderSelection('reports-folder-btn', 'reports-folder', 'reportsFolder');

    // Add event listener to load data button
    setupFileSelection('load-data-btn', 'open-file-dialog-for-file', 'filePath');

    // Add event listener for adding manager emails
    setupManagerEmailInput();

    // Add event listener to load email file button
    const loadEmailFileBtn = document.getElementById('load-email-file-btn');
    if (loadEmailFileBtn) {
        loadEmailFileBtn.addEventListener('click', () => {
            ipcRenderer.send('open-file-dialog-for-email-file');
        });
    } else {
        console.error("Load email file button not found");
    }

    // Listen for the selected file path for emails
    ipcRenderer.on('selected-email-file', (event, filePath) => {
        if (filePath && filePath.endsWith('.txt')) {
            loadEmailsFromFile(filePath);
        } else {
            alert('Please choose a valid .txt file.');
        }
    });
}

function setupFolderSelection(buttonId, inputId, settingKey) {
    const folderBtn = document.getElementById(buttonId);
    if (folderBtn) {
        folderBtn.addEventListener('click', () => {
            ipcRenderer.send('open-folder-dialog-for-directory');
            ipcRenderer.once('selected-directory', (event, folderPath) => {
                document.getElementById(inputId).value = folderPath;
                settings[settingKey] = folderPath;
            });
        });
    } else {
        console.error(`${buttonId} not found`);
    }
}

function setupFileSelection(buttonId, ipcEvent, settingKey) {
    const fileBtn = document.getElementById(buttonId);
    if (fileBtn) {
        fileBtn.addEventListener('click', () => {
            ipcRenderer.send(ipcEvent);
        });
    } else {
        console.error(`${buttonId} not found`);
    }

    ipcRenderer.on('selected-file', function (event, filePath) {
        if (filePath) {
            settings[settingKey] = filePath; // Set the file path in the settings object
            console.log("Selected file:", filePath);
        } else {
            alert('No file selected. Please choose a valid file.');
        }
    });
}

function setupManagerEmailInput() {
    const addManagerEmailBtn = document.getElementById('add-manager-email-btn');
    const managerEmailsList = document.getElementById('manager-emails-list');
    const managerEmailInput = document.getElementById('manager-email');

    if (addManagerEmailBtn && managerEmailsList && managerEmailInput) {
        addManagerEmailBtn.addEventListener('click', () => {
            const email = managerEmailInput.value.trim();
            if (email && validateEmail(email)) {
                settings.managerEmails = settings.managerEmails || [];
                settings.managerEmails.push(email);
                renderManagerEmails();
                managerEmailInput.value = ''; // Clear the input field
                managerEmailInput.disabled = false; // Ensure it remains enabled
            } else {
                alert("Please enter a valid email address.");
            }
        });
    }
}

function loadSettings() {
    if (fs.existsSync(settingsPath)) {
        settings = JSON.parse(fs.readFileSync(settingsPath, 'utf8')); // Load into the global settings object
        document.getElementById('invoices-folder').value = settings.invoicesFolder || '';
        document.getElementById('reports-folder').value = settings.reportsFolder || '';
        document.getElementById('email-server').value = settings.emailServer || '';
        document.getElementById('email-user').value = settings.emailUser || '';
        document.getElementById('email-password').value = settings.emailPassword || '';
        document.getElementById('schedule-time').value = settings.scheduleTime || '';
        renderManagerEmails();
    } else {
        console.error("Settings file not found. Loading defaults.");
    }
}

function renderManagerEmails() {
    const managerEmailsList = document.getElementById('manager-emails-list');
    managerEmailsList.innerHTML = ''; // Clear the current list
    if (settings.managerEmails && settings.managerEmails.length > 0) {
        const emailsToShow = settings.managerEmails; // Show only the first 5 emails
        emailsToShow.forEach((email, index) => {
            const listItem = document.createElement('li');
            listItem.textContent = email;
            const removeBtn = document.createElement('button');
            removeBtn.textContent = 'Remove';
            removeBtn.className = 'btn small-btn';
            removeBtn.addEventListener('click', () => {
                settings.managerEmails.splice(index, 1); // Remove the email from the list
                renderManagerEmails(); // Re-render the list
            });
            listItem.appendChild(removeBtn);
            managerEmailsList.appendChild(listItem);
        });

        // if (settings.managerEmails.length > 5) {
        //     const moreItem = document.createElement('li');
        //     moreItem.textContent = `...and ${settings.managerEmails.length - 5} more`;
        //     managerEmailsList.appendChild(moreItem);
        // }
    } else {
        const noEmailsItem = document.createElement('li');
        noEmailsItem.textContent = 'No manager emails added.';
        managerEmailsList.appendChild(noEmailsItem);
    }
}

function loadEmailsFromFile(filePath) {
    if (filePath && filePath.endsWith('.txt')) {
        fs.readFile(filePath, 'utf8', (err, data) => {
            if (err) {
                console.error("Error reading file:", err);
                alert("Failed to load emails from file. Please check the file and try again.");
                return;
            }
            const emails = data.split(/\r?\n/).filter(email => validateEmail(email));
            if (emails.length === 0) {
                alert("No valid emails found in the file.");
                return;
            }
            settings.managerEmails = settings.managerEmails || [];
            settings.managerEmails.push(...emails);
            renderManagerEmails();
            alert("Emails loaded successfully!");
        });
    } else {
        alert('Invalid file type. Please select a .txt file.');
    }
}

function validateEmail(email) {
    const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailPattern.test(email);
}

function saveSettings() {
    // Update the global settings object with the current values
    settings.invoicesFolder = document.getElementById('invoices-folder').value;
    settings.reportsFolder = document.getElementById('reports-folder').value;
    settings.emailServer = document.getElementById('email-server').value;
    settings.emailUser = document.getElementById('email-user').value;
    settings.emailPassword = document.getElementById('email-password').value;
    settings.scheduleTime = document.getElementById('schedule-time').value;

    try {
        fs.writeFileSync(settingsPath, JSON.stringify(settings, null, 2), 'utf8');
        alert('Settings saved successfully!');
    } catch (error) {
        console.error("Error saving settings:", error);
        alert('Failed to save settings. Please check console for details.');
    }
}

module.exports = { initializeSettingsPage };
