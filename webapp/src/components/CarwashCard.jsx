import React from 'react'

export default function CarwashCard({ carwash, onClick }) {
  return (
    <div onClick={onClick} className="card card-hover cursor-pointer animate-in">
      <div className="flex justify-between items-start">
        <div className="flex-1">
          <h3 className="font-semibold text-gray-900">{carwash.name}</h3>
          <p className="text-sm text-gray-500 mt-0.5">{carwash.address}</p>
          
          <div className="flex items-center gap-3 mt-3">
            {carwash.distance && (
              <span className="text-xs text-gray-500 flex items-center gap-1">
                📍 {carwash.distance.toFixed(1)} км
              </span>
            )}
            {carwash.rating && (
              <span className="text-xs text-gray-500 flex items-center gap-1">
                ⭐ {carwash.rating}
              </span>
            )}
          </div>
        </div>
        
        <div className="text-right">
          {carwash.available_slots_today > 0 ? (
            <span className="badge badge-success">
              ✓ {carwash.available_slots_today} слотов
            </span>
          ) : (
            <span className="badge badge-error">Нет мест</span>
          )}
        </div>
      </div>
    </div>
  )
}
