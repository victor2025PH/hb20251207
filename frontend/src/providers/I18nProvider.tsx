import React, { createContext, useContext, useState, useCallback, useEffect } from 'react'
import { getTelegramUser } from '../utils/telegram'

// 語言類型
type Language = 'zh-TW' | 'zh-CN' | 'en'

// 翻譯文本
const translations: Record<Language, Record<string, string>> = {
  'zh-TW': {
    app_name: '幸運紅包',
    wallet: '錢包',
    packets: '紅包',
    earn: '賺取',
    game: '遊戲',
    profile: '我的',
    send_red_packet: '發紅包',
    recharge: '充值',
    withdraw: '提現',
    records: '記錄',
    total_assets: '總資產',
    invite_friends: '邀請好友',
    daily_checkin: '每日簽到',
    select_group: '選擇群組',
    amount: '金額',
    quantity: '數量',
    message: '祝福語',
    best_wishes: '恭喜發財！',
    send: '發送',
    cancel: '取消',
    confirm: '確認',
    loading: '載入中...',
    no_data: '暫無數據',
    error: '發生錯誤',
    success: '操作成功',
    notifications: '通知',
    sound: '音效',
    language: '語言',
    settings: '設置',
    level: '等級',
    balance: '餘額',
  },
  'zh-CN': {
    app_name: '幸运红包',
    wallet: '钱包',
    packets: '红包',
    earn: '赚取',
    game: '游戏',
    profile: '我的',
    send_red_packet: '发红包',
    recharge: '充值',
    withdraw: '提现',
    records: '记录',
    total_assets: '总资产',
    invite_friends: '邀请好友',
    daily_checkin: '每日签到',
    select_group: '选择群组',
    amount: '金额',
    quantity: '数量',
    message: '祝福语',
    best_wishes: '恭喜发财！',
    send: '发送',
    cancel: '取消',
    confirm: '确认',
    loading: '加载中...',
    no_data: '暂无数据',
    error: '发生错误',
    success: '操作成功',
    notifications: '通知',
    sound: '音效',
    language: '语言',
    settings: '设置',
    level: '等级',
    balance: '余额',
  },
  'en': {
    app_name: 'Lucky Red Packet',
    wallet: 'Wallet',
    packets: 'Packets',
    earn: 'Earn',
    game: 'Game',
    profile: 'Profile',
    send_red_packet: 'Send Packet',
    recharge: 'Recharge',
    withdraw: 'Withdraw',
    records: 'Records',
    total_assets: 'Total Assets',
    invite_friends: 'Invite Friends',
    daily_checkin: 'Daily Check-in',
    select_group: 'Select Group',
    amount: 'Amount',
    quantity: 'Quantity',
    message: 'Message',
    best_wishes: 'Best Wishes!',
    send: 'Send',
    cancel: 'Cancel',
    confirm: 'Confirm',
    loading: 'Loading...',
    no_data: 'No Data',
    error: 'Error',
    success: 'Success',
    notifications: 'Notifications',
    sound: 'Sound',
    language: 'Language',
    settings: 'Settings',
    level: 'Level',
    balance: 'Balance',
  },
}

// Context 類型
interface I18nContextType {
  language: Language
  setLanguage: (lang: Language) => void
  t: (key: string) => string
}

const I18nContext = createContext<I18nContextType | null>(null)

// 檢測 Telegram 語言
function detectLanguage(): Language {
  const user = getTelegramUser()
  const langCode = user?.language_code || navigator.language || 'zh-CN'
  
  if (langCode.startsWith('zh')) {
    // 繁體中文地區
    if (['zh-TW', 'zh-HK', 'zh-MO'].some(l => langCode.includes(l))) {
      return 'zh-TW'
    }
    return 'zh-CN'
  }
  
  return 'en'
}

export function I18nProvider({ children }: { children: React.ReactNode }) {
  const [language, setLanguageState] = useState<Language>(() => {
    const saved = localStorage.getItem('language') as Language
    return saved || detectLanguage()
  })

  const setLanguage = useCallback((lang: Language) => {
    setLanguageState(lang)
    localStorage.setItem('language', lang)
  }, [])

  const t = useCallback((key: string): string => {
    return translations[language][key] || key
  }, [language])

  useEffect(() => {
    document.documentElement.lang = language
  }, [language])

  return (
    <I18nContext.Provider value={{ language, setLanguage, t }}>
      {children}
    </I18nContext.Provider>
  )
}

export function useTranslation() {
  const context = useContext(I18nContext)
  if (!context) {
    throw new Error('useTranslation must be used within I18nProvider')
  }
  return context
}

