import { useState } from 'react'
import { motion } from 'framer-motion'
import { ArrowRightLeft, Wallet, Zap, Sparkles, TrendingUp } from 'lucide-react'
import { useTranslation } from '../providers/I18nProvider'
import { useSound } from '../hooks/useSound'
import PageTransition from '../components/PageTransition'
import { useQuery } from '@tanstack/react-query'
import { getBalance, getUserProfile } from '../utils/api'

export default function ExchangePage() {
  const { t } = useTranslation()
  const { playSound } = useSound()
  const [fromToken, setFromToken] = useState<'USDT' | 'TON' | 'ENERGY'>('USDT')
  const [toToken, setToToken] = useState<'USDT' | 'TON' | 'ENERGY'>('TON')
  const [amount, setAmount] = useState('')

  const { data: balance } = useQuery({
    queryKey: ['balance'],
    queryFn: getBalance,
  })

  const { data: profile } = useQuery({
    queryKey: ['profile'],
    queryFn: getUserProfile,
  })

  // 汇率（模拟）
  const exchangeRates: Record<string, number> = {
    'USDT->TON': 1.2,
    'TON->USDT': 0.83,
    'USDT->ENERGY': 10,
    'ENERGY->USDT': 0.1,
    'TON->ENERGY': 12,
    'ENERGY->TON': 0.083,
  }

  const rate = exchangeRates[`${fromToken}->${toToken}`] || 1
  const convertedAmount = amount ? (parseFloat(amount) * rate).toFixed(6) : '0.00'

  const getBalanceValue = (token: string) => {
    if (token === 'USDT') return balance?.usdt || 0
    if (token === 'TON') return balance?.ton || 0
    if (token === 'ENERGY') return profile?.energy_balance || 0
    return 0
  }

  const handleExchange = () => {
    if (!amount || parseFloat(amount) <= 0) {
      playSound('click')
      return
    }
    if (parseFloat(amount) > getBalanceValue(fromToken)) {
      playSound('click')
      return
    }
    playSound('success')
    // TODO: 调用兑换API
    alert(`兑换成功！${amount} ${fromToken} = ${convertedAmount} ${toToken}`)
  }

  const tokenConfig = {
    USDT: { icon: Wallet, color: 'text-green-400', bg: 'from-green-500/20 to-emerald-500/20', border: 'border-green-500/30' },
    TON: { icon: TrendingUp, color: 'text-blue-400', bg: 'from-blue-500/20 to-cyan-500/20', border: 'border-blue-500/30' },
    ENERGY: { icon: Zap, color: 'text-yellow-400', bg: 'from-yellow-500/20 to-orange-500/20', border: 'border-yellow-500/30' },
  }

  return (
    <PageTransition>
      <div className="h-full flex flex-col p-4 pb-24 gap-4 overflow-y-auto scrollbar-hide">
        <h1 className="text-xl font-bold text-white flex items-center gap-2">
          <ArrowRightLeft size={24} className="text-purple-400" />
          {t('exchange') || '币种兑换'}
        </h1>

        {/* 兑换卡片 */}
        <div className="bg-[#1C1C1E] border border-white/5 rounded-3xl p-6 space-y-4">
          {/* 从 */}
          <div className="space-y-2">
            <label className="block text-gray-300 text-sm font-medium">从</label>
            <div className="flex gap-3">
              <div className="flex-1">
                <input
                  type="number"
                  value={amount}
                  onChange={(e) => setAmount(e.target.value)}
                  placeholder="0.00"
                  className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white text-lg font-bold focus:outline-none focus:border-purple-500/50 transition-colors"
                />
                <div className="mt-1 text-xs text-gray-500">
                  余额: {getBalanceValue(fromToken).toFixed(6)}
                </div>
              </div>
              <select
                value={fromToken}
                onChange={(e) => setFromToken(e.target.value as any)}
                className="bg-gradient-to-br px-4 py-3 rounded-xl border text-white font-bold focus:outline-none"
                style={{
                  background: `linear-gradient(135deg, ${tokenConfig[fromToken].bg.split(' ')[1]}, ${tokenConfig[fromToken].bg.split(' ')[3]})`,
                  borderColor: tokenConfig[fromToken].border.split(' ')[1].replace('border-', '').replace('/30', ''),
                }}
              >
                <option value="USDT">USDT</option>
                <option value="TON">TON</option>
                <option value="ENERGY">能量</option>
              </select>
            </div>
          </div>

          {/* 交换箭头 */}
          <div className="flex justify-center">
            <motion.button
              onClick={() => {
                const temp = fromToken
                setFromToken(toToken)
                setToToken(temp)
                playSound('click')
              }}
              className="w-12 h-12 rounded-full bg-purple-500/20 border border-purple-500/30 flex items-center justify-center hover:bg-purple-500/30 transition-colors"
              whileHover={{ rotate: 180, scale: 1.1 }}
              whileTap={{ scale: 0.9 }}
            >
              <ArrowRightLeft size={20} className="text-purple-400" />
            </motion.button>
          </div>

          {/* 到 */}
          <div className="space-y-2">
            <label className="block text-gray-300 text-sm font-medium">到</label>
            <div className="flex gap-3">
              <div className="flex-1">
                <div className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white text-lg font-bold">
                  {convertedAmount}
                </div>
                <div className="mt-1 text-xs text-gray-500">
                  余额: {getBalanceValue(toToken).toFixed(6)}
                </div>
              </div>
              <select
                value={toToken}
                onChange={(e) => setToToken(e.target.value as any)}
                className="bg-gradient-to-br px-4 py-3 rounded-xl border text-white font-bold focus:outline-none"
                style={{
                  background: `linear-gradient(135deg, ${tokenConfig[toToken].bg.split(' ')[1]}, ${tokenConfig[toToken].bg.split(' ')[3]})`,
                  borderColor: tokenConfig[toToken].border.split(' ')[1].replace('border-', '').replace('/30', ''),
                }}
              >
                <option value="USDT">USDT</option>
                <option value="TON">TON</option>
                <option value="ENERGY">能量</option>
              </select>
            </div>
          </div>

          {/* 汇率显示 */}
          <div className="bg-purple-500/10 border border-purple-500/20 rounded-xl p-3 flex items-center justify-between">
            <span className="text-xs text-gray-400">汇率</span>
            <span className="text-sm font-bold text-purple-300">
              1 {fromToken} = {rate} {toToken}
            </span>
          </div>

          {/* 兑换按钮 */}
          <motion.button
            onClick={handleExchange}
            className="w-full py-4 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-xl font-bold text-base shadow-lg shadow-purple-500/20 active:scale-[0.98] transition-transform flex items-center justify-center gap-2"
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
          >
            <Sparkles size={18} />
            立即兑换
          </motion.button>
        </div>

        {/* 说明 */}
        <div className="bg-blue-500/10 border border-blue-500/20 rounded-xl p-4">
          <h3 className="text-sm font-bold text-blue-300 mb-2">💡 兑换说明</h3>
          <ul className="text-xs text-gray-400 space-y-1">
            <li>• 支持 USDT、TON、能量之间的互相兑换</li>
            <li>• 汇率实时更新，以实际兑换时为准</li>
            <li>• 兑换即时到账，无需等待</li>
            <li>• 能量可通过签到、邀请等方式获得</li>
          </ul>
        </div>
      </div>
    </PageTransition>
  )
}

