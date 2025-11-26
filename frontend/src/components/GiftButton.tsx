import { motion } from 'framer-motion'
import { Gift, Sparkles } from 'lucide-react'
import { useTranslation } from '../providers/I18nProvider'

interface GiftButtonProps {
  onClick: () => void
}

export default function GiftButton({ onClick }: GiftButtonProps) {
  const { t } = useTranslation()
  
  return (
    <motion.button
      onClick={onClick}
      className="relative w-full h-44 rounded-3xl overflow-hidden group"
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
    >
      {/* 動態背景 */}
      <div className="absolute inset-0 bg-gradient-to-br from-red-900/80 via-orange-900/60 to-red-900/80" />
      
      {/* 動態光波 */}
      <motion.div
        className="absolute inset-0 bg-gradient-radial from-orange-500/20 via-transparent to-transparent"
        animate={{
          scale: [1, 1.5, 1],
          opacity: [0.3, 0.6, 0.3],
        }}
        transition={{
          duration: 3,
          repeat: Infinity,
          ease: 'easeInOut',
        }}
      />
      
      {/* 浮動粒子 */}
      {[...Array(8)].map((_, i) => (
        <motion.div
          key={i}
          className="absolute w-2 h-2 bg-yellow-400/60 rounded-full"
          style={{
            left: `${10 + (i * 12)}%`,
          }}
          animate={{
            y: [100, -20],
            opacity: [0, 1, 0],
            scale: [0.5, 1, 0.5],
          }}
          transition={{
            duration: 3 + Math.random() * 2,
            repeat: Infinity,
            delay: i * 0.3,
            ease: 'easeOut',
          }}
        />
      ))}
      
      {/* 邊框光效 */}
      <div className="absolute inset-0 rounded-3xl border-2 border-orange-500/30 group-hover:border-orange-400/60 transition-colors" />
      
      {/* 頂部光線 */}
      <motion.div
        className="absolute top-0 left-1/4 right-1/4 h-[2px] bg-gradient-to-r from-transparent via-orange-400 to-transparent"
        animate={{
          opacity: [0.3, 1, 0.3],
          scaleX: [0.5, 1, 0.5],
        }}
        transition={{
          duration: 2,
          repeat: Infinity,
        }}
      />
      
      {/* 內容 */}
      <div className="relative z-10 h-full flex flex-col items-center justify-center gap-3">
        {/* 禮物圖標 */}
        <motion.div
          className="relative"
          animate={{
            y: [0, -8, 0],
          }}
          transition={{
            duration: 2,
            repeat: Infinity,
            ease: 'easeInOut',
          }}
        >
          {/* 光暈 */}
          <motion.div
            className="absolute inset-0 -m-4 bg-orange-500 rounded-full blur-xl"
            animate={{
              opacity: [0.3, 0.6, 0.3],
              scale: [0.8, 1.2, 0.8],
            }}
            transition={{
              duration: 2,
              repeat: Infinity,
            }}
          />
          
          {/* 圖標容器 */}
          <div className="relative w-20 h-20 bg-gradient-to-br from-orange-400 via-red-500 to-red-600 rounded-full flex items-center justify-center shadow-2xl shadow-orange-500/50">
            <Gift size={36} className="text-white" />
            
            {/* 閃光 */}
            <motion.div
              className="absolute -top-1 -right-1"
              animate={{
                scale: [1, 1.2, 1],
                opacity: [0.8, 1, 0.8],
              }}
              transition={{
                duration: 1.5,
                repeat: Infinity,
              }}
            >
              <Sparkles size={16} className="text-yellow-300" />
            </motion.div>
          </div>
        </motion.div>
        
        {/* 文字 */}
        <div className="text-center">
          <motion.h2
            className="text-2xl font-black text-white mb-1 tracking-wide"
            animate={{
              textShadow: [
                '0 0 10px rgba(255, 200, 100, 0.3)',
                '0 0 20px rgba(255, 200, 100, 0.6)',
                '0 0 10px rgba(255, 200, 100, 0.3)',
              ],
            }}
            transition={{
              duration: 2,
              repeat: Infinity,
            }}
          >
            {t('send_red_packet')}
          </motion.h2>
          <p className="text-orange-200/80 text-sm">
            點擊發送紅包給好友
          </p>
        </div>
      </div>
      
      {/* 角落裝飾 */}
      <div className="absolute top-3 left-3 w-8 h-8 border-t-2 border-l-2 border-orange-500/30 rounded-tl-lg" />
      <div className="absolute top-3 right-3 w-8 h-8 border-t-2 border-r-2 border-orange-500/30 rounded-tr-lg" />
      <div className="absolute bottom-3 left-3 w-8 h-8 border-b-2 border-l-2 border-orange-500/30 rounded-bl-lg" />
      <div className="absolute bottom-3 right-3 w-8 h-8 border-b-2 border-r-2 border-orange-500/30 rounded-br-lg" />
    </motion.button>
  )
}

