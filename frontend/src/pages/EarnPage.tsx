import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Gift, Users, Calendar, ChevronRight, CheckCircle } from 'lucide-react'
import { useTranslation } from '../providers/I18nProvider'
import { checkIn, getCheckInStatus } from '../utils/api'
import { haptic, showAlert, getTelegram } from '../utils/telegram'

export default function EarnPage() {
  const { t } = useTranslation()
  const queryClient = useQueryClient()

  const { data: checkInStatus } = useQuery({
    queryKey: ['checkin-status'],
    queryFn: getCheckInStatus,
  })

  const checkInMutation = useMutation({
    mutationFn: checkIn,
    onSuccess: (data) => {
      haptic('success')
      showAlert(`簽到成功！獲得 ${data.reward} 積分，已連續簽到 ${data.streak} 天`)
      queryClient.invalidateQueries({ queryKey: ['checkin-status'] })
    },
    onError: (error: Error) => {
      haptic('error')
      showAlert(error.message)
    },
  })

  const handleInvite = () => {
    const telegram = getTelegram()
    if (telegram) {
      // 分享邀請鏈接
      const inviteLink = `https://t.me/YourBotUsername?start=invite_${Date.now()}`
      telegram.openTelegramLink(`https://t.me/share/url?url=${encodeURIComponent(inviteLink)}&text=${encodeURIComponent('來一起搶紅包吧！')}`)
    }
  }

  return (
    <div className="h-full overflow-y-auto scrollbar-hide pb-20 p-4 space-y-4">
      <h1 className="text-xl font-bold">{t('earn')}</h1>

      {/* 每日簽到 */}
      <div className="bg-gradient-to-br from-orange-500/20 via-brand-darker to-red-500/20 border border-orange-500/30 rounded-2xl p-4">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-orange-500 to-red-600 flex items-center justify-center">
              <Calendar size={24} className="text-white" />
            </div>
            <div>
              <h3 className="text-white font-bold">{t('daily_checkin')}</h3>
              <p className="text-orange-300 text-sm">
                已連續簽到 {checkInStatus?.streak || 0} 天
              </p>
            </div>
          </div>
          
          <button
            onClick={() => checkInMutation.mutate()}
            disabled={checkInStatus?.checked_today || checkInMutation.isPending}
            className={`px-6 py-2 rounded-xl font-bold transition-colors ${
              checkInStatus?.checked_today
                ? 'bg-gray-600 text-gray-400'
                : 'bg-gradient-to-r from-orange-500 to-red-600 text-white active:scale-95'
            }`}
          >
            {checkInStatus?.checked_today ? (
              <span className="flex items-center gap-1">
                <CheckCircle size={16} /> 已簽到
              </span>
            ) : checkInMutation.isPending ? (
              '簽到中...'
            ) : (
              '簽到'
            )}
          </button>
        </div>

        {/* 簽到日曆預覽 */}
        <div className="flex justify-between">
          {[1, 2, 3, 4, 5, 6, 7].map((day) => (
            <div
              key={day}
              className={`w-10 h-10 rounded-lg flex items-center justify-center text-sm font-bold ${
                day <= (checkInStatus?.streak || 0)
                  ? 'bg-orange-500 text-white'
                  : 'bg-white/5 text-gray-500'
              }`}
            >
              {day}
            </div>
          ))}
        </div>
      </div>

      {/* 邀請好友 */}
      <div className="bg-brand-darker border border-purple-500/20 rounded-2xl overflow-hidden">
        <div className="p-4">
          <div className="flex items-center gap-3 mb-3">
            <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-purple-500 to-pink-600 flex items-center justify-center">
              <Users size={24} className="text-white" />
            </div>
            <div>
              <h3 className="text-white font-bold">{t('invite_friends')}</h3>
              <p className="text-purple-300 text-sm">邀請好友獲得永久 10% 返佣</p>
            </div>
          </div>

          <div className="grid grid-cols-3 gap-2 mb-4">
            <div className="bg-white/5 rounded-xl p-3 text-center">
              <div className="text-2xl font-bold text-white">0</div>
              <div className="text-xs text-gray-400">已邀請</div>
            </div>
            <div className="bg-white/5 rounded-xl p-3 text-center">
              <div className="text-2xl font-bold text-green-400">0</div>
              <div className="text-xs text-gray-400">有效用戶</div>
            </div>
            <div className="bg-white/5 rounded-xl p-3 text-center">
              <div className="text-2xl font-bold text-brand-gold">0</div>
              <div className="text-xs text-gray-400">總收益</div>
            </div>
          </div>

          <button
            onClick={handleInvite}
            className="w-full py-3 bg-gradient-to-r from-purple-500 to-pink-600 rounded-xl text-white font-bold active:scale-[0.98] transition-transform"
          >
            立即邀請
          </button>
        </div>
      </div>

      {/* 任務列表 */}
      <div className="space-y-2">
        <h3 className="text-gray-400 text-sm font-medium">更多任務</h3>
        
        <TaskItem
          icon={Gift}
          title="首次發紅包"
          reward="+50 積分"
          completed={false}
        />
        <TaskItem
          icon={Users}
          title="邀請 5 位好友"
          reward="+200 積分"
          completed={false}
        />
      </div>
    </div>
  )
}

function TaskItem({ icon: Icon, title, reward, completed }: {
  icon: React.ElementType
  title: string
  reward: string
  completed: boolean
}) {
  return (
    <div className="flex items-center justify-between p-4 bg-brand-darker rounded-xl">
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-lg bg-white/5 flex items-center justify-center">
          <Icon size={18} className="text-gray-400" />
        </div>
        <div>
          <div className="text-white font-medium">{title}</div>
          <div className="text-brand-gold text-sm">{reward}</div>
        </div>
      </div>
      {completed ? (
        <CheckCircle size={20} className="text-green-500" />
      ) : (
        <ChevronRight size={20} className="text-gray-500" />
      )}
    </div>
  )
}

