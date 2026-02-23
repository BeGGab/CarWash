import React, { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useBookingStore, useAppStore } from '../store'

const tg = window.Telegram?.WebApp

export default function BookingPage() {
  const { id } = useParams()
  const navigate = useNavigate()
  const { haptic, telegramUser } = useAppStore()
  const { selectedCarwash, selectedDate, selectedSlot, selectedWashType, setCarInfo, setGuestInfo } = useBookingStore()
  
  const [carPlate, setCarPlate] = useState('')
  const [carModel, setCarModel] = useState('')
  const [guestName, setGuestName] = useState(telegramUser?.first_name || '')
  const [guestPhone, setGuestPhone] = useState('')
  
  const isValid = carPlate.length >= 6 && carModel.length >= 2 && guestName && guestPhone.length >= 10
  
  const handleSubmit = () => {
    if (!isValid) return
    haptic('medium')
    setCarInfo(carPlate.toUpperCase(), carModel)
    setGuestInfo(guestName, guestPhone)
    navigate('/confirm')
  }
  
  // Request phone from Telegram
  const requestContact = () => {
    // In real app, this would use Telegram's requestContact
    // For demo, we'll just show a placeholder
    setGuestPhone('+79991234567')
  }
  
  return (
    <div className="px-4 pt-4 pb-24">
      <h2 className="text-xl font-bold mb-4">Данные для бронирования</h2>
      
      {/* Summary */}
      <div className="card mb-4 bg-gray-50">
        <div className="text-sm text-gray-600">
          <div>🏢 {selectedCarwash?.name}</div>
          <div>📅 {selectedDate} в {selectedSlot?.start_time}</div>
          <div>🧽 {selectedWashType?.name} — {selectedWashType?.base_price}₽</div>
        </div>
      </div>
      
      {/* Car Info */}
      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Госномер</label>
          <input
            type="text"
            value={carPlate}
            onChange={(e) => setCarPlate(e.target.value.toUpperCase())}
            placeholder="А123БВ77"
            className="w-full px-4 py-3 rounded-xl border border-gray-200 focus:border-wash-primary focus:outline-none"
          />
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Марка и модель</label>
          <input
            type="text"
            value={carModel}
            onChange={(e) => setCarModel(e.target.value)}
            placeholder="Toyota Camry"
            className="w-full px-4 py-3 rounded-xl border border-gray-200 focus:border-wash-primary focus:outline-none"
          />
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Ваше имя</label>
          <input
            type="text"
            value={guestName}
            onChange={(e) => setGuestName(e.target.value)}
            placeholder="Иван"
            className="w-full px-4 py-3 rounded-xl border border-gray-200 focus:border-wash-primary focus:outline-none"
          />
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Телефон</label>
          <div className="flex gap-2">
            <input
              type="tel"
              value={guestPhone}
              onChange={(e) => setGuestPhone(e.target.value)}
              placeholder="+7 999 123 45 67"
              className="flex-1 px-4 py-3 rounded-xl border border-gray-200 focus:border-wash-primary focus:outline-none"
            />
            <button 
              onClick={requestContact}
              className="px-4 py-3 bg-gray-100 rounded-xl text-sm"
            >
              📱
            </button>
          </div>
        </div>
      </div>
      
      {/* Submit */}
      <div className="fixed bottom-0 left-0 right-0 p-4 bg-white border-t">
        <button 
          onClick={handleSubmit} 
          disabled={!isValid}
          className="btn-primary w-full"
        >
          Продолжить
        </button>
      </div>
    </div>
  )
}
