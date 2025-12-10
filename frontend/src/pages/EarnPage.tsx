import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Check, Star, Sparkles, UserPlus, Trophy, Copy, CheckCircle, Users, Coins, Gift, ChevronRight, Share2 } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'
import { useTranslation } from '../providers/I18nProvider'
import { checkIn, getCheckInStatus, getInviteStats, INVITE_MILESTONES, type InviteStats, getReferralStats, getReferralTree } from '../utils/api'
import { haptic, showAlert, getTelegram } from '../utils/telegram'
import { useSound } from '../hooks/useSound'
import TelegramStar from '../components/TelegramStar'
import PageTransition from '../components/PageTransition'
import ReferralTree from '../components/ReferralTree'

export default function EarnPage() {
  const { t } = useTranslation()
  const { playSound } = useSound()
  const queryClient = useQueryClient()
  const [activeTab, setActiveTab] = useState<'checkin' | 'invite' | 'referral'>('checkin')
  const [copied, setCopied] = useState(false)

  // 簽到狀態
  const { data: checkInStatus } = useQuery({
    queryKey: ['checkin-status'],
    queryFn: getCheckInStatus,
  })

  // 邀請統計
  const { data: inviteStats } = useQuery<InviteStats>({
    queryKey: ['invite-stats'],
    queryFn: getInviteStats,
  })

  const checkInMutation = useMutation({
    mutationFn: checkIn,
    onSuccess: (data) => {
      haptic('success')
      playSound('success')
      showAlert(`${t('checkin_success')} +${data.reward} points, ${data.streak} days`)
      queryClient.invalidateQueries({ queryKey: ['checkin-status'] })
    },
    onError: (error: Error) => {
      haptic('error')
      playSound('click')
      showAlert(error.message)
    },
  })

  const handleCopyInviteCode = async () => {
    if (!inviteStats?.invite_code) return
    try {
      await navigator.clipboard.writeText(inviteStats.invite_code)
      setCopied(true)
      haptic('success')
      playSound('success')
      setTimeout(() => setCopied(false), 2000)
    } catch {
      showAlert(t('copy_failed'))
    }
  }

  const handleShareInvite = async () => {
    try {
      playSound('pop')
      haptic('light')
      
      // 檢查邀請鏈接是否存在
      if (!inviteStats?.invite_link) {
        showAlert('邀請鏈接未生成，請稍後再試', 'error')
        return
      }
      
      const telegram = getTelegram()
      const shareMessage = `🎁 來搶紅包啦！\n\n我在玩紅包遊戲，送你 0.5 USDT 新人獎勵！\n\n點擊加入：${inviteStats.invite_link}`
      const shareUrl = `https://t.me/share/url?url=${encodeURIComponent(inviteStats.invite_link)}&text=${encodeURIComponent(shareMessage)}`
      
      // 優先使用 Telegram WebApp 的分享功能
      if (telegram) {
        try {
          // 檢查是否有 openTelegramLink 方法
          if (typeof telegram.openTelegramLink === 'function') {
            telegram.openTelegramLink(shareUrl)
            haptic('success')
            return
          }
          // 如果沒有 openTelegramLink，嘗試使用 openLink
          if (typeof telegram.openLink === 'function') {
            telegram.openLink(shareUrl)
            haptic('success')
            return
          }
        } catch (error) {
          console.error('[handleShareInvite] Telegram share error:', error)
          // 如果 Telegram 方法失敗，繼續使用備用方案
        }
      }
      
      // 備用方案 1: 使用 Web Share API（如果支持）
      if (navigator.share) {
        try {
          await navigator.share({
            title: '邀請你來搶紅包！',
            text: shareMessage,
            url: inviteStats.invite_link
          })
          haptic('success')
          showAlert('分享成功！', 'success')
          return
        } catch (error: any) {
          // 用戶取消分享不算錯誤
          if (error.name !== 'AbortError') {
            console.error('[handleShareInvite] Web Share API error:', error)
          }
        }
      }
      
      // 備用方案 2: 複製邀請鏈接到剪貼板
      try {
        await navigator.clipboard.writeText(inviteStats.invite_link)
        haptic('success')
        showAlert('邀請鏈接已複製到剪貼板！', 'success')
      } catch (error) {
        console.error('[handleShareInvite] Clipboard error:', error)
        showAlert('無法複製鏈接，請手動複製：' + inviteStats.invite_link, 'error')
      }
    } catch (error) {
      console.error('[handleShareInvite] Unexpected error:', error)
      haptic('error')
      showAlert('分享失敗，請稍後再試', 'error')
    }
  }

  const totalDays = 7
  const DURATION = 4
  // 如果今天已签到，显示已签到的天数；如果今天未签到，显示已签到的天数（下一个要签到的是 streak + 1）
  const currentStreak = checkInStatus?.streak || 0
  const todayChecked = checkInStatus?.checked_today || false
  // 计算进度：如果今天已签到，进度是 streak/totalDays；如果今天未签到，进度是 streak/totalDays（下一个要签到的是 streak + 1）
  const progressPercent = todayChecked 
    ? (currentStreak / totalDays) * 100 
    : (currentStreak / totalDays) * 100

  // 計算里程碑進度
  const inviteCount = inviteStats?.invite_count || 0
  const milestonesWithStatus = INVITE_MILESTONES.map(m => ({
    ...m,
    achieved: inviteCount >= m.target,
  }))
  const nextMilestone = milestonesWithStatus.find(m => !m.achieved)

  return (
    <PageTransition>
      <div className="h-full flex flex-col p-3 pb-20 gap-3 overflow-y-auto scrollbar-hide">
        {/* 標籤切換 */}
        <div className="flex gap-2 shrink-0">
          <motion.button
            onClick={() => setActiveTab('checkin')}
            className={`flex-1 py-2.5 rounded-xl font-bold text-sm transition-all flex items-center justify-center gap-2 ${
              activeTab === 'checkin'
                ? 'bg-orange-500 text-white shadow-lg shadow-orange-500/20'
                : 'bg-[#1C1C1E] text-gray-400 border border-white/5'
            }`}
            whileTap={{ scale: 0.98 }}
          >
            <Sparkles size={16} />
            每日簽到
          </motion.button>
          <motion.button
            onClick={() => setActiveTab('invite')}
            className={`flex-1 py-2.5 rounded-xl font-bold text-sm transition-all flex items-center justify-center gap-2 ${
              activeTab === 'invite'
                ? 'bg-purple-500 text-white shadow-lg shadow-purple-500/20'
                : 'bg-[#1C1C1E] text-gray-400 border border-white/5'
            }`}
            whileTap={{ scale: 0.98 }}
          >
            <UserPlus size={16} />
            邀請好友
          </motion.button>
          <motion.button
            onClick={() => setActiveTab('referral')}
            className={`flex-1 py-2.5 rounded-xl font-bold text-sm transition-all flex items-center justify-center gap-2 ${
              activeTab === 'referral'
                ? 'bg-emerald-500 text-white shadow-lg shadow-emerald-500/20'
                : 'bg-[#1C1C1E] text-gray-400 border border-white/5'
            }`}
            whileTap={{ scale: 0.98 }}
          >
            <Users size={16} />
            推薦系統
          </motion.button>
        </div>

        <AnimatePresence mode="wait">
          {activeTab === 'referral' ? (
            <motion.div
              key="referral"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              className="space-y-3"
            >
              <ReferralTree />
            </motion.div>
          ) : activeTab === 'checkin' ? (
            <motion.div
              key="checkin"
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 20 }}
              className="space-y-3"
            >
              {/* 簽到卡片 */}
              <div className="bg-[#1C1C1E] border border-white/5 rounded-2xl p-4 shadow-xl relative overflow-hidden">
                <div className="absolute top-0 right-0 w-64 h-64 bg-orange-500/5 blur-[80px] rounded-full pointer-events-none" />
                
                <h2 className="text-base font-bold text-white mb-4 relative z-10 pl-1">{t('daily_checkin')}</h2>
                
                {/* 龍珠進度 */}
                <div className="relative mb-4 px-2">
                  <div className="w-full flex justify-between relative z-10">
                    {Array.from({ length: totalDays }).map((_, i) => {
                      const day = i + 1
                      // 如果今天已签到，点亮到 streak 的位置；如果今天未签到，点亮到 streak 的位置（下一个要签到的是 streak + 1）
                      const isChecked = checkInStatus?.checked_today 
                        ? day <= currentStreak  // 今天已签到，点亮已签到的天数
                        : day < currentStreak + 1  // 今天未签到，点亮已签到的天数，下一个要签到的是 streak + 1
                      const isToday = !checkInStatus?.checked_today && day === currentStreak + 1  // 下一个要签到的龙珠
                      const cycleDelay = (i / (totalDays - 1)) * DURATION
                      
                      return (
                        <div key={day} className="flex flex-col items-center relative">
                          <motion.div
                            className="w-9 h-9 rounded-full flex items-center justify-center relative shadow-[inset_-3px_-3px_6px_rgba(0,0,0,0.5),inset_2px_2px_4px_rgba(255,255,255,0.2),0_4px_6px_rgba(0,0,0,0.3)]"
                            style={{
                              background: isChecked || isToday
                                ? 'radial-gradient(circle at 35% 35%, #fbbf24, #f97316, #ea580c)'
                                : 'radial-gradient(circle at 35% 35%, #52525b, #27272a, #18181b)'
                            }}
                            animate={{
                              scale: [1, 1.2, 1],
                              filter: ['brightness(1)', 'brightness(1.4)', 'brightness(1)']
                            }}
                            transition={{
                              duration: 0.5,
                              repeat: Infinity,
                              delay: cycleDelay,
                              repeatDelay: DURATION - 0.5,
                              ease: "easeOut"
                            }}
                          >
                            {isChecked ? (
                              <Check size={16} strokeWidth={4} className="text-red-900 drop-shadow-sm" />
                            ) : (
                              <Star size={14} className={`${isChecked || isToday ? 'fill-red-600 text-red-700' : 'fill-gray-600 text-gray-700'}`} />
                            )}
                            <div className="absolute top-1.5 left-2 w-2.5 h-1.5 bg-white/30 rounded-full blur-[0.5px] -rotate-45" />
                          </motion.div>
                          <span className={`text-xs font-bold uppercase tracking-wide mt-3 ${isToday || isChecked ? 'text-white' : 'text-gray-600'}`}>
                            D{day}
                          </span>
                        </div>
                      )
                    })}
                  </div>
                  
                  {/* 進度條 */}
                  <div className="absolute left-[18px] right-[18px] h-[4px] z-0" style={{ top: '18px' }}>
                    <div className="w-full h-full bg-[#2C2C2E] rounded-full overflow-hidden relative">
                      <motion.div
                        className="h-full rounded-full"
                        style={{
                          background: 'linear-gradient(90deg, #fbbf24 0%, #f97316 50%, #ef4444 100%)',
                        }}
                        initial={{ width: 0 }}
                        animate={{ width: `${progressPercent}%` }}
                        transition={{ duration: 0.8, ease: "easeOut" }}
                      />
                    </div>
                  </div>
                </div>

                <motion.button
                  onClick={() => {
                    // 如果已簽到，顯示提示
                    if (checkInStatus?.checked_today) {
                      showAlert('今天已簽到，請明天再來', 'info')
                      return
                    }
                    // 如果正在簽到中，不執行
                    if (checkInMutation.isPending) {
                      return
                    }
                    checkInMutation.mutate()
                  }}
                  className="w-full py-3.5 rounded-xl bg-gradient-to-r from-orange-500 to-red-600 text-white font-bold text-sm shadow-lg shadow-orange-500/20 flex items-center justify-center gap-2 cursor-pointer"
                  style={{ opacity: checkInStatus?.checked_today || checkInMutation.isPending ? 0.5 : 1 }}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                >
                  <Sparkles size={16} className="fill-white" />
                  {checkInStatus?.checked_today ? t('checked_in') : checkInMutation.isPending ? t('checking_in') : t('checkin_points')}
                </motion.button>
              </div>

              {/* 任務入口 */}
              <div className="grid grid-cols-2 gap-3">
                <motion.div
                  onClick={handleShareInvite}
                  className="bg-[#1C1C1E] border border-white/5 rounded-2xl p-4 flex flex-col items-center justify-center text-center hover:border-orange-500/30 transition-colors cursor-pointer group"
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                >
                  <div className="w-12 h-12 bg-[#2C2C2E] rounded-full flex items-center justify-center mb-3 group-hover:scale-110 transition-transform">
                    <UserPlus className="text-orange-500" size={20} />
                  </div>
                  <h3 className="text-white text-sm font-bold mb-1">{t('invite_friends')}</h3>
                  <p className="text-gray-500 text-xs">+1.5 USDT</p>
                </motion.div>

                <motion.div
                  onClick={() => navigate('/tasks')}
                  className="bg-[#1C1C1E] border border-white/5 rounded-2xl p-4 flex flex-col items-center justify-center text-center hover:border-blue-500/30 transition-colors cursor-pointer group"
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                >
                  <div className="w-12 h-12 bg-[#2C2C2E] rounded-full flex items-center justify-center mb-3 group-hover:scale-110 transition-transform">
                    <Trophy className="text-blue-500" size={20} />
                  </div>
                  <h3 className="text-white text-sm font-bold mb-1">{t('tasks')}</h3>
                  <p className="text-gray-500 text-xs">完成任務領獎勵</p>
                </motion.div>
              </div>
            </motion.div>
          ) : (
            <motion.div
              key="invite"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              className="space-y-3"
            >
              {/* 邀請統計卡片 */}
              <div className="bg-gradient-to-br from-purple-500/20 to-pink-500/20 border border-purple-500/30 rounded-2xl p-4">
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-lg font-bold text-white flex items-center gap-2">
                    <Gift className="text-purple-400" size={20} />
                    我的邀請
                  </h2>
                  <div className="text-purple-400 text-sm">
                    +1 USDT/人
                  </div>
                </div>

                <div className="grid grid-cols-3 gap-3 mb-4">
                  <div className="bg-black/20 rounded-xl p-3 text-center">
                    <div className="text-2xl font-bold text-white">{inviteStats?.invite_count || 0}</div>
                    <div className="text-xs text-gray-400 flex items-center justify-center gap-1">
                      <Users size={12} />
                      已邀請
                    </div>
                  </div>
                  <div className="bg-black/20 rounded-xl p-3 text-center">
                    <div className="text-2xl font-bold text-green-400">{inviteStats?.invite_earnings?.toFixed(2) || '0.00'}</div>
                    <div className="text-xs text-gray-400 flex items-center justify-center gap-1">
                      <Coins size={12} />
                      已獲得
                    </div>
                  </div>
                  <div className="bg-black/20 rounded-xl p-3 text-center">
                    <div className="text-2xl font-bold text-yellow-400">{nextMilestone?.reward || '-'}</div>
                    <div className="text-xs text-gray-400 flex items-center justify-center gap-1">
                      <Trophy size={12} />
                      下個獎勵
                    </div>
                  </div>
                </div>

                {/* 邀請碼 */}
                <div className="bg-black/30 rounded-xl p-3 mb-4">
                  <div className="text-xs text-gray-400 mb-2">我的邀請碼</div>
                  <div className="flex items-center gap-2">
                    <code className="flex-1 text-lg font-bold text-white bg-white/5 px-4 py-2 rounded-lg text-center tracking-widest">
                      {inviteStats?.invite_code || '---'}
                    </code>
                    <button
                      onClick={handleCopyInviteCode}
                      className="p-3 bg-purple-500 rounded-lg hover:bg-purple-400 transition-colors"
                    >
                      {copied ? (
                        <CheckCircle size={20} className="text-white" />
                      ) : (
                        <Copy size={20} className="text-white" />
                      )}
                    </button>
                  </div>
                </div>

                {/* 分享按鈕 */}
                <motion.button
                  onClick={handleShareInvite}
                  className="w-full py-3.5 rounded-xl bg-gradient-to-r from-purple-500 to-pink-500 text-white font-bold text-sm shadow-lg shadow-purple-500/20 flex items-center justify-center gap-2"
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                >
                  <Share2 size={16} />
                  分享邀請鏈接
                </motion.button>
              </div>

              {/* 里程碑獎勵 */}
              <div className="bg-[#1C1C1E] border border-white/5 rounded-2xl p-4">
                <h3 className="text-base font-bold text-white mb-3 flex items-center gap-2">
                  <Trophy className="text-yellow-500" size={18} />
                  邀請里程碑
                </h3>
                <div className="space-y-2">
                  {milestonesWithStatus.map((milestone, index) => (
                    <div
                      key={milestone.target}
                      className={`flex items-center justify-between p-3 rounded-xl transition-colors ${
                        milestone.achieved
                          ? 'bg-green-500/10 border border-green-500/30'
                          : 'bg-[#2C2C2E]'
                      }`}
                    >
                      <div className="flex items-center gap-3">
                        <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
                          milestone.achieved ? 'bg-green-500' : 'bg-gray-700'
                        }`}>
                          {milestone.achieved ? (
                            <Check size={16} className="text-white" />
                          ) : (
                            <span className="text-xs text-gray-400">{index + 1}</span>
                          )}
                        </div>
                        <div>
                          <div className="text-white text-sm font-medium">邀請 {milestone.target} 人</div>
                          <div className="text-xs text-gray-500">
                            {milestone.achieved ? '已完成' : `還差 ${milestone.target - inviteCount} 人`}
                          </div>
                        </div>
                      </div>
                      <div className={`text-sm font-bold ${
                        milestone.achieved ? 'text-green-400' : 'text-yellow-400'
                      }`}>
                        +{milestone.reward} USDT
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* 邀請列表 */}
              {inviteStats?.invitees && inviteStats.invitees.length > 0 && (
                <div className="bg-[#1C1C1E] border border-white/5 rounded-2xl p-4">
                  <h3 className="text-base font-bold text-white mb-3 flex items-center justify-between">
                    <span className="flex items-center gap-2">
                      <Users className="text-blue-400" size={18} />
                      我邀請的好友
                    </span>
                    <span className="text-xs text-gray-500">{inviteStats.invitees.length} 人</span>
                  </h3>
                  <div className="space-y-2 max-h-48 overflow-y-auto">
                    {inviteStats.invitees.map((invitee, index) => (
                      <div
                        key={invitee.tg_id}
                        className="flex items-center justify-between p-2 bg-[#2C2C2E] rounded-lg"
                      >
                        <div className="flex items-center gap-2">
                          <div className="w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 to-purple-500 flex items-center justify-center text-white text-xs font-bold">
                            {invitee.first_name?.[0] || invitee.username?.[0] || '?'}
                          </div>
                          <div>
                            <div className="text-white text-sm">
                              {invitee.first_name || invitee.username || `User ${invitee.tg_id}`}
                            </div>
                            <div className="text-xs text-gray-500">
                              {invitee.joined_at ? new Date(invitee.joined_at).toLocaleDateString() : '-'}
                            </div>
                          </div>
                        </div>
                        <div className="text-green-400 text-xs font-bold">+1 USDT</div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* 邀請規則 */}
              <div className="bg-yellow-500/10 border border-yellow-500/30 rounded-xl p-4">
                <h4 className="text-yellow-500 font-bold mb-2 flex items-center gap-2">
                  <Gift size={16} />
                  邀請獎勵說明
                </h4>
                <ul className="text-yellow-200/80 text-xs space-y-1.5">
                  <li>• 邀請好友註冊，雙方各得獎勵</li>
                  <li>• 邀請人獲得 1 USDT，被邀請人獲得 0.5 USDT</li>
                  <li>• 好友充值，您可獲得 5% 返佣</li>
                  <li>• 達到里程碑可獲得額外獎勵</li>
                </ul>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </PageTransition>
  )
}
