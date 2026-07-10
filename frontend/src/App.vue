<template>
  <div id="app-container">
    <!-- Settings Panel Modal -->
    <div v-if="showSettings" class="settings-modal-overlay" @click="showSettings = false">
      <div class="settings-modal-content" @click.stop>
        <SettingsPanel @close="showSettings = false" @settings-changed="handleSettingsChange" />
      </div>
    </div>

    <!-- Settings Button (always visible) -->
    <button v-if="!showSettings" class="settings-fab" @click="showSettings = true" title="Open Settings">
      ⚙️
    </button>

    <!-- Main Router View -->
    <router-view />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import SettingsPanel from './components/SettingsPanel.vue'

const showSettings = ref(false)

const handleSettingsChange = (settings) => {
  console.log('Settings updated:', settings)
  // Broadcast settings change to other components
  window.dispatchEvent(new CustomEvent('settings-changed', { detail: settings }))
}
</script>

<style>
/* 全局样式重置 */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

#app {
  font-family: 'JetBrains Mono', 'Space Grotesk', 'Noto Sans SC', monospace;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #000000;
  background-color: #ffffff;
}

/* 滚动条样式 */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: #f1f1f1;
}

::-webkit-scrollbar-thumb {
  background: #000000;
}

::-webkit-scrollbar-thumb:hover {
  background: #333333;
}

/* 全局按钮样式 */
button {
  font-family: inherit;
}

/* Settings FAB (Floating Action Button) */
.settings-fab {
  position: fixed;
  bottom: 30px;
  right: 30px;
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  color: white;
  font-size: 28px;
  cursor: pointer;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
  transition: all 0.3s ease;
  z-index: 99;
  display: flex;
  align-items: center;
  justify-content: center;
}

.settings-fab:hover {
  transform: scale(1.1);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
}

.settings-fab:active {
  transform: scale(0.95);
}

/* Settings Modal */
.settings-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  animation: fadeIn 0.3s ease;
}

.settings-modal-content {
  width: 90%;
  max-width: 600px;
  max-height: 90vh;
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  animation: slideUp 0.3s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

@keyframes slideUp {
  from {
    transform: translateY(50px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}
</style>
