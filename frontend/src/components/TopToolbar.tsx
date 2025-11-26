import { useState } from 'react'
import { Bell, Volume2, VolumeX, Globe, ChevronDown, Star } from 'lucide-react'
import { useTranslation } from '../providers/I18nProvider'

export default function TopToolbar() {
  const { t, language, setLanguage } = useTranslation()
  const [isMuted, setIsMuted] = useState(false)
  const [showLangMenu, setShowLangMenu] = useState(false)
  const [hasNotification] = useState(true)

  const langLabel = {
    'zh-TW': '繁',
    'zh-CN': '简',
    'en': 'EN',
  }[language]

  return (
    <div className="relative z-50 flex items-center justify-between px-4 py-2 bg-gradient-to-b from-brand-dark/80 to-transparent backdrop-blur-sm">
      {/* 左側：通知和音效 */}
      <div className="flex items-center gap-3">
        <button
          className="relative p-1.5 rounded-full bg-white/5 hover:bg-white/10 transition-colors"
          title={t('notifications')}
        >
          <Bell size={16} className="text-gray-300" />
          {hasNotification && (
            <span className="absolute top-0 right-0 w-2 h-2 bg-red-500 rounded-full animate-pulse" />
          )}
        </button>
        
        <button
          className="p-1.5 rounded-full bg-white/5 hover:bg-white/10 transition-colors"
          onClick={() => setIsMuted(!isMuted)}
          title={t('sound')}
        >
          {isMuted ? (
            <VolumeX size={16} className="text-gray-300" />
          ) : (
            <Volume2 size={16} className="text-gray-300" />
          )}
        </button>
      </div>

      {/* 右側：語言和星星 */}
      <div className="flex items-center gap-3">
        <div className="relative">
          <button
            className="flex items-center gap-1 p-1.5 rounded-full bg-white/5 hover:bg-white/10 transition-colors"
            onClick={() => setShowLangMenu(!showLangMenu)}
            title={t('language')}
          >
            <Globe size={16} className="text-gray-300" />
            <span className="text-xs font-bold text-gray-300">{langLabel}</span>
            <ChevronDown size={12} className={`text-gray-300 transition-transform ${showLangMenu ? 'rotate-180' : ''}`} />
          </button>

          {showLangMenu && (
            <div className="absolute right-0 mt-2 w-32 bg-brand-darker rounded-lg shadow-xl overflow-hidden border border-white/10">
              <button
                className="block w-full px-4 py-2 text-left text-sm text-gray-200 hover:bg-white/10"
                onClick={() => { setLanguage('zh-TW'); setShowLangMenu(false) }}
              >
                繁體中文
              </button>
              <button
                className="block w-full px-4 py-2 text-left text-sm text-gray-200 hover:bg-white/10"
                onClick={() => { setLanguage('zh-CN'); setShowLangMenu(false) }}
              >
                简体中文
              </button>
              <button
                className="block w-full px-4 py-2 text-left text-sm text-gray-200 hover:bg-white/10"
                onClick={() => { setLanguage('en'); setShowLangMenu(false) }}
              >
                English
              </button>
            </div>
          )}
        </div>

        <div className="flex items-center gap-1 p-1.5 rounded-full bg-white/5">
          <Star size={16} className="text-yellow-400 fill-yellow-400" />
          <span className="text-xs font-bold text-yellow-300">0</span>
        </div>
      </div>
    </div>
  )
}

