import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { ChevronDown, X } from 'lucide-react'
import { useTranslation } from '../providers/I18nProvider'
import { getUserChats, sendRedPacket, type ChatInfo } from '../utils/api'
import { haptic, showAlert } from '../utils/telegram'

export default function SendRedPacket() {
  const navigate = useNavigate()
  const { t } = useTranslation()
  const queryClient = useQueryClient()

  const [selectedChat, setSelectedChat] = useState<ChatInfo | null>(null)
  const [showChatModal, setShowChatModal] = useState(false)
  const [amount, setAmount] = useState('')
  const [quantity, setQuantity] = useState('1')
  const [currency, setCurrency] = useState('USDT')
  const [packetType, setPacketType] = useState<'random' | 'fixed'>('random')
  const [message, setMessage] = useState('')

  // 獲取群組列表
  const { data: chats } = useQuery({
    queryKey: ['chats'],
    queryFn: getUserChats,
  })

  // 發送紅包
  const sendMutation = useMutation({
    mutationFn: sendRedPacket,
    onSuccess: () => {
      haptic('success')
      queryClient.invalidateQueries({ queryKey: ['balance'] })
      queryClient.invalidateQueries({ queryKey: ['redpackets'] })
      showAlert(t('success'))
      navigate('/packets')
    },
    onError: (error: Error) => {
      haptic('error')
      showAlert(error.message)
    },
  })

  const handleSubmit = () => {
    if (!selectedChat) {
      showAlert(t('select_group'))
      return
    }
    if (!amount || parseFloat(amount) <= 0) {
      showAlert('請輸入金額')
      return
    }
    if (!quantity || parseInt(quantity) < 1) {
      showAlert('請輸入數量')
      return
    }

    haptic('medium')
    sendMutation.mutate({
      chat_id: selectedChat.id,
      amount: parseFloat(amount),
      currency,
      quantity: parseInt(quantity),
      type: packetType,
      message: message || t('best_wishes'),
    })
  }

  return (
    <div className="h-full flex flex-col bg-brand-dark">
      {/* 頂部 */}
      <div className="flex items-center justify-between p-4 border-b border-white/5">
        <button onClick={() => navigate(-1)} className="p-2">
          <X size={24} />
        </button>
        <h1 className="text-lg font-bold">{t('send_red_packet')}</h1>
        <div className="w-10" />
      </div>

      {/* 表單 */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 pb-24">
        {/* 選擇群組 */}
        <div>
          <label className="block text-gray-400 text-sm mb-2">{t('select_group')}</label>
          <button
            type="button"
            onClick={() => setShowChatModal(true)}
            className="w-full flex items-center justify-between p-4 bg-brand-darker rounded-xl border border-white/5"
          >
            <span className={selectedChat ? 'text-white' : 'text-gray-500'}>
              {selectedChat?.title || '點擊選擇群組'}
            </span>
            <ChevronDown size={18} className="text-gray-400" />
          </button>
        </div>

        {/* 幣種選擇 */}
        <div>
          <label className="block text-gray-400 text-sm mb-2">幣種</label>
          <div className="flex gap-2">
            {['USDT', 'TON', 'Stars'].map((c) => (
              <button
                key={c}
                type="button"
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

        {/* 紅包類型 */}
        <div>
          <label className="block text-gray-400 text-sm mb-2">紅包類型</label>
          <div className="flex gap-2">
            <button
              type="button"
              onClick={() => setPacketType('random')}
              className={`flex-1 py-3 rounded-xl border transition-colors ${
                packetType === 'random'
                  ? 'bg-brand-red border-brand-red text-white'
                  : 'bg-brand-darker border-white/5 text-gray-400'
              }`}
            >
              隨機金額
            </button>
            <button
              type="button"
              onClick={() => setPacketType('fixed')}
              className={`flex-1 py-3 rounded-xl border transition-colors ${
                packetType === 'fixed'
                  ? 'bg-brand-red border-brand-red text-white'
                  : 'bg-brand-darker border-white/5 text-gray-400'
              }`}
            >
              固定金額
            </button>
          </div>
        </div>

        {/* 金額 */}
        <div>
          <label className="block text-gray-400 text-sm mb-2">{t('amount')}</label>
          <input
            type="number"
            value={amount}
            onChange={(e) => setAmount(e.target.value)}
            placeholder="0.00"
            className="w-full p-4 bg-brand-darker rounded-xl border border-white/5 text-white text-xl font-bold text-center focus:outline-none focus:border-brand-red"
          />
        </div>

        {/* 數量 */}
        <div>
          <label className="block text-gray-400 text-sm mb-2">{t('quantity')}</label>
          <input
            type="number"
            value={quantity}
            onChange={(e) => setQuantity(e.target.value)}
            placeholder="1"
            min="1"
            className="w-full p-4 bg-brand-darker rounded-xl border border-white/5 text-white text-center focus:outline-none focus:border-brand-red"
          />
        </div>

        {/* 祝福語 */}
        <div>
          <label className="block text-gray-400 text-sm mb-2">{t('message')}</label>
          <input
            type="text"
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            placeholder={t('best_wishes')}
            className="w-full p-4 bg-brand-darker rounded-xl border border-white/5 text-white focus:outline-none focus:border-brand-red"
          />
        </div>
      </div>

      {/* 發送按鈕 */}
      <div className="fixed bottom-0 left-0 right-0 p-4 bg-brand-dark/90 backdrop-blur border-t border-white/5">
        <button
          onClick={handleSubmit}
          disabled={sendMutation.isPending}
          className="w-full py-4 bg-gradient-to-r from-brand-red to-orange-500 rounded-xl text-white font-bold text-lg disabled:opacity-50"
        >
          {sendMutation.isPending ? t('loading') : t('send')}
        </button>
      </div>

      {/* 群組選擇彈窗 */}
      {showChatModal && (
        <div className="fixed inset-0 z-50 flex items-end justify-center bg-black/50" onClick={() => setShowChatModal(false)}>
          <div className="w-full max-h-[70vh] bg-brand-darker rounded-t-3xl" onClick={(e) => e.stopPropagation()}>
            <div className="p-4 border-b border-white/5">
              <h3 className="text-lg font-bold text-center">{t('select_group')}</h3>
            </div>
            <div className="overflow-y-auto max-h-[60vh]">
              {chats?.map((chat) => (
                <button
                  key={chat.id}
                  onClick={() => { setSelectedChat(chat); setShowChatModal(false); }}
                  className="w-full flex items-center gap-3 p-4 hover:bg-white/5 transition-colors"
                >
                  <div className="w-10 h-10 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white font-bold">
                    {chat.title[0]}
                  </div>
                  <span className="text-white">{chat.title}</span>
                </button>
              ))}
              {!chats?.length && (
                <div className="p-8 text-center text-gray-400">
                  {t('no_data')}
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

