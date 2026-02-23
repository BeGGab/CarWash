import React, { useState } from 'react'

const tg = window.Telegram?.WebApp

export default function LocationButton({ location, onLocationUpdate }) {
  const [isLoading, setIsLoading] = useState(false)
  
  const requestLocation = () => {
    setIsLoading(true)
    
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          onLocationUpdate({
            latitude: position.coords.latitude,
            longitude: position.coords.longitude
          })
          setIsLoading(false)
        },
        (error) => {
          console.error('Geolocation error:', error)
          setIsLoading(false)
          // Fallback to demo location
          onLocationUpdate({ latitude: 55.7558, longitude: 37.6173 })
        },
        { enableHighAccuracy: true, timeout: 10000 }
      )
    } else {
      setIsLoading(false)
      onLocationUpdate({ latitude: 55.7558, longitude: 37.6173 })
    }
  }
  
  return (
    <button 
      onClick={requestLocation}
      disabled={isLoading}
      className={`w-full mb-4 py-3 px-4 rounded-xl flex items-center justify-center gap-2 font-medium transition-all
        ${location ? 'bg-green-50 text-green-700 border border-green-200' : 'bg-wash-primary text-white'}`}
    >
      {isLoading ? (
        <>
          <span className="animate-spin">⏳</span>
          <span>Определение...</span>
        </>
      ) : location ? (
        <>
          <span>📍</span>
          <span>Геолокация получена</span>
        </>
      ) : (
        <>
          <span>📍</span>
          <span>Отправить местоположение</span>
        </>
      )}
    </button>
  )
}
