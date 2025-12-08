/**
 * Web登录界面
 * 支持多种登录方式：Google、Telegram、Facebook、WhatsApp、Wallet、Magic Link
 */
import React, { useState, useEffect, useCallback } from 'react';
import { Globe, MessageCircle, Facebook, MessageSquare, Wallet, Key } from 'lucide-react';
import { googleAuth, walletAuth, verifyMagicLink, getCurrentUser } from '../utils/api';
import { useAuth } from '../utils/auth/useAuth';
import { getInitData, getTelegramUser } from '../utils/telegram';

interface WebLoginScreenProps {
  onLoginSuccess?: () => void;
}

// Google Client ID (硬编码)
const GOOGLE_CLIENT_ID = '853109842218-v250plv0gc9f3gl6tvbh3ltsckoj0156.apps.googleusercontent.com';

export function WebLoginScreen({ onLoginSuccess }: WebLoginScreenProps) {
  const { login, loginWithMagicLink } = useAuth();
  const [loading, setLoading] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [walletAddress, setWalletAddress] = useState('');
  const [magicLinkToken, setMagicLinkToken] = useState('');
  const [showDebug, setShowDebug] = useState(false);
  const [debugLogs, setDebugLogs] = useState<string[]>([]);
  const [telegramInfo, setTelegramInfo] = useState<any>(null);

  // 初始化调试信息
  useEffect(() => {
    const updateTelegramInfo = () => {
      const initData = getInitData();
      const user = getTelegramUser();
      const webApp = (window as any).Telegram?.WebApp;
      
      setTelegramInfo({
        hasWebApp: !!webApp,
        platform: webApp?.platform || 'unknown',
        version: webApp?.version || 'unknown',
        hasInitData: !!initData && initData.length > 0,
        initDataLength: initData?.length || 0,
        initDataPreview: initData ? initData.substring(0, 100) + '...' : 'empty',
        user: user ? {
          id: user.id,
          username: user.username,
          first_name: user.first_name,
        } : null,
      });
    };

    updateTelegramInfo();
    const interval = setInterval(updateTelegramInfo, 2000); // 每2秒更新一次

    // 拦截 console.log 来捕获关键日志
    const originalLog = console.log;
    const originalWarn = console.warn;
    const originalError = console.error;

    console.log = (...args: any[]) => {
      originalLog.apply(console, args);
      const message = args.map(a => typeof a === 'object' ? JSON.stringify(a) : String(a)).join(' ');
      if (message.includes('[Auth]') || message.includes('[Telegram]') || message.includes('[API')) {
        setDebugLogs(prev => [...prev.slice(-49), `[${new Date().toLocaleTimeString()}] ${message}`]);
      }
    };

    console.warn = (...args: any[]) => {
      originalWarn.apply(console, args);
      const message = args.map(a => typeof a === 'object' ? JSON.stringify(a) : String(a)).join(' ');
      if (message.includes('[Auth]') || message.includes('[Telegram]') || message.includes('[API')) {
        setDebugLogs(prev => [...prev.slice(-49), `[${new Date().toLocaleTimeString()}] ⚠️ ${message}`]);
      }
    };

    console.error = (...args: any[]) => {
      originalError.apply(console, args);
      const message = args.map(a => typeof a === 'object' ? JSON.stringify(a) : String(a)).join(' ');
      setDebugLogs(prev => [...prev.slice(-49), `[${new Date().toLocaleTimeString()}] ❌ ${message}`]);
    };

    return () => {
      clearInterval(interval);
      console.log = originalLog;
      console.warn = originalWarn;
      console.error = originalError;
    };
  }, []);

  // Google 登录成功回调
  const handleGoogleCredentialResponse = useCallback(async (response: any) => {
    console.log('[Google Login] Credential response received', { hasCredential: !!response.credential });
    setLoading('google');
    setError(null);
    try {
      // 解码 JWT Token 获取用户信息
      let userInfo: any = {};
      try {
        const payload = JSON.parse(atob(response.credential.split('.')[1]));
        userInfo = {
          email: payload.email,
          given_name: payload.given_name,
          family_name: payload.family_name,
          picture: payload.picture,
        };
        console.log('[Google Login] Decoded user info', { email: userInfo.email });
      } catch (e) {
        console.warn('Failed to decode Google token:', e);
      }

      // 发送 POST 请求到后端 /api/v1/auth/web/google
      console.log('[Google Login] Calling login function...');
      await login('google', {
        id_token: response.credential,
        email: userInfo.email,
        given_name: userInfo.given_name,
        family_name: userInfo.family_name,
        picture: userInfo.picture,
      });
      
      console.log('[Google Login] Login successful, waiting for state update...');
      // 等待状态更新完成
      await new Promise(resolve => setTimeout(resolve, 100));
      
      console.log('[Google Login] Calling onLoginSuccess callback...');
      if (onLoginSuccess) {
        onLoginSuccess();
      } else {
        console.warn('[Google Login] onLoginSuccess callback is not defined');
        // 如果没有回调，直接刷新页面
        window.location.reload();
      }
    } catch (err: any) {
      console.error('[Google Login] Login failed:', err);
      setError(err.message || 'Google登录失败');
      setLoading(null);
    }
  }, [login, onLoginSuccess]);

  // 初始化 Google Sign-In
  useEffect(() => {
    // 检查是否已加载 Google 脚本
    if (document.querySelector('script[src="https://accounts.google.com/gsi/client"]')) {
      // 脚本已存在，直接初始化
      if (window.google?.accounts?.id) {
        window.google.accounts.id.initialize({
          client_id: GOOGLE_CLIENT_ID,
          callback: handleGoogleCredentialResponse,
        });
      }
      return;
    }

    // 加载 Google GSI 脚本
    const script = document.createElement('script');
    script.src = 'https://accounts.google.com/gsi/client';
    script.async = true;
    script.defer = true;
    script.onload = () => {
      // 初始化 Google Sign-In
      if (window.google?.accounts?.id) {
        window.google.accounts.id.initialize({
          client_id: GOOGLE_CLIENT_ID,
          callback: handleGoogleCredentialResponse,
        });
      }
    };
    document.head.appendChild(script);

    return () => {
      // 不清理脚本，因为可能被其他组件使用
    };
  }, [handleGoogleCredentialResponse]);

  // Google登录按钮点击（触发 Google 登录流程）
  const handleGoogleLogin = async () => {
    setLoading('google');
    setError(null);
    try {
      if (window.google?.accounts?.id) {
        // 使用 Google One Tap 登录（弹出登录窗口）
        const googleAccounts = window.google.accounts;
        googleAccounts.id.prompt((notification: any) => {
          if (notification.isNotDisplayed()) {
            // One Tap 不可用，尝试使用弹出窗口
            if (!googleAccounts.oauth2) {
              setError('Google登录服务未加载，请刷新页面重试');
              setLoading(null);
              return;
            }
            const client = googleAccounts.oauth2.initTokenClient({
              client_id: GOOGLE_CLIENT_ID,
              scope: 'openid email profile',
              callback: async (tokenResponse: any) => {
                try {
                  // 使用 access_token 获取用户信息
                  const userInfoResponse = await fetch(
                    `https://www.googleapis.com/oauth2/v2/userinfo?access_token=${tokenResponse.access_token}`
                  );
                  const userInfo = await userInfoResponse.json();
                  
                  // OAuth2 流程：使用 access_token 获取用户信息后，直接使用降级登录
                  // 不发送 id_token（因为 access_token 不是 JWT 格式），后端会使用降级逻辑
                  await login('google', {
                    id_token: '', // 空字符串，触发后端降级逻辑
                    email: userInfo.email,
                    given_name: userInfo.given_name,
                    family_name: userInfo.family_name,
                    picture: userInfo.picture,
                  });
                  
                  // 等待状态更新完成
                  await new Promise(resolve => setTimeout(resolve, 100));
                  
                  onLoginSuccess?.();
                } catch (err: any) {
                  setError(err.message || 'Google登录失败');
                  setLoading(null);
                }
              },
            });
            client.requestAccessToken();
          } else if (notification.isSkippedMoment()) {
            // 用户跳过了 One Tap，使用弹出窗口
            if (!googleAccounts.oauth2) {
              setError('Google登录服务未加载，请刷新页面重试');
              setLoading(null);
              return;
            }
            const client = googleAccounts.oauth2.initTokenClient({
              client_id: GOOGLE_CLIENT_ID,
              scope: 'openid email profile',
              callback: async (tokenResponse: any) => {
                try {
                  const userInfoResponse = await fetch(
                    `https://www.googleapis.com/oauth2/v2/userinfo?access_token=${tokenResponse.access_token}`
                  );
                  const userInfo = await userInfoResponse.json();
                  
                  // OAuth2 流程：使用 access_token 获取用户信息后，直接使用降级登录
                  // 不发送 id_token（因为 access_token 不是 JWT 格式），后端会使用降级逻辑
                  await login('google', {
                    id_token: '', // 空字符串，触发后端降级逻辑
                    email: userInfo.email,
                    given_name: userInfo.given_name,
                    family_name: userInfo.family_name,
                    picture: userInfo.picture,
                  });
                  
                  // 等待状态更新完成
                  await new Promise(resolve => setTimeout(resolve, 100));
                  
                  onLoginSuccess?.();
                } catch (err: any) {
                  setError(err.message || 'Google登录失败');
                  setLoading(null);
                }
              },
            });
            client.requestAccessToken();
          }
        });
      } else {
        setError('Google登录服务未加载，请刷新页面重试');
        setLoading(null);
      }
    } catch (err: any) {
      setError(err.message || 'Google登录失败');
      setLoading(null);
    }
  };

  // Telegram登录（网页版）
  const handleTelegramLogin = async () => {
    setLoading('telegram');
    setError(null);
    try {
      // 检查是否有 Telegram WebApp 和有效的 initData
      const initData = getInitData();
      const tgUser = getTelegramUser();
      
      if (!initData || initData.length === 0) {
        // 如果没有 initData，说明不是在真正的 Telegram MiniApp 中
        setError('请在Telegram中打开此应用，或使用其他登录方式');
        setLoading(null);
        return;
      }
      
      if (!tgUser) {
        // 如果有 initData 但没有用户信息，可能是 initData 格式错误
        setError('Telegram用户信息不可用，请刷新页面重试或使用其他登录方式');
        setLoading(null);
        return;
      }
      
      // 如果有有效的 initData 和用户信息，尝试获取用户信息
      // 这应该由 AuthGuard 自动处理，但这里提供一个手动触发的方式
      try {
        const response = await getCurrentUser();
        // 如果成功，说明已经通过 Telegram 认证
        // 刷新页面以更新认证状态
        window.location.reload();
      } catch (err: any) {
        // 如果失败，检查错误类型
        if (err?.isUnauthorized || err?.response?.status === 401) {
          // initData 可能无效、已过期或 hash 验证失败
          setError('Telegram认证失败：initData无效或已过期，请刷新页面重试或使用其他登录方式');
        } else {
          setError(err?.message || 'Telegram登录失败，请重试');
        }
      }
    } catch (err: any) {
      setError(err.message || 'Telegram登录失败');
    } finally {
      setLoading(null);
    }
  };

  // Facebook登录（占位）
  const handleFacebookLogin = async () => {
    setLoading('facebook');
    setError(null);
    try {
      // TODO: 集成Facebook OAuth SDK
      setError('Facebook登录功能即将推出');
    } catch (err: any) {
      setError(err.message || 'Facebook登录失败');
    } finally {
      setLoading(null);
    }
  };

  // WhatsApp登录（占位）
  const handleWhatsAppLogin = async () => {
    setLoading('whatsapp');
    setError(null);
    try {
      // TODO: 集成WhatsApp OAuth SDK
      setError('WhatsApp登录功能即将推出');
    } catch (err: any) {
      setError(err.message || 'WhatsApp登录失败');
    } finally {
      setLoading(null);
    }
  };

  // Wallet连接
  const handleWalletConnect = async () => {
    if (!walletAddress) {
      setError('请输入钱包地址');
      return;
    }
    
    setLoading('wallet');
    setError(null);
    try {
      await login('wallet', {
        address: walletAddress,
        network: 'TON'
      });
      
      // 等待状态更新完成
      await new Promise(resolve => setTimeout(resolve, 100));
      
      onLoginSuccess?.();
    } catch (err: any) {
      setError(err.message || '钱包连接失败');
    } finally {
      setLoading(null);
    }
  };

  // Magic Link登录
  const handleMagicLinkLogin = async () => {
    if (!magicLinkToken) {
      setError('请输入Magic Link Token');
      return;
    }
    
    setLoading('magiclink');
    setError(null);
    try {
      await loginWithMagicLink(magicLinkToken);
      
      // 等待状态更新完成
      await new Promise(resolve => setTimeout(resolve, 100));
      
      onLoginSuccess?.();
    } catch (err: any) {
      setError(err.message || 'Magic Link验证失败');
    } finally {
      setLoading(null);
    }
  };

  return (
    <div className="web-login-screen">
      <div className="login-container">
        <h2>登录到红包游戏</h2>
        <p style={{ textAlign: 'center', color: '#666', fontSize: '0.9rem', marginBottom: '1.5rem' }}>
          选择一种登录方式
        </p>

        {/* 调试按钮 */}
        <button
          onClick={() => setShowDebug(!showDebug)}
          style={{
            position: 'absolute',
            top: '10px',
            right: '10px',
            padding: '5px 10px',
            fontSize: '12px',
            backgroundColor: '#666',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer',
            zIndex: 1000,
          }}
        >
          {showDebug ? '隐藏' : '显示'}调试
        </button>

        {/* 调试面板 */}
        {showDebug && (
          <div style={{
            marginBottom: '1rem',
            padding: '1rem',
            backgroundColor: '#1a1a1a',
            borderRadius: '8px',
            color: '#fff',
            fontSize: '11px',
            maxHeight: '300px',
            overflow: 'auto',
          }}>
            <h3 style={{ marginTop: 0, marginBottom: '0.5rem', fontSize: '14px' }}>🐛 调试信息</h3>
            
            {/* Telegram 信息 */}
            <div style={{ marginBottom: '1rem', padding: '0.5rem', backgroundColor: '#2a2a2a', borderRadius: '4px' }}>
              <strong>📱 Telegram:</strong>
              <div>WebApp: {telegramInfo?.hasWebApp ? '✅' : '❌'}</div>
              <div>平台: {telegramInfo?.platform || 'unknown'}</div>
              <div>版本: {telegramInfo?.version || 'unknown'}</div>
              <div>InitData: {telegramInfo?.hasInitData ? `✅ (${telegramInfo.initDataLength} 字符)` : '❌ 空'}</div>
              {telegramInfo?.user && (
                <div>用户: {telegramInfo.user.first_name} (@{telegramInfo.user.username || '无'})</div>
              )}
              {telegramInfo?.initDataPreview && (
                <details style={{ marginTop: '0.5rem' }}>
                  <summary style={{ cursor: 'pointer' }}>InitData 预览</summary>
                  <pre style={{ fontSize: '10px', wordBreak: 'break-all' }}>{telegramInfo.initDataPreview}</pre>
                </details>
              )}
            </div>

            {/* 日志 */}
            <div>
              <strong>📋 日志 ({debugLogs.length}):</strong>
              <div style={{ maxHeight: '150px', overflow: 'auto', marginTop: '0.5rem' }}>
                {debugLogs.length === 0 ? (
                  <div style={{ color: '#888' }}>暂无日志</div>
                ) : (
                  debugLogs.map((log, idx) => (
                    <div key={idx} style={{ marginBottom: '2px', wordBreak: 'break-all', fontSize: '10px' }}>
                      {log}
                    </div>
                  ))
                )}
              </div>
            </div>

            {/* 复制按钮 */}
            <button
              onClick={() => {
                const data = {
                  telegramInfo,
                  logs: debugLogs,
                  timestamp: new Date().toISOString(),
                };
                navigator.clipboard.writeText(JSON.stringify(data, null, 2));
                alert('调试信息已复制到剪贴板！');
              }}
              style={{
                marginTop: '0.5rem',
                padding: '5px 10px',
                fontSize: '11px',
                backgroundColor: '#4CAF50',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer',
              }}
            >
              复制调试信息
            </button>
          </div>
        )}
        
        {error && (
          <div className="error-message" style={{ 
            color: '#ef4444', 
            backgroundColor: '#fee2e2',
            padding: '0.75rem',
            borderRadius: '8px',
            marginBottom: '1rem',
            fontSize: '0.9rem'
          }}>
            {error}
          </div>
        )}

        {/* 社交登录选项 */}
        <div className="login-options">
          {/* Google登录 */}
          <button 
            onClick={handleGoogleLogin} 
            disabled={!!loading}
            className="login-option-button google-button"
          >
            <Globe size={20} />
            <span>{loading === 'google' ? '登录中...' : '使用Google登录'}</span>
          </button>

          {/* Telegram登录 */}
          <button 
            onClick={handleTelegramLogin} 
            disabled={!!loading}
            className="login-option-button telegram-button"
          >
            <MessageCircle size={20} />
            <span>{loading === 'telegram' ? '登录中...' : '使用Telegram登录'}</span>
          </button>

          {/* Facebook登录 */}
          <button 
            onClick={handleFacebookLogin} 
            disabled={!!loading}
            className="login-option-button facebook-button"
          >
            <Facebook size={20} />
            <span>{loading === 'facebook' ? '登录中...' : '使用Facebook登录'}</span>
          </button>

          {/* WhatsApp登录 */}
          <button 
            onClick={handleWhatsAppLogin} 
            disabled={!!loading}
            className="login-option-button whatsapp-button"
          >
            <MessageSquare size={20} />
            <span>{loading === 'whatsapp' ? '登录中...' : '使用WhatsApp登录'}</span>
          </button>
        </div>

        {/* 分隔线 */}
        <div style={{ 
          display: 'flex', 
          alignItems: 'center', 
          margin: '1.5rem 0',
          color: '#999'
        }}>
          <div style={{ flex: 1, height: '1px', backgroundColor: '#ddd' }} />
          <span style={{ padding: '0 1rem', fontSize: '0.9rem' }}>或</span>
          <div style={{ flex: 1, height: '1px', backgroundColor: '#ddd' }} />
        </div>

        {/* Wallet连接 */}
        <div className="login-section">
          <h3>钱包连接</h3>
          <input
            type="text"
            placeholder="输入钱包地址"
            value={walletAddress}
            onChange={(e) => setWalletAddress(e.target.value)}
            disabled={!!loading}
            style={{ width: '100%', padding: '0.75rem', marginBottom: '0.75rem', borderRadius: '8px', border: '1px solid #ddd' }}
          />
          <button 
            onClick={handleWalletConnect} 
            disabled={!!loading || !walletAddress}
            className="login-option-button wallet-button"
          >
            <Wallet size={20} />
            <span>{loading === 'wallet' ? '连接中...' : '连接钱包'}</span>
          </button>
        </div>

        {/* Magic Link登录 */}
        <div className="login-section" style={{ marginTop: '1rem' }}>
          <h3>Magic Link登录</h3>
          <p style={{ fontSize: '0.85rem', color: '#666', marginBottom: '0.5rem' }}>
            从Telegram机器人获取Magic Link后，在此输入Token
          </p>
          <input
            type="text"
            placeholder="输入Magic Link Token"
            value={magicLinkToken}
            onChange={(e) => setMagicLinkToken(e.target.value)}
            disabled={!!loading}
            style={{ width: '100%', padding: '0.75rem', marginBottom: '0.75rem', borderRadius: '8px', border: '1px solid #ddd' }}
          />
          <button 
            onClick={handleMagicLinkLogin} 
            disabled={!!loading || !magicLinkToken}
            className="login-option-button magic-link-button"
          >
            <Key size={20} />
            <span>{loading === 'magiclink' ? '验证中...' : '验证Magic Link'}</span>
          </button>
        </div>
      </div>

      <style>{`
        .web-login-screen {
          display: flex;
          justify-content: center;
          align-items: center;
          min-height: 100vh;
          padding: 1rem;
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          box-sizing: border-box;
        }
        .login-container {
          background: white;
          padding: 1.5rem;
          border-radius: 16px;
          box-shadow: 0 10px 40px rgba(0,0,0,0.1);
          max-width: 450px;
          width: 100%;
          box-sizing: border-box;
          overflow-y: auto;
          max-height: 90vh;
        }
        @media (max-width: 480px) {
          .login-container {
            padding: 1rem;
            border-radius: 12px;
          }
          .login-options {
            grid-template-columns: 1fr !important;
          }
        }
        .login-container h2 {
          margin: 0 0 0.5rem 0;
          text-align: center;
          color: #333;
          font-size: 1.5rem;
        }
        .login-options {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 0.75rem;
          margin-bottom: 1rem;
        }
        .login-section {
          margin-bottom: 1rem;
        }
        .login-section h3 {
          margin: 0 0 0.75rem 0;
          font-size: 0.95rem;
          color: #555;
          font-weight: 600;
        }
        .login-option-button {
          width: 100%;
          padding: 0.875rem 1rem;
          border: none;
          border-radius: 10px;
          font-size: 0.95rem;
          font-weight: 500;
          cursor: pointer;
          transition: all 0.3s;
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 0.5rem;
          color: white;
        }
        .login-option-button:disabled {
          opacity: 0.6;
          cursor: not-allowed;
        }
        .google-button {
          background: #4285f4;
        }
        .google-button:hover:not(:disabled) {
          background: #357ae8;
          transform: translateY(-2px);
          box-shadow: 0 4px 12px rgba(66, 133, 244, 0.4);
        }
        .telegram-button {
          background: #0088cc;
        }
        .telegram-button:hover:not(:disabled) {
          background: #0077b3;
          transform: translateY(-2px);
          box-shadow: 0 4px 12px rgba(0, 136, 204, 0.4);
        }
        .facebook-button {
          background: #1877f2;
        }
        .facebook-button:hover:not(:disabled) {
          background: #166fe5;
          transform: translateY(-2px);
          box-shadow: 0 4px 12px rgba(24, 119, 242, 0.4);
        }
        .whatsapp-button {
          background: #25d366;
        }
        .whatsapp-button:hover:not(:disabled) {
          background: #20ba5a;
          transform: translateY(-2px);
          box-shadow: 0 4px 12px rgba(37, 211, 102, 0.4);
        }
        .wallet-button {
          background: #0088cc;
          color: white;
        }
        .wallet-button:hover:not(:disabled) {
          background: #0077b3;
          transform: translateY(-2px);
          box-shadow: 0 4px 12px rgba(0, 136, 204, 0.4);
        }
        .magic-link-button {
          background: #9c27b0;
          color: white;
        }
        .magic-link-button:hover:not(:disabled) {
          background: #7b1fa2;
          transform: translateY(-2px);
          box-shadow: 0 4px 12px rgba(156, 39, 176, 0.4);
        }
      `}</style>
    </div>
  );
}

// 扩展 Window 类型以支持 Google API
declare global {
  interface Window {
    google?: {
      accounts: {
        id: {
          initialize: (config: { client_id: string; callback: (response: any) => void }) => void;
          renderButton: (element: HTMLElement, config: any) => void;
          prompt: (callback: (notification: any) => void) => void;
        };
        oauth2: {
          initTokenClient: (config: {
            client_id: string;
            scope: string;
            callback: (response: any) => void;
          }) => {
            requestAccessToken: () => void;
          };
        };
      };
    };
  }
}

