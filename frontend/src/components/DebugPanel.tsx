/**
 * 调试面板组件
 * 在 Telegram MiniApp 中显示调试信息，无需开发者工具
 */
import { useState, useEffect } from 'react';
import { getInitData, getTelegramUser, initTelegram } from '../utils/telegram';
import { isInTelegram } from '../utils/platform';

interface DebugInfo {
  timestamp: string;
  type: 'info' | 'warning' | 'error' | 'success';
  message: string;
  data?: any;
}

export default function DebugPanel() {
  const [isOpen, setIsOpen] = useState(false);
  const [logs, setLogs] = useState<DebugInfo[]>([]);
  const [telegramInfo, setTelegramInfo] = useState<any>(null);
  const [apiRequests, setApiRequests] = useState<any[]>([]);

  useEffect(() => {
    // 只在开发环境或 URL 参数包含 debug=true 时显示
    const urlParams = new URLSearchParams(window.location.search);
    const isDebugMode = import.meta.env.DEV || urlParams.get('debug') === 'true';
    
    if (!isDebugMode) {
      return;
    }

    // 初始化 Telegram 信息
    const updateTelegramInfo = async () => {
      await initTelegram();
      const initData = getInitData();
      const user = getTelegramUser();
      
      setTelegramInfo({
        hasWebApp: !!window.Telegram?.WebApp,
        platform: window.Telegram?.WebApp?.platform,
        version: window.Telegram?.WebApp?.version,
        hasInitData: !!initData,
        initDataLength: initData?.length || 0,
        initDataPreview: initData ? initData.substring(0, 100) + '...' : 'empty',
        user: user ? {
          id: user.id,
          username: user.username,
          first_name: user.first_name,
          last_name: user.last_name,
        } : null,
        fullInitData: initData || 'empty',
      });
    };

    updateTelegramInfo();

    // 拦截 console.log 来捕获日志
    const originalLog = console.log;
    const originalWarn = console.warn;
    const originalError = console.error;

    console.log = (...args: any[]) => {
      originalLog.apply(console, args);
      if (args[0]?.includes?.('[Auth]') || args[0]?.includes?.('[API') || args[0]?.includes?.('[Telegram]')) {
        addLog('info', args.join(' '), args);
      }
    };

    console.warn = (...args: any[]) => {
      originalWarn.apply(console, args);
      if (args[0]?.includes?.('[Auth]') || args[0]?.includes?.('[API') || args[0]?.includes?.('[Telegram]')) {
        addLog('warning', args.join(' '), args);
      }
    };

    console.error = (...args: any[]) => {
      originalError.apply(console, args);
      addLog('error', args.join(' '), args);
    };

    // 拦截 API 请求
    const originalFetch = window.fetch;
    window.fetch = async (...args: any[]) => {
      const url = args[0];
      const options = args[1] || {};
      const headers = options.headers || {};
      
      setApiRequests(prev => [...prev, {
        url,
        method: options.method || 'GET',
        headers: headers,
        timestamp: new Date().toISOString(),
      }]);

      try {
        const response = await originalFetch.apply(window, args);
        return response;
      } catch (error) {
        addLog('error', `API Request failed: ${url}`, error);
        throw error;
      }
    };

    return () => {
      console.log = originalLog;
      console.warn = originalWarn;
      console.error = originalError;
      window.fetch = originalFetch;
    };
  }, []);

  const addLog = (type: DebugInfo['type'], message: string, data?: any) => {
    setLogs(prev => [...prev, {
      timestamp: new Date().toLocaleTimeString(),
      type,
      message,
      data,
    }].slice(-50)); // 只保留最近50条
  };

  // 只在开发环境或 debug=true 时显示
  const urlParams = new URLSearchParams(window.location.search);
  const isDebugMode = import.meta.env.DEV || urlParams.get('debug') === 'true';
  
  if (!isDebugMode) {
    return null;
  }

  return (
    <>
      {/* 浮动按钮 */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        style={{
          position: 'fixed',
          bottom: '80px',
          right: '20px',
          width: '50px',
          height: '50px',
          borderRadius: '50%',
          backgroundColor: '#007bff',
          color: 'white',
          border: 'none',
          cursor: 'pointer',
          zIndex: 9999,
          fontSize: '20px',
          boxShadow: '0 2px 10px rgba(0,0,0,0.3)',
        }}
        title="调试面板"
      >
        🐛
      </button>

      {/* 调试面板 */}
      {isOpen && (
        <div
          style={{
            position: 'fixed',
            top: '0',
            left: '0',
            right: '0',
            bottom: '0',
            backgroundColor: 'rgba(0,0,0,0.8)',
            zIndex: 10000,
            padding: '20px',
            overflow: 'auto',
            color: 'white',
            fontSize: '12px',
          }}
        >
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '20px' }}>
            <h2 style={{ margin: 0 }}>🐛 调试面板</h2>
            <button
              onClick={() => setIsOpen(false)}
              style={{
                backgroundColor: '#dc3545',
                color: 'white',
                border: 'none',
                padding: '5px 15px',
                borderRadius: '5px',
                cursor: 'pointer',
              }}
            >
              关闭
            </button>
          </div>

          {/* Telegram 信息 */}
          <div style={{ marginBottom: '20px', padding: '15px', backgroundColor: '#1a1a1a', borderRadius: '5px' }}>
            <h3 style={{ marginTop: 0 }}>📱 Telegram 信息</h3>
            <pre style={{ whiteSpace: 'pre-wrap', wordBreak: 'break-all' }}>
              {JSON.stringify(telegramInfo, null, 2)}
            </pre>
          </div>

          {/* 环境信息 */}
          <div style={{ marginBottom: '20px', padding: '15px', backgroundColor: '#1a1a1a', borderRadius: '5px' }}>
            <h3 style={{ marginTop: 0 }}>🌐 环境信息</h3>
            <div>
              <div>URL: {window.location.href}</div>
              <div>User Agent: {navigator.userAgent}</div>
              <div>在 Telegram 中: {isInTelegram() ? '✅ 是' : '❌ 否'}</div>
              <div>JWT Token: {localStorage.getItem('auth_token') ? '✅ 存在' : '❌ 不存在'}</div>
            </div>
          </div>

          {/* API 请求 */}
          <div style={{ marginBottom: '20px', padding: '15px', backgroundColor: '#1a1a1a', borderRadius: '5px' }}>
            <h3 style={{ marginTop: 0 }}>📡 最近的 API 请求 ({apiRequests.length})</h3>
            <div style={{ maxHeight: '200px', overflow: 'auto' }}>
              {apiRequests.slice(-10).map((req, idx) => (
                <div key={idx} style={{ marginBottom: '10px', padding: '10px', backgroundColor: '#2a2a2a', borderRadius: '3px' }}>
                  <div><strong>{req.method}</strong> {req.url}</div>
                  <div style={{ fontSize: '10px', color: '#aaa' }}>{req.timestamp}</div>
                  {req.headers && (
                    <details style={{ marginTop: '5px' }}>
                      <summary style={{ cursor: 'pointer' }}>Headers</summary>
                      <pre style={{ fontSize: '10px' }}>{JSON.stringify(req.headers, null, 2)}</pre>
                    </details>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* 日志 */}
          <div style={{ padding: '15px', backgroundColor: '#1a1a1a', borderRadius: '5px' }}>
            <h3 style={{ marginTop: 0 }}>📋 日志 ({logs.length})</h3>
            <div style={{ maxHeight: '300px', overflow: 'auto' }}>
              {logs.map((log, idx) => (
                <div
                  key={idx}
                  style={{
                    marginBottom: '5px',
                    padding: '5px',
                    backgroundColor: log.type === 'error' ? '#4a1a1a' : log.type === 'warning' ? '#4a4a1a' : '#1a1a2a',
                    borderRadius: '3px',
                    fontSize: '11px',
                  }}
                >
                  <span style={{ color: '#aaa' }}>[{log.timestamp}]</span>{' '}
                  <span style={{ color: log.type === 'error' ? '#ff6b6b' : log.type === 'warning' ? '#ffd93d' : '#6bcf7f' }}>
                    {log.type.toUpperCase()}
                  </span>{' '}
                  {log.message}
                  {log.data && (
                    <details style={{ marginTop: '5px' }}>
                      <summary style={{ cursor: 'pointer', fontSize: '10px' }}>详情</summary>
                      <pre style={{ fontSize: '10px', whiteSpace: 'pre-wrap' }}>
                        {JSON.stringify(log.data, null, 2)}
                      </pre>
                    </details>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* 操作按钮 */}
          <div style={{ marginTop: '20px', display: 'flex', gap: '10px' }}>
            <button
              onClick={() => {
                setLogs([]);
                setApiRequests([]);
              }}
              style={{
                backgroundColor: '#6c757d',
                color: 'white',
                border: 'none',
                padding: '10px 20px',
                borderRadius: '5px',
                cursor: 'pointer',
              }}
            >
              清空日志
            </button>
            <button
              onClick={() => {
                const data = {
                  telegramInfo,
                  logs,
                  apiRequests,
                  environment: {
                    url: window.location.href,
                    userAgent: navigator.userAgent,
                    isInTelegram: isInTelegram(),
                    hasToken: !!localStorage.getItem('auth_token'),
                  },
                };
                navigator.clipboard.writeText(JSON.stringify(data, null, 2));
                alert('调试信息已复制到剪贴板！');
              }}
              style={{
                backgroundColor: '#28a745',
                color: 'white',
                border: 'none',
                padding: '10px 20px',
                borderRadius: '5px',
                cursor: 'pointer',
              }}
            >
              复制调试信息
            </button>
          </div>
        </div>
      )}
    </>
  );
}
