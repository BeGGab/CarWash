import React from 'react'

export default function WashTypeSelector({ washTypes, selected, onSelect }) {
  return (
    <div className="space-y-2">
      {washTypes.map((wt) => {
        const isSelected = selected?.id === wt.id
        return (
          <button
            key={wt.id}
            onClick={() => onSelect(wt)}
            className={`w-full p-3 rounded-xl text-left transition-all flex justify-between items-center ${
              isSelected 
                ? 'bg-wash-primary text-white' 
                : 'bg-white border border-gray-200'
            }`}
          >
            <div>
              <div className="font-medium">{wt.name}</div>
              <div className={`text-xs ${isSelected ? 'text-white/75' : 'text-gray-500'}`}>
                🕐 {wt.duration_minutes} мин
              </div>
            </div>
            <div className="font-semibold">{wt.base_price}₽</div>
          </button>
        )
      })}
    </div>
  )
}
