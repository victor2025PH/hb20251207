import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useMutation, useQuery } from '@tanstack/react-query'
import { motion, AnimatePresence } from 'framer-motion'
import confetti from 'canvas-confetti'
import { useSound } from '../hooks/useSound'
import { useAuth } from '../utils/auth/useAuth'
import { claimRedPacket, getRedPacket, type RedPacket } from '../utils/api'
import { showAlert } from '../utils/telegram'
import { isInTelegram } from '../utils/platform'
import { useTranslation } from '../providers/I18nProvider'
import ResultModal from '../components/ResultModal'
import Loading from '../components/Loading'

export default function ClaimRedPacketPage() {
  const { uuid } = useParams<{ uuid: string }>()
  const navigate = useNavigate()
  const { t } = useTranslation()
  const { playSound } = useSound()
  const { isAuthenticated, loading: authLoading } = useAuth()
  const [showResultModal, setShowResultModal] = useState(false)
  const [claimAmount, setClaimAmount] = useState(0)
  const [claimMessage, setClaimMessage] = useState('')
  const [packetInfo, setPacketInfo] = useState<RedPacket | null>(null)
  const [showAuthPrompt, setShowAuthPrompt] = useState(false)

  // 获取红包信息
  const { data: packet, isLoading: isLoadingPacket, isError, error } = useQuery<RedPacket>({
    queryKey: ['redpacket', uuid],
    queryFn: () => getRedPacket(uuid!),
    enabled: !!uuid,
    retry: 1,
  })

  // 使用 useEffect 替代 onError
  useEffect(() => {
    if (isError && error) {
      const errorMessage = (error as any).response?.data?.detail || (error as Error).message || t('packet_not_found')
      showAlert(errorMessage, 'error', t('error'))
      setTimeout(() => {
        navigate('/packets')
      }, 2000)
    }
  }, [isError, error, navigate])

  // 抢红包 mutation
  const claimMutation = useMutation({
    mutationFn: (packetId: string) => claimRedPacket(packetId),
    onSuccess: (result) => {
      // 檢查領取是否成功
      if (!result.success) {
        playSound('click')
        showAlert(result.message || t('claim_failed'), 'error')
        return
      }
      
      // 檢查金額是否有效
      if (!result.amount || result.amount <= 0) {
        console.error('[claimRedPacket] Invalid amount:', result)
        playSound('click')
        showAlert(t('claim_failed_invalid_amount'), 'error')
        return
      }
      
      // 顯示結果
      setClaimAmount(result.amount)
      setClaimMessage(result.message || t('claim_success', { amount: result.amount, currency: packet?.currency || 'USDT' }))
      setPacketInfo(packet || null)
      setShowResultModal(true)
      
      // 成功動畫
      playSound('success')
      triggerSuccessConfetti()
    },
    onError: (error: any) => {
      playSound('click')
      const errorMessage = error.response?.data?.detail || error.message || t('claim_failed')
      showAlert(errorMessage, 'error')
    }
  })

  const triggerSuccessConfetti = () => {
    const end = Date.now() + 1000
    const colors = ['#bb0000', '#ffffff', '#fb923c', '#fbbf24']
    const frame = () => {
      confetti({
        particleCount: 10,
        angle: 60,
        spread: 55,
        origin: { x: 0 },
        colors: colors,
        zIndex: 1000,
      })
      confetti({
        particleCount: 10,
        angle: 120,
        spread: 55,
        origin: { x: 1 },
        colors: colors,
        zIndex: 1000,
      })
      confetti({
        particleCount: 15,
        angle: 90,
        spread: 70,
        origin: { x: 0.5, y: 0 },
        colors: colors,
        zIndex: 1000,
      })
      if (Date.now() < end) {
        requestAnimationFrame(frame)
      }
    }
    frame()
  }

  // 检查认证状态
  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      // 如果未认证，显示提示
      setShowAuthPrompt(true)
    }
  }, [authLoading, isAuthenticated])

  // 自动抢红包（仅在已认证时）
  useEffect(() => {
    if (uuid && packet && isAuthenticated && !claimMutation.isPending && !showResultModal && !showAuthPrompt) {
      // 延迟一下再抢，让用户看到页面
      const timer = setTimeout(() => {
        claimMutation.mutate(uuid)
      }, 500)
      return () => clearTimeout(timer)
    }
  }, [uuid, packet, isAuthenticated, claimMutation, showResultModal, showAuthPrompt])

  if (authLoading || isLoadingPacket || claimMutation.isPending) {
    return (
      <div className="fixed inset-0 bg-brand-dark flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-orange-500 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
          <p className="text-gray-400">{t('claiming')}</p>
        </div>
      </div>
    )
  }

  // 未认证提示
  if (showAuthPrompt && !isAuthenticated) {
    const isTelegram = isInTelegram()
    return (
      <div className="fixed inset-0 bg-brand-dark flex items-center justify-center p-6">
        <motion.div
          initial={{ scale: 0.9, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          className="bg-[#1C1C1E] border border-orange-500/30 rounded-3xl p-6 max-w-md w-full text-center"
        >
          <div className="text-6xl mb-4">🔐</div>
          <h2 className="text-2xl font-bold text-white mb-4">{t('need_login')}</h2>
          <p className="text-gray-400 mb-6">
            {isTelegram 
              ? t('please_login_telegram')
              : t('please_login_miniapp')}
          </p>
          <div className="flex flex-col gap-3">
            {!isTelegram && (
              <button
                onClick={() => navigate('/')}
                className="w-full py-3 bg-gradient-to-r from-orange-600 to-red-600 text-white rounded-xl font-bold"
              >
                {t('go_to_login')}
              </button>
            )}
            <button
              onClick={() => navigate('/packets')}
              className="w-full py-3 bg-[#2C2C2E] text-gray-300 rounded-xl font-bold"
            >
              {t('return_to_packets')}
            </button>
          </div>
        </motion.div>
      </div>
    )
  }

  if (!packet) {
    return (
      <div className="fixed inset-0 bg-brand-dark flex items-center justify-center p-6">
        <div className="text-center">
          <p className="text-red-400 mb-4">{t('packet_expired')}</p>
          <button
            onClick={() => navigate('/packets')}
            className="px-4 py-2 bg-orange-500 text-white rounded-lg"
          >
            返回紅包列表
          </button>
        </div>
      </div>
    )
  }

  return (
    <>
      <div className="fixed inset-0 bg-brand-dark flex items-center justify-center p-6">
        <div className="text-center">
          <motion.div
            initial={{ scale: 0.8, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            className="mb-6"
          >
            <div className="text-6xl mb-4">🧧</div>
            <h2 className="text-2xl font-bold text-white mb-2">{t('grab_red_packet')}</h2>
            <p className="text-gray-400">{packet?.message || t('default_blessing')}</p>
          </motion.div>
        </div>
      </div>

      {/* 搶紅包成功彈窗 */}
      {showResultModal && packetInfo && (
        <ResultModal
          isOpen={showResultModal}
          onClose={() => {
            setShowResultModal(false)
            setTimeout(() => {
              navigate('/packets')
            }, 300)
          }}
          amount={claimAmount}
          currency={packetInfo.currency?.toUpperCase() || 'USDT'}
          senderName={packetInfo.sender_name || t('anonymous_user')}
          senderLevel={Math.floor(Math.random() * 50) + 1}
          message={packetInfo.message || t('default_blessing')}
          senderAvatar={`https://api.dicebear.com/7.x/avataaars/svg?seed=${packetInfo.sender_id}`}
        />
      )}
    </>
  )
}

