import React from 'react'
import { format, addDays } from 'date-fns'
import { ru } from 'date-fns/locale'

export default function DateSelector({ selected, onSelect, daysAhead = 7 }) {
  const dates = Array.from({ length: daysAhead }, (_, i) => addDays(new Date(), i))
  
  return (
    <div className="flex gap-2 overflow-x-auto pb-2 -mx-1 px-1">
      {dates.map((date, idx) => {
        const isSelected = selected === format(date, 'yyyy-MM-dd')
        const dayName = idx === 0 ? 'Сегодня' : idx === 1 ? 'Завтра' : format(date, 'EE', { locale: ru })
        const dayNum = format(date, 'd')
        
        return (
          <button
            key={date.toISOString()}
            onClick={() => onSelect(format(date, 'yyyy-MM-dd'))}
            className={`flex-shrink-0 w-16 py-3 rounded-xl text-center transition-all ${
              isSelected 
                ? 'bg-wash-primary text-white' 
                : 'bg-white border border-gray-200 text-gray-700'
            }`}
          >
            <div className="text-xs opacity-75">{dayName}</div>
            <div className="text-lg font-semibold">{dayNum}</div>
          </button>
        )
      })}
    </div>
  )
}
