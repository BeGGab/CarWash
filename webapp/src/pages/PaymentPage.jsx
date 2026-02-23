import React from 'react'
import { useParams, useNavigate } from 'react-router-dom'

export default function PaymentPage() {
  const { id } = useParams()
  const navigate = useNavigate()
  
  return (
    <div className="px-4 pt-4 flex flex-col items-center justify-center min-h-[60vh]">
      <div className="animate-spin text-4xl mb-4">💳</div>
      <h2 className="text-xl font-semibold mb-2">Переход к оплате...</h2>
      <p className="text-gray-500 text-sm">Подождите, открываем платёжную страницу</p>
    </div>
  )
}
