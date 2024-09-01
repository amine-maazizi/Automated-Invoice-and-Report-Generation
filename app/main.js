const { app, BrowserWindow, ipcMain, dialog } = require('electron');
const path = require('path');
const { spawn, execFile } = require('child_process');
const os = require('os');

let mainWindow;
let backendProcess;

// Define paths for development and production backends
const backendDevPath = path.join(__dirname, '../src/app.py'); // Development: Python script
const backendProdPath = path.join(__dirname, '../dist/app'); // Production: Executable

// Set the environment ('development' or 'production')
const environment = 'development'; // Change this to 'production' when building for production

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1000,
    height: 700,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: false,
      nodeIntegration: true,
    },
  });

  mainWindow.loadFile('index.html');

  // When the window is closed, also stop the backend process
  mainWindow.on('closed', () => {
    mainWindow = null;
    if (backendProcess) backendProcess.kill(); // Kill the backend process when closing the app
  });
}

app.whenReady().then(() => {
  if (environment === 'development') {
    // Development: Start the backend server as a Python subprocess with spawn
    backendProcess = spawn('python', [backendDevPath], {
      stdio: 'inherit', // Inherit stdout and stderr from the parent process
    });
  } else if (environment === 'production') {
    // Production: Start the backend server from the executable with execFile
    backendProcess = execFile(backendProdPath, [], { shell: true }, (error, stdout, stderr) => {
      if (error) {
        console.error('Failed to start backend process:', error);
        return;
      }
      if (stdout) console.log(`Backend stdout: ${stdout}`);
      if (stderr) console.error(`Backend stderr: ${stderr}`);
    });
  }

  backendProcess.on('error', (err) => {
    console.error('Failed to start backend process:', err);
  });

  backendProcess.on('exit', (code, signal) => {
    console.log(`Backend process exited with code ${code} and signal ${signal}`);
  });

  createWindow();
  
  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

ipcMain.on('open-file-dialog-for-file', function (event) {
  if (os.platform() === 'linux' || os.platform() === 'win32') {
    dialog.showOpenDialog({
      properties: ['openFile']
    }).then(result => {
      if (!result.canceled) {
        event.sender.send('selected-file', result.filePaths[0]);
      }
    }).catch(err => console.log(err));
  } else {
    dialog.showOpenDialog({
      properties: ['openFile', 'openDirectory']
    }).then(result => {
      if (!result.canceled) {
        event.sender.send('selected-file', result.filePaths[0]);
      }
    }).catch(err => console.log(err));
  }
});

ipcMain.on('open-file-dialog-for-email-file', function (event) {
  // Set file filters to allow only .txt files
  const fileOptions = {
    properties: ['openFile'],
    filters: [{ name: 'Text Files', extensions: ['txt'] }]
  };

  // Show the dialog based on the operating system
  dialog.showOpenDialog(fileOptions).then(result => {
    if (!result.canceled) {
      const selectedFilePath = result.filePaths[0];
      // Check if the file extension is .txt
      if (path.extname(selectedFilePath).toLowerCase() === '.txt') {
        event.sender.send('selected-email-file', selectedFilePath);
      } else {
        // Handle invalid file type
        event.sender.send('selected-email-file', null);
        dialog.showErrorBox('Invalid File Type', 'Please select a valid .txt file.');
      }
    }
  }).catch(err => console.log(err));
});

ipcMain.on('open-folder-dialog-for-directory', (event) => {
  dialog.showOpenDialog({
    properties: ['openDirectory']
  }).then(result => {
    if (!result.canceled) {
      event.sender.send('selected-directory', result.filePaths[0]);
    }
  }).catch(err => console.log(err));
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});
