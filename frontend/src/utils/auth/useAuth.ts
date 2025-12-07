/**
 * 认证Hook
 * 统一管理用户认证状态
 */
import { useState, useEffect, useCallback } from 'react';
import { detectPlatform, isInTelegram } from '../platform';
import { initTelegram, getTelegramUser, getInitData } from '../telegram';
import { getCurrentUser, googleAuth, walletAuth, verifyMagicLink } from '../api';

export interface User {
  id: number;
  uuid?: string;
  tg_id?: number;
  username?: string;
  first_name?: string;
  last_name?: string;
  wallet_address?: string;
  wallet_network?: string;
  primary_platform?: string;
  balance_usdt?: number;
  balance_ton?: number;
  balance_stars?: number;
  balance_points?: number;
}

export interface AuthState {
  user: User | null;
  loading: boolean;
  isAuthenticated: boolean;
  platform: string;
}

export function useAuth() {
  const [authState, setAuthState] = useState<AuthState>({
    user: null,
    loading: true,
    isAuthenticated: false,
    platform: 'unknown'
  });

  // 初始化认证
  const initAuth = useCallback(async () => {
    try {
      const platformInfo = detectPlatform();
      
      // Telegram环境：自动登录
      if (isInTelegram()) {
        // 初始化 Telegram WebApp（等待完全准备好）
        await initTelegram();
        
        // 再次等待 initData 准备就绪（最多等待 3 秒）
        // 有些情况下，initData 可能在 ready 事件之后才可用
        let initData = getInitData();
        let attempts = 0;
        const maxAttempts = 30; // 3秒，每次100ms
        
        console.log('[Auth] 等待 initData 准备就绪...', {
          initialInitDataLength: initData.length,
          hasWebApp: !!window.Telegram?.WebApp,
          platform: window.Telegram?.WebApp?.platform
        });
        
        while ((!initData || initData.length === 0) && attempts < maxAttempts) {
          await new Promise(resolve => setTimeout(resolve, 100));
          initData = getInitData();
          attempts++;
          
          if (attempts % 10 === 0) {
            console.log(`[Auth] 等待 initData... (${attempts}/${maxAttempts})`, {
              hasWebApp: !!window.Telegram?.WebApp,
              initDataLength: initData.length,
              hasUser: !!getTelegramUser()
            });
          }
        }
        
        if (initData && initData.length > 0) {
          try {
            console.log('[Auth] 尝试使用 Telegram initData 认证...', {
              initDataLength: initData.length,
              hasUser: !!getTelegramUser()
            });
            
            // 通过Telegram initData获取用户信息
            const response = await getCurrentUser();
            setAuthState({
              user: response.data,
              loading: false,
              isAuthenticated: true,
              platform: 'telegram'
            });
            console.log('[Auth] Telegram 自动登录成功', response.data);
            return;
          } catch (error: any) {
            // 认证失败，记录详细错误
            console.error('[Auth] Telegram认证失败:', error);
            console.error('[Auth] 错误详情:', {
              message: error?.message,
              response: error?.response?.data,
              status: error?.response?.status,
              initDataLength: initData.length,
              hasUser: !!getTelegramUser()
            });
            // 不设置 loading=false，让下面的逻辑处理
          }
        } else {
          // 在 Telegram 环境中但没有 initData，记录警告
          console.warn('[Auth] Telegram 环境中 initData 为空，无法自动登录', {
            hasWebApp: !!window.Telegram?.WebApp,
            platform: window.Telegram?.WebApp?.platform,
            version: window.Telegram?.WebApp?.version
          });
        }
      }
      
      // Web环境：检查是否有JWT Token
      const token = localStorage.getItem('auth_token');
      if (token) {
        try {
          const response = await getCurrentUser();
          setAuthState({
            user: response.data,
            loading: false,
            isAuthenticated: true,
            platform: platformInfo.platform
          });
          return;
        } catch (error) {
          // Token无效，清除
          localStorage.removeItem('auth_token');
        }
      }
      
      // 未认证
      setAuthState({
        user: null,
        loading: false,
        isAuthenticated: false,
        platform: platformInfo.platform
      });
    } catch (error) {
      console.error('Auth initialization error:', error);
      setAuthState({
        user: null,
        loading: false,
        isAuthenticated: false,
        platform: 'unknown'
      });
    }
  }, []);

  // 登录（Web环境）
  const login = useCallback(async (provider: 'google' | 'wallet', credentials: any) => {
    try {
      let response;
      if (provider === 'google') {
        response = await googleAuth(credentials);
      } else {
        response = await walletAuth(credentials);
      }
      
      // 注意：api.interceptors.response 已经返回了 response.data
      // 所以 response 本身就是 { access_token, user } 对象
      const authData = response.data || response;
      
      // 保存Token
      if (!authData.access_token) {
        throw new Error('登录响应中缺少 access_token');
      }
      localStorage.setItem('auth_token', authData.access_token);
      
      // 登录成功后，重新获取完整的用户信息
      try {
        const userResponse = await getCurrentUser();
        setAuthState({
          user: userResponse.data,
          loading: false,
          isAuthenticated: true,
          platform: detectPlatform().platform
        });
      } catch (userError) {
        // 如果获取用户信息失败，使用登录响应中的用户信息
        console.warn('获取用户信息失败，使用登录响应中的信息:', userError);
        setAuthState({
          user: authData.user,
          loading: false,
          isAuthenticated: true,
          platform: detectPlatform().platform
        });
      }
      
      return authData;
    } catch (error) {
      console.error('Login error:', error);
      throw error;
    }
  }, []);

  // Magic Link登录
  const loginWithMagicLink = useCallback(async (token: string) => {
    try {
      const response = await verifyMagicLink(token);
      
      // 注意：api.interceptors.response 已经返回了 response.data
      const authData = response.data || response;
      
      // 保存Token
      if (!authData.access_token) {
        throw new Error('Magic Link验证响应中缺少 access_token');
      }
      localStorage.setItem('auth_token', authData.access_token);
      
      setAuthState({
        user: authData.user,
        loading: false,
        isAuthenticated: true,
        platform: detectPlatform().platform
      });
      
      return authData;
    } catch (error) {
      console.error('Magic link login error:', error);
      throw error;
    }
  }, []);

  // 登出
  const logout = useCallback(() => {
    localStorage.removeItem('auth_token');
    setAuthState({
      user: null,
      loading: false,
      isAuthenticated: false,
      platform: detectPlatform().platform
    });
  }, []);

  // 初始化
  useEffect(() => {
    initAuth();
  }, [initAuth]);

  return {
    ...authState,
    login,
    loginWithMagicLink,
    logout,
    refresh: initAuth
  };
}

