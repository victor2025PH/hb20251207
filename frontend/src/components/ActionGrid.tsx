import { motion } from 'framer-motion'
import { LucideIcon } from 'lucide-react'

interface ActionItem {
  icon: LucideIcon
  label: string
  color: string
  bgColor: string
  onClick: () => void
}

interface ActionGridProps {
  actions: ActionItem[]
}

export default function ActionGrid({ actions }: ActionGridProps) {
  return (
    <div className="grid grid-cols-4 gap-3">
      {actions.map((action, index) => (
        <motion.button
          key={action.label}
          onClick={action.onClick}
          className="relative flex flex-col items-center gap-2 p-3 rounded-2xl bg-gray-800/50 border border-white/5 overflow-hidden group"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: index * 0.1 }}
          whileHover={{ scale: 1.05, y: -2 }}
          whileTap={{ scale: 0.95 }}
        >
          {/* 懸停背景 */}
          <motion.div
            className={`absolute inset-0 ${action.bgColor} opacity-0 group-hover:opacity-100 transition-opacity duration-300`}
          />
          
          {/* 圖標 */}
          <motion.div
            className={`relative z-10 w-11 h-11 rounded-xl ${action.bgColor} flex items-center justify-center`}
            whileHover={{ rotate: [0, -10, 10, 0] }}
            transition={{ duration: 0.3 }}
          >
            <action.icon size={20} className={action.color} />
          </motion.div>
          
          {/* 標籤 */}
          <span className="relative z-10 text-[11px] text-gray-300 font-medium group-hover:text-white transition-colors">
            {action.label}
          </span>
          
          {/* 底部光線 */}
          <motion.div
            className={`absolute bottom-0 left-1/4 right-1/4 h-[2px] rounded-full ${action.bgColor.replace('/10', '')}`}
            initial={{ scaleX: 0, opacity: 0 }}
            whileHover={{ scaleX: 1, opacity: 0.6 }}
            transition={{ duration: 0.2 }}
          />
        </motion.button>
      ))}
    </div>
  )
}

