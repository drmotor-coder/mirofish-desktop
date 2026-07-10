<template>
  <div class="settings-panel">
    <div class="settings-header">
      <h2>⚙️ Настройки</h2>
      <button class="close-btn" @click="$emit('close')" title="Закрыть">✕</button>
    </div>

    <div class="settings-content">
      <!-- Модель LLM -->
      <div class="settings-group">
        <h3>🤖 Модель LLM</h3>
        <div class="setting-row">
          <label>Активная модель:</label>
          <select v-model="settings.model" @change="applyModel(settings.model)">
            <option v-if="availableModels.length === 0" disabled value="">
              (модели не найдены — проверьте Ollama)
            </option>
            <option v-for="model in availableModels" :key="model" :value="model">
              {{ model }}
            </option>
          </select>
          <button class="mini-btn" @click="loadAvailableModels" title="Обновить список">↻</button>
        </div>
        <p class="hint">
          Модель, на которой считает MiroFish. Изменение применяется к бэкенду сразу.
          <span v-if="activeBackendModel"> Сейчас на бэкенде: <b>{{ activeBackendModel }}</b></span>
        </p>
        <p v-if="modelStatus" :class="modelStatusType" class="update-status">{{ modelStatus }}</p>
      </div>

      <!-- Бэкенд -->
      <div class="settings-group">
        <h3>🔌 Бэкенд (сервис MiroFish)</h3>
        <div class="setting-row">
          <label>Адрес бэкенда:</label>
          <input
            v-model="settings.backendUrl"
            type="text"
            @change="saveSetting('backendUrl', settings.backendUrl)"
            placeholder="http://127.0.0.1:18500"
          />
        </div>
        <button @click="testBackend" :class="{ loading: testingBackend }">
          {{ testingBackend ? '⏳ Проверка...' : '🔌 Проверить связь' }}
        </button>
        <p class="hint">Адрес API-сервиса (обычно http://127.0.0.1:18500)</p>
      </div>

      <!-- Ollama -->
      <div class="settings-group">
        <h3>🧠 Ollama (модели на V100)</h3>
        <div class="setting-row">
          <label>Адрес Ollama:</label>
          <input
            v-model="settings.ollamaUrl"
            type="text"
            @change="onOllamaChange"
            placeholder="http://localhost:11434"
          />
        </div>
        <button @click="testOllama" :class="{ loading: testingOllama }">
          {{ testingOllama ? '⏳ Проверка...' : '🧠 Проверить связь' }}
        </button>
        <p class="hint">Сервер локальных моделей ({{ availableModels.length }} моделей найдено)</p>
      </div>

      <!-- Обновления -->
      <div class="settings-group">
        <h3>🔄 Обновления приложения</h3>
        <div class="setting-row checkbox">
          <label>
            <input
              v-model="settings.autoUpdate"
              type="checkbox"
              @change="saveSetting('autoUpdate', settings.autoUpdate)"
            />
            <span>Проверять обновления автоматически</span>
          </label>
        </div>
        <button @click="checkUpdates">🔄 Проверить обновления сейчас</button>
        <p v-if="updateStatus" :class="updateStatus" class="update-status">{{ updateMessage }}</p>
      </div>

      <!-- Сброс -->
      <div class="settings-group danger-zone">
        <h3>⚠️ Сброс</h3>
        <button @click="resetSettings" class="danger-btn">
          🔄 Сбросить настройки приложения
        </button>
        <p class="hint">Сбросит настройки интерфейса к значениям по умолчанию.</p>
      </div>
    </div>

    <!-- Подвал -->
    <div class="settings-footer">
      <p class="version">Версия: {{ appVersion }}</p>
      <p class="saved" v-if="showSaved">✅ Сохранено</p>
    </div>
  </div>
</template>

<script>
const DEFAULTS = {
  model: '',
  backendUrl: 'http://127.0.0.1:18500',
  ollamaUrl: 'http://localhost:11434',
  autoUpdate: true,
};

export default {
  name: 'SettingsPanel',
  props: {
    appVersion: { type: String, default: '0.1.4' },
  },
  emits: ['close', 'settings-changed'],
  data() {
    return {
      settings: { ...DEFAULTS },
      availableModels: [],
      activeBackendModel: '',
      testingBackend: false,
      testingOllama: false,
      updateStatus: null,
      updateMessage: '',
      modelStatus: '',
      modelStatusType: 'success',
      showSaved: false,
    };
  },
  mounted() {
    this.loadSettings();
    this.loadAvailableModels();
    this.loadActiveModel();
  },
  methods: {
    loadSettings() {
      const saved = localStorage.getItem('mirofish_settings');
      if (saved) {
        try {
          this.settings = { ...DEFAULTS, ...JSON.parse(saved) };
        } catch (e) {
          console.error('Не удалось загрузить настройки:', e);
        }
      }
    },

    async loadAvailableModels() {
      try {
        const response = await fetch(`${this.settings.ollamaUrl}/api/tags`);
        const data = await response.json();
        this.availableModels = (data.models || []).map((m) => m.name);
      } catch (error) {
        console.warn('Не удалось загрузить модели:', error);
        this.availableModels = [];
      }
    },

    // Считываем, какая модель реально стоит на бэкенде
    async loadActiveModel() {
      try {
        const r = await fetch(`${this.settings.backendUrl}/api/config/model`);
        const data = await r.json();
        if (data && data.model) {
          this.activeBackendModel = data.model;
          if (!this.settings.model) this.settings.model = data.model;
        }
      } catch (e) {
        console.warn('Не удалось получить активную модель:', e);
      }
    },

    // Реально применяем модель к бэкенду
    async applyModel(model) {
      this.saveSetting('model', model);
      this.modelStatus = '⏳ Применяю модель...';
      this.modelStatusType = 'info';
      try {
        const r = await fetch(`${this.settings.backendUrl}/api/config/model`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ model }),
        });
        const data = await r.json();
        if (r.ok && data.success) {
          this.activeBackendModel = data.model;
          this.modelStatus = `✅ Модель применена: ${data.model}`;
          this.modelStatusType = 'success';
        } else {
          this.modelStatus = `❌ Ошибка: ${data.error || 'не удалось применить'}`;
          this.modelStatusType = 'error';
        }
      } catch (e) {
        this.modelStatus = `❌ Бэкенд недоступен: ${e.message}`;
        this.modelStatusType = 'error';
      }
      setTimeout(() => { this.modelStatus = ''; }, 4000);
    },

    onOllamaChange() {
      this.saveSetting('ollamaUrl', this.settings.ollamaUrl);
      this.loadAvailableModels();
    },

    saveSetting(key, value) {
      this.settings[key] = value;
      localStorage.setItem('mirofish_settings', JSON.stringify(this.settings));
      this.showSaved = true;
      setTimeout(() => { this.showSaved = false; }, 2000);
      this.$emit('settings-changed', this.settings);
    },

    async testBackend() {
      this.testingBackend = true;
      try {
        const r = await fetch(`${this.settings.backendUrl}/health`);
        if (r.ok) {
          this.updateStatus = 'success';
          this.updateMessage = '✅ Бэкенд на связи';
        } else {
          this.updateStatus = 'error';
          this.updateMessage = `❌ Бэкенд ответил ошибкой (${r.status})`;
        }
      } catch (error) {
        this.updateStatus = 'error';
        this.updateMessage = `❌ Нет связи: ${error.message}`;
      }
      this.testingBackend = false;
      setTimeout(() => { this.updateStatus = null; }, 3000);
    },

    async testOllama() {
      this.testingOllama = true;
      try {
        const r = await fetch(`${this.settings.ollamaUrl}/api/tags`);
        if (r.ok) {
          this.updateStatus = 'success';
          this.updateMessage = '✅ Ollama на связи';
          await this.loadAvailableModels();
        } else {
          this.updateStatus = 'error';
          this.updateMessage = '❌ Ollama ответила ошибкой';
        }
      } catch (error) {
        this.updateStatus = 'error';
        this.updateMessage = `❌ Нет связи: ${error.message}`;
      }
      this.testingOllama = false;
      setTimeout(() => { this.updateStatus = null; }, 3000);
    },

    checkUpdates() {
      if (window.electronAPI) {
        window.electronAPI.checkForUpdates();
        this.updateStatus = 'info';
        this.updateMessage = '⏳ Проверяю обновления...';
        setTimeout(() => { this.updateStatus = null; }, 3000);
      } else {
        this.updateStatus = 'info';
        this.updateMessage = 'ℹ️ Автообновления доступны только в приложении';
        setTimeout(() => { this.updateStatus = null; }, 3000);
      }
    },

    resetSettings() {
      if (confirm('Сбросить настройки интерфейса к значениям по умолчанию?')) {
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
  max-height: 90vh;
  background: #f5f7fa;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.settings-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 18px 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.settings-header h2 {
  margin: 0;
  font-size: 22px;
}

.close-btn {
  background: rgba(255, 255, 255, 0.2);
  border: none;
  color: white;
  width: 38px;
  height: 38px;
  border-radius: 50%;
  font-size: 18px;
  cursor: pointer;
  transition: all 0.2s ease;
}
.close-btn:hover { background: rgba(255, 255, 255, 0.35); transform: scale(1.08); }

.settings-content {
  flex: 1;
  overflow-y: auto;
  padding: 18px;
}

.settings-group {
  background: white;
  padding: 18px;
  border-radius: 8px;
  margin-bottom: 14px;
  border-left: 4px solid #667eea;
}
.settings-group.danger-zone { border-left-color: #ef4444; background: #fef2f2; }
.settings-group h3 { margin: 0 0 14px 0; color: #1f2937; font-size: 15px; }

.setting-row {
  display: flex;
  align-items: center;
  margin-bottom: 10px;
  gap: 10px;
}
.setting-row label { min-width: 130px; font-weight: 500; color: #374151; font-size: 14px; }
.setting-row input[type="text"],
.setting-row select {
  flex: 1;
  padding: 8px 12px;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  font-size: 14px;
}
.setting-row input:focus, .setting-row select:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}
.setting-row.checkbox label { display: flex; align-items: center; gap: 10px; min-width: auto; cursor: pointer; }
.setting-row.checkbox input[type="checkbox"] { width: 18px; height: 18px; cursor: pointer; }

.mini-btn {
  padding: 6px 10px;
  background: #eef2ff;
  color: #4f46e5;
  border: 1px solid #c7d2fe;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
}
.mini-btn:hover { background: #e0e7ff; }

.hint { font-size: 12px; color: #9ca3af; margin: 8px 0 0 0; }
.hint b { color: #4f46e5; }

button {
  padding: 9px 15px;
  background: #667eea;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.2s ease;
  margin-top: 8px;
}
button:hover:not(.danger-btn):not(.loading):not(.mini-btn) { background: #5568d3; }
button.loading { opacity: 0.6; cursor: not-allowed; }
button.mini-btn { margin-top: 0; }

.danger-btn { background: #ef4444; width: 100%; }
.danger-btn:hover { background: #dc2626; }

.update-status {
  margin-top: 10px;
  padding: 9px;
  border-radius: 6px;
  font-size: 13px;
  font-weight: 500;
}
.update-status.success { background: #d1fae5; color: #065f46; }
.update-status.error { background: #fee2e2; color: #991b1b; }
.update-status.info { background: #dbeafe; color: #0c4a6e; }

.settings-footer {
  padding: 13px 20px;
  background: #f9fafb;
  border-top: 1px solid #e5e7eb;
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
  color: #6b7280;
}
.settings-footer p { margin: 0; }
.saved { color: #10b981; font-weight: 600; }
</style>
