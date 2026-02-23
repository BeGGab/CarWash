/**
 * Zustand store для CarWash Mini App
 */
import { create } from 'zustand'

// Telegram WebApp
const tg = window.Telegram?.WebApp

// ==================== App Store ====================

export const useAppStore = create((set, get) => ({
  // Состояние
  isLoading: false,
  error: null,
  
  // Telegram данные
  telegramUser: tg?.initDataUnsafe?.user || null,
  
  // Пользователь
  user: null,
  isAuthenticated: false,
  
  // Геолокация
  location: null,
  
  // Actions
  setLoading: (isLoading) => set({ isLoading }),
  setError: (error) => set({ error }),
  clearError: () => set({ error: null }),
  
  setUser: (user) => set({ user, isAuthenticated: !!user }),
  
  setLocation: (location) => set({ location }),
  
  // Показать главную кнопку Telegram
  showMainButton: (text, onClick) => {
    if (tg?.MainButton) {
      tg.MainButton.setText(text)
      tg.MainButton.onClick(onClick)
      tg.MainButton.show()
    }
  },
  
  hideMainButton: () => {
    if (tg?.MainButton) {
      tg.MainButton.hide()
    }
  },
  
  // Haptic feedback
  haptic: (type = 'light') => {
    if (tg?.HapticFeedback) {
      tg.HapticFeedback.impactOccurred(type)
    }
  }
}))

// ==================== Booking Store ====================

export const useBookingStore = create((set, get) => ({
  // Выбранные данные
  selectedCarwash: null,
  selectedDate: null,
  selectedSlot: null,
  selectedWashType: null,
  
  // Данные автомобиля
  carPlate: '',
  carModel: '',
  
  // Контактные данные
  guestName: '',
  guestPhone: '',
  
  // Созданное бронирование
  currentBooking: null,
  
  // Actions
  setSelectedCarwash: (carwash) => set({ selectedCarwash: carwash }),
  setSelectedDate: (date) => set({ selectedDate: date }),
  setSelectedSlot: (slot) => set({ selectedSlot: slot }),
  setSelectedWashType: (washType) => set({ selectedWashType: washType }),
  
  setCarInfo: (plate, model) => set({ carPlate: plate, carModel: model }),
  setGuestInfo: (name, phone) => set({ guestName: name, guestPhone: phone }),
  
  setCurrentBooking: (booking) => set({ currentBooking: booking }),
  
  // Очистить данные
  reset: () => set({
    selectedCarwash: null,
    selectedDate: null,
    selectedSlot: null,
    selectedWashType: null,
    carPlate: '',
    carModel: '',
    currentBooking: null
  }),
  
  // Проверка готовности к созданию брони
  isReadyToBook: () => {
    const state = get()
    return !!(
      state.selectedCarwash &&
      state.selectedDate &&
      state.selectedSlot &&
      state.selectedWashType &&
      state.carPlate &&
      state.carModel &&
      state.guestName &&
      state.guestPhone
    )
  }
}))

// ==================== Carwashes Store ====================

export const useCarwashesStore = create((set) => ({
  carwashes: [],
  isLoading: false,
  error: null,
  
  setCarwashes: (carwashes) => set({ carwashes }),
  setLoading: (isLoading) => set({ isLoading }),
  setError: (error) => set({ error })
}))

// ==================== My Bookings Store ====================

export const useMyBookingsStore = create((set) => ({
  bookings: [],
  isLoading: false,
  error: null,
  activeTab: 'active', // 'active' | 'history'
  
  setBookings: (bookings) => set({ bookings }),
  setLoading: (isLoading) => set({ isLoading }),
  setError: (error) => set({ error }),
  setActiveTab: (tab) => set({ activeTab: tab })
}))
