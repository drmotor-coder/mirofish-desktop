const { app, BrowserWindow, Menu, ipcMain } = require('electron');
const { autoUpdater } = require('electron-updater');
const path = require('path');
const isDev = process.env.NODE_ENV === 'development' || process.argv.includes('--dev');
const { spawn } = require('child_process');
const os = require('os');

let mainWindow;
let backendProcess;

// Конфиг auto-updates
autoUpdater.checkForUpdatesAndNotify();

const createWindow = () => {
  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      nodeIntegration: false,
      contextIsolation: true,
      enableRemoteModule: false,
    },
    icon: path.join(__dirname, '../assets/icon.png'),
  });

  const startUrl = isDev
    ? 'http://localhost:3000'
    : `file://${path.join(__dirname, '../frontend/dist/index.html')}`;

  mainWindow.loadURL(startUrl);

  if (isDev) {
    mainWindow.webContents.openDevTools();
  }

  mainWindow.on('closed', () => {
    mainWindow = null;
  });
};

const startBackend = () => {
  const pythonPath = path.join(app.getAppPath(), 'backend', 'venv', 'Scripts', 'python.exe');
  const scriptPath = path.join(app.getAppPath(), 'backend', 'run.py');

  backendProcess = spawn('python', [scriptPath], {
    cwd: path.join(app.getAppPath(), 'backend'),
    stdio: 'pipe',
  });

  backendProcess.stdout.on('data', (data) => {
    console.log(`Backend: ${data}`);
  });

  backendProcess.stderr.on('data', (data) => {
    console.error(`Backend Error: ${data}`);
  });
};

app.on('ready', () => {
  startBackend();
  createWindow();
  createMenu();
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    if (backendProcess) {
      backendProcess.kill();
    }
    app.quit();
  }
});

app.on('activate', () => {
  if (mainWindow === null) {
    createWindow();
  }
});

// IPC для обновлений
ipcMain.on('check-for-updates', async () => {
  try {
    await autoUpdater.checkForUpdatesAndNotify();
  } catch (error) {
    console.error('Update check failed:', error);
  }
});

// IPC для выбора модели
ipcMain.handle('get-available-models', async () => {
  try {
    const response = await fetch('http://localhost:11434/api/tags');
    const data = await response.json();
    return data.models || [];
  } catch (error) {
    console.error('Failed to fetch models:', error);
    return [];
  }
});

// Меню
const createMenu = () => {
  const template = [
    {
      label: 'File',
      submenu: [
        {
          label: 'Exit',
          accelerator: 'CmdOrCtrl+Q',
          click: () => {
            if (backendProcess) {
              backendProcess.kill();
            }
            app.quit();
          },
        },
      ],
    },
    {
      label: 'Edit',
      submenu: [
        { role: 'undo' },
        { role: 'redo' },
        { type: 'separator' },
        { role: 'cut' },
        { role: 'copy' },
        { role: 'paste' },
      ],
    },
    {
      label: 'View',
      submenu: [
        { role: 'reload' },
        { role: 'forceReload' },
        { role: 'toggleDevTools' },
      ],
    },
    {
      label: 'Help',
      submenu: [
        {
          label: 'Check for Updates',
          click: () => {
            ipcMain.emit('check-for-updates');
          },
        },
      ],
    },
  ];

  Menu.setApplicationMenu(Menu.buildFromTemplate(template));
};

// Auto-updater события
autoUpdater.on('update-available', () => {
  if (mainWindow) {
    mainWindow.webContents.send('update-available');
  }
});

autoUpdater.on('update-downloaded', () => {
  if (mainWindow) {
    mainWindow.webContents.send('update-downloaded');
  }
});

ipcMain.on('restart-app', () => {
  autoUpdater.quitAndInstall();
});
