import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import './index.css'

// Initialize Telegram WebApp if available
if (window.Telegram?.WebApp) {
  window.Telegram.WebApp.ready()
  window.Telegram.WebApp.expand()
  
  // Debug info in development
  if (import.meta.env.DEV) {
    console.log('[Telegram] WebApp initialized')
    console.log('[Telegram] initData present:', !!window.Telegram.WebApp.initData)
    console.log('[Telegram] initDataUnsafe:', window.Telegram.WebApp.initDataUnsafe)
  }
}

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
