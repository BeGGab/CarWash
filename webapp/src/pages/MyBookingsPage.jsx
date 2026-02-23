import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAppStore } from '../store'
import Loader from '../components/Loader'

export default function MyBookingsPage() {
  const navigate = useNavigate()
  const { haptic } = useAppStore()
  const [activeTab, setActiveTab] = useState('active')
  const [bookings, setBookings] = useState([])
  const [isLoading, setIsLoading] = useState(true)
  
  useEffect(() => {
    setIsLoading(true)
    // Demo data
    setTimeout(() => {
      setBookings([
        {
          id: 'b1',
          car_wash_name: 'АвтоСпа Premium',
          slot_date: '2026-02-21',
          start_time: '14:00',
          wash_type_name: 'Стандарт',
          car_plate: 'А123БВ77',
          final_price: 700,
          status: 'confirmed'
        },
        {
          id: 'b2',
          car_wash_name: 'Чистый Кузов',
          slot_date: '2026-02-15',
          start_time: '10:00',
          wash_type_name: 'Премиум',
          car_plate: 'В456ГД99',
          final_price: 1200,
          status: 'completed'
        }
      ])
      setIsLoading(false)
    }, 500)
  }, [activeTab])
  
  const filteredBookings = bookings.filter(b => 
    activeTab === 'active' 
      ? ['confirmed', 'pending_payment', 'in_progress'].includes(b.status)
      : ['completed', 'cancelled'].includes(b.status)
  )
  
  const statusConfig = {
    pending_payment: { icon: '⏳', text: 'Ожидает оплаты', color: 'text-yellow-600' },
    confirmed: { icon: '✅', text: 'Подтверждено', color: 'text-green-600' },
    in_progress: { icon: '🔄', text: 'Выполняется', color: 'text-blue-600' },
    completed: { icon: '✔️', text: 'Завершено', color: 'text-gray-600' },
    cancelled: { icon: '❌', text: 'Отменено', color: 'text-red-600' }
  }
  
  return (
    <div className="px-4 pt-4">
      <h2 className="text-xl font-bold mb-4">Мои брони</h2>
      
      {/* Tabs */}
      <div className="flex gap-2 mb-4">
        <button 
          onClick={() => { haptic('light'); setActiveTab('active') }}
          className={`flex-1 py-2 rounded-xl font-medium transition-all ${
            activeTab === 'active' ? 'bg-wash-primary text-white' : 'bg-gray-100'
          }`}
        >
          Активные
        </button>
        <button 
          onClick={() => { haptic('light'); setActiveTab('history') }}
          className={`flex-1 py-2 rounded-xl font-medium transition-all ${
            activeTab === 'history' ? 'bg-wash-primary text-white' : 'bg-gray-100'
          }`}
        >
          История
        </button>
      </div>
      
      {isLoading ? <Loader /> : (
        <div className="space-y-3 pb-8">
          {filteredBookings.length > 0 ? (
            filteredBookings.map((booking) => {
              const status = statusConfig[booking.status] || {}
              return (
                <div 
                  key={booking.id}
                  onClick={() => { haptic('light'); navigate(`/booking/${booking.id}`) }}
                  className="card card-hover cursor-pointer"
                >
                  <div className="flex justify-between items-start mb-2">
                    <h3 className="font-semibold">{booking.car_wash_name}</h3>
                    <span className={`text-xs font-medium ${status.color}`}>
                      {status.icon} {status.text}
                    </span>
                  </div>
                  <div className="text-sm text-gray-600 space-y-1">
                    <div>📅 {booking.slot_date} в {booking.start_time}</div>
                    <div>🧽 {booking.wash_type_name}</div>
                    <div>🚗 {booking.car_plate}</div>
                  </div>
                  <div className="mt-2 pt-2 border-t flex justify-between items-center">
                    <span className="text-sm text-gray-500">Стоимость</span>
                    <span className="font-semibold">{booking.final_price}₽</span>
                  </div>
                </div>
              )
            })
          ) : (
            <div className="text-center py-12 text-gray-500">
              <p>{activeTab === 'active' ? 'Нет активных бронирований' : 'История пуста'}</p>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
