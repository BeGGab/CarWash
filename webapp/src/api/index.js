/**
 * API клиент для CarWash Mini App
 */

const API_BASE = import.meta.env.VITE_API_URL || '/api/v1'

// Получаем данные Telegram
const getTelegramInitData = () => {
  const tg = window.Telegram?.WebApp
  return {
    initData: tg?.initData || '',
    initDataUnsafe: tg?.initDataUnsafe || {},
    user: tg?.initDataUnsafe?.user || null
  }
}

// Базовый fetch с авторизацией
const apiFetch = async (endpoint, options = {}) => {
  const { initData, user } = getTelegramInitData()
  
  const headers = {
    'Content-Type': 'application/json',
    'X-Telegram-Init-Data': initData,
    ...(user?.id && { 'X-Telegram-Id': user.id.toString() }),
    ...options.headers
  }
  
  const response = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers
  })
  
  if (!response.ok) {
    const error = await response.json().catch(() => ({}))
    throw new Error(error.detail || 'Ошибка запроса')
  }
  
  return response.json()
}

// ==================== Автомойки ====================

export const carwashAPI = {
  // Получить список моек
  getList: async ({ latitude, longitude, radius = 10, page = 1 } = {}) => {
    const params = new URLSearchParams({ page: page.toString() })
    if (latitude) params.append('latitude', latitude.toString())
    if (longitude) params.append('longitude', longitude.toString())
    if (radius) params.append('radius', radius.toString())
    
    return apiFetch(`/carwashes?${params}`)
  },
  
  // Получить одну мойку
  getOne: async (id) => {
    return apiFetch(`/carwashes/${id}`)
  },
  
  // Получить слоты мойки
  getSlots: async (id, date, washTypeId) => {
    const params = new URLSearchParams({ slot_date: date })
    if (washTypeId) params.append('wash_type_id', washTypeId)
    
    return apiFetch(`/carwashes/${id}/slots?${params}`)
  }
}

// ==================== Бронирования ====================

export const bookingAPI = {
  // Создать бронирование
  create: async (data) => {
    return apiFetch('/bookings/create', {
      method: 'POST',
      body: JSON.stringify(data)
    })
  },
  
  // Мои бронирования
  getMy: async (phone, status, page = 1) => {
    const params = new URLSearchParams({ phone, page: page.toString() })
    if (status) params.append('status', status)
    
    return apiFetch(`/bookings/my?${params}`)
  },
  
  // Детали бронирования
  getOne: async (id) => {
    return apiFetch(`/bookings/${id}`)
  },
  
  // Отменить бронирование
  cancel: async (id, reason) => {
    const params = new URLSearchParams()
    if (reason) params.append('reason', reason)
    
    return apiFetch(`/bookings/${id}/cancel?${params}`, {
      method: 'POST'
    })
  }
}

// ==================== Платежи ====================

export const paymentAPI = {
  // Создать платеж
  create: async (bookingId, returnUrl) => {
    return apiFetch('/payments/create', {
      method: 'POST',
      body: JSON.stringify({
        booking_id: bookingId,
        return_url: returnUrl
      })
    })
  },
  
  // Проверить статус платежа
  getStatus: async (paymentId) => {
    return apiFetch(`/payments/status/${paymentId}`)
  }
}

// ==================== Типы мойки ====================

export const washTypeAPI = {
  getAll: async () => {
    return apiFetch('/wash-types')
  }
}

// ==================== Пользователь ====================

export const userAPI = {
  // Авторизация через Telegram
  auth: async (telegramData) => {
    return apiFetch('/users/telegram/auth', {
      method: 'POST',
      body: JSON.stringify(telegramData)
    })
  },
  
  // Получить профиль
  getProfile: async () => {
    return apiFetch('/users/me')
  },
  
  // Верификация телефона
  verifyPhone: async (phone) => {
    return apiFetch('/users/verify-phone', {
      method: 'POST',
      body: JSON.stringify({ phone_number: phone })
    })
  }
}

export default {
  carwash: carwashAPI,
  booking: bookingAPI,
  payment: paymentAPI,
  washType: washTypeAPI,
  user: userAPI
}
