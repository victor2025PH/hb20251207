import { motion, AnimatePresence } from 'framer-motion'
import { useQuery } from '@tanstack/react-query'
import { Wallet, TrendingUp, Star } from 'lucide-react'
import { getBalance } from '../utils/api'
import { useTranslation } from '../providers/I18nProvider'
import { useState, useEffect } from 'react'

// 數字動畫組件
function AnimatedNumber({ value, decimals = 2 }: { value: number; decimals?: number }) {
  const [displayValue, setDisplayValue] = useState(value)
  
  useEffect(() => {
    const duration = 500 // ms
    const steps = 20
    const increment = (value - displayValue) / steps
    let current = displayValue
    let step = 0
    
    const timer = setInterval(() => {
      step++
      current += increment
      if (step >= steps) {
        setDisplayValue(value)
        clearInterval(timer)
      } else {
        setDisplayValue(current)
      }
    }, duration / steps)
    
    return () => clearInterval(timer)
  }, [value])
  
  return <span>{displayValue.toFixed(decimals)}</span>
}

// 上升粒子組件（參考設計風格）
function BalanceParticle({ id, x, delay, duration, tx, ty, scale }: {
  id: string
  x: number
  delay: number
  duration: number
  tx: number
  ty: number
  scale: number
}) {
  return (
    <motion.div
      key={id}
      className="absolute z-0 pointer-events-none"
      initial={{ opacity: 0, y: 140, x: 0, scale: 0 }}
      animate={{ 
        opacity: [0, 0.8, 0], 
        y: ty, 
        x: tx, 
        scale: scale 
      }}
      transition={{ 
        duration, 
        repeat: Infinity, 
        ease: "linear", 
        delay 
      }}
      style={{ 
        bottom: 0, 
        left: `${x}%` 
      }}
    >
      <div className="w-1 h-1 rounded-full bg-cyan-300 shadow-[0_0_4px_currentColor]" />
    </motion.div>
  )
}

export default function AssetHeader() {
  const { t } = useTranslation()
  
  const { data: balance, isLoading } = useQuery({
    queryKey: ['balance'],
    queryFn: getBalance,
    staleTime: 30000,
    refetchInterval: 60000,
  })
  
  const usdt = balance?.usdt ?? 0
  const stars = balance?.stars ?? 0
  
  // 粒子動畫配置（參考設計）
  const balanceParticles = Array.from({ length: 8 }).map((_, i) => ({
    id: `bal-${i}`,
    x: Math.random() * 100,
    y: 110,
    tx: (Math.random() - 0.5) * 50,
    ty: -120 - Math.random() * 80,
    delay: Math.random() * 3,
    duration: 3 + Math.random() * 2,
    scale: 0.3 + Math.random() * 0.5,
  }))
  
  return (
    <motion.div
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      className="fixed top-16 left-0 right-0 z-30 px-4 pt-2 pointer-events-none"
    >
      <div className="relative">
        {/* 背景光暈 */}
        <div className="absolute inset-0 bg-gradient-to-r from-cyan-500/10 via-purple-500/10 to-cyan-500/10 rounded-2xl blur-xl" />
        
        {/* 主卡片 */}
        <div className="relative bg-gradient-to-br from-cyan-900/20 via-[#1C1C1E] to-blue-900/20 border border-cyan-500/20 rounded-3xl overflow-hidden backdrop-blur-sm">
          {/* 頂部光線 */}
          <motion.div
            className="absolute top-0 left-0 right-0 h-[1px] bg-gradient-to-r from-transparent via-cyan-400 to-transparent"
            animate={{
              opacity: [0.3, 1, 0.3],
            }}
            transition={{
              duration: 2,
              repeat: Infinity,
            }}
          />
          
          {/* 上升粒子動畫 */}
          <div className="absolute inset-0 overflow-hidden pointer-events-none">
            {balanceParticles.map((p) => (
              <BalanceParticle key={p.id} {...p} />
            ))}
          </div>
          
          {/* 頂部漸變 */}
          <div className="absolute top-0 inset-x-0 h-16 bg-gradient-to-b from-cyan-500/10 to-transparent opacity-60" />
          
          <div className="relative z-10 flex flex-col items-center justify-center py-3 px-4">
            <div className="flex items-center gap-1 mb-1">
              <Wallet size={10} className="text-cyan-300/60" />
              <span className="text-cyan-300/60 text-[9px] font-bold uppercase tracking-[0.15em]">
                {t('total_assets')}
              </span>
            </div>
            
            <AnimatePresence mode="wait">
              {isLoading ? (
                <motion.div
                  key="loading"
                  className="h-8 w-32 bg-white/10 rounded animate-pulse"
                />
              ) : (
                <motion.div
                  key="value"
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="text-2xl font-black text-white tracking-tighter drop-shadow-md"
                >
                  <AnimatedNumber value={usdt} />
                </motion.div>
              )}
            </AnimatePresence>
            
            {/* Stars 標籤 */}
            <div className="bg-[#0f0f11]/60 backdrop-blur-md px-2 py-0.5 rounded-full border border-cyan-500/20 flex items-center gap-1 shadow-sm mt-1">
              <motion.div
                className="w-1 h-1 rounded-full bg-cyan-400"
                animate={{ opacity: [0.5, 1, 0.5] }}
                transition={{ duration: 1.5, repeat: Infinity }}
              />
              <span className="text-cyan-200 text-[8px] font-bold">Stars</span>
            </div>
          </div>
          
          {/* 底部進度條 */}
          <div className="absolute bottom-0 left-0 w-full h-1 bg-cyan-500/20">
            <motion.div
              className="h-full bg-cyan-500 shadow-[0_0_10px_cyan]"
              initial={{ width: '0%' }}
              animate={{ width: '45%' }}
              transition={{ duration: 1.5, ease: "easeOut", delay: 0.2 }}
            />
          </div>
        </div>
      </div>
    </motion.div>
  )
}
