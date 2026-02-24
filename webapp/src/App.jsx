import { useEffect, useState } from 'react';
import './App.css';

// URL вашего API. Замените, если он отличается.
const API_BASE_URL = 'https://0f7a-209-127-202-171.ngrok-free.app/api/v1';

// Получаем объект WebApp из глобального window
const tg = window.Telegram.WebApp;

function App() {
  // Состояния для хранения данных пользователя, загрузки и ошибок
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    // Эта функция будет вызвана один раз при загрузке приложения
    const fetchUserData = async () => {
      try {
        // Проверяем, что initData доступна (приложение открыто в Telegram)
        if (!tg.initData) {
          throw new Error("Не удалось получить данные Telegram (initData). Откройте приложение через Telegram.");
        }

        // Отправляем POST-запрос на наш бэкенд для аутентификации/получения пользователя
        const response = await fetch(`${API_BASE_URL}/users/telegram/auth`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            // Отправляем initData в заголовке для проверки на бэкенде
            'X-Telegram-Init-Data': tg.initData,
          },
        });

        if (!response.ok) {
          // Попытаемся прочитать тело ответа как текст, чтобы избежать ошибки парсинга JSON
          const errorText = await response.text();
          try {
            const errorData = JSON.parse(errorText);
            throw new Error(errorData.detail || `Ошибка сервера: ${response.status}`);
          } catch (e) {
            throw new Error(`Ошибка сервера: ${response.status}. Ответ: ${errorText}`);
          }
        }

        const userData = await response.json();
        setUser(userData); // Сохраняем данные пользователя

      } catch (err) {
        setError(err.message); // Сохраняем текст ошибки
        // Показываем ошибку во всплывающем окне Telegram для отладки
        tg.showAlert(err.message);
      } finally {
        setLoading(false); // Завершаем загрузку
      }
    };

    tg.ready(); // Сообщаем Telegram, что приложение готово
    fetchUserData();
  }, []); // Пустой массив зависимостей означает, что эффект выполнится один раз

  // Отображение в зависимости от состояния
  if (loading) {
    return <div className="container"><h1>Загрузка...</h1></div>;
  }

  if (error) {
    return <div className="container error"><h1>Ошибка</h1><p>{error}</p></div>;
  }

  return (
    <div className="container">
      {user ? (
        <>
          <header>
            <h1>🚿 CarWash</h1>
            <p>Добро пожаловать, {user.first_name || user.username}!</p>
          </header>
          
          <div className="user-stats">
            <div className="stat-item">
              <span>Всего бронирований</span>
              <strong>{user.total_bookings}</strong>
            </div>
            <div className="stat-item">
              <span>Завершено</span>
              <strong>{user.completed_bookings}</strong>
            </div>
          </div>

          <div className="actions">
            <button className="button-primary" onClick={() => tg.showAlert('Функция "Новое бронирование" в разработке!')}>
              📅 Новое бронирование
            </button>
            <button onClick={() => tg.showAlert('Функция "Мои бронирования" в разработке!')}>
              📋 Мои бронирования
            </button>
          </div>
        </>
      ) : (
        <h1>Пользователь не найден</h1>
      )}
    </div>
  );
}

export default App;
