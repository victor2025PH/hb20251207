import { useState, useEffect, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Gift, Zap, Sparkles, Trophy, TrendingUp, ArrowLeft, Star, Coins, DollarSign, Circle } from 'lucide-react'
import { useTranslation } from '../providers/I18nProvider'
import { useSound } from '../hooks/useSound'
import { useNavigate } from 'react-router-dom'
import PageTransition from '../components/PageTransition'
import TelegramStar from '../components/TelegramStar'
import confetti from 'canvas-confetti'

interface Prize {
  id: number
  name: string
  value: number
  icon: React.ElementType
  color: string
  bgGradient: string
  probability: number
}

const prizes: Prize[] = [
  { id: 1, name: 'Energy', value: 100, icon: Zap, color: 'text-yellow-400', bgGradient: 'from-yellow-500/40 to-orange-500/40', probability: 10 },
  { id: 2, name: 'Energy', value: 50, icon: Zap, color: 'text-yellow-400', bgGradient: 'from-yellow-500/40 to-orange-500/40', probability: 20 },
  { id: 3, name: 'Energy', value: 30, icon: Zap, color: 'text-yellow-400', bgGradient: 'from-yellow-500/40 to-orange-500/40', probability: 25 },
  { id: 4, name: 'Fortune', value: 20, icon: Sparkles, color: 'text-purple-400', bgGradient: 'from-purple-500/40 to-pink-500/40', probability: 15 },
  { id: 5, name: 'Fortune', value: 10, icon: Sparkles, color: 'text-purple-400', bgGradient: 'from-purple-500/40 to-pink-500/40', probability: 20 },
  { id: 6, name: 'XP', value: 50, icon: TrendingUp, color: 'text-cyan-400', bgGradient: 'from-cyan-500/40 to-blue-500/40', probability: 10 },
]

interface CoinSymbol {
  id: string
  x: number
  y: number
  icon: React.ElementType
  size: number
  rotation: number
  isFlying: boolean
  vx: number
  vy: number
  life: number
  maxLife: number
}

export default function LuckyWheelPage() {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const { playSound } = useSound()
  const [isHolding, setIsHolding] = useState(false)
  const [holdProgress, setHoldProgress] = useState(0)
  const [isExploding, setIsExploding] = useState(false)
  const [selectedPrize, setSelectedPrize] = useState<Prize | null>(null)
  const [spinsLeft, setSpinsLeft] = useState(3)
  const [coins, setCoins] = useState<CoinSymbol[]>([])
  const [showNoChancesModal, setShowNoChancesModal] = useState(false)
  const holdTimerRef = useRef<number | null>(null)
  const progressTimerRef = useRef<number | null>(null)
  const coinIntervalRef = useRef<number | null>(null)
  const redPacketRef = useRef<HTMLDivElement>(null)
  const HOLD_DURATION = 2000

  const coinIcons = [Coins, DollarSign, Star, Sparkles, Circle, Trophy]

  const restoreRedPacket = () => {
    if (!redPacketRef.current) return

    const initialCoins: CoinSymbol[] = []
    const addCoin = (idPrefix: string, yMin: number, yMax: number, count: number, minSize: number, maxSize: number) => {
      for (let i = 0; i < count; i++) {
        const yPercent = yMin + Math.random() * (yMax - yMin)
        const xPercent = Math.random()
        initialCoins.push({
          id: `${idPrefix}-${i}-${Date.now()}`,
          x: xPercent * 100,
          y: yPercent * 100,
          icon: coinIcons[Math.floor(Math.random() * coinIcons.length)],
          size: minSize + Math.random() * (maxSize - minSize),
          rotation: Math.random() * 360,
          isFlying: false,
          vx: 0,
          vy: 0,
          life: 0,
          maxLife: 100 + Math.random() * 50,
        })
      }
    }

    addCoin('coin-bottom', 0.6, 1.0, 40, 10, 18)
    addCoin('coin-middle', 0.3, 0.6, 20, 8, 14)
    addCoin('coin-top', 0.0, 0.3, 10, 6, 12)

    setCoins(initialCoins)
  }

  useEffect(() => {
    restoreRedPacket()
  }, [])

  const drawPrize = () => {
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
    return selected
  }

  const handleStart = () => {
    if (spinsLeft <= 0) {
      setShowNoChancesModal(true)
      return
    }
    if (isExploding) return

    setIsHolding(true)
    setHoldProgress(0)
    playSound('click')

    setCoins(prev => prev.map(coin => ({
      ...coin,
      isFlying: true,
      vx: (Math.random() - 0.5) * 2,
      vy: -3 - Math.random() * 3,
      life: 0,
    })))

    const startTime = Date.now()
    progressTimerRef.current = window.setInterval(() => {
      const elapsed = Date.now() - startTime
      const progress = Math.min(100, (elapsed / HOLD_DURATION) * 100)
      setHoldProgress(progress)

      if (progress >= 100) {
        handleComplete()
      }
    }, 16)
  }

  const handleEnd = () => {
    setIsHolding(false)
    if (holdTimerRef.current) {
      window.clearTimeout(holdTimerRef.current)
      holdTimerRef.current = null
    }
    if (progressTimerRef.current) {
      window.clearInterval(progressTimerRef.current)
      progressTimerRef.current = null
    }
    if (coinIntervalRef.current) {
      window.clearInterval(coinIntervalRef.current)
      coinIntervalRef.current = null
    }
    setHoldProgress(0)
  }

  const handleComplete = () => {
    if (isExploding) return

    setIsHolding(false)
    setIsExploding(true)
    playSound('success')

    if (progressTimerRef.current) {
      window.clearInterval(progressTimerRef.current)
      progressTimerRef.current = null
    }

    if (redPacketRef.current) {
      const rect = redPacketRef.current.getBoundingClientRect()
      const centerX = rect.left + rect.width / 2
      const centerY = rect.top + rect.height / 2

      const explosionCoins: CoinSymbol[] = []
      for (let i = 0; i < 50; i++) {
        const angle = (Math.PI * 2 * i) / 50 + Math.random() * 0.5
        const speed = 4 + Math.random() * 4
        explosionCoins.push({
          id: `explosion-${Date.now()}-${i}`,
          x: centerX,
          y: centerY,
          icon: coinIcons[Math.floor(Math.random() * coinIcons.length)],
          size: 10 + Math.random() * 12,
          rotation: Math.random() * 360,
          isFlying: true,
          vx: Math.cos(angle) * speed,
          vy: Math.sin(angle) * speed,
          life: 0,
          maxLife: 80 + Math.random() * 40,
        })
      }
      setCoins(prev => [...prev, ...explosionCoins])
    }

    const end = Date.now() + 2000
    const colors = ['#fbbf24', '#f472b6', '#8b5cf6', '#10b981', '#3b82f6', '#ec4899', '#a855f7', '#06b6d4']
    const frame = () => {
      for (let i = 0; i < 8; i++) {
        confetti({
          particleCount: 15,
          angle: i * 45,
          spread: 70,
          origin: { x: 0.5, y: 0.5 },
          colors: colors,
          zIndex: 1000,
          gravity: 0.8,
          drift: (Math.random() - 0.5) * 0.5,
        })
      }
      if (Date.now() < end) {
        requestAnimationFrame(frame)
      }
    }
    frame()

    setTimeout(() => {
      const prize = drawPrize()
      setSelectedPrize(prize)
      setSpinsLeft(prev => prev - 1)
      setIsExploding(false)
    }, 1500)
  }

  useEffect(() => {
    if (coins.length === 0) return

    const animate = () => {
      setCoins(prev => {
        const updated = prev
          .map(coin => {
            if (!coin.isFlying) return coin

            return {
              ...coin,
              x: coin.x + coin.vx,
              y: coin.y + coin.vy,
              rotation: coin.rotation + 5,
              life: coin.life + 1,
              vy: coin.vy + 0.1,
            }
          })
          .filter(coin => {
            if (!coin.isFlying) return true
            return coin.life < coin.maxLife && coin.y > -100 && coin.y < window.innerHeight + 100
          })

        if (updated.some(c => c.isFlying)) {
          requestAnimationFrame(animate)
        }
        return updated
      })
    }

    requestAnimationFrame(animate)
  }, [coins.length])

  return (
    <PageTransition>
      <div className="h-full flex flex-col overflow-hidden">
        {/* 顶部标题栏 */}
        <div className="flex items-center justify-between px-4 py-3 shrink-0 border-b border-white/5">
          <button
            onClick={() => navigate(-1)}
            className="w-10 h-10 rounded-xl bg-white/5 flex items-center justify-center hover:bg-white/10 transition-colors"
          >
            <ArrowLeft size={20} className="text-white" />
          </button>
          <h1 className="text-lg font-bold text-white flex items-center gap-2">
            <Trophy size={20} className="text-yellow-400" />
            {t('lucky_red')}
          </h1>
          <div className="w-10" />
        </div>


        {/* 主要内容区域 */}
        <div className="flex-1 flex flex-col items-center justify-start gap-4 p-4 min-h-0 pt-8 relative">
          {/* 大红包 */}
          <div
            ref={redPacketRef}
            className="relative shrink-0 w-72 h-96"
            onMouseDown={handleStart}
            onMouseUp={handleEnd}
            onMouseLeave={handleEnd}
            onTouchStart={handleStart}
            onTouchEnd={handleEnd}
            onTouchCancel={handleEnd}
          >
            {/* 虚拟币符号层 */}
            <div className="absolute inset-0 pointer-events-none z-10 overflow-hidden">
              {coins.filter(coin => !coin.isFlying).map(coin => {
                const Icon = coin.icon
                return (
                  <motion.div
                    key={coin.id}
                    className="absolute"
                    style={{
                      left: `${coin.x}%`,
                      top: `${coin.y}%`,
                      transform: `translate(-50%, -50%) rotate(${coin.rotation}deg)`,
                    }}
                    animate={isHolding ? {
                      scale: [1, 1.3, 1],
                      opacity: [0.8, 1, 0.8],
                    } : {
                      opacity: [0.8, 1, 0.8],
                    }}
                    transition={{
                      duration: 0.5,
                      repeat: Infinity,
                      ease: "easeInOut",
                    }}
                  >
                    <Icon
                      size={coin.size}
                      className="text-yellow-400"
                      style={{
                        filter: isHolding
                          ? 'drop-shadow(0 0 8px #fbbf24) drop-shadow(0 0 16px #fbbf24)'
                          : 'drop-shadow(0 0 4px rgba(251, 191, 36, 0.5)) drop-shadow(0 0 8px rgba(251, 191, 36, 0.3))',
                      }}
                    />
                  </motion.div>
                )
              })}
            </div>

            {/* 红包主体 */}
            <motion.div
              className="relative w-72 h-96 rounded-3xl shadow-2xl overflow-visible"
              style={{
                background: 'linear-gradient(180deg, #dc2626 0%, #b91c1c 50%, #991b1b 100%)',
                boxShadow: isHolding
                  ? '0 0 80px rgba(220, 38, 38, 0.9), 0 0 120px rgba(220, 38, 38, 0.7), inset 0 0 60px rgba(255, 255, 255, 0.2)'
                  : isExploding
                  ? '0 0 120px rgba(220, 38, 38, 1), 0 0 180px rgba(220, 38, 38, 0.8)'
                  : '0 0 40px rgba(220, 38, 38, 0.6), inset 0 0 30px rgba(255, 255, 255, 0.1)',
              }}
              animate={isHolding ? {
                x: [0, -4, 4, -4, 4, -2, 2, 0],
                y: [0, -2, 2, -2, 2, -1, 1, 0],
                rotate: [0, -1, 1, -1, 1, -0.5, 0.5, 0],
                scale: [1, 1.03, 1, 1.03, 1],
              } : isExploding ? {
                scale: [1, 1.3, 0.9, 1],
                rotate: [0, 8, -8, 0],
              } : {
                scale: 1,
                rotate: 0,
                x: 0,
                y: 0,
              }}
              transition={{
                duration: isHolding ? 0.25 : isExploding ? 0.5 : 0.2,
                repeat: isHolding ? Infinity : 0,
                ease: "easeInOut",
              }}
            >
              <div className="absolute inset-0 overflow-hidden rounded-3xl">
                {/* 光泽效果 */}
                <div
                  className="absolute inset-0"
                  style={{
                    background: 'linear-gradient(135deg, rgba(255, 255, 255, 0.25) 0%, transparent 40%, rgba(0, 0, 0, 0.15) 100%)',
                    mixBlendMode: 'overlay',
                  }}
                />

                {/* 高光反射 */}
                <motion.div
                  className="absolute top-0 left-0 w-full h-1/3"
                  style={{
                    background: 'linear-gradient(180deg, rgba(255, 255, 255, 0.35) 0%, transparent 100%)',
                  }}
                  animate={isHolding ? {
                    opacity: [0.35, 0.6, 0.35],
                  } : {}}
                  transition={{
                    duration: 0.5,
                    repeat: isHolding ? Infinity : 0,
                    ease: "easeInOut",
                  }}
                />

                {/* 红包纹理 */}
                <div
                  className="absolute inset-0 opacity-10"
                  style={{
                    backgroundImage: `
                      repeating-linear-gradient(45deg, transparent, transparent 10px, rgba(0,0,0,0.05) 10px, rgba(0,0,0,0.05) 20px),
                      repeating-linear-gradient(-45deg, transparent, transparent 10px, rgba(0,0,0,0.05) 10px, rgba(0,0,0,0.05) 20px)
                    `,
                  }}
                />

                {/* 金色横带 */}
                <div className="absolute bottom-32 left-0 right-0 h-12 bg-gradient-to-b from-amber-300 via-amber-400 to-amber-500 border-y-2 border-amber-600/30 shadow-inner">
                  <div className="absolute inset-0 bg-gradient-to-b from-transparent via-white/20 to-transparent" />
                </div>

                {/* 进度条 */}
                {isHolding && (
                  <div className="absolute bottom-8 left-8 right-8 h-2 bg-white/20 rounded-full overflow-hidden z-30">
                    <motion.div
                      className="h-full bg-gradient-to-r from-yellow-400 via-orange-400 to-red-500 rounded-full"
                      initial={{ width: 0 }}
                      animate={{ width: `${holdProgress}%` }}
                      transition={{ duration: 0.1 }}
                    />
                  </div>
                )}

                {/* 爆炸光效 */}
                {isExploding && (
                  <motion.div
                    className="absolute inset-0 rounded-full"
                    style={{
                      background: 'radial-gradient(circle, rgba(255, 215, 0, 0.9) 0%, rgba(220, 38, 38, 0.7) 30%, transparent 70%)',
                    }}
                    initial={{ scale: 0, opacity: 1 }}
                    animate={{ scale: 3, opacity: 0 }}
                    transition={{ duration: 0.8, ease: "easeOut" }}
                  />
                )}
              </div>
            </motion.div>
            
          {/* 盾牌形状底座 + 大星星 */}
          <div 
            className="absolute w-28 h-28 z-30 pointer-events-none"
            style={{
              top: '10%',
              left: '50%',
              transform: 'translateX(-50%)',
            }}
          >
              <motion.div
                className="w-full h-full flex items-center justify-center"
                animate={isHolding ? {
                  scale: [1, 1.15, 1],
                } : {
                  scale: 1,
                }}
                transition={{
                  duration: 0.5,
                  repeat: isHolding ? Infinity : 0,
                  ease: "easeInOut",
                }}
                style={{
                  transformOrigin: 'center center',
                }}
              >
                <div className="relative w-full h-full flex items-center justify-center">
                  {/* 盾牌 3D 立体底座 - 多层叠加实现立体感 */}
                  
                  {/* 最底层阴影 - 给出深度感 */}
                  <div
                    className="absolute"
                    style={{
                      width: '90%',
                      height: '90%',
                      top: '12%',
                      left: '5%',
                      clipPath: 'polygon(50% 0%, 100% 18%, 100% 62%, 50% 100%, 0% 62%, 0% 18%)',
                      background: 'rgba(0, 0, 0, 0.5)',
                      filter: 'blur(8px)',
                    }}
                  />
                  
                  {/* 盾牌底层 - 深色边缘 */}
                  <div
                    className="absolute"
                    style={{
                      width: '88%',
                      height: '88%',
                      top: '6%',
                      left: '6%',
                      clipPath: 'polygon(50% 0%, 100% 18%, 100% 62%, 50% 100%, 0% 62%, 0% 18%)',
                      background: 'linear-gradient(180deg, #92400e 0%, #78350f 50%, #451a03 100%)',
                    }}
                  />
                  
                  {/* 盾牌主体 - 金色渐变 */}
                  <div
                    className="absolute"
                    style={{
                      width: '80%',
                      height: '80%',
                      top: '8%',
                      left: '10%',
                      clipPath: 'polygon(50% 0%, 100% 18%, 100% 62%, 50% 100%, 0% 62%, 0% 18%)',
                      background: 'linear-gradient(160deg, #fcd34d 0%, #fbbf24 20%, #f59e0b 50%, #d97706 80%, #b45309 100%)',
                      filter: isHolding 
                        ? 'drop-shadow(0 0 16px #fbbf24) drop-shadow(0 0 32px #f59e0b)'
                        : 'drop-shadow(0 0 8px rgba(251, 191, 36, 0.6))',
                    }}
                  />
                  
                  {/* 盾牌内凹效果 - 深色中心 */}
                  <div
                    className="absolute"
                    style={{
                      width: '60%',
                      height: '60%',
                      top: '18%',
                      left: '20%',
                      clipPath: 'polygon(50% 5%, 95% 20%, 95% 60%, 50% 95%, 5% 60%, 5% 20%)',
                      background: 'linear-gradient(180deg, #b45309 0%, #92400e 50%, #78350f 100%)',
                    }}
                  />
                  
                  {/* 顶部高光 - 凸起光泽 */}
                  <div
                    className="absolute"
                    style={{
                      width: '50%',
                      height: '20%',
                      top: '10%',
                      left: '15%',
                      background: 'linear-gradient(180deg, rgba(255,255,255,0.6) 0%, rgba(255,255,255,0.2) 50%, transparent 100%)',
                      borderRadius: '50%',
                      filter: 'blur(1px)',
                    }}
                  />
                  
                  {/* 左侧边缘高光 */}
                  <div
                    className="absolute"
                    style={{
                      width: '10%',
                      height: '40%',
                      top: '15%',
                      left: '12%',
                      background: 'linear-gradient(90deg, rgba(255,255,255,0.4) 0%, transparent 100%)',
                      borderRadius: '50%',
                      filter: 'blur(2px)',
                      transform: 'rotate(-15deg)',
                    }}
                  />

                  {/* 大星星图标 - 和右上角一模一样的 TelegramStar */}
                  <div className="absolute inset-0 flex items-center justify-center z-10">
                    <motion.div
                      animate={isHolding ? {
                        rotate: [0, 8, -8, 0],
                        scale: [1, 1.08, 1],
                      } : {
                        scale: [1, 1.03, 1],
                      }}
                      transition={{
                        duration: isHolding ? 0.3 : 2,
                        repeat: Infinity,
                        ease: "easeInOut",
                      }}
                      style={{
                        filter: isHolding 
                          ? 'drop-shadow(0 0 16px #ffd700) drop-shadow(0 0 32px #fbbf24)'
                          : 'drop-shadow(0 0 8px rgba(255, 215, 0, 0.8))',
                      }}
                    >
                      <TelegramStar 
                        size={56} 
                        withSpray={isHolding}
                      />
                    </motion.div>
                  </div>
                  
                  {/* 按下时的脉冲发光 */}
                  {isHolding && (
                    <motion.div
                      className="absolute"
                      style={{
                        width: '100%',
                        height: '100%',
                        clipPath: 'polygon(50% 0%, 100% 18%, 100% 62%, 50% 100%, 0% 62%, 0% 18%)',
                        background: 'radial-gradient(circle, rgba(255,215,0,0.5) 0%, transparent 60%)',
                      }}
                      animate={{
                        opacity: [0.2, 0.6, 0.2],
                        scale: [1, 1.05, 1],
                      }}
                      transition={{
                        duration: 0.4,
                        repeat: Infinity,
                      }}
                    />
                  )}
                </div>
              </motion.div>
          </div>
          </div>

          {/* 剩余次数 */}
          <div className="w-full max-w-sm shrink-0">
            <div className="bg-purple-500/10 border border-purple-500/20 rounded-xl p-3 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Sparkles size={18} className="text-purple-400" />
                <span className="text-sm text-gray-300">{t('remaining_today')}</span>
              </div>
              <span className="text-2xl font-bold text-purple-400">{spinsLeft}</span>
            </div>
          </div>
        </div>

        {/* 次数用完提示窗 */}
        <AnimatePresence>
          {showNoChancesModal && (
            <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="absolute inset-0 bg-black/80 backdrop-blur-sm"
                onClick={() => setShowNoChancesModal(false)}
              />
              <motion.div
                initial={{ scale: 0.5, opacity: 0, y: 50 }}
                animate={{ scale: 1, opacity: 1, y: 0 }}
                exit={{ scale: 0.5, opacity: 0, y: 50 }}
                className="relative bg-[#1C1C1E] border border-purple-500/30 rounded-3xl p-8 text-center shadow-2xl max-w-sm w-full"
              >
                <div className="w-16 h-16 mx-auto mb-4 bg-gradient-to-br from-purple-500/40 to-pink-500/40 rounded-full flex items-center justify-center border-4 border-white/20">
                  <Sparkles size={32} className="text-purple-400" />
                </div>
                <h2 className="text-2xl font-bold text-white mb-4">{t('no_chances_left')}</h2>
                <p className="text-gray-400 mb-6">{t('come_tomorrow')}</p>
                <motion.button
                  onClick={() => setShowNoChancesModal(false)}
                  className="w-full py-3 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-xl font-bold"
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                >
                  {t('got_it')}
                </motion.button>
              </motion.div>
            </div>
          )}
        </AnimatePresence>

        {/* 结果弹窗 */}
        <AnimatePresence>
          {selectedPrize && (
            <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="absolute inset-0 bg-black/80 backdrop-blur-sm"
                onClick={() => {
                  setSelectedPrize(null)
                  setTimeout(() => {
                    restoreRedPacket()
                  }, 100)
                }}
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
                  className={`w-20 h-20 mx-auto mb-4 bg-gradient-to-br ${selectedPrize.bgGradient} rounded-full flex items-center justify-center border-4 border-white/20`}
                >
                  <selectedPrize.icon size={40} className={selectedPrize.color} />
                </motion.div>
                <h2 className="text-2xl font-bold text-white mb-2">{t('congrats')}</h2>
                <p className={`text-4xl font-black ${selectedPrize.color} mb-1`}>
                  +{selectedPrize.value}
                </p>
                <p className={`text-lg font-bold ${selectedPrize.color} mb-6`}>
                  {selectedPrize.name}
                </p>
                <motion.button
                  onClick={() => {
                    setSelectedPrize(null)
                    setTimeout(() => {
                      restoreRedPacket()
                    }, 100)
                  }}
                  className="w-full py-3 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-xl font-bold"
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                >
                  {t('awesome')}
                </motion.button>
              </motion.div>
            </div>
          )}
        </AnimatePresence>
      </div>
    </PageTransition>
  )
}
