import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useBookingStore, useAppStore } from '../store'

const tg = window.Telegram?.WebApp

export default function ConfirmPage() {
  const navigate = useNavigate()
  const { haptic } = useAppStore()
  const { selectedCarwash, selectedDate, selectedSlot, selectedWashType, carPlate, carModel, guestName, guestPhone, setCurrentBooking } = useBookingStore()
  
  const [isLoading, setIsLoading] = useState(false)
  
  const price = selectedWashType?.base_price || 0
  const prepayment = price * 0.5
  
  const handlePay = async () => {
    setIsLoading(true)
    haptic('medium')
    
    // Simulate API call
    setTimeout(() => {
      const booking = {
        id: 'book_' + Date.now(),
        car_wash_name: selectedCarwash?.name,
        car_wash_address: selectedCarwash?.address,
        slot_date: selectedDate,
        start_time: selectedSlot?.start_time,
        wash_type_name: selectedWashType?.name,
        car_plate: carPlate,
        car_model: carModel,
        final_price: price,
        status: 'confirmed',
        payment_status: 'paid',
        qr_code: 'QR_' + Date.now()
      }
      
      setCurrentBooking(booking)
      setIsLoading(false)
      
      // Show success and navigate
      haptic('success')
      navigate(`/booking/${booking.id}`)
    }, 1500)
  }
  
  return (
    <div className="px-4 pt-4 pb-24">
      <h2 className="text-xl font-bold mb-4">Подтверждение</h2>
      
      {/* Booking Details */}
      <div className="card mb-4">
        <h3 className="font-semibold text-lg mb-3">{selectedCarwash?.name}</h3>
        
        <div className="space-y-2 text-sm">
          <div className="flex justify-between">
            <span className="text-gray-500">Адрес</span>
            <span>{selectedCarwash?.address}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-500">Дата</span>
            <span>{selectedDate}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-500">Время</span>
            <span>{selectedSlot?.start_time} - {selectedSlot?.end_time}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-500">Услуга</span>
            <span>{selectedWashType?.name}</span>
          </div>
          
          <hr className="my-3" />
          
          <div className="flex justify-between">
            <span className="text-gray-500">Автомобиль</span>
            <span>{carModel}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-500">Госномер</span>
            <span className="font-mono">{carPlate}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-500">Клиент</span>
            <span>{guestName}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-500">Телефон</span>
            <span>{guestPhone}</span>
          </div>
        </div>
      </div>
      
      {/* Price */}
      <div className="card mb-4 bg-wash-primary/5 border-wash-primary/20">
        <div className="flex justify-between items-center mb-2">
          <span className="text-gray-600">Стоимость услуги</span>
          <span className="font-semibold">{price}₽</span>
        </div>
        <div className="flex justify-between items-center text-lg">
          <span className="font-semibold">Предоплата (50%)</span>
          <span className="font-bold text-wash-primary">{prepayment}₽</span>
        </div>
        <p className="text-xs text-gray-500 mt-2">
          Оставшиеся {prepayment}₽ оплачиваются на месте
        </p>
      </div>
      
      {/* Info */}
      <div className="text-xs text-gray-500 text-center mb-4">
        Отмена бесплатна за 2+ часа до начала
      </div>
      
      {/* Pay Button */}
      <div className="fixed bottom-0 left-0 right-0 p-4 bg-white border-t">
        <button 
          onClick={handlePay}
          disabled={isLoading}
          className="btn-primary w-full flex items-center justify-center gap-2"
        >
          {isLoading ? (
            <>
              <span className="animate-spin">⏳</span>
              <span>Обработка...</span>
            </>
          ) : (
            <>
              <span>💳</span>
              <span>Оплатить {prepayment}₽</span>
            </>
          )}
        </button>
      </div>
    </div>
  )
}
