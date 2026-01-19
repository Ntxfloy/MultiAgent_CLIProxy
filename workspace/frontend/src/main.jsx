import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'
import './index.css' // Keep index.css for any other base global styles if present or needed.
import './CyberpunkTheme.css' // Ensure the theme is loaded.

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
