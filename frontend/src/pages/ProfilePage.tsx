import React, { useState, useEffect, useRef } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Settings, ChevronRight, Shield, HelpCircle, FileText, LogOut, MessageSquare } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import { useTranslation } from '../providers/I18nProvider'
import { getUserProfile, getBalance } from '../utils/api'
import { getTelegramUser } from '../utils/telegram'
import FeedbackModal from '../components/FeedbackModal'

export default function ProfilePage() {
  const navigate = useNavigate()
  const { t } = useTranslation()
  const tgUser = getTelegramUser()
  const [showFeedbackModal, setShowFeedbackModal] = useState(false)
  const settingsButtonRef = useRef<HTMLButtonElement>(null)

  // 添加全局点击监听器作为备用方案
  useEffect(() => {
    console.log('[ProfilePage] 🔧 设置全局点击监听器')
    const handleGlobalClick = (e: MouseEvent) => {
      const target = e.target as HTMLElement
      // 检查是否点击了设置按钮或其子元素
      if (settingsButtonRef.current && (target === settingsButtonRef.current || settingsButtonRef.current.contains(target))) {
        console.log('[ProfilePage] 🌐 全局点击检测到设置按钮！')
        e.preventDefault()
        e.stopPropagation()
        console.log('[ProfilePage] 🌐 执行导航到 /settings')
        navigate('/settings')
      }
    }

    // 在捕获阶段监听，确保能捕获到事件
    document.addEventListener('click', handleGlobalClick, true)
    console.log('[ProfilePage] ✅ 全局点击监听器已添加')

    return () => {
      document.removeEventListener('click', handleGlobalClick, true)
      console.log('[ProfilePage] 🧹 全局点击监听器已移除')
    }
  }, [navigate])

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


  return (
    <div className="h-full overflow-y-auto scrollbar-hide pb-20 p-4 space-y-4 relative" style={{ zIndex: 10 }}>
      {/* 用戶卡片 */}
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

        {/* 資產 */}
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

      {/* 菜單列表 */}
      <div className="space-y-2 relative">
        <MenuLink
          ref={settingsButtonRef}
          icon={Settings}
          title={t('settings')}
          to="/settings"
          navigate={navigate}
        />
        <MenuLink
          icon={Shield}
          title={t('security_settings')}
          to="/security"
          navigate={navigate}
        />
        <MenuLink
          icon={HelpCircle}
          title={t('help_center')}
          to="/help"
          navigate={navigate}
        />
        <MenuLink
          icon={FileText}
          title={t('user_agreement')}
          to="/agreement"
          navigate={navigate}
        />
        <MenuItem
          icon={MessageSquare}
          title={t('submit_feedback') || '提交反馈'}
          onClick={() => {
            console.log('[ProfilePage] ✅ Submit Feedback button clicked')
            setShowFeedbackModal(true)
          }}
        />
      </div>

      {/* 反馈弹窗 */}
      <FeedbackModal
        isOpen={showFeedbackModal}
        onClose={() => setShowFeedbackModal(false)}
      />
    </div>
  )
}

// 使用按钮 + navigate 的菜单项（用于导航，完全模仿 MenuItem 的实现）
const MenuLink = React.forwardRef<HTMLButtonElement, {
  icon: React.ElementType
  title: string
  to: string
  navigate: (path: string) => void
}>(({ icon: Icon, title, to, navigate }, ref) => {
  const handleClick = (e: React.MouseEvent<HTMLButtonElement>) => {
    e.preventDefault()
    e.stopPropagation()
    console.log('=== [MenuLink] 按钮点击开始 ===')
    console.log('[MenuLink] 🔵 Button clicked:', title, 'to:', to)
    console.log('[MenuLink] 🔵 Current URL:', window.location.href)
    console.log('[MenuLink] 🔵 Current pathname:', window.location.pathname)
    console.log('[MenuLink] 🔵 Event details:', {
      type: e.type,
      target: e.target,
      currentTarget: e.currentTarget,
      button: e.button,
      bubbles: e.bubbles,
      cancelable: e.cancelable,
      defaultPrevented: e.defaultPrevented,
      isPropagationStopped: e.isPropagationStopped()
    })
    try {
      console.log('[MenuLink] 🔵 Attempting navigation to:', to)
      navigate(to)
      console.log('[MenuLink] ✅ Navigation executed successfully')
      console.log('[MenuLink] 🔵 URL after navigation:', window.location.href)
      console.log('=== [MenuLink] 按钮点击结束 ===')
    } catch (error) {
      console.error('[MenuLink] ❌ Navigation error:', error)
      console.error('[MenuLink] ❌ Error details:', {
        message: error instanceof Error ? error.message : String(error),
        stack: error instanceof Error ? error.stack : undefined,
        name: error instanceof Error ? error.name : undefined
      })
      // 备用方案：使用 window.location
      console.log('[MenuLink] 🔄 Trying window.location fallback')
      window.location.href = to
      console.log('=== [MenuLink] 按钮点击结束（使用 fallback）===')
    }
  }

  return (
    <button
      ref={ref}
      type="button"
      onClick={handleClick}
      onMouseDown={(e) => {
        console.log('[MenuLink] 🟢 MouseDown event:', title)
      }}
      onMouseUp={(e) => {
        console.log('[MenuLink] 🟡 MouseUp event:', title)
      }}
      onTouchStart={(e) => {
        console.log('[MenuLink] 🟠 TouchStart event:', title)
      }}
      className="w-full flex items-center justify-between p-4 bg-brand-darker rounded-xl active:bg-white/5 transition-colors cursor-pointer hover:bg-white/10"
      style={{ 
        pointerEvents: 'auto', 
        position: 'relative',
        zIndex: 1000,
        isolation: 'isolate',
        WebkitTapHighlightColor: 'transparent',
        touchAction: 'manipulation'
      }}
      data-menu-item="true"
      data-menu-path={to}
    >
      <div className="flex items-center gap-3 pointer-events-none">
        <Icon size={20} className="text-gray-400" />
        <span className="text-white">{title}</span>
      </div>
      <ChevronRight size={18} className="text-gray-500 pointer-events-none" />
    </button>
  )
})

MenuLink.displayName = 'MenuLink'

// 使用按钮的菜单项（用于非导航操作）
function MenuItem({ icon: Icon, title, onClick }: {
  icon: React.ElementType
  title: string
  onClick: () => void
}) {
  const handleClick = (e: React.MouseEvent<HTMLButtonElement>) => {
    e.preventDefault()
    e.stopPropagation()
    console.log('[MenuItem] Button clicked:', title)
    try {
      onClick()
      console.log('[MenuItem] onClick handler executed successfully')
    } catch (error) {
      console.error('[MenuItem] Error in onClick handler:', error)
    }
  }

  return (
    <button
      type="button"
      onClick={handleClick}
      className="w-full flex items-center justify-between p-4 bg-brand-darker rounded-xl active:bg-white/5 transition-colors cursor-pointer"
      style={{ 
        pointerEvents: 'auto', 
        position: 'relative',
        zIndex: 100,
        isolation: 'isolate'
      }}
    >
      <div className="flex items-center gap-3">
        <Icon size={20} className="text-gray-400" />
        <span className="text-white">{title}</span>
      </div>
      <ChevronRight size={18} className="text-gray-500" />
    </button>
  )
}

