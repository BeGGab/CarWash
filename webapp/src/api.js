// Централизованный клиент для работы с API CarWash Mini App
// Базовый URL API задаётся через переменную окружения VITE_API_BASE_URL.
// Примеры:
// - при одинаковом домене для фронта и API: VITE_API_BASE_URL="/api/v1"
// - при отдельном домене API: VITE_API_BASE_URL="https://api.example.com/api/v1"

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api/v1';

async function request(path, options = {}) {
  const url = `${API_BASE_URL}${path}`;

  const resp = await fetch(url, {
    headers: {
      'Content-Type': 'application/json',
      ...(options.headers || {}),
    },
    ...options,
  });

  const text = await resp.text();
  let data;
  try {
    data = text ? JSON.parse(text) : null;
  } catch {
    data = text;
  }

  if (!resp.ok) {
    const detail = data && data.detail ? data.detail : `HTTP ${resp.status}`;
    throw new Error(detail);
  }

  return data;
}

// --- Auth / Users ---

export async function authWithTelegram(initData) {
  return request('/users/telegram/auth', {
    method: 'POST',
    headers: {
      'X-Telegram-Init-Data': initData,
    },
  });
}

export async function getCurrentUser(telegramId) {
  return request('/users/me', {
    method: 'GET',
    headers: {
      'x-telegram-id': String(telegramId),
    },
  });
}

// --- Carwashes ---

export async function getCarwashes(params = {}) {
  const query = new URLSearchParams(params).toString();
  return request(`/carwashes/${query ? `?${query}` : ''}`, {
    method: 'GET',
  });
}

export async function getCarwashById(id) {
  return request(`/carwashes/${id}`, { method: 'GET' });
}

// --- Bookings ---

export async function getMyBookingsByPhone(phone, { status, page = 1, perPage = 20 } = {}) {
  const params = new URLSearchParams({
    phone,
    page: String(page),
    per_page: String(perPage),
  });
  if (status) params.set('status', status);
  return request(`/bookings/my?${params.toString()}`, { method: 'GET' });
}

// Функция создания бронирования должна соответствовать схеме SBookingCreate.
// Здесь оставляем заготовку, чтобы при необходимости заполнить все поля.
export async function createBooking(payload) {
  // payload должен соответствовать src/schemas/booking.py::SBookingCreate
  return request('/bookings/create', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

