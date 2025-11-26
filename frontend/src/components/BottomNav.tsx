import { NavLink } from 'react-router-dom'
import { Wallet, Gift, TrendingUp, Gamepad2, User } from 'lucide-react'
import { useTranslation } from '../providers/I18nProvider'

const navItems = [
  { path: '/', icon: Wallet, labelKey: 'wallet' },
  { path: '/packets', icon: Gift, labelKey: 'packets' },
  { path: '/earn', icon: TrendingUp, labelKey: 'earn' },
  { path: '/game', icon: Gamepad2, labelKey: 'game' },
  { path: '/profile', icon: User, labelKey: 'profile' },
]

export default function BottomNav() {
  const { t } = useTranslation()

  return (
    <nav className="flex items-center justify-around px-2 py-2 bg-brand-darker border-t border-white/5 safe-area-pb">
      {navItems.map(({ path, icon: Icon, labelKey }) => (
        <NavLink
          key={path}
          to={path}
          className={({ isActive }) =>
            `flex flex-col items-center gap-0.5 px-3 py-1 rounded-lg transition-colors ${
              isActive
                ? 'text-brand-red'
                : 'text-gray-400 hover:text-gray-200'
            }`
          }
        >
          <Icon size={20} />
          <span className="text-[10px] font-medium">{t(labelKey)}</span>
        </NavLink>
      ))}
    </nav>
  )
}

