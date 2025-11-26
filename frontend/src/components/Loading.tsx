import { useTranslation } from '../providers/I18nProvider'

export default function Loading() {
  const { t } = useTranslation()
  
  return (
    <div className="h-full flex items-center justify-center bg-brand-dark">
      <div className="text-center">
        <div className="w-12 h-12 border-4 border-brand-red border-t-transparent rounded-full animate-spin mx-auto mb-4" />
        <p className="text-gray-400">{t('loading')}</p>
      </div>
    </div>
  )
}

