<template>
  <div class="model-selector-panel">
    <div class="selector-header">
      <span class="selector-title">🤖 LLM Model Selection</span>
      <button class="refresh-btn" @click="loadModels" :disabled="loading">
        <span v-if="loading">⏳ Loading...</span>
        <span v-else>🔄 Refresh</span>
      </button>
    </div>

    <div class="models-grid">
      <div
        v-for="model in availableModels"
        :key="model.name"
        class="model-card"
        :class="{ active: selectedModel === model.name }"
        @click="selectModel(model.name)"
      >
        <div class="model-name">{{ model.name }}</div>
        <div class="model-size">{{ formatSize(model.size) }}</div>
        <div class="model-modified">{{ formatDate(model.modified_at) }}</div>
        <button
          v-if="selectedModel === model.name"
          class="check-mark"
          @click.stop
        >
          ✓
        </button>
      </div>
    </div>

    <div v-if="availableModels.length === 0" class="no-models">
      <p>No models available. Make sure Ollama is running on localhost:11434</p>
      <button @click="loadModels" class="retry-btn">Retry</button>
    </div>

    <div v-if="selectedModel" class="selected-info">
      <div class="info-badge">
        <span class="badge-label">Current Model:</span>
        <span class="badge-value">{{ selectedModel }}</span>
      </div>
      <p class="info-note">This model will be used for all LLM operations</p>
    </div>

    <div v-if="error" class="error-message">
      {{ error }}
    </div>
  </div>
</template>

<script>
export default {
  name: 'ModelSelector',
  data() {
    return {
      availableModels: [],
      selectedModel: null,
      loading: false,
      error: null,
    };
  },
  mounted() {
    this.loadModels();
    this.restoreSelectedModel();
  },
  methods: {
    async loadModels() {
      this.loading = true;
      this.error = null;

      try {
        if (window.electronAPI) {
          const models = await window.electronAPI.getAvailableModels();
          this.availableModels = models;
        } else {
          // Fallback для браузера без Electron
          const response = await fetch('http://localhost:11434/api/tags');
          const data = await response.json();
          this.availableModels = data.models || [];
        }
      } catch (err) {
        this.error = `Failed to load models: ${err.message}`;
        console.error('Model loading error:', err);
      } finally {
        this.loading = false;
      }
    },

    selectModel(modelName) {
      this.selectedModel = modelName;
      localStorage.setItem('selectedModel', modelName);

      if (window.electronAPI) {
        window.electronAPI.setSelectedModel(modelName);
      }

      this.$emit('model-selected', modelName);
    },

    restoreSelectedModel() {
      const saved = localStorage.getItem('selectedModel');
      if (saved) {
        this.selectedModel = saved;
      }
    },

    formatSize(bytes) {
      if (!bytes) return 'N/A';
      const sizes = ['B', 'KB', 'MB', 'GB'];
      let size = bytes;
      let sizeIndex = 0;

      while (size >= 1024 && sizeIndex < sizes.length - 1) {
        size /= 1024;
        sizeIndex++;
      }

      return `${size.toFixed(1)} ${sizes[sizeIndex]}`;
    },

    formatDate(dateString) {
      if (!dateString) return 'N/A';
      const date = new Date(dateString);
      return date.toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        year: '2-digit',
      });
    },
  },
};
</script>

<style scoped>
.model-selector-panel {
  padding: 20px;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  border-radius: 12px;
  margin-bottom: 20px;
  border: 1px solid #e0e7ff;
}

.selector-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 2px solid #e0e7ff;
}

.selector-title {
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
}

.refresh-btn {
  padding: 8px 16px;
  background-color: #3b82f6;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s ease;
}

.refresh-btn:hover:not(:disabled) {
  background-color: #2563eb;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
}

.refresh-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.models-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 12px;
  margin-bottom: 20px;
}

.model-card {
  padding: 16px;
  background: white;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.model-card:hover {
  border-color: #3b82f6;
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.15);
  transform: translateY(-2px);
}

.model-card.active {
  border-color: #10b981;
  background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.2);
}

.model-name {
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 8px;
  font-size: 15px;
  word-break: break-word;
}

.model-size {
  font-size: 13px;
  color: #6b7280;
  margin-bottom: 4px;
}

.model-modified {
  font-size: 12px;
  color: #9ca3af;
}

.check-mark {
  position: absolute;
  top: 8px;
  right: 8px;
  width: 32px;
  height: 32px;
  background-color: #10b981;
  color: white;
  border: none;
  border-radius: 50%;
  font-size: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
}

.check-mark:hover {
  background-color: #059669;
  transform: scale(1.1);
}

.no-models {
  text-align: center;
  padding: 40px 20px;
  background: white;
  border-radius: 8px;
  border: 2px dashed #fca5a5;
}

.no-models p {
  color: #dc2626;
  margin-bottom: 15px;
  font-size: 14px;
}

.retry-btn {
  padding: 10px 20px;
  background-color: #ef4444;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.retry-btn:hover {
  background-color: #dc2626;
}

.selected-info {
  padding: 15px;
  background: white;
  border-left: 4px solid #10b981;
  border-radius: 6px;
  margin-bottom: 15px;
}

.info-badge {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 8px;
}

.badge-label {
  font-weight: 600;
  color: #374151;
  font-size: 14px;
}

.badge-value {
  padding: 4px 12px;
  background-color: #d1fae5;
  color: #065f46;
  border-radius: 4px;
  font-family: 'Courier New', monospace;
  font-size: 13px;
  font-weight: 600;
}

.info-note {
  font-size: 12px;
  color: #6b7280;
  margin: 0;
}

.error-message {
  padding: 12px;
  background-color: #fee2e2;
  color: #991b1b;
  border-radius: 6px;
  font-size: 13px;
  border-left: 4px solid #dc2626;
  margin-top: 15px;
}
</style>
