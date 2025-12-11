import { X, FileText, Shield, Lock, AlertCircle } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import { useTranslation } from '../providers/I18nProvider'
import PageTransition from '../components/PageTransition'

export default function UserAgreementPage() {
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
          <h1 className="text-lg font-bold">{t('user_agreement')}</h1>
          <div className="w-10" />
        </div>

        {/* 內容區域 */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {/* 服務條款 */}
          <div className="bg-brand-darker rounded-xl p-4">
            <div className="flex items-center gap-3 mb-4">
              <FileText size={20} className="text-orange-400" />
              <h2 className="text-white font-semibold">{t('terms_of_service')}</h2>
            </div>
            <div className="text-gray-300 text-sm leading-relaxed space-y-3">
              <Section title={t('terms_section_1_title') || '1. 服務說明'}>
                <p>{t('terms_section_1_content') || '本平台提供紅包發送、領取、遊戲等服務。用戶在使用本服務時，應當遵守相關法律法規和本協議的約定。'}</p>
              </Section>
              <Section title={t('terms_section_2_title') || '2. 用戶註冊'}>
                <p>{t('terms_section_2_content') || '用戶註冊時應當提供真實、準確、完整的個人信息。用戶對其賬戶和密碼的安全負責，不得將賬戶轉讓或出借給他人使用。'}</p>
              </Section>
              <Section title={t('terms_section_3_title') || '3. 服務使用規範'}>
                <ul className="list-disc list-inside space-y-2 ml-2">
                  <li>{t('terms_section_3_item_1') || '不得利用本服務從事任何違法違規活動'}</li>
                  <li>{t('terms_section_3_item_2') || '不得進行任何形式的欺詐、洗錢等非法行為'}</li>
                  <li>{t('terms_section_3_item_3') || '不得干擾、破壞本服務的正常運行'}</li>
                  <li>{t('terms_section_3_item_4') || '不得侵犯他人的知識產權或其他合法權益'}</li>
                </ul>
              </Section>
              <Section title={t('terms_section_4_title') || '4. 紅包服務'}>
                <p>{t('terms_section_4_content') || '用戶發送紅包時，應當確保賬戶餘額充足。紅包一經發送，不可撤回。領取的紅包金額將直接進入用戶賬戶餘額。'}</p>
              </Section>
              <Section title={t('terms_section_5_title') || '5. 遊戲服務'}>
                <p>{t('terms_section_5_content') || '用戶參與遊戲時，應當遵守遊戲規則。遊戲結果以系統記錄為準。禁止使用外掛、作弊等不正當手段。'}</p>
              </Section>
              <Section title={t('terms_section_6_title') || '6. 免責聲明'}>
                <p>{t('terms_section_6_content') || '因不可抗力、網絡故障、系統維護等原因導致服務中斷或數據丟失的，平台不承擔責任。用戶應當自行備份重要數據。'}</p>
              </Section>
            </div>
          </div>

          {/* 隱私政策 */}
          <div className="bg-brand-darker rounded-xl p-4">
            <div className="flex items-center gap-3 mb-4">
              <Shield size={20} className="text-green-400" />
              <h2 className="text-white font-semibold">{t('privacy_policy')}</h2>
            </div>
            <div className="text-gray-300 text-sm leading-relaxed space-y-3">
              <Section title={t('privacy_section_1_title') || '1. 信息收集'}>
                <p>{t('privacy_section_1_content') || '我們會收集您在使用服務過程中提供的信息，包括但不限於：Telegram 用戶信息、交易記錄、設備信息等。'}</p>
              </Section>
              <Section title={t('privacy_section_2_title') || '2. 信息使用'}>
                <p>{t('privacy_section_2_content') || '我們使用收集的信息用於提供、維護和改進服務，處理交易，發送通知等。我們不會向第三方出售您的個人信息。'}</p>
              </Section>
              <Section title={t('privacy_section_3_title') || '3. 信息保護'}>
                <p>{t('privacy_section_3_content') || '我們採用業界標準的安全措施保護您的個人信息，包括數據加密、訪問控制等。但無法保證絕對安全，請您妥善保管賬戶信息。'}</p>
              </Section>
              <Section title={t('privacy_section_4_title') || '4. 信息共享'}>
                <p>{t('privacy_section_4_content') || '我們僅在法律要求或為提供服務所必需的情況下，才會與第三方共享您的信息。'}</p>
              </Section>
            </div>
          </div>

          {/* 風險提示 */}
          <div className="bg-yellow-500/10 border border-yellow-500/30 rounded-xl p-4">
            <div className="flex items-start gap-3">
              <AlertCircle size={20} className="text-yellow-400 mt-0.5" />
              <div className="flex-1">
                <h3 className="text-yellow-400 font-semibold mb-2">{t('risk_warning')}</h3>
                <ul className="text-gray-300 text-sm space-y-2">
                  <li>• {t('risk_warning_1') || '數字貨幣交易存在價格波動風險，請謹慎投資'}</li>
                  <li>• {t('risk_warning_2') || '請妥善保管您的賬戶和密碼，避免被盜用'}</li>
                  <li>• {t('risk_warning_3') || '謹防釣魚網站和詐騙信息，不要點擊可疑鏈接'}</li>
                  <li>• {t('risk_warning_4') || '如發現異常情況，請立即聯繫客服'}</li>
                </ul>
              </div>
            </div>
          </div>

          {/* 更新日期 */}
          <div className="text-center text-gray-500 text-xs py-4">
            {t('last_updated')}：2024-12-10
          </div>
        </div>
      </div>
    </PageTransition>
  )
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div>
      <h4 className="text-white font-semibold mb-2">{title}</h4>
      <div className="text-gray-300">{children}</div>
    </div>
  )
}

