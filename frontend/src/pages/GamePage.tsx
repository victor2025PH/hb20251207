import { Gamepad2, ExternalLink, Shield, Headphones, Star } from 'lucide-react'
import { useTranslation } from '../providers/I18nProvider'
import { getTelegram } from '../utils/telegram'

export default function GamePage() {
  const { t } = useTranslation()

  const handleOpenGame = () => {
    const telegram = getTelegram()
    // 跳轉到金福寶局遊戲網站
    const gameUrl = 'https://game.example.com' // 替換為實際遊戲網址
    if (telegram) {
      telegram.openLink(gameUrl)
    } else {
      window.open(gameUrl, '_blank')
    }
  }

  return (
    <div className="h-full overflow-y-auto scrollbar-hide pb-20 p-4">
      <h1 className="text-xl font-bold mb-4">{t('game')}</h1>

      {/* 遊戲卡片 */}
      <div className="relative bg-gradient-to-br from-purple-600/30 via-brand-darker to-pink-600/30 border border-purple-500/30 rounded-3xl overflow-hidden">
        {/* 背景裝飾 */}
        <div className="absolute inset-0 overflow-hidden">
          <div className="absolute top-0 right-0 w-32 h-32 bg-purple-500/20 rounded-full blur-3xl" />
          <div className="absolute bottom-0 left-0 w-32 h-32 bg-pink-500/20 rounded-full blur-3xl" />
        </div>

        <div className="relative p-6">
          {/* 標題 */}
          <div className="flex items-center gap-4 mb-6">
            <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-brand-gold to-orange-600 flex items-center justify-center shadow-lg shadow-brand-gold/30">
              <Gamepad2 size={32} className="text-white" />
            </div>
            <div>
              <h2 className="text-2xl font-black text-white">金福寶局</h2>
              <p className="text-purple-300 text-sm">Gold Fortune Bureau</p>
            </div>
          </div>

          {/* 特點 */}
          <div className="space-y-3 mb-6">
            <Feature icon={Star} text="多種遊戲類型" />
            <Feature icon={Shield} text="安全可靠的遊戲環境" />
            <Feature icon={Headphones} text="24/7 在線客服支援" />
          </div>

          {/* 開始遊戲按鈕 */}
          <button
            onClick={handleOpenGame}
            className="w-full py-4 bg-gradient-to-r from-brand-gold via-orange-500 to-brand-gold rounded-xl text-white font-bold text-lg flex items-center justify-center gap-2 active:scale-[0.98] transition-transform shadow-lg shadow-brand-gold/30"
          >
            開始遊戲
            <ExternalLink size={18} />
          </button>
        </div>
      </div>

      {/* 提示 */}
      <div className="mt-4 p-4 bg-brand-darker/50 rounded-xl border border-white/5">
        <p className="text-gray-400 text-sm text-center">
          點擊「開始遊戲」將跳轉到外部遊戲網站
        </p>
      </div>
    </div>
  )
}

function Feature({ icon: Icon, text }: { icon: React.ElementType; text: string }) {
  return (
    <div className="flex items-center gap-3">
      <div className="w-8 h-8 rounded-lg bg-white/10 flex items-center justify-center">
        <Icon size={16} className="text-brand-gold" />
      </div>
      <span className="text-white/80">{text}</span>
    </div>
  )
}

