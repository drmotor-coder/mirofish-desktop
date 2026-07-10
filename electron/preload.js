const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
  // Обновления
  onUpdateAvailable: (callback) => ipcRenderer.on('update-available', callback),
  onUpdateDownloaded: (callback) => ipcRenderer.on('update-downloaded', callback),
  checkForUpdates: () => ipcRenderer.send('check-for-updates'),
  restartApp: () => ipcRenderer.send('restart-app'),

  // Модели
  getAvailableModels: () => ipcRenderer.invoke('get-available-models'),
  setSelectedModel: (model) => ipcRenderer.send('set-model', model),
});
