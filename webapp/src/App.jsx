import { useEffect, useState } from 'react';
import './index.css';

import {
  authWithTelegram,
  getCarwashes,
  getMyBookingsByPhone,
} from './api';

const tg = window.Telegram?.WebApp;
const TELEGRAM_DEBUG = import.meta.env.VITE_TELEGRAM_DEBUG === 'true';

function App() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [view, setView] = useState('home'); // home | book | my | profile

  const [carwashes, setCarwashes] = useState([]);
  const [bookings, setBookings] = useState([]);
  const [bookingsLoading, setBookingsLoading] = useState(false);

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const action = params.get('action');
    if (action === 'book') setView('book');
    if (action === 'my') setView('my');
    if (action === 'profile') setView('profile');

    const bootstrap = async () => {
      try {
        let initData = tg?.initData;

        if (!initData) {
          if (!TELEGRAM_DEBUG) {
            throw new Error(
              'Не удалось получить данные Telegram (initData). Откройте приложение через Telegram.'
            );
          }
          // В режиме отладки можно подставить тестовые данные
          initData = 'debug-init-data';
        }

        const userData = await authWithTelegram(initData);
        setUser(userData);

        // Параллельно подгружаем список моек
        const cw = await getCarwashes();
        setCarwashes(Array.isArray(cw) ? cw : cw.items || []);
      } catch (err) {
        setError(err.message);
        if (tg?.showAlert) {
          tg.showAlert(err.message);
        }
      } finally {
        setLoading(false);
      }
    };

    if (tg?.ready) {
      tg.ready();
    }
    bootstrap();
  }, []);

  const loadBookings = async () => {
    if (!user?.phone_number) {
      setError('Телефон не подтверждён. Подтвердите номер в боте.');
      if (tg?.showAlert) {
        tg.showAlert('Телефон не подтверждён. Подтвердите номер в боте.');
      }
      return;
    }
    setBookingsLoading(true);
    try {
      const data = await getMyBookingsByPhone(user.phone_number);
      setBookings(data.items || []);
    } catch (err) {
      setError(err.message);
      if (tg?.showAlert) {
        tg.showAlert(err.message);
      }
    } finally {
      setBookingsLoading(false);
    }
  };

  useEffect(() => {
    if (view === 'my' && user) {
      loadBookings();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [view, user]);

  if (loading) {
    return (
      <div className="container">
        <h1>Загрузка...</h1>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container error">
        <h1>Ошибка</h1>
        <p>{error}</p>
      </div>
    );
  }

  if (!user) {
    return (
      <div className="container">
        <h1>Пользователь не найден</h1>
      </div>
    );
  }

  const renderContent = () => {
    if (view === 'book') {
      return (
        <>
          <h2>📅 Новое бронирование</h2>
          {carwashes.length === 0 ? (
            <p>Поблизости пока нет доступных моек.</p>
          ) : (
            <ul className="list">
              {carwashes.map((cw) => (
                <li key={cw.id} className="list-item">
                  <div className="list-item-main">
                    <strong>{cw.name}</strong>
                    <span>{cw.address}</span>
                  </div>
                  <div className="list-item-meta">
                    {cw.distance && <span>{cw.distance.toFixed(1)} км</span>}
                  </div>
                </li>
              ))}
            </ul>
          )}
          <p className="hint">
            Подробный выбор даты и слота пока реализуется в Telegram‑боте. Mini App
            отображает список доступных моек.
          </p>
        </>
      );
    }

    if (view === 'my') {
      return (
        <>
          <h2>📋 Мои бронирования</h2>
          {bookingsLoading ? (
            <p>Загружаем бронирования...</p>
          ) : bookings.length === 0 ? (
            <p>У вас пока нет активных бронирований.</p>
          ) : (
            <ul className="list">
              {bookings.map((b) => (
                <li key={b.id} className="list-item">
                  <div className="list-item-main">
                    <strong>{b.car_wash_name}</strong>
                    <span>
                      {b.slot_date} • {b.start_time}
                    </span>
                  </div>
                  <div className="list-item-meta">
                    <span>{b.status}</span>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </>
      );
    }

    if (view === 'profile') {
      return (
        <>
          <h2>👤 Профиль</h2>
          <div className="profile">
            <div className="profile-row">
              <span>Имя</span>
              <strong>{user.first_name} {user.last_name || ''}</strong>
            </div>
            <div className="profile-row">
              <span>Username</span>
              <strong>{user.username ? `@${user.username}` : 'не указан'}</strong>
            </div>
            <div className="profile-row">
              <span>Телефон</span>
              <strong>{user.phone_number || 'не подтверждён'}</strong>
            </div>
            <div className="profile-row">
              <span>Всего бронирований</span>
              <strong>{user.total_bookings}</strong>
            </div>
            <div className="profile-row">
              <span>Завершено</span>
              <strong>{user.completed_bookings}</strong>
            </div>
          </div>
          <p className="hint">
            Изменение профиля (имя, телефон) выполняется через Telegram‑бота в разделе
            «Профиль».
          </p>
        </>
      );
    }

    return (
      <>
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
      </>
    );
  };

  return (
    <div className="container">
      <header>
        <h1>🚿 CarWash</h1>
        <p>Добро пожаловать, {user.first_name || user.username}!</p>
      </header>

      {renderContent()}

      <div className="actions">
        <button
          className={view === 'book' ? 'button-primary' : ''}
          onClick={() => setView('book')}
        >
          📅 Новое бронирование
        </button>
        <button
          className={view === 'my' ? 'button-primary' : ''}
          onClick={() => setView('my')}
        >
          📋 Мои бронирования
        </button>
        <button
          className={view === 'profile' ? 'button-primary' : ''}
          onClick={() => setView('profile')}
        >
          👤 Профиль
        </button>
      </div>
    </div>
  );
}

export default App;
