const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
  // Обновления
  onUpdateChecking: (callback) => ipcRenderer.on('update-checking', callback),
  onUpdateAvailable: (callback) => ipcRenderer.on('update-available', (e, version) => callback(version)),
  onUpdateNotAvailable: (callback) => ipcRenderer.on('update-not-available', (e, version) => callback(version)),
  onUpdateError: (callback) => ipcRenderer.on('update-error', (e, message) => callback(message)),
  onUpdateDownloaded: (callback) => ipcRenderer.on('update-downloaded', callback),
  checkForUpdates: () => ipcRenderer.send('check-for-updates'),
  restartApp: () => ipcRenderer.send('restart-app'),

  // Модели
  getAvailableModels: () => ipcRenderer.invoke('get-available-models'),
  setSelectedModel: (model) => ipcRenderer.send('set-model', model),

  // Сохранение отчёта в файл (нативный диалог)
  saveReport: (content, defaultName) => ipcRenderer.invoke('save-report', { content, defaultName }),

  // Реальная версия приложения
  getAppVersion: () => ipcRenderer.invoke('get-app-version'),
});
