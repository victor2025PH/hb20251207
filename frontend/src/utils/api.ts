import axios from 'axios'
import { getInitData, getTelegramUser } from './telegram'

// API 基礎 URL
const API_BASE = import.meta.env.VITE_API_URL || '/api'

// 創建 axios 實例
const api = axios.create({
  baseURL: API_BASE,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// 請求攔截器 - 添加認證信息（JWT Token 和 Telegram initData）
api.interceptors.request.use((config) => {
  // 檢查是否在 Telegram 環境中（必須有有效的 initData）
  const initData = getInitData()
  const isInTelegramEnv = initData && initData.length > 0
  
  // 在 Telegram 環境中，優先使用 initData（即使有 JWT token）
  // 因為 Telegram MiniApp 應該使用 Telegram 認證
  if (isInTelegramEnv) {
    config.headers['X-Telegram-Init-Data'] = initData
    
    // 解析 initData 获取用户信息（用于日志）
    let tgUserId = null
    try {
      const params = new URLSearchParams(initData)
      const userStr = params.get('user')
      if (userStr) {
        const userData = JSON.parse(userStr)
        tgUserId = userData.id
      }
    } catch (e) {
      // 忽略解析错误
    }
    
    // 如果同時有 JWT token，也添加（作為備用）
    const token = localStorage.getItem('auth_token')
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`
      console.log('[API Request]', config.url, 'with Telegram initData (primary) and JWT token (fallback)', {
        method: config.method,
        initDataLength: initData.length,
        tgUserId: tgUserId,
        initDataPreview: initData.substring(0, 50) + '...',
        hasJWT: true
      })
    } else {
      console.log('[API Request]', config.url, 'with Telegram auth only:', {
        method: config.method,
        initDataLength: initData.length,
        tgUserId: tgUserId,
        initDataPreview: initData.substring(0, 50) + '...',
        hasJWT: false
      })
    }
    return config
  }
  
  // 非 Telegram 環境：使用 JWT Token（Web 登錄）
  const token = localStorage.getItem('auth_token')
  if (token) {
    config.headers['Authorization'] = `Bearer ${token}`
    console.log('[API Request]', config.url, 'with JWT token', {
      method: config.method,
      tokenLength: token.length,
      tokenPreview: token.substring(0, 20) + '...'
    })
    return config
  }
  
  // 既沒有 JWT Token 也沒有有效的 Telegram initData
  // 對於需要認證的端點，這會導致 401，但我們在響應攔截器中處理
  console.debug('[API Request]', config.url, 'without valid auth - token and initData are both empty/missing', {
    method: config.method,
    hasInitData: !!initData,
    initDataLength: initData?.length || 0,
    hasToken: !!token
  })
  return config
})

// 響應攔截器 - 統一錯誤處理
api.interceptors.response.use(
  (response) => {
    // 記錄成功的響應
    console.log('[API Success]', response.config.url, {
      status: response.status,
      data: response.data
    })
    return response.data
  },
  (error: any) => {
    // 如果是 401 错误且没有认证信息，静默处理（不显示错误）
    // 这通常发生在未登录时尝试访问需要认证的 API
    if (error.response?.status === 401) {
      const token = localStorage.getItem('auth_token')
      const initData = getInitData()
      if (!token && (!initData || initData.length === 0)) {
        // 没有认证信息，这是正常的，静默处理
        if (import.meta.env.DEV) {
          console.debug('[API] 401 Unauthorized - 未提供认证信息（这是正常的）')
        }
        // 返回一个特殊的错误对象，让调用者知道这是未认证的情况
        const silentError = new Error('Unauthorized')
        ;(silentError as any).isUnauthorized = true
        ;(silentError as any).response = error.response
        return Promise.reject(silentError)
      }
    }
    
    let message = '請求失敗'
    if (error.response?.data?.detail) {
      message = typeof error.response.data.detail === 'string' 
        ? error.response.data.detail 
        : JSON.stringify(error.response.data.detail)
    } else if (error.message) {
      message = typeof error.message === 'string' ? error.message : String(error.message)
    }
    console.error('[API Error]', error.config?.url, message, error.response?.data)
    // 對於搜索 API，如果返回空數組，不應該視為錯誤
    if (error.config?.url?.includes('/search') && error.response?.status === 200) {
      return []
    }
    return Promise.reject(new Error(message))
  }
)

export default api

// ============ Web认证相关 API ============

export interface GoogleAuthRequest {
  id_token: string
  email?: string
  given_name?: string
  family_name?: string
  picture?: string
}

export interface WalletAuthRequest {
  address: string
  network?: string
  signature?: string
  message?: string
}

export interface MagicLinkVerifyRequest {
  token: string
}

export interface AuthResponse {
  access_token: string
  token_type: string
  user: {
    id: number
    uuid?: string
    tg_id?: number
    username?: string
    first_name?: string
    last_name?: string
    wallet_address?: string
    wallet_network?: string
    primary_platform?: string
  }
}

// Google OAuth登录
export async function googleAuth(request: GoogleAuthRequest): Promise<AuthResponse> {
  // api.interceptors.response 已经返回了 response.data
  // 所以 response 本身就是 AuthResponse 类型（不是 AxiosResponse）
  const response = await api.post<AuthResponse>('/v1/auth/web/google', request)
  return response as unknown as AuthResponse
}

// Wallet连接登录
export async function walletAuth(request: WalletAuthRequest): Promise<AuthResponse> {
  // api.interceptors.response 已经返回了 response.data
  // 所以 response 本身就是 AuthResponse 类型（不是 AxiosResponse）
  const response = await api.post<AuthResponse>('/v1/auth/web/wallet', request)
  return response as unknown as AuthResponse
}

// 验证Magic Link
export async function verifyMagicLink(token: string): Promise<AuthResponse> {
  // api.interceptors.response 已经返回了 response.data
  // 所以 response 本身就是 AuthResponse 类型（不是 AxiosResponse）
  const response = await api.post<AuthResponse>('/v1/auth/link/magic-link/verify', { token })
  return response as unknown as AuthResponse
}

// 生成Magic Link（需要Telegram认证）
export async function generateMagicLink(
  linkType: string = 'magic_login',
  expiresInHours: number = 24
): Promise<{ data: { token: string; link_url: string; expires_at: string } }> {
  return api.post('/v1/auth/link/magic-link/generate', {
    link_type: linkType,
    expires_in_hours: expiresInHours
  })
}

// 获取当前用户（支持JWT Token 和 Telegram initData）
// Auth API endpoints
export async function getCurrentUser(): Promise<{ data: any }> {
  // 始终使用 api 实例，让拦截器自动处理认证
  // 拦截器会优先使用 JWT Token，如果没有则使用 Telegram initData
  // 注意：响应拦截器返回的是 response.data，所以这里直接返回后端数据
  // 但为了保持类型一致性，我们包装成 { data: ... } 格式
  const result = await api.get('/v1/users/me')
  // 如果 result 已经是对象且包含 data 字段，直接返回
  // 否则包装成 { data: result } 格式
  if (result && typeof result === 'object' && 'data' in result) {
    return result as { data: any }
  }
  return { data: result }
}

// 导出api对象供useAuth使用
export { api }

// ============ 用戶相關 API ============

export interface UserProfile {
  id: number
  tg_id: number
  username: string | null
  first_name: string | null
  level: number
  xp: number
  energy_balance?: number
  created_at: string
}

export interface Balance {
  usdt: number
  ton: number
  stars: number
  points?: number
}

export async function getUserProfile(): Promise<UserProfile> {
  return api.get('/v1/users/me')
}

export async function getBalance(): Promise<Balance> {
  return api.get('/v1/users/me/balance')
}

// ============ 紅包相關 API ============

export interface RedPacket {
  id: string
  uuid?: string  // 添加 uuid 字段
  sender_id: number
  sender_name: string
  amount: number
  currency: string
  quantity: number
  remaining: number
  type: 'random' | 'fixed'
  message: string
  status: 'active' | 'completed' | 'expired'
  created_at: string
  expires_at: string
  message_sent?: boolean  // 消息是否成功發送到群組
  share_link?: string  // 分享鏈接（如果機器人不在群組中）
  is_claimed?: boolean  // 當前用戶是否已領取
}

export interface SendRedPacketParams {
  chat_id: number | null  // null 表示发送到公开页面
  amount: number
  currency: string
  quantity: number
  type: 'random' | 'fixed'
  message?: string
  bomb_number?: number  // 0-9, 仅当 type='fixed' 时有效
  chat_title?: string  // 群组/用户名称（可选）
}

export async function listRedPackets(): Promise<RedPacket[]> {
  try {
    const result = await api.get('/v1/redpackets')
    return Array.isArray(result) ? result : []
  } catch (error: any) {
    console.error('[listRedPackets] Error:', error)
    // 返回空數組而不是拋出錯誤
    return []
  }
}

export async function getRedPacket(id: string): Promise<RedPacket> {
  return api.get(`/v1/redpackets/${id}`)
}

export async function sendRedPacket(params: SendRedPacketParams): Promise<RedPacket> {
  // 轉換參數格式以匹配後端 API
  // 將 currency 轉換為小寫（後端期望小寫：usdt, ton, stars, points）
  const currency = (params.currency || 'USDT').toLowerCase()
  const requestBody: any = {
    currency: currency,
    packet_type: params.type || 'random',
    total_amount: params.amount,
    total_count: params.quantity,
    message: params.message || '恭喜發財！🧧',
    // chat_id 為 null 時表示公開紅包，會顯示在公開紅包頁面
    // chat_id 有值時表示私密紅包，只發送到指定群組或用戶
    chat_id: params.chat_id ?? null,
  }
  
  // 如果提供了 chat_title，添加到請求中
  if (params.chat_title) {
    requestBody.chat_title = params.chat_title
  }
  
  // 如果提供了 bomb_number，添加到請求中
  if (params.bomb_number !== undefined) {
    requestBody.bomb_number = params.bomb_number
  }
  
  console.log('[sendRedPacket] Sending request:', requestBody)
  console.log('[sendRedPacket] 紅包類型:', params.chat_id === null ? '公開紅包' : '私密紅包')
  console.log('[sendRedPacket] chat_id 詳情:', {
    original: params.chat_id,
    type: typeof params.chat_id,
    isNull: params.chat_id === null,
    isUndefined: params.chat_id === undefined,
    inRequestBody: requestBody.chat_id,
    requestBodyType: typeof requestBody.chat_id
  })
  return api.post('/redpackets/create', requestBody)
}

export async function claimRedPacket(id: string): Promise<{ success: boolean; amount: number; is_luckiest: boolean; message: string }> {
  try {
    console.log('[claimRedPacket] 開始搶紅包:', id)
    const response = await api.post(`/v1/redpackets/${id}/claim`)
    console.log('[claimRedPacket] API 響應:', response)
    
    // Axios 返回的是 AxiosResponse，需要访问 data 属性
    const result = response.data as any
    console.log('[claimRedPacket] 解析後的結果:', result)
    
    // 確保返回格式正確
    if (result && typeof result === 'object') {
      const claimResult = {
        success: result.success ?? true,
        amount: result.amount ?? 0,
        is_luckiest: result.is_luckiest ?? false,
        message: result.message || '領取成功'
      }
      console.log('[claimRedPacket] 最終返回:', claimResult)
      return claimResult
    }
    
    // 如果返回格式不對，返回默認值
    console.error('[claimRedPacket] 返回格式錯誤:', result)
    return {
      success: false,
      amount: 0,
      is_luckiest: false,
      message: '領取失敗：返回數據格式錯誤'
    }
  } catch (error: any) {
    console.error('[claimRedPacket] 搶紅包失敗:', error)
    // 重新拋出錯誤，讓上層處理
    throw error
  }
}

// ============ 群組相關 API ============

export interface ChatInfo {
  id: number
  title: string
  type: string
  username?: string  // 群組或用戶名
  link?: string  // 群組鏈接（用於基於鏈接的群組）
  user_in_group?: boolean  // 用戶是否在群組中
  bot_in_group?: boolean  // Bot 是否在群組中
  status_message?: string  // 狀態提示信息
  last_used?: string  // 最後使用時間（用於歷史記錄）
}

export async function getUserChats(): Promise<ChatInfo[]> {
  return api.get('/v1/chats')
}

export async function searchChats(query: string, tgId?: number): Promise<ChatInfo[]> {
  // 處理群鏈接格式和 @ 開頭的格式
  let processedQuery = query.trim()
  
  // 處理 @ 開頭的格式（移除 @ 符號）
  if (processedQuery.startsWith('@')) {
    processedQuery = processedQuery.substring(1)
  }
  
  // 處理 t.me/ 鏈接格式
  if (processedQuery.includes('t.me/')) {
    const match = processedQuery.match(/t\.me\/([^/?]+)/)
    if (match) {
      processedQuery = match[1]
    }
  }
  
  // 如果處理後的查詢為空，使用原始查詢
  if (!processedQuery) {
    processedQuery = query.trim()
  }
  
  // 獲取用戶 ID（優先使用傳入的參數，否則從 Telegram WebApp 獲取）
  const userId = tgId || getTelegramUser()?.id
  
  // 構建查詢參數 - 使用完整鏈接格式以便後端正確識別
  let finalQuery = processedQuery
  // 如果查詢看起來像 username（不包含空格和特殊字符），嘗試構建完整鏈接
  if (!finalQuery.includes('://') && !finalQuery.includes('t.me/') && /^[a-zA-Z0-9_]+$/.test(finalQuery)) {
    // 對於純 username，後端會自動處理，這裡保持原樣
    finalQuery = processedQuery
  }
  
  const params = new URLSearchParams({ q: finalQuery })
  if (userId) {
    params.append('tg_id', userId.toString())
  }
  
  try {
    const result = await api.get(`/v1/chats/search?${params.toString()}`)
    console.log('[searchChats] API response:', result)
    // 確保返回的是數組
    return Array.isArray(result) ? result : []
  } catch (error: any) {
    console.error('[searchChats] API error:', error)
    // 如果錯誤是空結果，返回空數組而不是拋出錯誤
    if (error.message?.includes('not found') || error.response?.status === 404) {
      return []
    }
    throw error
  }
}

export async function searchUsers(query: string, tgId?: number): Promise<ChatInfo[]> {
  // 處理用戶名格式（移除 @ 符號）
  let processedQuery = query.trim().replace(/^@/, '')
  // 如果是群鏈接，也嘗試提取用戶名
  if (query.includes('t.me/')) {
    const match = query.match(/t\.me\/([^/?]+)/)
    if (match) {
      processedQuery = match[1]
    }
  }
  
  // 獲取用戶 ID（優先使用傳入的參數，否則從 Telegram WebApp 獲取）
  const userId = tgId || getTelegramUser()?.id
  
  // 構建查詢參數
  const params = new URLSearchParams({ q: processedQuery })
  if (userId) {
    params.append('tg_id', userId.toString())
  }
  
  try {
    const result = await api.get(`/v1/chats/users/search?${params.toString()}`)
    console.log('[searchUsers] API response:', result)
    // 確保返回的是數組
    return Array.isArray(result) ? result : []
  } catch (error: any) {
    console.error('[searchUsers] API error:', error)
    // 如果錯誤是空結果，返回空數組而不是拋出錯誤
    if (error.message?.includes('not found') || error.response?.status === 404) {
      return []
    }
    throw error
  }
}

export async function checkUserInChat(chatId: number, link?: string, tgId?: number): Promise<{ in_group: boolean; message?: string }> {
  const params: Record<string, string> = {}
  if (link) {
    params.link = link
  }
  // 獲取用戶 ID（優先使用傳入的參數，否則從 Telegram WebApp 獲取）
  const userId = tgId || getTelegramUser()?.id
  if (userId) {
    params.tg_id = userId.toString()
  }
  return api.get(`/v1/chats/${chatId}/check`, { params })
}

// ============ 簽到相關 API ============

export interface CheckInResult {
  success: boolean
  reward: number
  streak: number
  message: string
}

export async function checkIn(): Promise<CheckInResult> {
  return api.post('/v1/checkin')
}

export async function getCheckInStatus(): Promise<{
  checked_today: boolean
  streak: number
  last_check_in: string | null
}> {
  return api.get('/v1/checkin/status')
}

// ============ 錢包相關 API ============

export async function createRechargeOrder(amount: number, currency: string): Promise<{
  order_id: string
  status: string
  payment_url?: string
}> {
  return api.post('/v1/wallet/recharge', { amount, currency })
}

export async function createWithdrawOrder(amount: number, currency: string, address: string): Promise<{
  order_id: string
  status: string
}> {
  return api.post('/v1/wallet/withdraw', { amount, currency, address })
}

// ============ 兌換相關 API ============

export interface ExchangeRequest {
  from_currency: string
  to_currency: string
  amount: number
}

export interface ExchangeResponse {
  success: boolean
  from_currency: string
  to_currency: string
  from_amount: number
  to_amount: number
  exchange_rate: number
  transaction_id: number
  message: string
}

export async function exchangeCurrency(request: ExchangeRequest): Promise<ExchangeResponse> {
  return api.post('/exchange', request)
}

export interface ExchangeRateRequest {
  from_currency: string
  to_currency: string
}

export interface ExchangeRateResponse {
  from_currency: string
  to_currency: string
  rate: number
  source: 'market' | 'fixed'
  updated_at?: string
}

export async function getExchangeRate(request: ExchangeRateRequest): Promise<ExchangeRateResponse> {
  return api.get('/exchange/rate', {
    params: {
      from_currency: request.from_currency,
      to_currency: request.to_currency
    }
  })
}

// ============ 消息相關 API ============

export interface Message {
  id: number
  message_type: string
  status: string
  title?: string
  content: string
  action_url?: string
  source?: string
  source_name?: string
  can_reply: boolean
  meta_data?: Record<string, any>  // 使用 meta_data 而不是 metadata
  created_at: string
  read_at?: string
  reply_to_id?: number
}

export interface MessageListResponse {
  total: number
  page: number
  limit: number
  unread_count: number
  messages: Message[]
}

export interface UnreadCountResponse {
  unread_count: number
  unread_by_type: Record<string, number>
}

export interface NotificationSettings {
  notification_method: string
  enable_system: boolean
  enable_redpacket: boolean
  enable_balance: boolean
  enable_activity: boolean
  enable_miniapp: boolean
  enable_telegram: boolean
}

export async function getMessages(params?: {
  message_type?: string
  status?: string
  page?: number
  limit?: number
}): Promise<MessageListResponse> {
  const queryParams = new URLSearchParams()
  if (params?.message_type) queryParams.append('message_type', params.message_type)
  if (params?.status) queryParams.append('status', params.status)
  if (params?.page) queryParams.append('page', params.page.toString())
  if (params?.limit) queryParams.append('limit', params.limit.toString())
  
  const query = queryParams.toString()
  // 如果沒有認證信息，返回空結果（本地測試）
  try {
    return await api.get(`/v1/messages/${query ? '?' + query : ''}`)
  } catch (error: any) {
    // 如果是認證錯誤，返回空結果
    if (error.message?.includes('Unauthorized') || error.response?.status === 401) {
      return {
        total: 0,
        page: 1,
        limit: params?.limit || 20,
        unread_count: 0,
        messages: []
      }
    }
    throw error
  }
}

export async function getUnreadCount(): Promise<UnreadCountResponse> {
  try {
    return await api.get('/v1/messages/unread-count')
  } catch (error: any) {
    // 如果是認證錯誤，返回空結果
    if (error.message?.includes('Unauthorized') || error.response?.status === 401) {
      return {
        unread_count: 0,
        unread_by_type: {}
      }
    }
    throw error
  }
}

export async function getMessage(messageId: number): Promise<Message> {
  return api.get(`/v1/messages/${messageId}`)
}

export async function markMessageAsRead(messageId: number): Promise<{ success: boolean }> {
  return api.put(`/v1/messages/${messageId}/read`)
}

export async function deleteMessage(messageId: number): Promise<{ success: boolean }> {
  return api.delete(`/v1/messages/${messageId}`)
}

export async function replyMessage(messageId: number, content: string): Promise<Message> {
  return api.post(`/v1/messages/${messageId}/reply`, { content })
}

export async function getNotificationSettings(): Promise<NotificationSettings> {
  return api.get('/v1/messages/settings')
}

export async function updateNotificationSettings(settings: Partial<NotificationSettings>): Promise<NotificationSettings> {
  return api.put('/v1/messages/settings', settings)
}

// ============ 邀請相關 API ============

export interface InviteStats {
  invite_code: string
  invite_count: number
  invite_earnings: number
  invite_link: string
  next_milestone: number | null
  next_milestone_reward: number | null
  progress_to_next: number
  invitees: {
    tg_id: number
    username: string | null
    first_name: string | null
    joined_at: string | null
  }[]
}

export interface InviteMilestone {
  target: number
  reward: number
  achieved: boolean
}

export async function getInviteStats(): Promise<InviteStats> {
  try {
    const result = await api.get('/v1/users/me/invite')
    return result as unknown as InviteStats
  } catch (error: any) {
    // 如果 API 不存在，返回默認數據
    console.error('[getInviteStats] Error:', error)
    return {
      invite_code: '',
      invite_count: 0,
      invite_earnings: 0,
      invite_link: '',
      next_milestone: 5,
      next_milestone_reward: 5,
      progress_to_next: 0,
      invitees: []
    }
  }
}

export async function generateInviteCode(): Promise<{ invite_code: string; invite_link: string }> {
  return api.post('/v1/users/me/invite/generate')
}

// 任務相關 API
export interface TaskStatus {
  task_type: string
  task_name: string
  task_description: string
  completed: boolean
  can_claim: boolean
  progress: {
    current: number
    target: number
    completed: boolean
  }
  reward_amount: number
  reward_currency: string
  red_packet_id?: string
  completed_at?: string
  claimed_at?: string
}

export async function getTaskStatus(): Promise<TaskStatus[]> {
  return api.get('/v1/tasks/status')
}

export async function claimTaskPacket(taskType: string): Promise<{ success: boolean; amount: number; currency: string; message: string }> {
  return api.post(`/v1/tasks/${taskType}/claim`)
}

export async function recordShare(): Promise<{ success: boolean; share_count: number; message: string }> {
  return api.post('/v1/share/record')
}

export async function getRecommendedPackets(): Promise<RedPacket[]> {
  return api.get('/v1/redpackets/recommended')
}

// ============ 推荐系统 API ============

export interface ReferralStats {
  tier1_count: number
  tier2_count: number
  total_referrals: number
  total_reward: string
  reward_count: number
  tier1_reward: string
  tier2_reward: string
}

export interface ReferralTreeNode {
  user_id: number
  username: string | null
  referral_code: string | null
  referrals: ReferralTreeNode[]
}

export async function getReferralStats(): Promise<ReferralStats> {
  return api.get('/v1/users/me/referral/stats')
}

export async function getReferralTree(): Promise<ReferralTreeNode> {
  return api.get('/v1/users/me/referral/tree')
}

export const INVITE_MILESTONES: InviteMilestone[] = [
  { target: 5, reward: 5, achieved: false },
  { target: 10, reward: 15, achieved: false },
  { target: 25, reward: 50, achieved: false },
  { target: 50, reward: 150, achieved: false },
  { target: 100, reward: 500, achieved: false },
]

// ============ 用户反馈 API ============

export interface FeedbackRequest {
  type: 'bug' | 'feature' | 'suggestion' | 'other'
  title: string
  content: string
  contact?: string
  screenshot_url?: string
}

export interface FeedbackResponse {
  success: boolean
  feedback_id: number
  message: string
}

export async function submitFeedback(request: FeedbackRequest): Promise<FeedbackResponse> {
  return api.post('/v1/feedback/submit', request)
}

export async function getFeedbackTypes(): Promise<{ types: Array<{ value: string; label: string }> }> {
  return api.get('/v1/feedback/types')
}

