import { useState } from 'react'
import { X, Shield, Lock, Key, Smartphone, AlertTriangle, CheckCircle } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import { useTranslation } from '../providers/I18nProvider'
import { showAlert } from '../utils/telegram'
import PageTransition from '../components/PageTransition'

export default function SecuritySettingsPage() {
  const navigate = useNavigate()
  const { t } = useTranslation()

  return (
    <PageTransition>
      <div className="h-full flex flex-col bg-brand-dark">
        {/* 頂部導航 */}
        <div className="flex items-center justify-between p-4 border-b border-white/5">
          <button 
            onClick={(e) => {
              e.preventDefault()
              e.stopPropagation()
              navigate('/profile')
            }} 
            className="p-2"
          >
            <X size={24} className="text-white" />
          </button>
          <h1 className="text-lg font-bold">{t('security_settings')}</h1>
          <div className="w-10" />
        </div>

        {/* 內容區域 */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {/* 賬戶安全 */}
          <div className="bg-brand-darker rounded-xl p-4">
            <div className="flex items-center gap-3 mb-4">
              <Shield size={20} className="text-orange-400" />
              <h2 className="text-white font-semibold">{t('account_security')}</h2>
            </div>
            <div className="space-y-3">
              <SecurityItem
                icon={Lock}
                title={t('login_password')}
                description={t('login_password_desc')}
                onClick={() => showAlert(t('password_settings_developing'), 'info')}
              />
              <SecurityItem
                icon={Key}
                title={t('transaction_password')}
                description={t('transaction_password_desc')}
                onClick={() => showAlert(t('transaction_password_settings_developing'), 'info')}
              />
              <SecurityItem
                icon={Smartphone}
                title={t('two_factor_auth')}
                description={t('two_factor_auth_desc')}
                onClick={() => showAlert(t('two_factor_auth_developing'), 'info')}
              />
            </div>
          </div>

          {/* 交易安全 */}
          <div className="bg-brand-darker rounded-xl p-4">
            <div className="flex items-center gap-3 mb-4">
              <Shield size={20} className="text-green-400" />
              <h2 className="text-white font-semibold">{t('transaction_security')}</h2>
            </div>
            <div className="space-y-3">
              <SecurityItem
                icon={AlertTriangle}
                title={t('withdrawal_whitelist')}
                description={t('withdrawal_whitelist_desc')}
                onClick={() => showAlert(t('withdrawal_whitelist_developing'), 'info')}
              />
              <SecurityItem
                icon={CheckCircle}
                title={t('transaction_limit')}
                description={t('transaction_limit_desc')}
                onClick={() => showAlert(t('transaction_limit_developing'), 'info')}
              />
            </div>
          </div>

          {/* 安全提示 */}
          <div className="bg-yellow-500/10 border border-yellow-500/30 rounded-xl p-4">
            <div className="flex items-start gap-3">
              <AlertTriangle size={20} className="text-yellow-400 mt-0.5" />
              <div className="flex-1">
                <h3 className="text-yellow-400 font-semibold mb-2">{t('security_tips')}</h3>
                <ul className="text-gray-300 text-sm space-y-2">
                  <li>• {t('security_tip_1')}</li>
                  <li>• {t('security_tip_2')}</li>
                  <li>• {t('security_tip_3')}</li>
                  <li>• {t('security_tip_4')}</li>
                  <li>• {t('security_tip_5')}</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </div>
    </PageTransition>
  )
}

function SecurityItem({
  icon: Icon,
  title,
  description,
  onClick,
}: {
  icon: React.ElementType
  title: string
  description: string
  onClick: () => void
}) {
  return (
    <button
      onClick={onClick}
      className="w-full flex items-center gap-3 p-3 rounded-lg bg-white/5 hover:bg-white/10 transition-colors text-left"
    >
      <Icon size={20} className="text-orange-400" />
      <div className="flex-1">
        <div className="text-white font-medium">{title}</div>
        <div className="text-gray-400 text-sm mt-1">{description}</div>
      </div>
    </button>
  )
}

