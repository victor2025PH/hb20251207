import { useState, useEffect, useRef } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Settings, ChevronRight, Shield, HelpCircle, FileText, LogOut, MessageSquare } from 'lucide-react'
import { useNavigate, Link } from 'react-router-dom'
import { useTranslation } from '../providers/I18nProvider'
import { getUserProfile, getBalance } from '../utils/api'
import { getTelegramUser } from '../utils/telegram'
import FeedbackModal from '../components/FeedbackModal'

export default function ProfilePage() {
  const navigate = useNavigate()
  const { t } = useTranslation()
  const tgUser = getTelegramUser()
  const [showFeedbackModal, setShowFeedbackModal] = useState(false)
  const menuContainerRef = useRef<HTMLDivElement>(null)

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

  // 确保菜单按钮可以点击
  useEffect(() => {
    if (menuContainerRef.current) {
      const buttons = menuContainerRef.current.querySelectorAll('button[data-testid^="menu-link"]')
      buttons.forEach((btn) => {
        // 确保按钮可以接收点击
        btn.style.pointerEvents = 'auto'
        btn.style.zIndex = '1000'
        btn.style.position = 'relative'
      })
    }
  }, [])

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
      <div 
        ref={menuContainerRef}
        className="space-y-2 relative" 
        style={{ 
          zIndex: 1000,
          position: 'relative',
          pointerEvents: 'auto',
          isolation: 'isolate'
        }}
        onMouseEnter={() => console.log('[ProfilePage] 🟢 Menu container mouse enter')}
        onMouseLeave={() => console.log('[ProfilePage] 🔴 Menu container mouse leave')}
      >
        <MenuLink
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

// 使用按钮 + navigate 的菜单项（用于导航，更可靠）
function MenuLink({ icon: Icon, title, to, navigate }: {
  icon: React.ElementType
  title: string
  to: string
  navigate: (path: string) => void
}) {
  const buttonRef = useRef<HTMLButtonElement>(null)

  // 使用多种事件确保点击能触发
  const handleNavigation = () => {
    console.log('[MenuLink] 🚀 Navigating to:', to)
    try {
      navigate(to)
      console.log('[MenuLink] ✅ Navigation successful')
    } catch (error) {
      console.error('[MenuLink] ❌ Navigation error:', error)
      // 备用方案
      window.location.href = to
    }
  }

  const handleClick = (e: React.MouseEvent<HTMLButtonElement>) => {
    e.preventDefault()
    e.stopPropagation()
    console.log('[MenuLink] 🔵 onClick:', title)
    handleNavigation()
  }

  const handleMouseDown = (e: React.MouseEvent<HTMLButtonElement>) => {
    // 不阻止默认行为，让点击更自然
    console.log('[MenuLink] 🟢 MouseDown:', title)
  }

  const handleTouchStart = (e: React.TouchEvent<HTMLButtonElement>) => {
    console.log('[MenuLink] 🟡 TouchStart:', title)
    // 移动端立即导航
    e.preventDefault()
    handleNavigation()
  }

  // 确保按钮可以点击
  useEffect(() => {
    if (buttonRef.current) {
      const btn = buttonRef.current
      btn.style.pointerEvents = 'auto'
      btn.style.zIndex = '1000'
      btn.style.position = 'relative'
      
      // 添加全局点击监听作为备用
      const handleGlobalClick = (e: MouseEvent) => {
        if (e.target === btn || btn.contains(e.target as Node)) {
          console.log('[MenuLink] 🌐 Global click detected:', title)
          try {
            navigate(to)
          } catch (error) {
            window.location.href = to
          }
        }
      }
      
      btn.addEventListener('click', handleGlobalClick, true)
      
      return () => {
        btn.removeEventListener('click', handleGlobalClick, true)
      }
    }
  }, [title, to, navigate])

  return (
    <button
      ref={buttonRef}
      type="button"
      onClick={handleClick}
      onMouseDown={handleMouseDown}
      onTouchStart={handleTouchStart}
      className="w-full flex items-center justify-between p-4 bg-brand-darker rounded-xl active:bg-white/5 transition-colors cursor-pointer hover:bg-white/10"
      style={{ 
        pointerEvents: 'auto', 
        position: 'relative',
        zIndex: 1000,
        isolation: 'isolate',
        WebkitTapHighlightColor: 'transparent',
        touchAction: 'manipulation',
        userSelect: 'none'
      }}
      data-testid={`menu-link-${to.replace('/', '')}`}
      data-nav-to={to}
    >
      <div className="flex items-center gap-3 pointer-events-none">
        <Icon size={20} className="text-gray-400" />
        <span className="text-white">{title}</span>
      </div>
      <ChevronRight size={18} className="text-gray-500 pointer-events-none" />
    </button>
  )
}

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

