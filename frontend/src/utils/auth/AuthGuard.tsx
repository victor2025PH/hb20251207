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
  const { user, loading, isAuthenticated, platform } = useAuth();
  const [platformInfo, setPlatformInfo] = useState(detectPlatform());
  const [platformRules, setPlatformRules] = useState(getPlatformRules());

  useEffect(() => {
    setPlatformInfo(detectPlatform());
    setPlatformRules(getPlatformRules());
  }, []);

  // 加载中
  if (loading) {
    return (
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        minHeight: '100vh' 
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
  // 检查是否真的在 Telegram 环境中
  // 注意：即使 initData 为空，如果检测到 Telegram WebApp 对象，也应该尝试认证
  const isRealTelegram = platformInfo.isTelegram && 
    typeof window !== 'undefined' && 
    (window as any).Telegram?.WebApp;
  
  // 检查是否有 initData 或 initDataUnsafe
  const hasInitData = isRealTelegram && (
    (window as any).Telegram?.WebApp?.initData ||
    (window as any).Telegram?.WebApp?.initDataUnsafe?.user
  );
  
  if (isRealTelegram && !hasInitData) {
    // Telegram环境但initData为空，可能是配置问题
    // 给用户一些时间让 Telegram 初始化，或者显示提示
    return (
      <div style={{ 
        padding: '2rem', 
        textAlign: 'center',
        color: 'white'
      }}>
        <h2>正在初始化...</h2>
        <p>正在获取Telegram认证信息，请稍候...</p>
        <p style={{ fontSize: '0.9rem', color: '#999', marginTop: '1rem' }}>
          如果长时间停留在此页面，请确保在Telegram中打开此应用。
        </p>
        {fallback || null}
      </div>
    );
  }
  
  if (isRealTelegram && hasInitData && !isAuthenticated) {
    // Telegram环境有initData但认证失败，可能是API问题
    return (
      <div style={{ 
        padding: '2rem', 
        textAlign: 'center',
        color: 'white'
      }}>
        <h2>认证失败</h2>
        <p>无法验证Telegram认证信息，请稍后重试。</p>
        <button 
          onClick={() => window.location.reload()}
          style={{
            marginTop: '1rem',
            padding: '0.5rem 1rem',
            backgroundColor: '#007bff',
            color: 'white',
            border: 'none',
            borderRadius: '0.25rem',
            cursor: 'pointer'
          }}
        >
          刷新页面
        </button>
        {fallback || null}
      </div>
    );
  }

  // Web环境或其他环境 - 显示登录界面
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

