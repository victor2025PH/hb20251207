import { useState } from 'react'
import { X, Globe, Bell, Moon, Sun, Volume2, VolumeX, Languages } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import { useTranslation } from '../providers/I18nProvider'
import { getNotificationSettings, updateNotificationSettings, type NotificationSettings } from '../utils/api'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { showAlert } from '../utils/telegram'
import PageTransition from '../components/PageTransition'

export default function SettingsPage() {
  const navigate = useNavigate()
  const { t, language, setLanguage } = useTranslation()
  const queryClient = useQueryClient()

  // 獲取通知設置
  const { data: notificationSettings } = useQuery({
    queryKey: ['notification-settings'],
    queryFn: getNotificationSettings,
  })

  // 更新通知設置
  const updateMutation = useMutation<NotificationSettings, Error, Partial<NotificationSettings>>({
    mutationFn: updateNotificationSettings,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['notification-settings'] })
      showAlert(t('settings_saved'), 'success')
    },
    onError: () => {
      showAlert(t('save_failed'), 'error')
    },
  })

  // 語言選項
  const languages = [
    { code: 'zh-TW', nameKey: 'lang_zh_tw', flag: '🇹🇼' },
    { code: 'zh-CN', nameKey: 'lang_zh_cn', flag: '🇨🇳' },
    { code: 'en', nameKey: 'lang_en', flag: '🇺🇸' },
  ]

  const handleLanguageChange = (langCode: string) => {
    setLanguage(langCode as 'zh-TW' | 'zh-CN' | 'en')
    showAlert(t('language_changed'), 'success')
  }

  const handleNotificationToggle = (
    key: 'red_packet_notifications' | 'balance_notifications' | 'game_notifications',
    value: boolean
  ) => {
    if (notificationSettings) {
      const updateData: Partial<NotificationSettings> = {}
      updateData[key] = value
      updateMutation.mutate(updateData)
    }
  }

  return (
    <PageTransition>
      <div className="h-full flex flex-col bg-brand-dark">
        {/* 頂部導航 */}
        <div className="flex items-center justify-between p-4 border-b border-white/5">
          <button onClick={() => navigate(-1)} className="p-2">
            <X size={24} />
          </button>
          <h1 className="text-lg font-bold">{t('settings')}</h1>
          <div className="w-10" />
        </div>

        {/* 內容區域 */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {/* 語言設置 */}
          <div className="bg-brand-darker rounded-xl p-4">
            <div className="flex items-center gap-3 mb-4">
              <Globe size={20} className="text-orange-400" />
              <h2 className="text-white font-semibold">{t('language_settings')}</h2>
            </div>
            <div className="space-y-2">
              {languages.map((lang) => (
                <button
                  key={lang.code}
                  onClick={() => handleLanguageChange(lang.code)}
                  className={`w-full flex items-center justify-between p-3 rounded-lg transition-colors ${
                    language === lang.code
                      ? 'bg-orange-500/20 border border-orange-500/50'
                      : 'bg-white/5 hover:bg-white/10'
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <span className="text-2xl">{lang.flag}</span>
                    <span className="text-white">{t(lang.nameKey)}</span>
                  </div>
                  {language === lang.code && (
                    <div className="w-2 h-2 rounded-full bg-orange-500" />
                  )}
                </button>
              ))}
            </div>
          </div>

          {/* 通知設置 */}
          <div className="bg-brand-darker rounded-xl p-4">
            <div className="flex items-center gap-3 mb-4">
              <Bell size={20} className="text-orange-400" />
              <h2 className="text-white font-semibold">{t('notifications')}</h2>
            </div>
            <div className="space-y-3">
              <SettingToggle
                label={t('red_packet_notifications')}
                description={t('red_packet_notifications_desc')}
                checked={notificationSettings?.red_packet_notifications ?? true}
                onChange={(checked) => handleNotificationToggle('red_packet_notifications', checked)}
              />
              <SettingToggle
                label={t('balance_notifications')}
                description={t('balance_notifications_desc')}
                checked={notificationSettings?.balance_notifications ?? true}
                onChange={(checked) => handleNotificationToggle('balance_notifications', checked)}
              />
              <SettingToggle
                label={t('game_notifications')}
                description={t('game_notifications_desc')}
                checked={notificationSettings?.game_notifications ?? true}
                onChange={(checked) => handleNotificationToggle('game_notifications', checked)}
              />
            </div>
          </div>

          {/* 其他設置 */}
          <div className="bg-brand-darker rounded-xl p-4">
            <div className="flex items-center gap-3 mb-4">
              <Moon size={20} className="text-orange-400" />
              <h2 className="text-white font-semibold">{t('other_settings')}</h2>
            </div>
            <div className="space-y-3">
              <SettingItem
                label={t('sound_effects')}
                description={t('sound_effects_desc')}
                icon={Volume2}
                onClick={() => showAlert(t('sound_settings_developing'), 'info')}
              />
              <SettingItem
                label={t('vibration')}
                description={t('vibration_desc')}
                icon={Bell}
                onClick={() => showAlert(t('vibration_settings_developing'), 'info')}
              />
            </div>
          </div>
        </div>
      </div>
    </PageTransition>
  )
}

function SettingToggle({
  label,
  description,
  checked,
  onChange,
}: {
  label: string
  description?: string
  checked: boolean
  onChange: (checked: boolean) => void
}) {
  return (
    <div className="flex items-center justify-between">
      <div className="flex-1">
        <div className="text-white font-medium">{label}</div>
        {description && <div className="text-gray-400 text-sm mt-1">{description}</div>}
      </div>
      <button
        onClick={() => onChange(!checked)}
        className={`relative w-12 h-6 rounded-full transition-colors ${
          checked ? 'bg-orange-500' : 'bg-gray-600'
        }`}
      >
        <div
          className={`absolute top-1 left-1 w-4 h-4 bg-white rounded-full transition-transform ${
            checked ? 'translate-x-6' : 'translate-x-0'
          }`}
        />
      </button>
    </div>
  )
}

function SettingItem({
  label,
  description,
  icon: Icon,
  onClick,
}: {
  label: string
  description?: string
  icon: React.ElementType
  onClick: () => void
}) {
  return (
    <button
      onClick={onClick}
      className="w-full flex items-center justify-between p-3 rounded-lg bg-white/5 hover:bg-white/10 transition-colors"
    >
      <div className="flex items-center gap-3">
        <Icon size={20} className="text-gray-400" />
        <div>
          <div className="text-white font-medium">{label}</div>
          {description && <div className="text-gray-400 text-sm mt-1">{description}</div>}
        </div>
      </div>
    </button>
  )
}

