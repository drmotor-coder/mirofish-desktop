import axios from 'axios'
import i18n from '../i18n'

// Определяем адрес бэкенда:
// 1) пользовательская настройка из SettingsPanel (localStorage)
// 2) переменная сборки VITE_API_BASE_URL
// 3) заводской бэкенд-сервис по умолчанию (localhost:5002)
function resolveBackendUrl() {
  try {
    const saved = localStorage.getItem('mirofish_settings')
    if (saved) {
      const parsed = JSON.parse(saved)
      if (parsed && parsed.backendUrl) return parsed.backendUrl
    }
  } catch (e) {
    console.warn('Не удалось прочитать настройки бэкенда:', e)
  }
  // 127.0.0.1 (не localhost) — на Windows localhost уходит в IPv6 и Docker-порт не отвечает
  return import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:18500'
}

// 创建axios实例
const service = axios.create({
  baseURL: resolveBackendUrl(),
  timeout: 300000, // 5分钟超时（本体生成可能需要较长时间）
  headers: {
    'Content-Type': 'application/json'
  }
})

// При изменении настроек — сразу переключаем адрес без перезапуска
if (typeof window !== 'undefined') {
  window.addEventListener('settings-changed', (e) => {
    const url = e?.detail?.backendUrl
    if (url) service.defaults.baseURL = url
  })
}

// 请求拦截器
service.interceptors.request.use(
  config => {
    config.headers['Accept-Language'] = i18n.global.locale.value
    return config
  },
  error => {
    console.error('Request error:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器（容错重试机制）
service.interceptors.response.use(
  response => {
    const res = response.data
    
    // 如果返回的状态码不是success，则抛出错误
    if (!res.success && res.success !== undefined) {
      console.error('API Error:', res.error || res.message || 'Unknown error')
      return Promise.reject(new Error(res.error || res.message || 'Error'))
    }
    
    return res
  },
  error => {
    console.error('Response error:', error)
    
    // 处理超时
    if (error.code === 'ECONNABORTED' && error.message.includes('timeout')) {
      console.error('Request timeout')
    }
    
    // 处理网络错误
    if (error.message === 'Network Error') {
      console.error('Network error - please check your connection')
    }
    
    return Promise.reject(error)
  }
)

// 带重试的请求函数
export const requestWithRetry = async (requestFn, maxRetries = 3, delay = 1000) => {
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await requestFn()
    } catch (error) {
      if (i === maxRetries - 1) throw error
      
      console.warn(`Request failed, retrying (${i + 1}/${maxRetries})...`)
      await new Promise(resolve => setTimeout(resolve, delay * Math.pow(2, i)))
    }
  }
}

export default service
