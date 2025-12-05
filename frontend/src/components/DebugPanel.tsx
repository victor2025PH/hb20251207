/**
 * Telegram MiniApp 調試面板
 * 在 URL 後加 #debug=1 啟用
 * 例如：https://mini.usdt2026.cc/lucky-wheel#debug=1
 */
import { useState, useEffect, useRef } from 'react'
import { X, Bug, Terminal, AlertCircle, Globe, Database, ChevronDown, ChevronUp, Trash2 } from 'lucide-react'

interface LogEntry {
  type: 'log' | 'error' | 'warn' | 'info'
  message: string
  timestamp: Date
}

interface NetworkEntry {
  method: string
  url: string
  status?: number
  duration?: number
  timestamp: Date
}

export default function DebugPanel() {
  const [isEnabled, setIsEnabled] = useState(false)
  const [isExpanded, setIsExpanded] = useState(true)
  const [activeTab, setActiveTab] = useState<'console' | 'network' | 'storage' | 'info'>('console')
  const [logs, setLogs] = useState<LogEntry[]>([])
  const [networks, setNetworks] = useState<NetworkEntry[]>([])
  const [storage, setStorage] = useState<Record<string, string>>({})
  const logsEndRef = useRef<HTMLDivElement>(null)

  // 檢查是否啟用調試模式
  useEffect(() => {
    const checkDebugMode = () => {
      const hash = window.location.hash
      const enabled = hash.includes('debug=1')
      setIsEnabled(enabled)
      if (enabled) {
        console.log('[DebugPanel] Debug mode enabled')
      }
    }
    
    checkDebugMode()
    window.addEventListener('hashchange', checkDebugMode)
    return () => window.removeEventListener('hashchange', checkDebugMode)
  }, [])

  // 攔截 console
  useEffect(() => {
    if (!isEnabled) return

    const originalLog = console.log
    const originalError = console.error
    const originalWarn = console.warn
    const originalInfo = console.info

    const addLog = (type: LogEntry['type'], args: any[]) => {
      const message = args.map(arg => {
        if (typeof arg === 'object') {
          try {
            return JSON.stringify(arg, null, 2)
          } catch {
            return String(arg)
          }
        }
        return String(arg)
      }).join(' ')

      setLogs(prev => [...prev.slice(-100), { type, message, timestamp: new Date() }])
    }

    console.log = (...args) => {
      originalLog.apply(console, args)
      addLog('log', args)
    }
    console.error = (...args) => {
      originalError.apply(console, args)
      addLog('error', args)
    }
    console.warn = (...args) => {
      originalWarn.apply(console, args)
      addLog('warn', args)
    }
    console.info = (...args) => {
      originalInfo.apply(console, args)
      addLog('info', args)
    }

    // 捕獲未處理的錯誤
    const errorHandler = (event: ErrorEvent) => {
      addLog('error', [`Uncaught Error: ${event.message} at ${event.filename}:${event.lineno}`])
    }
    window.addEventListener('error', errorHandler)

    // 捕獲 Promise 錯誤
    const rejectionHandler = (event: PromiseRejectionEvent) => {
      addLog('error', [`Unhandled Promise Rejection: ${event.reason}`])
    }
    window.addEventListener('unhandledrejection', rejectionHandler)

    return () => {
      console.log = originalLog
      console.error = originalError
      console.warn = originalWarn
      console.info = originalInfo
      window.removeEventListener('error', errorHandler)
      window.removeEventListener('unhandledrejection', rejectionHandler)
    }
  }, [isEnabled])

  // 攔截 fetch
  useEffect(() => {
    if (!isEnabled) return

    const originalFetch = window.fetch
    window.fetch = async (...args) => {
      const url = typeof args[0] === 'string' ? args[0] : (args[0] as Request).url
      const method = (args[1]?.method || 'GET').toUpperCase()
      const startTime = Date.now()

      const entry: NetworkEntry = {
        method,
        url: url.length > 50 ? url.substring(0, 50) + '...' : url,
        timestamp: new Date(),
      }

      try {
        const response = await originalFetch.apply(window, args)
        entry.status = response.status
        entry.duration = Date.now() - startTime
        setNetworks(prev => [...prev.slice(-50), entry])
        return response
      } catch (error) {
        entry.status = 0
        entry.duration = Date.now() - startTime
        setNetworks(prev => [...prev.slice(-50), entry])
        throw error
      }
    }

    return () => {
      window.fetch = originalFetch
    }
  }, [isEnabled])

  // 讀取 localStorage
  useEffect(() => {
    if (!isEnabled) return
    
    const readStorage = () => {
      const items: Record<string, string> = {}
      for (let i = 0; i < localStorage.length; i++) {
        const key = localStorage.key(i)
        if (key) {
          const value = localStorage.getItem(key) || ''
          items[key] = value.length > 100 ? value.substring(0, 100) + '...' : value
        }
      }
      setStorage(items)
    }

    readStorage()
    const interval = setInterval(readStorage, 2000)
    return () => clearInterval(interval)
  }, [isEnabled])

  // 自動滾動到底部
  useEffect(() => {
    if (activeTab === 'console' && logsEndRef.current) {
      logsEndRef.current.scrollIntoView({ behavior: 'smooth' })
    }
  }, [logs, activeTab])

  if (!isEnabled) return null

  const telegramInfo = {
    platform: window.Telegram?.WebApp?.platform || 'N/A',
    version: window.Telegram?.WebApp?.version || 'N/A',
    initData: window.Telegram?.WebApp?.initData ? '✅ Present' : '❌ Missing',
    user: window.Telegram?.WebApp?.initDataUnsafe?.user?.id || 'N/A',
    colorScheme: window.Telegram?.WebApp?.colorScheme || 'N/A',
  }

  const getLogColor = (type: LogEntry['type']) => {
    switch (type) {
      case 'error': return 'text-red-400 bg-red-500/10'
      case 'warn': return 'text-yellow-400 bg-yellow-500/10'
      case 'info': return 'text-blue-400 bg-blue-500/10'
      default: return 'text-gray-300'
    }
  }

  return (
    <div className="fixed bottom-0 left-0 right-0 z-[9999] bg-black/95 backdrop-blur border-t border-green-500/30 text-xs font-mono">
      {/* 標題欄 */}
      <div 
        className="flex items-center justify-between px-3 py-2 bg-green-500/20 cursor-pointer"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <div className="flex items-center gap-2 text-green-400">
          <Bug size={14} />
          <span className="font-bold">Debug Panel</span>
          <span className="text-green-400/60">#{window.location.pathname}</span>
        </div>
        <div className="flex items-center gap-2">
          {isExpanded ? <ChevronDown size={14} /> : <ChevronUp size={14} />}
          <button
            onClick={(e) => {
              e.stopPropagation()
              window.location.hash = ''
              setIsEnabled(false)
            }}
            className="p-1 hover:bg-white/10 rounded"
          >
            <X size={14} />
          </button>
        </div>
      </div>

      {isExpanded && (
        <>
          {/* Tab 欄 */}
          <div className="flex border-b border-gray-700">
            {[
              { id: 'console', icon: Terminal, label: 'Console', count: logs.length },
              { id: 'network', icon: Globe, label: 'Network', count: networks.length },
              { id: 'storage', icon: Database, label: 'Storage', count: Object.keys(storage).length },
              { id: 'info', icon: AlertCircle, label: 'Info' },
            ].map(tab => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`flex items-center gap-1 px-3 py-1.5 border-b-2 transition-colors ${
                  activeTab === tab.id
                    ? 'border-green-500 text-green-400 bg-green-500/10'
                    : 'border-transparent text-gray-500 hover:text-gray-300'
                }`}
              >
                <tab.icon size={12} />
                <span>{tab.label}</span>
                {tab.count !== undefined && (
                  <span className="text-[10px] bg-gray-700 px-1 rounded">{tab.count}</span>
                )}
              </button>
            ))}
          </div>

          {/* 內容區 */}
          <div className="h-40 overflow-y-auto">
            {activeTab === 'console' && (
              <div className="p-2 space-y-1">
                {logs.length === 0 ? (
                  <div className="text-gray-500 text-center py-4">No logs yet</div>
                ) : (
                  <>
                    <button
                      onClick={() => setLogs([])}
                      className="flex items-center gap-1 text-gray-500 hover:text-gray-300 mb-2"
                    >
                      <Trash2 size={12} /> Clear
                    </button>
                    {logs.map((log, i) => (
                      <div key={i} className={`px-2 py-1 rounded ${getLogColor(log.type)}`}>
                        <span className="text-gray-500">{log.timestamp.toLocaleTimeString()}</span>
                        <span className="ml-2">{log.message}</span>
                      </div>
                    ))}
                    <div ref={logsEndRef} />
                  </>
                )}
              </div>
            )}

            {activeTab === 'network' && (
              <div className="p-2">
                {networks.length === 0 ? (
                  <div className="text-gray-500 text-center py-4">No network requests yet</div>
                ) : (
                  <table className="w-full">
                    <thead>
                      <tr className="text-gray-500 text-left">
                        <th className="px-2 py-1">Method</th>
                        <th className="px-2 py-1">URL</th>
                        <th className="px-2 py-1">Status</th>
                        <th className="px-2 py-1">Time</th>
                      </tr>
                    </thead>
                    <tbody>
                      {networks.map((net, i) => (
                        <tr key={i} className={net.status && net.status >= 400 ? 'text-red-400' : 'text-gray-300'}>
                          <td className="px-2 py-1 text-blue-400">{net.method}</td>
                          <td className="px-2 py-1 truncate max-w-[150px]">{net.url}</td>
                          <td className="px-2 py-1">{net.status || 'ERR'}</td>
                          <td className="px-2 py-1">{net.duration}ms</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                )}
              </div>
            )}

            {activeTab === 'storage' && (
              <div className="p-2">
                {Object.keys(storage).length === 0 ? (
                  <div className="text-gray-500 text-center py-4">No localStorage items</div>
                ) : (
                  <table className="w-full">
                    <thead>
                      <tr className="text-gray-500 text-left">
                        <th className="px-2 py-1">Key</th>
                        <th className="px-2 py-1">Value</th>
                      </tr>
                    </thead>
                    <tbody>
                      {Object.entries(storage).map(([key, value]) => (
                        <tr key={key} className="text-gray-300">
                          <td className="px-2 py-1 text-cyan-400">{key}</td>
                          <td className="px-2 py-1 truncate max-w-[200px]">{value}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                )}
              </div>
            )}

            {activeTab === 'info' && (
              <div className="p-3 space-y-2">
                <h3 className="text-green-400 font-bold mb-2">Telegram WebApp Info</h3>
                {Object.entries(telegramInfo).map(([key, value]) => (
                  <div key={key} className="flex justify-between">
                    <span className="text-gray-500">{key}:</span>
                    <span className="text-gray-300">{value}</span>
                  </div>
                ))}
                <hr className="border-gray-700 my-2" />
                <div className="flex justify-between">
                  <span className="text-gray-500">URL:</span>
                  <span className="text-gray-300 truncate max-w-[200px]">{window.location.href}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500">User Agent:</span>
                  <span className="text-gray-300 truncate max-w-[200px]">{navigator.userAgent.slice(0, 50)}...</span>
                </div>
              </div>
            )}
          </div>
        </>
      )}
    </div>
  )
}

