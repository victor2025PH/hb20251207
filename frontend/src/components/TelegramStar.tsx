import { motion } from 'framer-motion'

interface TelegramStarProps {
  size?: number
  className?: string
  withSpray?: boolean
}

const TelegramStar: React.FC<TelegramStarProps> = ({ size = 24, className = "", withSpray = false }) => {
  // 粒子配置（參考設計）
  const particles = [
    // Right Side Spray
    { angle: 0, dist: 18, delay: 0, size: 2.5, color: 'bg-yellow-300' },
    { angle: -25, dist: 15, delay: 0.2, size: 2, color: 'bg-white' },
    { angle: 25, dist: 15, delay: 0.4, size: 2, color: 'bg-orange-300' },
    { angle: -45, dist: 12, delay: 0.1, size: 1.5, color: 'bg-yellow-200' },
    { angle: 45, dist: 12, delay: 0.3, size: 1.5, color: 'bg-yellow-200' },
    
    // Left Side Spray
    { angle: 180, dist: 18, delay: 0, size: 2.5, color: 'bg-yellow-300' },
    { angle: 155, dist: 15, delay: 0.2, size: 2, color: 'bg-white' },
    { angle: 205, dist: 15, delay: 0.4, size: 2, color: 'bg-orange-300' },
    { angle: 135, dist: 12, delay: 0.1, size: 1.5, color: 'bg-yellow-200' },
    { angle: 225, dist: 12, delay: 0.3, size: 1.5, color: 'bg-yellow-200' },
  ]

  return (
    <div className={`relative flex items-center justify-center ${className}`} style={{ width: size, height: size }}>
      {/* 粒子噴射層 */}
      {withSpray && particles.map((p, i) => (
        <motion.div
          key={i}
          className={`absolute rounded-full ${p.color} shadow-[0_0_4px_currentColor]`}
          style={{ 
            width: p.size, 
            height: p.size,
            zIndex: 0
          }}
          initial={{ opacity: 0, x: 0, y: 0, scale: 0 }}
          animate={{ 
            opacity: [0, 1, 0],
            x: Math.cos(p.angle * Math.PI / 180) * p.dist,
            y: Math.sin(p.angle * Math.PI / 180) * p.dist,
            scale: [0.5, 1, 0]
          }}
          transition={{
            duration: 1 + Math.random() * 0.5,
            repeat: Infinity,
            ease: "easeOut",
            delay: p.delay,
            repeatDelay: Math.random() * 0.2
          }}
        />
      ))}

      {/* 主星星形狀 - Telegram 風格圓角星星 */}
      <svg
        width="100%"
        height="100%"
        viewBox="0 0 24 24"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        className="drop-shadow-md z-10 relative"
      >
        <path
          d="M12 1.5L14.65 8.44L22 9.06L16.37 13.78L18.14 21L12 17.1L5.86 21L7.63 13.78L2 9.06L9.35 8.44L12 1.5Z"
          className="fill-[#FFD700]"
          stroke="#F59E0B"
          strokeWidth="1.5"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
        {/* 內部漸變反射提示 */}
        <path
          d="M12 3.5L13.8 8.8L19.5 9.3L15.1 13L16.5 18.5L12 15.5L7.5 18.5L8.9 13L4.5 9.3L10.2 8.8L12 3.5Z"
          className="fill-white/20"
          style={{ mixBlendMode: 'overlay' }}
        />
      </svg>
    </div>
  )
}

export default TelegramStar

