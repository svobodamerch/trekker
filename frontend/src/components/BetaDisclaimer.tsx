import { useState, useEffect } from 'react'
import { SoftCard } from './SoftCard'

export function BetaDisclaimer() {
  const [showDisclaimer, setShowDisclaimer] = useState(false)

  useEffect(() => {
    // Show only if not previously accepted
    const accepted = localStorage.getItem('beta_disclaimer_accepted')
    if (!accepted) {
      setShowDisclaimer(true)
    }
  }, [])

  const handleAccept = () => {
    localStorage.setItem('beta_disclaimer_accepted', 'true')
    setShowDisclaimer(false)
  }

  if (!showDisclaimer) return null

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
      <SoftCard className="max-w-md w-full bg-white p-6">
        <h2 className="text-lg font-semibold text-soft-800 mb-4">
          Перед началом
        </h2>
        
        <div className="space-y-3 text-sm text-soft-600 mb-6">
          <p>
            Это приложение создано для личного самонаблюдения: коротких ежедневных отметок состояния, дневниковых записей, целей и мягкой рефлексии.
          </p>
          
          <div className="bg-soft-50 rounded-lg p-4 space-y-2">
            <p className="font-medium text-soft-700">Важно:</p>
            <ul className="list-disc list-inside space-y-1 text-soft-600">
              <li>это не медицинская помощь</li>
              <li>это не психотерапия</li>
              <li>приложение не ставит диагнозы</li>
              <li>рекомендации и AI-отражения являются гипотезами для размышления, а не инструкциями к действию</li>
            </ul>
          </div>
          
          <p>
            Если тебе тяжело, небезопасно или нужна срочная помощь, пожалуйста, обратись к близким, врачу, психологу или в экстренные службы.
          </p>
          
          <p className="text-xs text-soft-400">
            Продолжая пользоваться приложением, ты понимаешь, что участвуешь в раннем тестировании, где возможны ошибки и изменения.
          </p>
        </div>

        <button
          onClick={handleAccept}
          className="w-full py-3 bg-soft-600 text-white rounded-xl font-medium hover:bg-soft-700"
        >
          Понятно, начать
        </button>
      </SoftCard>
    </div>
  )
}

export function BetaBadge() {
  return (
    <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-yellow-100 text-yellow-800">
      Бета
    </span>
  )
}

export function AboutSection() {
  return (
    <div className="p-4">
      <h3 className="font-semibold text-soft-800 mb-3">О приложении</h3>
      <div className="text-sm text-soft-600 space-y-2">
        <p>
          Это пространство для ежедневного самонаблюдения.
        </p>
        <p>Здесь можно:</p>
        <ul className="list-disc list-inside space-y-1">
          <li>отмечать настроение, энергию и тревогу</li>
          <li>сохранять короткие инсайты дня</li>
          <li>видеть динамику за неделю</li>
          <li>формулировать цели на разные сроки</li>
          <li>описывать жизнь мечты</li>
          <li>мягко возвращаться к практике после пауз</li>
        </ul>
        <p className="text-soft-500 mt-3">
          Главный принцип: без давления и чувства вины. Пропуски нормальны. Цели можно менять. Один короткий ответ уже достаточно.
        </p>
      </div>
    </div>
  )
}

export function PrivacySection() {
  return (
    <div className="p-4">
      <h3 className="font-semibold text-soft-800 mb-3">Данные</h3>
      <div className="text-sm text-soft-600 space-y-2">
        <p>
          Во время закрытого теста приложение сохраняет твои записи, цели и действия внутри продукта, чтобы основные функции работали: история, динамика, цели и недельные отражения.
        </p>
        <p>
          Мы не используем данные для медицинской диагностики и не продаем их третьим лицам.
        </p>
        <p>
          Так как это ранний тест, команда продукта может смотреть технические и продуктовые данные, чтобы исправлять ошибки и улучшать приложение.
        </p>
        <p className="font-medium text-soft-700 mt-3">
          Ты можешь запросить удаление своих данных в любой момент.
        </p>
      </div>
    </div>
  )
}

export function CrisisSupport() {
  return (
    <div className="p-4 bg-red-50 rounded-lg border border-red-200">
      <p className="text-sm text-red-700">
        Если ты чувствуешь, что тебе небезопасно, очень тяжело или ты можешь причинить вред себе или другим, пожалуйста, не оставайся с этим один.
      </p>
      <p className="text-sm text-red-600 mt-2">
        Обратись к близкому человеку, врачу, психологу или в экстренные службы своей страны. Это приложение не предназначено для помощи в кризисных ситуациях.
      </p>
    </div>
  )
}
