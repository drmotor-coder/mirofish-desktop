<template>
  <div class="settings-panel">
    <div class="settings-header">
      <h2>⚙️ Settings</h2>
      <button class="close-btn" @click="$emit('close')" title="Close">✕</button>
    </div>

    <div class="settings-content">
      <!-- LLM Model Settings -->
      <div class="settings-group">
        <h3>🤖 LLM Model</h3>
        <div class="setting-row">
          <label>Selected Model:</label>
          <select v-model="settings.model" @change="saveSetting('model', settings.model)">
            <option v-for="model in availableModels" :key="model" :value="model">
              {{ model }}
            </option>
          </select>
        </div>
        <p class="hint">The model used for all simulations and AI operations</p>
      </div>

      <!-- Backend Settings -->
      <div class="settings-group">
        <h3>⚙️ Backend Configuration</h3>
        <div class="setting-row">
          <label>Backend URL:</label>
          <input
            v-model="settings.backendUrl"
            type="text"
            @change="saveSetting('backendUrl', settings.backendUrl)"
            placeholder="http://localhost:5000"
          />
        </div>
        <button @click="testBackend" :class="{ loading: testingBackend }">
          {{ testingBackend ? '⏳ Testing...' : '🔌 Test Connection' }}
        </button>
        <p class="hint">Flask API server URL</p>
      </div>

      <!-- Ollama Settings -->
      <div class="settings-group">
        <h3>🧠 Ollama Configuration</h3>
        <div class="setting-row">
          <label>Ollama URL:</label>
          <input
            v-model="settings.ollamaUrl"
            type="text"
            @change="saveSetting('ollamaUrl', settings.ollamaUrl)"
            placeholder="http://localhost:11434"
          />
        </div>
        <button @click="testOllama" :class="{ loading: testingOllama }">
          {{ testingOllama ? '⏳ Testing...' : '🧠 Test Connection' }}
        </button>
        <p class="hint">Ollama LLM server URL</p>
      </div>

      <!-- GPU Settings -->
      <div class="settings-group">
        <h3>🎮 GPU Configuration</h3>
        <div class="setting-row">
          <label>CUDA Device:</label>
          <input
            v-model="settings.cudaDevice"
            type="text"
            @change="saveSetting('cudaDevice', settings.cudaDevice)"
            placeholder="0"
            maxlength="1"
          />
        </div>
        <p class="hint">CUDA_VISIBLE_DEVICES (0 for first GPU, 1 for second). Default: 0</p>
      </div>

      <!-- Simulation Settings -->
      <div class="settings-group">
        <h3>📊 Simulation Defaults</h3>
        <div class="setting-row">
          <label>Time Horizon (days):</label>
          <input
            v-model.number="settings.timeHorizon"
            type="number"
            @change="saveSetting('timeHorizon', settings.timeHorizon)"
            min="1"
            max="365"
          />
        </div>
        <div class="setting-row">
          <label>Simulation Steps:</label>
          <input
            v-model.number="settings.simulationSteps"
            type="number"
            @change="saveSetting('simulationSteps', settings.simulationSteps)"
            min="1"
            max="100"
          />
        </div>
        <p class="hint">Default parameters for new simulations</p>
      </div>

      <!-- LLM Parameters -->
      <div class="settings-group">
        <h3>🔬 LLM Parameters</h3>
        <div class="setting-row">
          <label>Temperature (0.0 - 2.0):</label>
          <input
            v-model.number="settings.temperature"
            type="range"
            @change="saveSetting('temperature', settings.temperature)"
            min="0"
            max="2"
            step="0.1"
          />
          <span class="value-display">{{ settings.temperature }}</span>
        </div>
        <div class="setting-row">
          <label>Context Length:</label>
          <input
            v-model.number="settings.contextLength"
            type="number"
            @change="saveSetting('contextLength', settings.contextLength)"
            min="512"
            max="32768"
            step="512"
          />
        </div>
        <p class="hint">Controls randomness (0=deterministic) and context window size</p>
      </div>

      <!-- Auto-Update Settings -->
      <div class="settings-group">
        <h3>🔄 Application Updates</h3>
        <div class="setting-row checkbox">
          <label>
            <input
              v-model="settings.autoUpdate"
              type="checkbox"
              @change="saveSetting('autoUpdate', settings.autoUpdate)"
            />
            <span>Check for updates automatically</span>
          </label>
        </div>
        <button @click="checkUpdates">
          🔄 Check for Updates Now
        </button>
        <p v-if="updateStatus" :class="updateStatus" class="update-status">
          {{ updateMessage }}
        </p>
      </div>

      <!-- Advanced Settings -->
      <div class="settings-group">
        <h3>🔧 Advanced</h3>
        <div class="setting-row checkbox">
          <label>
            <input
              v-model="settings.debugMode"
              type="checkbox"
              @change="saveSetting('debugMode', settings.debugMode)"
            />
            <span>Enable debug logging</span>
          </label>
        </div>
        <div class="setting-row checkbox">
          <label>
            <input
              v-model="settings.useLocalModels"
              type="checkbox"
              @change="saveSetting('useLocalModels', settings.useLocalModels)"
            />
            <span>Use only local models (no cloud API)</span>
          </label>
        </div>
      </div>

      <!-- Reset Settings -->
      <div class="settings-group danger-zone">
        <h3>⚠️ Danger Zone</h3>
        <button @click="resetSettings" class="danger-btn">
          🔄 Reset to Default Settings
        </button>
        <p class="hint">This will reset all settings to defaults. Cannot be undone.</p>
      </div>
    </div>

    <!-- Footer -->
    <div class="settings-footer">
      <p class="version">Version: {{ appVersion }}</p>
      <p class="saved" v-if="showSaved">✅ Settings saved</p>
    </div>
  </div>
</template>

<script>
export default {
  name: 'SettingsPanel',
  props: {
    appVersion: {
      type: String,
      default: '0.1.0',
    },
  },
  emits: ['close', 'settings-changed'],
  data() {
    return {
      settings: {
        model: 'qwen3.5:35b',
        backendUrl: 'http://localhost:5000',
        ollamaUrl: 'http://localhost:11434',
        cudaDevice: '0',
        timeHorizon: 90,
        simulationSteps: 30,
        temperature: 0.7,
        contextLength: 4096,
        autoUpdate: true,
        debugMode: false,
        useLocalModels: true,
      },
      availableModels: [],
      testingBackend: false,
      testingOllama: false,
      updateStatus: null,
      updateMessage: '',
      showSaved: false,
    };
  },
  mounted() {
    this.loadSettings();
    this.loadAvailableModels();
  },
  methods: {
    loadSettings() {
      // Load from localStorage
      const saved = localStorage.getItem('mirofish_settings');
      if (saved) {
        try {
          this.settings = JSON.parse(saved);
        } catch (e) {
          console.error('Failed to load settings:', e);
        }
      }
    },
    async loadAvailableModels() {
      try {
        const response = await fetch(`${this.settings.ollamaUrl}/api/tags`);
        const data = await response.json();
        this.availableModels = (data.models || []).map(m => m.name);
      } catch (error) {
        console.warn('Failed to load models:', error);
        this.availableModels = ['qwen3.5:35b', 'qwen3.6:35b', 'gemma-4-e4b'];
      }
    },
    saveSetting(key, value) {
      this.settings[key] = value;
      localStorage.setItem('mirofish_settings', JSON.stringify(this.settings));

      // Show saved indicator
      this.showSaved = true;
      setTimeout(() => {
        this.showSaved = false;
      }, 2000);

      this.$emit('settings-changed', this.settings);
    },
    async testBackend() {
      this.testingBackend = true;
      try {
        const response = await fetch(`${this.settings.backendUrl}/health`);
        if (response.ok) {
          this.updateStatus = 'success';
          this.updateMessage = '✅ Backend connection OK';
        } else {
          this.updateStatus = 'error';
          this.updateMessage = '❌ Backend returned error';
        }
      } catch (error) {
        this.updateStatus = 'error';
        this.updateMessage = `❌ Connection failed: ${error.message}`;
      }
      this.testingBackend = false;
      setTimeout(() => { this.updateStatus = null; }, 3000);
    },
    async testOllama() {
      this.testingOllama = true;
      try {
        const response = await fetch(`${this.settings.ollamaUrl}/api/tags`);
        if (response.ok) {
          this.updateStatus = 'success';
          this.updateMessage = '✅ Ollama connection OK';
          await this.loadAvailableModels();
        } else {
          this.updateStatus = 'error';
          this.updateMessage = '❌ Ollama returned error';
        }
      } catch (error) {
        this.updateStatus = 'error';
        this.updateMessage = `❌ Connection failed: ${error.message}`;
      }
      this.testingOllama = false;
      setTimeout(() => { this.updateStatus = null; }, 3000);
    },
    checkUpdates() {
      if (window.electronAPI) {
        window.electronAPI.checkForUpdates();
        this.updateStatus = 'info';
        this.updateMessage = '⏳ Checking for updates...';
        setTimeout(() => { this.updateStatus = null; }, 3000);
      } else {
        this.updateStatus = 'info';
        this.updateMessage = 'ℹ️ Auto-updates only available in Electron app';
      }
    },
    resetSettings() {
      if (confirm('Are you sure? This will reset all settings to defaults.')) {
        localStorage.removeItem('mirofish_settings');
        location.reload();
      }
    },
  },
};
</script>

<style scoped>
.settings-panel {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.settings-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-bottom: 2px solid rgba(255, 255, 255, 0.2);
}

.settings-header h2 {
  margin: 0;
  font-size: 24px;
}

.close-btn {
  background: rgba(255, 255, 255, 0.2);
  border: none;
  color: white;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  font-size: 20px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.close-btn:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: scale(1.1);
}

.settings-content {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
}

.settings-group {
  background: white;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 15px;
  border-left: 4px solid #667eea;
}

.settings-group.danger-zone {
  border-left-color: #ef4444;
  background: #fef2f2;
}

.settings-group h3 {
  margin: 0 0 15px 0;
  color: #1f2937;
  font-size: 16px;
}

.setting-row {
  display: flex;
  align-items: center;
  margin-bottom: 12px;
  gap: 10px;
}

.setting-row label {
  min-width: 150px;
  font-weight: 500;
  color: #374151;
}

.setting-row input[type="text"],
.setting-row input[type="number"],
.setting-row select {
  flex: 1;
  padding: 8px 12px;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  font-size: 14px;
  transition: all 0.3s ease;
}

.setting-row input:focus,
.setting-row select:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.setting-row input[type="range"] {
  flex: 1;
}

.value-display {
  min-width: 50px;
  text-align: right;
  color: #667eea;
  font-weight: 600;
}

.setting-row.checkbox {
  flex-direction: row;
  align-items: center;
}

.setting-row.checkbox label {
  display: flex;
  align-items: center;
  gap: 10px;
  min-width: auto;
  cursor: pointer;
}

.setting-row.checkbox input[type="checkbox"] {
  width: 20px;
  height: 20px;
  cursor: pointer;
}

.hint {
  font-size: 12px;
  color: #9ca3af;
  margin: 8px 0 0 0;
}

button {
  padding: 10px 16px;
  background-color: #667eea;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.3s ease;
  margin-top: 10px;
}

button:hover:not(.danger-btn):not(.loading) {
  background-color: #5568d3;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

button.loading {
  opacity: 0.6;
  cursor: not-allowed;
}

.danger-btn {
  background-color: #ef4444;
  width: 100%;
}

.danger-btn:hover {
  background-color: #dc2626;
  box-shadow: 0 4px 12px rgba(239, 68, 68, 0.3);
}

.update-status {
  margin-top: 10px;
  padding: 10px;
  border-radius: 6px;
  font-size: 13px;
  font-weight: 500;
}

.update-status.success {
  background-color: #d1fae5;
  color: #065f46;
}

.update-status.error {
  background-color: #fee2e2;
  color: #991b1b;
}

.update-status.info {
  background-color: #dbeafe;
  color: #0c4a6e;
}

.settings-footer {
  padding: 15px 20px;
  background: #f9fafb;
  border-top: 1px solid #e5e7eb;
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
  color: #6b7280;
}

.version {
  margin: 0;
}

.saved {
  margin: 0;
  color: #10b981;
  font-weight: 600;
}
</style>
