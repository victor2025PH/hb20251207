/**
 * AuthGuard组件
 * 自动检测平台并处理认证
 */
import React, { useEffect, useState } from 'react';
import { useAuth } from './useAuth';
import { detectPlatform, getPlatformRules } from '../platform';
import { WebLoginScreen } from '../../components/WebLoginScreen';

interface AuthGuardProps {
  children: React.ReactNode;
  requireAuth?: boolean;
  fallback?: React.ReactNode;
}

export function AuthGuard({ 
  children, 
  requireAuth = true,
  fallback 
}: AuthGuardProps) {
  // 所有 hooks 必须在组件顶部，在任何条件返回之前
  const { user, loading, isAuthenticated, platform } = useAuth();
  const [platformInfo, setPlatformInfo] = useState(() => {
    try {
      return detectPlatform();
    } catch (e) {
      console.error('Platform detection error:', e);
      return { platform: 'web' as const, isTelegram: false, isWeb: true, isMobile: false, isIOS: false, isAndroid: false, userAgent: '' };
    }
  });
  const [platformRules, setPlatformRules] = useState(() => {
    try {
      return getPlatformRules();
    } catch (e) {
      console.error('Platform rules error:', e);
      return { hideFinancialFeatures: false, showDeposit: true, showWithdraw: true, showExchange: true, showStars: true, showGame: true, platform: 'web' as const, isTelegram: false, isWeb: true, isMobile: false, isIOS: false, isAndroid: false, userAgent: '' };
    }
  });

  // 检查是否真的在 Telegram 环境中（需要同时有 WebApp 对象和 initData）
  const hasTelegramWebApp = typeof window !== 'undefined' && 
    (window as any).Telegram?.WebApp;
  
  // 检查是否有 initData（这是判断是否在真正的 Telegram 客户端中的关键）
  const hasInitData = hasTelegramWebApp && (
    (window as any).Telegram?.WebApp?.initData ||
    (window as any).Telegram?.WebApp?.initDataUnsafe?.user
  );
  
  // 如果在 Telegram 中但 initData 为空，等待一段时间后如果还是失败，显示登录选项
  const [telegramInitTimeout, setTelegramInitTimeout] = useState(false);

  useEffect(() => {
    try {
      setPlatformInfo(detectPlatform());
      setPlatformRules(getPlatformRules());
    } catch (e) {
      console.error('Platform update error:', e);
    }
  }, []);

  useEffect(() => {
    // 如果不在 Telegram 环境中，立即允许登录
    if (!hasTelegramWebApp) {
      setTelegramInitTimeout(true);
      return;
    }
    
    // 如果在 Telegram WebApp 中但 initData 为空，等待 1.5 秒后显示登录选项
    if (hasTelegramWebApp && !hasInitData && !isAuthenticated) {
      const timer = setTimeout(() => {
        setTelegramInitTimeout(true);
      }, 1500);
      return () => clearTimeout(timer);
    }
  }, [hasTelegramWebApp, hasInitData, isAuthenticated]);

  // 加载中
  if (loading) {
    return (
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        minHeight: '100vh',
        color: 'white'
      }}>
        <div>加载中...</div>
      </div>
    );
  }

  // 不需要认证
  if (!requireAuth) {
    return <>{children}</>;
  }

  // 已认证
  if (isAuthenticated && user) {
    return <>{children}</>;
  }

  // 未认证 - 显示登录界面
  
  // 如果不在 Telegram 环境中，或者等待超时，直接显示登录选项
  if (!hasTelegramWebApp || (hasTelegramWebApp && !hasInitData && telegramInitTimeout)) {
    return (
      <WebLoginScreen 
        onLoginSuccess={() => {
          // 登录成功后会通过useAuth自动更新状态
          window.location.reload();
        }}
      />
    );
  }
  
  // Telegram环境但initData为空，等待初始化（最多1.5秒）
  if (hasTelegramWebApp && !hasInitData && !telegramInitTimeout) {
    return (
      <div style={{ 
        padding: '2rem', 
        textAlign: 'center',
        color: 'white',
        minHeight: '100vh',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        alignItems: 'center',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
      }}>
        <h2>正在初始化...</h2>
        <p>正在获取Telegram认证信息，请稍候...</p>
        <div style={{ 
          marginTop: '2rem',
          padding: '1rem',
          backgroundColor: 'rgba(255,255,255,0.1)',
          borderRadius: '8px',
          fontSize: '0.9rem'
        }}>
          <p>如果长时间停留在此页面，您也可以使用其他登录方式。</p>
        </div>
      </div>
    );
  }
  
  // Telegram环境有initData但认证失败，显示登录选项
  if (hasTelegramWebApp && hasInitData && !isAuthenticated) {
    return (
      <div style={{ 
        padding: '2rem', 
        textAlign: 'center',
        color: 'white',
        minHeight: '100vh',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        alignItems: 'center',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
      }}>
        <h2>Telegram认证失败</h2>
        <p>无法验证Telegram认证信息。</p>
        <p style={{ fontSize: '0.9rem', marginTop: '1rem' }}>
          您可以使用其他登录方式继续。
        </p>
        <div style={{ marginTop: '2rem', width: '100%', maxWidth: '450px' }}>
          <WebLoginScreen 
            onLoginSuccess={() => {
              window.location.reload();
            }}
          />
        </div>
      </div>
    );
  }

  // 默认情况：显示登录界面（确保总是返回有效的 React 元素）
  return (
    <WebLoginScreen 
      onLoginSuccess={() => {
        // 登录成功后会通过useAuth自动更新状态
        window.location.reload();
      }}
    />
  );
}

/**
 * 平台规则Hook
 * 用于根据平台显示/隐藏功能
 */
export function usePlatformRules() {
  const [rules, setRules] = useState(getPlatformRules());
  
  useEffect(() => {
    setRules(getPlatformRules());
  }, []);
  
  return rules;
}

