import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Settings, ChevronRight, Shield, HelpCircle, FileText, MessageSquare } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import { useTranslation } from '../providers/I18nProvider'
import { getUserProfile, getBalance } from '../utils/api'
import { getTelegramUser } from '../utils/telegram'
import FeedbackModal from '../components/FeedbackModal'
import PageTransition from '../components/PageTransition'
import { useSound } from '../hooks/useSound'

export default function ProfilePage() {
  const navigate = useNavigate()
  const { t } = useTranslation()
  const { playSound } = useSound()
  const tgUser = getTelegramUser()
  const [showFeedbackModal, setShowFeedbackModal] = useState(false)

  const { data: profile } = useQuery({
    queryKey: ['profile'],
    queryFn: getUserProfile,
  })

  const { data: balance } = useQuery({
    queryKey: ['balance'],
    queryFn: getBalance,
  })

  const displayName = profile?.first_name || tgUser?.first_name || 'User'
  const username = profile?.username || tgUser?.username

  // 菜单项配置
  const menuItems = [
    {
      icon: Settings,
      title: t('settings'),
      path: '/settings',
      action: () => {
        playSound('click')
        navigate('/settings')
      },
    },
    {
      icon: Shield,
      title: t('security_settings'),
      path: '/security',
      action: () => {
        playSound('click')
        navigate('/security')
      },
    },
    {
      icon: HelpCircle,
      title: t('help_center'),
      path: '/help',
      action: () => {
        playSound('click')
        navigate('/help')
      },
    },
    {
      icon: FileText,
      title: t('user_agreement'),
      path: '/agreement',
      action: () => {
        playSound('click')
        navigate('/agreement')
      },
    },
    {
      icon: MessageSquare,
      title: t('submit_feedback') || '提交反馈',
      action: () => {
        playSound('click')
        setShowFeedbackModal(true)
      },
    },
  ]

  return (
    <PageTransition>
      <div className="h-full overflow-y-auto scrollbar-hide pb-20 p-4 space-y-4">
        {/* 用户卡片 */}
        <div className="bg-gradient-to-br from-brand-red/20 via-brand-darker to-orange-500/20 border border-brand-red/30 rounded-2xl p-4">
          <div className="flex items-center gap-4 mb-4">
            <div className="w-16 h-16 rounded-full bg-gradient-to-br from-brand-red to-orange-500 flex items-center justify-center text-2xl font-bold text-white">
              {displayName[0]?.toUpperCase()}
            </div>
            <div>
              <h2 className="text-xl font-bold text-white">{displayName}</h2>
              {username && <p className="text-gray-400">@{username}</p>}
              <div className="flex items-center gap-2 mt-1">
                <span className="px-2.5 py-1 bg-brand-red/20 text-brand-red text-sm rounded-full font-bold">
                  Lv.{profile?.level || 1}
                </span>
              </div>
            </div>
          </div>

          {/* 资产 */}
          <div className="grid grid-cols-3 gap-2">
            <div className="bg-white/5 rounded-xl p-3 text-center">
              <div className="text-lg font-bold text-white">{balance?.usdt?.toFixed(2) || '0.00'}</div>
              <div className="text-sm text-gray-400 font-medium">USDT</div>
            </div>
            <div className="bg-white/5 rounded-xl p-3 text-center">
              <div className="text-lg font-bold text-white">{balance?.ton?.toFixed(2) || '0.00'}</div>
              <div className="text-xs text-gray-400">TON</div>
            </div>
            <div className="bg-white/5 rounded-xl p-3 text-center">
              <div className="text-lg font-bold text-brand-gold">{balance?.stars || 0}</div>
              <div className="text-xs text-gray-400">Stars</div>
            </div>
          </div>
        </div>

        {/* 菜单列表 */}
        <div className="space-y-2">
          {menuItems.map((item, index) => {
            const Icon = item.icon
            return (
              <button
                key={index}
                type="button"
                onClick={item.action}
                className="w-full flex items-center justify-between p-4 bg-brand-darker rounded-xl hover:bg-white/5 active:bg-white/10 transition-colors"
              >
                <div className="flex items-center gap-3">
                  <Icon size={20} className="text-gray-400" />
                  <span className="text-white font-medium">{item.title}</span>
                </div>
                <ChevronRight size={18} className="text-gray-500" />
              </button>
            )
          })}
        </div>

        {/* 反馈弹窗 */}
        <FeedbackModal
          isOpen={showFeedbackModal}
          onClose={() => setShowFeedbackModal(false)}
        />
      </div>
    </PageTransition>
  )
}
