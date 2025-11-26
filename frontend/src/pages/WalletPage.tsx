import { useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { Plus, Minus, Gift, Clock, Users, ChevronRight, Wallet } from 'lucide-react'
import { useTranslation } from '../providers/I18nProvider'
import { getBalance, getUserProfile } from '../utils/api'

export default function WalletPage() {
  const navigate = useNavigate()
  const { t } = useTranslation()

  const { data: balance } = useQuery({
    queryKey: ['balance'],
    queryFn: getBalance,
    staleTime: 30000,
  })

  const { data: profile } = useQuery({
    queryKey: ['profile'],
    queryFn: getUserProfile,
    staleTime: 60000,
  })

  const usdt = balance?.usdt ?? 0
  const stars = balance?.stars ?? 0

  return (
    <div className="h-full overflow-y-auto scrollbar-hide pb-20 p-4 space-y-4">
      {/* 總資產橫幅 */}
      <div className="flex items-center justify-between bg-brand-darker border border-cyan-500/20 rounded-2xl px-4 py-3">
        <div className="flex items-center gap-2">
          <Wallet size={18} className="text-cyan-400" />
          <span className="text-cyan-300 text-sm font-bold">{t('total_assets')}</span>
        </div>
        <div className="flex items-center gap-6">
          <div className="text-right">
            <div className="text-white text-lg font-black">{usdt.toFixed(2)}</div>
            <div className="text-cyan-200 text-xs opacity-70">USDT</div>
          </div>
          <div className="text-right">
            <div className="text-white text-lg font-black">{stars}</div>
            <div className="text-yellow-300 text-xs opacity-70">Stars</div>
          </div>
        </div>
      </div>

      {/* 發紅包按鈕 */}
      <button
        onClick={() => navigate('/send')}
        className="w-full h-40 bg-gradient-to-br from-brand-red/20 via-brand-darker to-orange-900/20 border border-brand-red/30 rounded-3xl flex flex-col items-center justify-center gap-2 active:scale-[0.98] transition-transform"
      >
        <div className="w-16 h-16 bg-gradient-to-br from-orange-500 to-red-600 rounded-full flex items-center justify-center shadow-lg shadow-orange-500/30">
          <Gift size={28} className="text-white" />
        </div>
        <h2 className="text-xl font-black text-white">{t('send_red_packet')}</h2>
        <p className="text-orange-300/80 text-xs">點擊發送紅包</p>
      </button>

      {/* 操作按鈕 */}
      <div className="grid grid-cols-4 gap-3">
        <ActionButton icon={Plus} label={t('recharge')} color="text-green-400" onClick={() => navigate('/recharge')} />
        <ActionButton icon={Minus} label={t('withdraw')} color="text-white" onClick={() => navigate('/withdraw')} />
        <ActionButton icon={Clock} label={t('records')} color="text-white" onClick={() => navigate('/packets')} />
        <ActionButton icon={Gift} label={t('game')} color="text-purple-400" onClick={() => navigate('/game')} />
      </div>

      {/* 邀請好友 */}
      <button
        onClick={() => navigate('/earn')}
        className="w-full bg-brand-darker border border-purple-500/20 rounded-2xl flex items-center justify-between px-4 py-3 active:bg-white/5 transition-colors"
      >
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-purple-500 to-pink-600 flex items-center justify-center">
            <Users size={18} className="text-white" />
          </div>
          <div className="text-left">
            <div className="text-white font-bold text-sm">{t('invite_friends')}</div>
            <div className="text-purple-300 text-xs">永久獲得 10% 返佣</div>
          </div>
        </div>
        <ChevronRight size={16} className="text-gray-400" />
      </button>

      {/* 用戶等級 */}
      {profile && (
        <div className="bg-brand-darker border border-white/5 rounded-2xl p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-gray-400 text-sm">{t('level')}</span>
            <span className="text-white font-bold">Lv.{profile.level}</span>
          </div>
          <div className="h-2 bg-white/10 rounded-full overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-brand-red to-orange-500"
              style={{ width: `${(profile.xp % 100)}%` }}
            />
          </div>
        </div>
      )}
    </div>
  )
}

function ActionButton({ icon: Icon, label, color, onClick }: {
  icon: React.ElementType
  label: string
  color: string
  onClick: () => void
}) {
  return (
    <button
      onClick={onClick}
      className="flex flex-col items-center gap-1 p-3 bg-brand-darker rounded-xl active:bg-white/5 transition-colors"
    >
      <div className="w-10 h-10 rounded-xl bg-white/5 flex items-center justify-center">
        <Icon className={color} size={18} />
      </div>
      <span className="text-[10px] text-gray-400 font-medium">{label}</span>
    </button>
  )
}

