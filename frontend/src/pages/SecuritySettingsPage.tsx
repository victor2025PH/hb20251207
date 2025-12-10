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
          <button onClick={() => navigate(-1)} className="p-2">
            <X size={24} />
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
              <h2 className="text-white font-semibold">{t('account_security') || '賬戶安全'}</h2>
            </div>
            <div className="space-y-3">
              <SecurityItem
                icon={Lock}
                title={t('login_password') || '登錄密碼'}
                description={t('login_password_desc') || '設置或修改登錄密碼'}
                onClick={() => showAlert('密碼設置功能開發中', 'info')}
              />
              <SecurityItem
                icon={Key}
                title={t('transaction_password') || '交易密碼'}
                description={t('transaction_password_desc') || '設置交易密碼，保護您的資金安全'}
                onClick={() => showAlert('交易密碼設置功能開發中', 'info')}
              />
              <SecurityItem
                icon={Smartphone}
                title={t('two_factor_auth') || '雙重驗證'}
                description={t('two_factor_auth_desc') || '啟用雙重驗證，增強賬戶安全性'}
                onClick={() => showAlert('雙重驗證功能開發中', 'info')}
              />
            </div>
          </div>

          {/* 交易安全 */}
          <div className="bg-brand-darker rounded-xl p-4">
            <div className="flex items-center gap-3 mb-4">
              <Shield size={20} className="text-green-400" />
              <h2 className="text-white font-semibold">{t('transaction_security') || '交易安全'}</h2>
            </div>
            <div className="space-y-3">
              <SecurityItem
                icon={AlertTriangle}
                title={t('withdrawal_whitelist') || '提現白名單'}
                description={t('withdrawal_whitelist_desc') || '設置提現地址白名單，防止資金被盜'}
                onClick={() => showAlert('提現白名單功能開發中', 'info')}
              />
              <SecurityItem
                icon={CheckCircle}
                title={t('transaction_limit') || '交易限額'}
                description={t('transaction_limit_desc') || '設置單筆和每日交易限額'}
                onClick={() => showAlert('交易限額設置功能開發中', 'info')}
              />
            </div>
          </div>

          {/* 安全提示 */}
          <div className="bg-yellow-500/10 border border-yellow-500/30 rounded-xl p-4">
            <div className="flex items-start gap-3">
              <AlertTriangle size={20} className="text-yellow-400 mt-0.5" />
              <div className="flex-1">
                <h3 className="text-yellow-400 font-semibold mb-2">{t('security_tips') || '安全提示'}</h3>
                <ul className="text-gray-300 text-sm space-y-2">
                  <li>• {t('security_tip_1') || '請勿將密碼告知他人，包括客服人員'}</li>
                  <li>• {t('security_tip_2') || '定期更換密碼，建議每3個月更換一次'}</li>
                  <li>• {t('security_tip_3') || '不要在公共網絡環境下進行交易操作'}</li>
                  <li>• {t('security_tip_4') || '啟用雙重驗證可以大幅提升賬戶安全性'}</li>
                  <li>• {t('security_tip_5') || '如發現異常交易，請立即聯繫客服'}</li>
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

