import React, { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useAppStore, useBookingStore } from '../store'
import { QRCodeSVG } from 'qrcode.react'

export default function BookingDetailPage() {
  const { id } = useParams()
  const navigate = useNavigate()
  const { haptic } = useAppStore()
  const { currentBooking } = useBookingStore()
  
  const [booking, setBooking] = useState(null)
  const [showCancelModal, setShowCancelModal] = useState(false)
  
  useEffect(() => {
    // Use current booking or fetch from API
    if (currentBooking && currentBooking.id === id) {
      setBooking(currentBooking)
    } else {
      // Demo data
      setBooking({
        id,
        car_wash_name: 'АвтоСпа Premium',
        car_wash_address: 'ул. Ленина, 15',
        slot_date: '2026-02-21',
        start_time: '14:00',
        end_time: '14:30',
        wash_type_name: 'Стандарт',
        car_plate: 'А123БВ77',
        car_model: 'Toyota Camry',
        final_price: 700,
        status: 'confirmed',
        payment_status: 'paid',
        qr_code: `CARWASH_${id}_${Date.now()}`
      })
    }
  }, [id, currentBooking])
  
  const handleCancel = () => {
    haptic('warning')
    setShowCancelModal(true)
  }
  
  const confirmCancel = () => {
    haptic('medium')
    // API call to cancel
    navigate('/my-bookings')
  }
  
  if (!booking) return null
  
  const statusConfig = {
    pending_payment: { icon: '⏳', text: 'Ожидает оплаты', bg: 'bg-yellow-100 text-yellow-800' },
    confirmed: { icon: '✅', text: 'Подтверждено', bg: 'bg-green-100 text-green-800' },
    in_progress: { icon: '🔄', text: 'Выполняется', bg: 'bg-blue-100 text-blue-800' },
    completed: { icon: '✔️', text: 'Завершено', bg: 'bg-gray-100 text-gray-800' },
    cancelled: { icon: '❌', text: 'Отменено', bg: 'bg-red-100 text-red-800' }
  }
  
  const status = statusConfig[booking.status] || {}
  const canCancel = ['pending_payment', 'confirmed'].includes(booking.status)
  const showQR = booking.status === 'confirmed'
  
  return (
    <div className="px-4 pt-4 pb-24">
      {/* Status Badge */}
      <div className="flex justify-center mb-4">
        <span className={`badge text-sm px-4 py-1.5 ${status.bg}`}>
          {status.icon} {status.text}
        </span>
      </div>
      
      {/* QR Code */}
      {showQR && (
        <div className="card flex flex-col items-center py-6 mb-4">
          <div className="bg-white p-4 rounded-xl shadow-inner mb-3">
            <QRCodeSVG 
              value={booking.qr_code} 
              size={180}
              level="H"
            />
          </div>
          <p className="text-sm text-gray-500 text-center">
            Покажите этот QR-код<br/>администратору мойки
          </p>
        </div>
      )}
      
      {/* Booking Details */}
      <div className="card mb-4">
        <h3 className="font-semibold text-lg mb-3">{booking.car_wash_name}</h3>
        
        <div className="space-y-2 text-sm">
          <div className="flex items-start gap-2">
            <span>📍</span>
            <span>{booking.car_wash_address}</span>
          </div>
          <div className="flex items-center gap-2">
            <span>📅</span>
            <span>{booking.slot_date}</span>
          </div>
          <div className="flex items-center gap-2">
            <span>⏰</span>
            <span>{booking.start_time} - {booking.end_time}</span>
          </div>
          <div className="flex items-center gap-2">
            <span>🧽</span>
            <span>{booking.wash_type_name}</span>
          </div>
          
          <hr className="my-3" />
          
          <div className="flex items-center gap-2">
            <span>🚗</span>
            <span>{booking.car_model}</span>
          </div>
          <div className="flex items-center gap-2">
            <span>🔢</span>
            <span className="font-mono">{booking.car_plate}</span>
          </div>
        </div>
        
        <div className="mt-4 pt-3 border-t flex justify-between items-center">
          <span className="text-gray-500">Стоимость</span>
          <span className="text-xl font-bold">{booking.final_price}₽</span>
        </div>
      </div>
      
      {/* Actions */}
      {canCancel && (
        <button 
          onClick={handleCancel}
          className="w-full py-3 text-red-600 font-medium"
        >
          Отменить бронирование
        </button>
      )}
      
      {/* Cancel Modal */}
      {showCancelModal && (
        <div className="fixed inset-0 bg-black/50 flex items-end z-50" onClick={() => setShowCancelModal(false)}>
          <div className="bg-white w-full rounded-t-2xl p-4" onClick={e => e.stopPropagation()}>
            <h3 className="text-lg font-semibold text-center mb-2">Отменить бронирование?</h3>
            <p className="text-sm text-gray-500 text-center mb-4">
              При отмене менее чем за 2 часа возврат не производится
            </p>
            <div className="space-y-2">
              <button onClick={confirmCancel} className="w-full py-3 bg-red-500 text-white rounded-xl font-medium">
                Да, отменить
              </button>
              <button onClick={() => setShowCancelModal(false)} className="w-full py-3 bg-gray-100 rounded-xl font-medium">
                Нет, оставить
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
