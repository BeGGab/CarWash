import React from 'react'

export default function TimeSlots({ slots, selected, onSelect }) {
  if (!slots || slots.length === 0) {
    return <p className="text-sm text-gray-500 text-center py-4">Нет доступных слотов</p>
  }
  
  return (
    <div className="grid grid-cols-3 gap-2">
      {slots.map((slot) => {
        const isSelected = selected?.id === slot.id
        return (
          <button
            key={slot.id}
            onClick={() => onSelect(slot)}
            className={`slot-btn ${isSelected ? 'selected' : ''}`}
          >
            {slot.start_time}
          </button>
        )
      })}
    </div>
  )
}
