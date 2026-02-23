import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import './index.css'
 
// Мы не импортируем './index.css' здесь, так как стили уже подключены в App.jsx
// и базовые стили определены в index.html
// Если у вас есть глобальные стили, которые не зависят от App.jsx,
// вы можете создать файл global.css и импортировать его здесь.
 
ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
)

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
)
