import React, { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { X, Trophy, Sparkles, Users, Share2, Gamepad2, Target, CheckCircle, Gift } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import { getTaskStatus, claimTaskPacket } from '../utils/api'
import { showAlert } from '../utils/telegram'
import { useTranslation } from '../providers/I18nProvider'
import PageTransition from '../components/PageTransition'
import { motion } from 'framer-motion'

interface TaskStatus {
  task_type: string
  task_name: string
  task_description: string
  completed: boolean
  can_claim: boolean
  progress: {
    current: number
    target: number
    completed: boolean
  }
  reward_amount: number
  reward_currency: string
  category?: string  // daily, social, viral, game, challenge
  icon?: string  // 任務圖標
  red_packet_id?: string
  completed_at?: string
  claimed_at?: string
}

const categoryConfig = {
  daily: { name: '每日任務', color: 'from-orange-500 to-red-500', icon: '📅' },
  social: { name: '社交任務', color: 'from-blue-500 to-cyan-500', icon: '👥' },
  viral: { name: '傳播任務', color: 'from-purple-500 to-pink-500', icon: '📤' },
  game: { name: '遊戲任務', color: 'from-green-500 to-emerald-500', icon: '🎮' },
  challenge: { name: '挑戰任務', color: 'from-yellow-500 to-orange-500', icon: '🔥' },
  achievement: { name: '成就任務', color: 'from-indigo-500 to-purple-500', icon: '🏆' },
}

export default function TasksPage() {
  const navigate = useNavigate()
  const { t } = useTranslation()
  const queryClient = useQueryClient()
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null)

  const { data: tasks = [], isLoading, error } = useQuery<TaskStatus[]>({
    queryKey: ['tasks'],
    queryFn: getTaskStatus,
    refetchInterval: 30000, // 每30秒刷新一次
  })

  const claimMutation = useMutation({
    mutationFn: (taskType: string) => claimTaskPacket(taskType),
    onSuccess: (result, taskType) => {
      showAlert(result.message || '領取成功！', 'success')
      queryClient.invalidateQueries({ queryKey: ['tasks'] })
      queryClient.invalidateQueries({ queryKey: ['balance'] })
    },
    onError: (error: any) => {
      showAlert(error.message || '領取失敗', 'error')
    },
  })

  // 按分類分組任務
  const tasksByCategory = tasks.reduce((acc, task) => {
    const category = task.category || 'daily'
    if (!acc[category]) {
      acc[category] = []
    }
    acc[category].push(task)
    return acc
  }, {} as Record<string, TaskStatus[]>)

  // 獲取所有分類
  const categories = Object.keys(tasksByCategory)

  // 過濾任務
  const filteredTasks = selectedCategory
    ? tasksByCategory[selectedCategory] || []
    : tasks

  if (isLoading) {
    return (
      <PageTransition>
        <div className="h-full flex items-center justify-center bg-brand-dark">
          <div className="text-center">
            <div className="w-12 h-12 border-4 border-orange-500 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
            <p className="text-gray-400">載入任務中...</p>
          </div>
        </div>
      </PageTransition>
    )
  }

  if (error) {
    return (
      <PageTransition>
        <div className="h-full flex items-center justify-center bg-brand-dark">
          <div className="text-center">
            <p className="text-red-400 mb-4">載入失敗</p>
            <button
              onClick={() => queryClient.invalidateQueries({ queryKey: ['tasks'] })}
              className="px-4 py-2 bg-orange-500 rounded-lg text-white"
            >
              重試
            </button>
          </div>
        </div>
      </PageTransition>
    )
  }

  return (
    <PageTransition>
      <div className="h-full flex flex-col bg-brand-dark">
        {/* 頂部導航 */}
        <div className="flex items-center justify-between p-4 border-b border-white/5">
          <button onClick={() => navigate(-1)} className="p-2">
            <X size={24} />
          </button>
          <h1 className="text-lg font-bold flex items-center gap-2">
            <Trophy className="text-orange-400" size={20} />
            {t('tasks') || '任務中心'}
          </h1>
          <div className="w-10" />
        </div>

        {/* 分類篩選 */}
        {categories.length > 0 && (
          <div className="px-4 py-3 border-b border-white/5 overflow-x-auto">
            <div className="flex gap-2">
              <button
                onClick={() => setSelectedCategory(null)}
                className={`px-4 py-2 rounded-lg text-sm font-medium whitespace-nowrap transition-colors ${
                  selectedCategory === null
                    ? 'bg-orange-500 text-white'
                    : 'bg-white/5 text-gray-400 hover:bg-white/10'
                }`}
              >
                全部
              </button>
              {categories.map((category) => {
                const config = categoryConfig[category as keyof typeof categoryConfig] || categoryConfig.daily
                return (
                  <button
                    key={category}
                    onClick={() => setSelectedCategory(category)}
                    className={`px-4 py-2 rounded-lg text-sm font-medium whitespace-nowrap transition-colors flex items-center gap-2 ${
                      selectedCategory === category
                        ? `bg-gradient-to-r ${config.color} text-white`
                        : 'bg-white/5 text-gray-400 hover:bg-white/10'
                    }`}
                  >
                    <span>{config.icon}</span>
                    {config.name}
                  </button>
                )
              })}
            </div>
          </div>
        )}

        {/* 任務列表 */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {filteredTasks.length === 0 ? (
            <div className="text-center py-12">
              <Trophy size={48} className="text-gray-600 mx-auto mb-4" />
              <p className="text-gray-400">暫無可用任務</p>
            </div>
          ) : (
            filteredTasks.map((task) => (
              <TaskCard
                key={task.task_type}
                task={task}
                onClaim={() => claimMutation.mutate(task.task_type)}
                isClaiming={claimMutation.isPending}
              />
            ))
          )}
        </div>
      </div>
    </PageTransition>
  )
}

function TaskCard({
  task,
  onClaim,
  isClaiming,
}: {
  task: TaskStatus
  onClaim: () => void
  isClaiming: boolean
}) {
  const progressPercent = Math.min((task.progress.current / task.progress.target) * 100, 100)
  const category = task.category || 'daily'
  const config = categoryConfig[category as keyof typeof categoryConfig] || categoryConfig.daily
  const icon = task.icon || config.icon

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className={`bg-brand-darker rounded-xl p-4 border ${
        task.completed
          ? 'border-green-500/30 bg-green-500/5'
          : 'border-white/5 hover:border-white/10'
      } transition-colors`}
    >
      <div className="flex items-start gap-4">
        {/* 圖標 */}
        <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${config.color} flex items-center justify-center text-2xl shrink-0`}>
          {icon}
        </div>

        {/* 任務信息 */}
        <div className="flex-1 min-w-0">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-white font-semibold">{task.task_name}</h3>
            {task.completed && (
              <CheckCircle size={18} className="text-green-400" />
            )}
          </div>
          <p className="text-gray-400 text-sm mb-3">{task.task_description}</p>

          {/* 進度條 */}
          <div className="mb-3">
            <div className="flex items-center justify-between text-xs mb-1">
              <span className="text-gray-400">進度</span>
              <span className="text-white font-medium">
                {task.progress.current} / {task.progress.target}
              </span>
            </div>
            <div className="w-full h-2 bg-gray-700 rounded-full overflow-hidden">
              <motion.div
                className={`h-full rounded-full bg-gradient-to-r ${config.color}`}
                initial={{ width: 0 }}
                animate={{ width: `${progressPercent}%` }}
                transition={{ duration: 0.5 }}
              />
            </div>
          </div>

          {/* 獎勵 */}
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Gift size={16} className="text-orange-400" />
              <span className="text-orange-400 font-semibold">
                +{task.reward_amount} {task.reward_currency.toUpperCase()}
              </span>
            </div>

            {/* 操作按鈕 */}
            {task.can_claim ? (
              <button
                onClick={onClaim}
                disabled={isClaiming}
                className={`px-4 py-2 rounded-lg text-sm font-semibold bg-gradient-to-r ${config.color} text-white hover:opacity-90 transition-opacity disabled:opacity-50`}
              >
                {isClaiming ? '領取中...' : '領取'}
              </button>
            ) : task.completed ? (
              <span className="px-4 py-2 rounded-lg text-sm font-semibold bg-gray-700 text-gray-400">
                已領取
              </span>
            ) : (
              <button
                onClick={() => {
                  // 根據任務類型導航到對應頁面
                  if (task.task_type.includes('claim')) {
                    window.location.href = '/packets'
                  } else if (task.task_type.includes('send')) {
                    window.location.href = '/send'
                  } else if (task.task_type.includes('invite')) {
                    window.location.href = '/earn?tab=invite'
                  } else if (task.task_type.includes('wheel')) {
                    window.location.href = '/lucky-wheel'
                  }
                }}
                className="px-4 py-2 rounded-lg text-sm font-semibold bg-white/10 text-white hover:bg-white/20 transition-colors"
              >
                去完成
              </button>
            )}
          </div>
        </div>
      </div>
    </motion.div>
  )
}
