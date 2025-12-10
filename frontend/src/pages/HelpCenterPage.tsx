import { useState } from 'react'
import { X, HelpCircle, ChevronDown, ChevronUp, Gift, Wallet, Gamepad2, Shield, Info } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import { useTranslation } from '../providers/I18nProvider'
import { showAlert } from '../utils/telegram'
import PageTransition from '../components/PageTransition'

interface FAQItem {
  question: string
  answer: string
}

export default function HelpCenterPage() {
  const navigate = useNavigate()
  const { t } = useTranslation()
  const [expandedItems, setExpandedItems] = useState<Set<string>>(new Set())

  const toggleItem = (id: string) => {
    const newSet = new Set(expandedItems)
    if (newSet.has(id)) {
      newSet.delete(id)
    } else {
      newSet.add(id)
    }
    setExpandedItems(newSet)
  }

  // 常見問題分類
  const faqCategories = [
    {
      id: 'redpacket',
      title: t('red_packet_help') || '紅包相關',
      icon: Gift,
      items: [
        {
          id: 'rp1',
          question: t('faq_redpacket_1_q') || '如何發送紅包？',
          answer: t('faq_redpacket_1_a') || '在紅包頁面點擊「發送紅包」按鈕，選擇幣種、金額和數量，填寫祝福語後即可發送。支持 USDT、TON、Stars 和積分四種幣種。',
        },
        {
          id: 'rp2',
          question: t('faq_redpacket_2_q') || '如何領取紅包？',
          answer: t('faq_redpacket_2_a') || '在紅包列表中找到可領取的紅包，點擊「領取」按鈕即可。每個紅包每人只能領取一次。',
        },
        {
          id: 'rp3',
          question: t('faq_redpacket_3_q') || '紅包炸彈是什麼？',
          answer: t('faq_redpacket_3_a') || '紅包炸彈是一種特殊玩法，領取到指定數字（0-9）的用戶會被扣除一定金額作為懲罰。其他用戶可以獲得更多獎勵。',
        },
        {
          id: 'rp4',
          question: t('faq_redpacket_4_q') || '紅包過期了怎麼辦？',
          answer: t('faq_redpacket_4_a') || '過期的紅包會自動退還給發送者。您可以在錢包頁面查看退款記錄。',
        },
      ],
    },
    {
      id: 'wallet',
      title: t('wallet_help') || '錢包相關',
      icon: Wallet,
      items: [
        {
          id: 'w1',
          question: t('faq_wallet_1_q') || '如何充值？',
          answer: t('faq_wallet_1_a') || '在錢包頁面點擊「充值」按鈕，選擇幣種和網絡，複製地址或掃描二維碼進行轉賬。轉賬完成後等待區塊鏈確認即可到賬。',
        },
        {
          id: 'w2',
          question: t('faq_wallet_2_q') || '如何提現？',
          answer: t('faq_wallet_2_a') || '在錢包頁面點擊「提現」按鈕，輸入提現地址和金額，確認後提交申請。提現需要支付網絡手續費。',
        },
        {
          id: 'w3',
          question: t('faq_wallet_3_q') || '支持哪些幣種？',
          answer: t('faq_wallet_3_a') || '目前支持 USDT（TRC20/ERC20）、TON 和 Telegram Stars 三種幣種。',
        },
        {
          id: 'w4',
          question: t('faq_wallet_4_q') || '充值多久到賬？',
          answer: t('faq_wallet_4_a') || '充值到賬時間取決於區塊鏈網絡確認速度。USDT（TRC20）通常需要 1-3 分鐘，TON 需要 1-5 分鐘，ERC20 需要 5-15 分鐘。',
        },
      ],
    },
    {
      id: 'game',
      title: t('game_help') || '遊戲相關',
      icon: Gamepad2,
      items: [
        {
          id: 'g1',
          question: t('faq_game_1_q') || '如何參與遊戲？',
          answer: t('faq_game_1_a') || '在遊戲頁面選擇您喜歡的遊戲類型，點擊進入即可開始遊戲。部分遊戲需要消耗積分或代幣。',
        },
        {
          id: 'g2',
          question: t('faq_game_2_q') || '幸運轉盤如何玩？',
          answer: t('faq_game_2_a') || '點擊轉盤開始轉動，轉盤停止後根據指針指向的區域獲得對應獎勵。每次轉動需要消耗一定積分。',
        },
        {
          id: 'g3',
          question: t('faq_game_3_q') || '遊戲獎勵如何領取？',
          answer: t('faq_game_3_a') || '遊戲獲勝後，獎勵會自動發放到您的賬戶餘額中。您可以在錢包頁面查看餘額變化。',
        },
      ],
    },
    {
      id: 'security',
      title: t('security_help') || '安全相關',
      icon: Shield,
      items: [
        {
          id: 's1',
          question: t('faq_security_1_q') || '如何保護賬戶安全？',
          answer: t('faq_security_1_a') || '建議設置強密碼、啟用雙重驗證、不要將密碼告知他人、定期檢查賬戶活動記錄。',
        },
        {
          id: 's2',
          question: t('faq_security_2_q') || '賬戶被盜怎麼辦？',
          answer: t('faq_security_2_a') || '如發現賬戶異常，請立即聯繫客服並修改密碼。我們會協助您處理相關問題。',
        },
      ],
    },
  ]

  return (
    <PageTransition>
      <div className="h-full flex flex-col bg-brand-dark">
        {/* 頂部導航 */}
        <div className="flex items-center justify-between p-4 border-b border-white/5">
          <button onClick={() => navigate(-1)} className="p-2">
            <X size={24} />
          </button>
          <h1 className="text-lg font-bold">{t('help_center')}</h1>
          <div className="w-10" />
        </div>

        {/* 內容區域 */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {/* 快速入口 */}
          <div className="grid grid-cols-2 gap-3">
            <button
              onClick={() => navigate('/send')}
              className="bg-gradient-to-br from-orange-500/20 to-red-500/20 border border-orange-500/30 rounded-xl p-4 text-left"
            >
              <Gift size={24} className="text-orange-400 mb-2" />
              <div className="text-white font-semibold">{t('send_red_packet') || '發送紅包'}</div>
              <div className="text-gray-400 text-sm mt-1">{t('learn_how_to_send') || '學習如何發送'}</div>
            </button>
            <button
              onClick={() => navigate('/recharge')}
              className="bg-gradient-to-br from-green-500/20 to-emerald-500/20 border border-green-500/30 rounded-xl p-4 text-left"
            >
              <Wallet size={24} className="text-green-400 mb-2" />
              <div className="text-white font-semibold">{t('recharge') || '充值'}</div>
              <div className="text-gray-400 text-sm mt-1">{t('learn_how_to_recharge') || '學習如何充值'}</div>
            </button>
          </div>

          {/* 常見問題 */}
          <div className="space-y-4">
            <h2 className="text-white font-bold text-lg">{t('frequently_asked_questions') || '常見問題'}</h2>
            {faqCategories.map((category) => (
              <div key={category.id} className="bg-brand-darker rounded-xl p-4">
                <div className="flex items-center gap-3 mb-4">
                  <category.icon size={20} className="text-orange-400" />
                  <h3 className="text-white font-semibold">{category.title}</h3>
                </div>
                <div className="space-y-2">
                  {category.items.map((item) => (
                    <FAQItem
                      key={item.id}
                      item={item}
                      isExpanded={expandedItems.has(item.id)}
                      onToggle={() => toggleItem(item.id)}
                    />
                  ))}
                </div>
              </div>
            ))}
          </div>

          {/* 聯繫客服 */}
          <div className="bg-gradient-to-br from-blue-500/20 to-purple-500/20 border border-blue-500/30 rounded-xl p-4">
            <div className="flex items-start gap-3">
              <Info size={20} className="text-blue-400 mt-0.5" />
              <div className="flex-1">
                <h3 className="text-white font-semibold mb-2">{t('need_more_help') || '需要更多幫助？'}</h3>
                <p className="text-gray-300 text-sm mb-3">
                  {t('contact_support') || '如果以上問題無法解決您的疑問，請聯繫我們的客服團隊。'}
                </p>
                <button
                  onClick={() => showAlert('客服功能開發中', 'info')}
                  className="w-full py-2 bg-blue-500/20 border border-blue-500/50 rounded-lg text-blue-400 font-medium hover:bg-blue-500/30 transition-colors"
                >
                  {t('contact_customer_service') || '聯繫客服'}
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </PageTransition>
  )
}

function FAQItem({
  item,
  isExpanded,
  onToggle,
}: {
  item: FAQItem
  isExpanded: boolean
  onToggle: () => void
}) {
  return (
    <div className="border border-white/5 rounded-lg overflow-hidden">
      <button
        onClick={onToggle}
        className="w-full flex items-center justify-between p-3 text-left hover:bg-white/5 transition-colors"
      >
        <span className="text-white font-medium flex-1 pr-4">{item.question}</span>
        {isExpanded ? (
          <ChevronUp size={18} className="text-gray-400" />
        ) : (
          <ChevronDown size={18} className="text-gray-400" />
        )}
      </button>
      {isExpanded && (
        <div className="p-3 pt-0 text-gray-300 text-sm leading-relaxed border-t border-white/5">
          {item.answer}
        </div>
      )}
    </div>
  )
}

