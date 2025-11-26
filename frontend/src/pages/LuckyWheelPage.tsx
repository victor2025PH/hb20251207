import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Gift, Zap, Sparkles, Trophy, Star, Coins } from 'lucide-react'
import { useTranslation } from '../providers/I18nProvider'
import { useSound } from '../hooks/useSound'
import PageTransition from '../components/PageTransition'
import confetti from 'canvas-confetti'

interface Prize {
  id: number
  name: string
  icon: React.ElementType
  color: string
  probability: number // 概率权重
}

const prizes: Prize[] = [
  { id: 1, name: '10 USDT', icon: Coins, color: 'text-green-400', probability: 5 },
  { id: 2, name: '5 USDT', icon: Coins, color: 'text-green-400', probability: 10 },
  { id: 3, name: '50 能量', icon: Zap, color: 'text-yellow-400', probability: 15 },
  { id: 4, name: '20 能量', icon: Zap, color: 'text-yellow-400', probability: 20 },
  { id: 5, name: '100 积分', icon: Star, color: 'text-purple-400', probability: 20 },
  { id: 6, name: '50 积分', icon: Star, color: 'text-purple-400', probability: 30 },
]

export default function LuckyWheelPage() {
  const { t } = useTranslation()
  const { playSound } = useSound()
  const [isSpinning, setIsSpinning] = useState(false)
  const [selectedPrize, setSelectedPrize] = useState<Prize | null>(null)
  const [rotation, setRotation] = useState(0)
  const [spinsLeft, setSpinsLeft] = useState(3) // 每日免费次数

  // 计算每个奖品的角度
  const prizeAngle = 360 / prizes.length

  // 抽奖逻辑
  const spinWheel = () => {
    if (isSpinning || spinsLeft <= 0) return

    playSound('grab')
    setIsSpinning(true)

    // 根据概率选择奖品
    const totalWeight = prizes.reduce((sum, p) => sum + p.probability, 0)
    let random = Math.random() * totalWeight
    let selected: Prize | null = null

    for (const prize of prizes) {
      random -= prize.probability
      if (random <= 0) {
        selected = prize
        break
      }
    }

    if (!selected) selected = prizes[prizes.length - 1]

    // 计算旋转角度（多转几圈 + 目标角度）
    const targetIndex = prizes.findIndex(p => p.id === selected!.id)
    const targetAngle = targetIndex * prizeAngle
    const spins = 5 * 360 // 转5圈
    const finalRotation = rotation + spins + (360 - targetAngle)

    setRotation(finalRotation)

    // 动画结束后显示结果
    setTimeout(() => {
      setSelectedPrize(selected)
      setIsSpinning(false)
      setSpinsLeft(prev => prev - 1)
      playSound('success')

      // 喷花特效
      const end = Date.now() + 1000
      const colors = ['#fbbf24', '#f472b6', '#8b5cf6', '#10b981']
      const frame = () => {
        confetti({
          particleCount: 5,
          angle: 60,
          spread: 55,
          origin: { x: 0 },
          colors: colors,
          zIndex: 1000,
        })
        confetti({
          particleCount: 5,
          angle: 120,
          spread: 55,
          origin: { x: 1 },
          colors: colors,
          zIndex: 1000,
        })
        if (Date.now() < end) {
          requestAnimationFrame(frame)
        }
      }
      frame()
    }, 3000)
  }

  return (
    <PageTransition>
      <div className="h-full flex flex-col p-4 pb-24 gap-4 overflow-y-auto scrollbar-hide">
        <h1 className="text-xl font-bold text-white flex items-center gap-2">
          <Trophy size={24} className="text-yellow-400" />
          幸运转盘
        </h1>

        {/* 转盘容器 */}
        <div className="flex-1 flex items-center justify-center min-h-[400px]">
          <div className="relative w-80 h-80">
            {/* 转盘背景 */}
            <motion.div
              className="w-full h-full rounded-full border-4 border-purple-500/30 relative overflow-hidden bg-gradient-to-br from-purple-900/20 to-pink-900/20"
              animate={{ rotate: rotation }}
              transition={{ 
                duration: isSpinning ? 3 : 0,
                ease: "easeOut"
              }}
            >
              {/* 奖品扇形 */}
              {prizes.map((prize, index) => {
                const Icon = prize.icon
                const angle = index * prizeAngle
                const isHighlight = selectedPrize?.id === prize.id

                return (
                  <div
                    key={prize.id}
                    className="absolute inset-0"
                    style={{
                      transform: `rotate(${angle}deg)`,
                      transformOrigin: 'center',
                    }}
                  >
                    <div
                      className="absolute top-0 left-1/2 w-1/2 h-1/2 origin-bottom"
                      style={{
                        clipPath: `polygon(0 0, 100% 0, 50% 100%)`,
                        background: `linear-gradient(135deg, ${
                          index % 2 === 0 ? 'rgba(139,92,246,0.3)' : 'rgba(236,72,153,0.3)'
                        }, ${
                          index % 2 === 0 ? 'rgba(168,85,247,0.2)' : 'rgba(244,114,182,0.2)'
                        })`,
                        border: isHighlight ? '2px solid yellow' : 'none',
                      }}
                    />
                    {/* 奖品文字 */}
                    <div
                      className="absolute top-8 left-1/2 transform -translate-x-1/2"
                      style={{
                        transform: `translateX(-50%) rotate(${prizeAngle / 2}deg)`,
                        transformOrigin: 'center',
                      }}
                    >
                      <Icon size={20} className={prize.color} />
                      <div className={`text-[10px] font-bold ${prize.color} mt-1 whitespace-nowrap`}>
                        {prize.name}
                      </div>
                    </div>
                  </div>
                )
              })}

              {/* 中心圆 */}
              <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-20 h-20 bg-gradient-to-br from-purple-600 to-pink-600 rounded-full border-4 border-white/20 flex items-center justify-center shadow-lg z-10">
                <Gift size={32} className="text-white" />
              </div>
            </motion.div>

            {/* 指针 */}
            <div className="absolute top-0 left-1/2 -translate-x-1/2 -translate-y-2 z-20">
              <div className="w-0 h-0 border-l-[15px] border-r-[15px] border-t-[30px] border-l-transparent border-r-transparent border-t-yellow-400 drop-shadow-lg" />
            </div>
          </div>
        </div>

        {/* 剩余次数 */}
        <div className="bg-purple-500/10 border border-purple-500/20 rounded-xl p-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Sparkles size={20} className="text-purple-400" />
            <span className="text-sm text-gray-300">今日剩余次数</span>
          </div>
          <span className="text-2xl font-bold text-purple-400">{spinsLeft}</span>
        </div>

        {/* 抽奖按钮 */}
        <motion.button
          onClick={spinWheel}
          disabled={isSpinning || spinsLeft <= 0}
          className={`w-full py-4 rounded-xl font-bold text-lg shadow-lg transition-all flex items-center justify-center gap-2 ${
            isSpinning || spinsLeft <= 0
              ? 'bg-gray-600 text-gray-400 cursor-not-allowed'
              : 'bg-gradient-to-r from-purple-600 to-pink-600 text-white active:scale-[0.98]'
          }`}
          whileHover={!isSpinning && spinsLeft > 0 ? { scale: 1.02 } : {}}
          whileTap={!isSpinning && spinsLeft > 0 ? { scale: 0.98 } : {}}
        >
          {isSpinning ? (
            <>
              <motion.div
                animate={{ rotate: 360 }}
                transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full"
              />
              转盘中...
            </>
          ) : spinsLeft <= 0 ? (
            '今日次数已用完'
          ) : (
            <>
              <Trophy size={20} />
              开始抽奖
            </>
          )}
        </motion.button>

        {/* 结果弹窗 */}
        <AnimatePresence>
          {selectedPrize && (
            <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="absolute inset-0 bg-black/80 backdrop-blur-sm"
                onClick={() => setSelectedPrize(null)}
              />
              <motion.div
                initial={{ scale: 0.5, opacity: 0, y: 50 }}
                animate={{ scale: 1, opacity: 1, y: 0 }}
                exit={{ scale: 0.5, opacity: 0, y: 50 }}
                className="relative bg-[#1C1C1E] border border-purple-500/30 rounded-3xl p-8 text-center shadow-2xl max-w-sm w-full"
              >
                <motion.div
                  animate={{ rotate: [0, 360] }}
                  transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
                  className="w-20 h-20 mx-auto mb-4 bg-gradient-to-br from-purple-600 to-pink-600 rounded-full flex items-center justify-center"
                >
                  {selectedPrize && <selectedPrize.icon size={40} className={selectedPrize.color} />}
                </motion.div>
                <h2 className="text-2xl font-bold text-white mb-2">恭喜获得！</h2>
                <p className={`text-3xl font-black ${selectedPrize.color} mb-6`}>
                  {selectedPrize.name}
                </p>
                <motion.button
                  onClick={() => setSelectedPrize(null)}
                  className="w-full py-3 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-xl font-bold"
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                >
                  太棒了！
                </motion.button>
              </motion.div>
            </div>
          )}
        </AnimatePresence>
      </div>
    </PageTransition>
  )
}

