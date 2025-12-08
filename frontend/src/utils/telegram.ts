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
 * 返回一个 Promise，在 WebApp 完全准备好后解析
 */
export function initTelegram(): Promise<void> {
  return new Promise((resolve) => {
    const webApp = window.Telegram?.WebApp
    if (!webApp) {
      console.log('[Telegram] Not in Telegram environment')
      resolve()
      return
    }

    try {
      // 监听 ready 事件，确保 WebApp 完全初始化
      const onReady = () => {
        try {
          webApp.expand()
          // 注意：enableClosingConfirmation 在某些版本不支持
          try {
            webApp.enableClosingConfirmation()
          } catch (e) {
            // 忽略不支持的错误
          }
          
          const initData = webApp.initData || ''
          const user = webApp.initDataUnsafe?.user
          
          console.log('[Telegram] WebApp initialized', {
            version: webApp.version,
            platform: webApp.platform,
            user: user ? {
              id: user.id,
              username: user.username,
              first_name: user.first_name
            } : null,
            hasInitData: !!initData,
            initDataLength: initData.length,
            initDataPreview: initData ? initData.substring(0, 50) + '...' : 'empty'
          })
          
          // 如果 initData 为空，记录警告
          if (!initData || initData.length === 0) {
            console.warn('[Telegram] initData is empty - API requests will fail authentication')
            console.warn('[Telegram] 这可能是因为：')
            console.warn('[Telegram] 1. 不是在真正的 Telegram MiniApp 中打开')
            console.warn('[Telegram] 2. 或者 Telegram WebApp SDK 还没有完全加载')
            console.warn('[Telegram] 3. 或者需要等待更长时间')
          } else {
            console.log('[Telegram] initData 已准备就绪，可以用于认证')
          }
          
          resolve()
        } catch (error) {
          console.error('[Telegram] Init error:', error)
          resolve()
        }
      }
      
      // 调用 ready() 方法，然后使用 setTimeout 作为后备
      // Telegram WebApp SDK 的 ready() 方法会触发初始化
      webApp.ready()
      
      // 在真正的 Telegram MiniApp 中，initData 可能在 ready() 之后才可用
      // 使用轮询方式等待 initData 准备就绪（最多等待 2 秒）
      let pollAttempts = 0
      const maxPollAttempts = 20 // 2秒，每次100ms
      
      const pollForInitData = () => {
        const currentInitData = webApp.initData || ''
        const currentUser = webApp.initDataUnsafe?.user
        
        if (currentInitData && currentInitData.length > 0) {
          // initData 已准备就绪
          console.log('[Telegram] initData 已准备就绪（通过轮询）', {
            initDataLength: currentInitData.length,
            hasUser: !!currentUser
          })
          onReady()
        } else if (pollAttempts < maxPollAttempts) {
          // 继续等待
          pollAttempts++
          setTimeout(pollForInitData, 100)
        } else {
          // 超时，但仍然执行 onReady（可能不在真正的 Telegram 环境中）
          console.warn('[Telegram] 等待 initData 超时，可能不在真正的 Telegram MiniApp 中')
          onReady()
        }
      }
      
      // 立即检查一次，如果已有 initData 则直接执行
      if (webApp.initData && webApp.initData.length > 0) {
        onReady()
      } else {
        // 开始轮询
        setTimeout(pollForInitData, 100)
      }
    } catch (error) {
      console.error('[Telegram] Init error:', error)
      resolve()
    }
  })
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
 * 獲取初始化數據（別名，用於 WebSocket）
 */
export function getTelegramInitData(): string {
  return window.Telegram?.WebApp?.initData ?? ''
}

/**
 * 獲取 WebApp 實例（別名）
 */
export function getTelegramWebApp(): TelegramWebApp | null {
  return window.Telegram?.WebApp ?? null
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

// 全局彈窗管理器（用於在 miniapp 內部顯示，而不是使用 Telegram 系統彈窗）
let alertCallback: ((message: string, type?: 'success' | 'error' | 'warning' | 'info', title?: string) => void) | null = null
let confirmCallback: ((message: string, title?: string, confirmText?: string, cancelText?: string) => Promise<boolean>) | null = null

/**
 * 設置 Alert 回調（由組件調用）
 */
export function setAlertCallback(callback: (message: string, type?: 'success' | 'error' | 'warning' | 'info', title?: string) => void) {
  alertCallback = callback
}

/**
 * 設置 Confirm 回調（由組件調用）
 */
export function setConfirmCallback(callback: (message: string, title?: string, confirmText?: string, cancelText?: string) => Promise<boolean>) {
  confirmCallback = callback
}

/**
 * 顯示提示（在 miniapp 內部顯示，不使用 Telegram 系統彈窗）
 */
export function showAlert(message: string, type: 'success' | 'error' | 'warning' | 'info' = 'info', title?: string): Promise<void> {
  return new Promise((resolve) => {
    if (alertCallback) {
      alertCallback(message, type, title)
      // 延遲 resolve，讓用戶有時間看到彈窗
      setTimeout(resolve, 100)
    } else {
      // 如果沒有設置回調，回退到瀏覽器 alert（僅用於開發環境）
      console.warn('[showAlert] Alert callback not set, using fallback')
      alert(message)
      resolve()
    }
  })
}

/**
 * 顯示確認框（在 miniapp 內部顯示，不使用 Telegram 系統彈窗）
 */
export function showConfirm(message: string, title?: string, confirmText?: string, cancelText?: string): Promise<boolean> {
  return new Promise((resolve) => {
    if (confirmCallback) {
      confirmCallback(message, title, confirmText, cancelText).then(resolve)
    } else {
      // 如果沒有設置回調，回退到瀏覽器 confirm（僅用於開發環境）
      console.warn('[showConfirm] Confirm callback not set, using fallback')
      resolve(confirm(message))
    }
  })
}

