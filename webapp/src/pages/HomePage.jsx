import React, { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAppStore, useCarwashesStore, useBookingStore } from '../store'
import CarwashCard from '../components/CarwashCard'
import LocationButton from '../components/LocationButton'
import Loader from '../components/Loader'

export default function HomePage() {
  const navigate = useNavigate()
  const { location, setLocation, haptic } = useAppStore()
  const { carwashes, setCarwashes, isLoading, setLoading } = useCarwashesStore()
  const { reset: resetBooking } = useBookingStore()
  
  useEffect(() => { resetBooking() }, [resetBooking])
  
  useEffect(() => {
    setLoading(true)
    // Demo data
    setTimeout(() => {
      setCarwashes([
        { id: '1', name: 'АвтоСпа Premium', address: 'ул. Ленина, 15', distance: 1.2, rating: 4.8, available_slots_today: 5 },
        { id: '2', name: 'Чистый Кузов', address: 'пр. Мира, 42', distance: 2.5, rating: 4.5, available_slots_today: 3 },
        { id: '3', name: 'Express Wash', address: 'ул. Гагарина, 8', distance: 3.1, rating: 4.2, available_slots_today: 8 }
      ])
      setLoading(false)
    }, 500)
  }, [location])
  
  return (
    <div className="px-4 pt-4">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">🚗 CarWash</h1>
          <p className="text-sm text-gray-500">Бронирование без очередей</p>
        </div>
        <button onClick={() => { haptic('light'); navigate('/my-bookings') }} 
          className="w-10 h-10 bg-white rounded-full shadow-sm flex items-center justify-center">
          <span>📋</span>
        </button>
      </div>
      
      <LocationButton location={location} onLocationUpdate={setLocation} />
      
      {isLoading ? <Loader /> : (
        <div className="space-y-3 pb-8">
          {carwashes.map((cw, idx) => (
            <CarwashCard key={cw.id} carwash={cw} onClick={() => { haptic('light'); navigate(`/carwash/${cw.id}`) }} />
          ))}
        </div>
      )}
    </div>
  )
}
