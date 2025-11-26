/**
 * Telegram WebApp SDK 工具
 */

interface TelegramUser {
  id: number
  username?: string
  first_name?: string
  last_name?: string
  language_code?: string
}

interface TelegramWebApp {
  initData: string
  initDataUnsafe: {
    user?: TelegramUser
    auth_date?: number
    hash?: string
  }
  version: string
  platform: string
  colorScheme: 'light' | 'dark'
  themeParams: Record<string, string>
  isExpanded: boolean
  viewportHeight: number
  viewportStableHeight: number
  ready: () => void
  expand: () => void
  close: () => void
  enableClosingConfirmation: () => void
  disableClosingConfirmation: () => void
  showAlert: (message: string, callback?: () => void) => void
  showConfirm: (message: string, callback?: (confirmed: boolean) => void) => void
  showPopup: (params: {
    title?: string
    message: string
    buttons?: Array<{ type?: string; text: string; id?: string }>
  }, callback?: (id: string) => void) => void
  HapticFeedback: {
    impactOccurred: (style: 'light' | 'medium' | 'heavy' | 'rigid' | 'soft') => void
    notificationOccurred: (type: 'error' | 'success' | 'warning') => void
    selectionChanged: () => void
  }
  openLink: (url: string) => void
  openTelegramLink: (url: string) => void
}

declare global {
  interface Window {
    Telegram?: {
      WebApp?: TelegramWebApp
    }
  }
}

/**
 * 初始化 Telegram WebApp
 */
export function initTelegram(): void {
  const webApp = window.Telegram?.WebApp
  if (!webApp) {
    console.log('[Telegram] Not in Telegram environment')
    return
  }

  try {
    webApp.ready()
    webApp.expand()
    webApp.enableClosingConfirmation()
    console.log('[Telegram] WebApp initialized', {
      version: webApp.version,
      platform: webApp.platform,
      user: webApp.initDataUnsafe.user,
    })
  } catch (error) {
    console.error('[Telegram] Init error:', error)
  }
}

/**
 * 獲取 WebApp 實例
 */
export function getTelegram(): TelegramWebApp | null {
  return window.Telegram?.WebApp ?? null
}

/**
 * 獲取用戶信息
 */
export function getTelegramUser(): TelegramUser | null {
  return window.Telegram?.WebApp?.initDataUnsafe.user ?? null
}

/**
 * 獲取初始化數據（用於後端驗證）
 */
export function getInitData(): string {
  return window.Telegram?.WebApp?.initData ?? ''
}

/**
 * 是否在 Telegram 環境
 */
export function isTelegramEnv(): boolean {
  return Boolean(window.Telegram?.WebApp)
}

/**
 * 觸覺反饋
 */
export function haptic(type: 'light' | 'medium' | 'heavy' | 'success' | 'error' | 'warning' = 'light'): void {
  const webApp = window.Telegram?.WebApp
  if (!webApp?.HapticFeedback) return

  if (['success', 'error', 'warning'].includes(type)) {
    webApp.HapticFeedback.notificationOccurred(type as 'success' | 'error' | 'warning')
  } else {
    webApp.HapticFeedback.impactOccurred(type as 'light' | 'medium' | 'heavy')
  }
}

/**
 * 顯示提示
 */
export function showAlert(message: string): Promise<void> {
  return new Promise((resolve) => {
    const webApp = window.Telegram?.WebApp
    if (webApp) {
      webApp.showAlert(message, resolve)
    } else {
      alert(message)
      resolve()
    }
  })
}

/**
 * 顯示確認框
 */
export function showConfirm(message: string): Promise<boolean> {
  return new Promise((resolve) => {
    const webApp = window.Telegram?.WebApp
    if (webApp) {
      webApp.showConfirm(message, resolve)
    } else {
      resolve(confirm(message))
    }
  })
}

