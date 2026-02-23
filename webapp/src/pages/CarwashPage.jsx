import React, { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useBookingStore, useAppStore } from '../store'
import DateSelector from '../components/DateSelector'
import TimeSlots from '../components/TimeSlots'
import WashTypeSelector from '../components/WashTypeSelector'

export default function CarwashPage() {
  const { id } = useParams()
  const navigate = useNavigate()
  const { haptic } = useAppStore()
  const { selectedDate, selectedSlot, selectedWashType, setSelectedCarwash, setSelectedDate, setSelectedSlot, setSelectedWashType } = useBookingStore()
  
  const [carwash, setCarwash] = useState(null)
  const [slots, setSlots] = useState([])
  const [washTypes, setWashTypes] = useState([])
  
  useEffect(() => {
    // Demo data
    setCarwash({
      id, name: 'АвтоСпа Premium', address: 'ул. Ленина, 15', phone: '+7 (999) 123-45-67',
      rating: 4.8, working_hours: { start: '08:00', end: '22:00' }
    })
    setSelectedCarwash({ id, name: 'АвтоСпа Premium', address: 'ул. Ленина, 15' })
    
    setWashTypes([
      { id: 'wt1', name: 'Экспресс', duration_minutes: 15, base_price: 400 },
      { id: 'wt2', name: 'Стандарт', duration_minutes: 30, base_price: 700 },
      { id: 'wt3', name: 'Премиум', duration_minutes: 45, base_price: 1200 },
      { id: 'wt4', name: 'Люкс + химчистка', duration_minutes: 90, base_price: 2500 }
    ])
  }, [id])
  
  useEffect(() => {
    if (selectedDate) {
      setSlots([
        { id: 's1', start_time: '10:00', end_time: '10:30' },
        { id: 's2', start_time: '10:30', end_time: '11:00' },
        { id: 's3', start_time: '11:00', end_time: '11:30' },
        { id: 's4', start_time: '14:00', end_time: '14:30' },
        { id: 's5', start_time: '15:00', end_time: '15:30' },
        { id: 's6', start_time: '16:00', end_time: '16:30' }
      ])
    }
  }, [selectedDate])
  
  const handleContinue = () => {
    haptic('medium')
    navigate(`/book/${id}`)
  }
  
  if (!carwash) return null
  
  return (
    <div className="px-4 pt-4 pb-24">
      {/* Карточка мойки */}
      <div className="card mb-4">
        <h2 className="text-xl font-bold">{carwash.name}</h2>
        <p className="text-sm text-gray-500">{carwash.address}</p>
        <div className="flex items-center gap-4 mt-2 text-sm text-gray-600">
          <span>⭐ {carwash.rating}</span>
          <span>🕐 {carwash.working_hours.start} - {carwash.working_hours.end}</span>
        </div>
      </div>
      
      {/* Тип мойки */}
      <div className="mb-4">
        <h3 className="font-semibold mb-2">Тип мойки</h3>
        <WashTypeSelector 
          washTypes={washTypes} 
          selected={selectedWashType} 
          onSelect={(wt) => { haptic('light'); setSelectedWashType(wt) }} 
        />
      </div>
      
      {/* Выбор даты */}
      <div className="mb-4">
        <h3 className="font-semibold mb-2">Дата</h3>
        <DateSelector 
          selected={selectedDate} 
          onSelect={(d) => { haptic('light'); setSelectedDate(d); setSelectedSlot(null) }} 
        />
      </div>
      
      {/* Выбор времени */}
      {selectedDate && (
        <div className="mb-4 animate-in">
          <h3 className="font-semibold mb-2">Время</h3>
          <TimeSlots 
            slots={slots} 
            selected={selectedSlot} 
            onSelect={(s) => { haptic('light'); setSelectedSlot(s) }} 
          />
        </div>
      )}
      
      {/* Кнопка продолжить */}
      {selectedWashType && selectedDate && selectedSlot && (
        <div className="fixed bottom-0 left-0 right-0 p-4 bg-white border-t animate-in">
          <button onClick={handleContinue} className="btn-primary w-full">
            Продолжить — {selectedWashType.base_price}₽
          </button>
        </div>
      )}
    </div>
  )
}
