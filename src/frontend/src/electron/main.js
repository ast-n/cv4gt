import { app, BrowserWindow, nativeImage, dialog } from 'electron';
import { spawn } from 'child_process';
import path from 'path';
import { fileURLToPath } from 'url';
import fs from 'fs';

const isDev = !app.isPackaged;

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const baseFolder = path.join(__dirname, '..', '..', '..', '..')

const venvPython = process.platform === 'win32'
      ? path.join(baseFolder, '.venv', 'Scripts', 'python.exe')
      : path.join(baseFolder, '.venv', 'bin', 'python');

const pythonExecutable = fs.existsSync(venvPython)
      ? venvPython
      : 'python3';

const apiScript = path.join(baseFolder, 'src', 'api.py')

const pythonProcess = spawn(pythonExecutable, [apiScript], {cwd: baseFolder})

let closeSlated = false;

pythonProcess.stdout.on('data', (data) => {
    console.log(`Backend: ${data}`);
});

pythonProcess.stderr.on('data', (data) => {
    console.error(`Backend: ${data}`);
});

pythonProcess.on('close', (code) => {
    console.log(`Python process exited with code ${code}`);
    if (!closeSlated){
      dialog.showErrorBox("Backend Error", "Something caused the backend to close with an error. Check the console for more details.")
    }
    app.quit(); // Close frontend if backend closes or fails.
});

let mainWindow;

function createWindow() {
  const iconPath = path.join(__dirname, '..', 'assets', 'bin.png');
  const iconImg = nativeImage.createFromPath(iconPath);

  mainWindow = new BrowserWindow({
    width: 1920,
    height: 1080,
    icon: iconImg,
    webPreferences: {
      contextIsolation: false,
      nodeIntegration: true,
    },
    autoHideMenuBar: true,
    fullscreen: true
  });

  if (isDev) {
    mainWindow.loadURL('http://localhost:5173');
  } else {
    mainWindow.loadFile(path.join(__dirname, '../../index.html'));
  }

  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

app.whenReady().then(createWindow);

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    closeSlated = true;
    pythonProcess.kill('SIGINT');
    app.quit();
  }
});

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) createWindow();
});

app.on('quit', () => {console.log('Closed electron app.'); app.exit(0); });