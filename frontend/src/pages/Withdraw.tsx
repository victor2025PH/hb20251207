import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { X } from 'lucide-react'
import { useTranslation } from '../providers/I18nProvider'
import { createWithdrawOrder } from '../utils/api'
import { haptic, showAlert } from '../utils/telegram'

export default function Withdraw() {
  const navigate = useNavigate()
  const { t } = useTranslation()
  const queryClient = useQueryClient()

  const [amount, setAmount] = useState('')
  const [currency, setCurrency] = useState('USDT')
  const [address, setAddress] = useState('')

  const withdrawMutation = useMutation({
    mutationFn: () => createWithdrawOrder(parseFloat(amount), currency, address),
    onSuccess: () => {
      haptic('success')
      showAlert('提現申請已提交，請等待審核')
      queryClient.invalidateQueries({ queryKey: ['balance'] })
      navigate(-1)
    },
    onError: (error: Error) => {
      haptic('error')
      showAlert(error.message)
    },
  })

  const handleSubmit = () => {
    if (!amount || parseFloat(amount) <= 0) {
      showAlert('請輸入提現金額')
      return
    }
    if (!address) {
      showAlert('請輸入收款地址')
      return
    }
    haptic('medium')
    withdrawMutation.mutate()
  }

  return (
    <div className="h-full flex flex-col bg-brand-dark">
      {/* 頂部 */}
      <div className="flex items-center justify-between p-4 border-b border-white/5">
        <button onClick={() => navigate(-1)} className="p-2">
          <X size={24} />
        </button>
        <h1 className="text-lg font-bold">{t('withdraw')}</h1>
        <div className="w-10" />
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-4 pb-24">
        {/* 幣種選擇 */}
        <div>
          <label className="block text-gray-400 text-sm mb-2">選擇幣種</label>
          <div className="flex gap-2">
            {['USDT', 'TON'].map((c) => (
              <button
                key={c}
                onClick={() => setCurrency(c)}
                className={`flex-1 py-3 rounded-xl border transition-colors ${
                  currency === c
                    ? 'bg-brand-red border-brand-red text-white'
                    : 'bg-brand-darker border-white/5 text-gray-400'
                }`}
              >
                {c}
              </button>
            ))}
          </div>
        </div>

        {/* 提現金額 */}
        <div>
          <label className="block text-gray-400 text-sm mb-2">提現金額</label>
          <input
            type="number"
            value={amount}
            onChange={(e) => setAmount(e.target.value)}
            placeholder="0.00"
            className="w-full p-4 bg-brand-darker rounded-xl border border-white/5 text-white text-xl font-bold text-center focus:outline-none focus:border-brand-red"
          />
          <p className="text-gray-500 text-xs mt-2 text-right">
            手續費: 1 {currency} | 最低提現: 10 {currency}
          </p>
        </div>

        {/* 收款地址 */}
        <div>
          <label className="block text-gray-400 text-sm mb-2">收款地址</label>
          <input
            type="text"
            value={address}
            onChange={(e) => setAddress(e.target.value)}
            placeholder="請輸入 TRC-20 地址"
            className="w-full p-4 bg-brand-darker rounded-xl border border-white/5 text-white focus:outline-none focus:border-brand-red"
          />
        </div>

        {/* 提示 */}
        <div className="bg-brand-red/10 border border-brand-red/30 rounded-xl p-4">
          <h4 className="text-brand-red font-bold mb-2">注意事項</h4>
          <ul className="text-red-200/80 text-sm space-y-1">
            <li>• 請確認地址正確，轉錯無法找回</li>
            <li>• 提現申請需要 1-24 小時審核</li>
            <li>• 大額提現可能需要額外審核</li>
          </ul>
        </div>
      </div>

      {/* 提交按鈕 */}
      <div className="fixed bottom-0 left-0 right-0 p-4 bg-brand-dark/90 backdrop-blur border-t border-white/5">
        <button
          onClick={handleSubmit}
          disabled={withdrawMutation.isPending}
          className="w-full py-4 bg-gradient-to-r from-brand-red to-orange-500 rounded-xl text-white font-bold text-lg disabled:opacity-50"
        >
          {withdrawMutation.isPending ? '提交中...' : '提交提現'}
        </button>
      </div>
    </div>
  )
}

