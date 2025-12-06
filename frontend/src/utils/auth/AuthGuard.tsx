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
  if (platformInfo.isTelegram) {
    // Telegram环境但未认证，可能是initData问题
    return (
      <div style={{ 
        padding: '2rem', 
        textAlign: 'center' 
      }}>
        <h2>认证失败</h2>
        <p>无法获取Telegram认证信息，请确保在Telegram中打开此应用。</p>
        {fallback || null}
      </div>
    );
  }

  // Web环境 - 显示登录界面
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

