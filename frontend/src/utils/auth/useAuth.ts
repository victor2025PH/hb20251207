/**
 * 认证Hook
 * 统一管理用户认证状态
 */
import { useState, useEffect, useCallback } from 'react';
import { detectPlatform, isInTelegram } from '../platform';
import { initTelegram, getTelegramUser, getInitData } from '../telegram';
import { getCurrentUser, googleAuth, walletAuth, verifyMagicLink, type AuthResponse } from '../api';

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
            const tgUser = getTelegramUser();
            console.log('[Auth] 尝试使用 Telegram initData 认证...', {
              initDataLength: initData.length,
              hasUser: !!tgUser,
              userId: tgUser?.id,
              username: tgUser?.username,
              initDataPreview: initData.substring(0, 100) + '...'
            });
            
            // 通过Telegram initData获取用户信息
            // 注意：getCurrentUser() 会通过 API 拦截器自动发送 initData
            const response = await getCurrentUser();
            
            console.log('[Auth] Telegram getCurrentUser() 响应:', {
              hasData: !!response.data,
              userId: response.data?.id,
              username: response.data?.username
            });
            
            // 确保 response.data 存在且包含必要的字段
            const userData = response.data || response;
            if (!userData || !userData.id) {
              console.error('[Auth] Telegram 认证响应数据无效:', userData);
              throw new Error('Invalid user data received from server');
            }
            
            setAuthState({
              user: userData,
              loading: false,
              isAuthenticated: true,
              platform: 'telegram'
            });
            console.log('[Auth] Telegram 自动登录成功', {
              userId: userData.id,
              username: userData.username,
              isAuthenticated: true
            });
            return;
          } catch (error: any) {
            // 认证失败，记录详细错误信息
            console.error('[Auth] Telegram认证失败:', {
              error: error.message,
              status: error?.response?.status,
              isUnauthorized: error?.isUnauthorized,
              responseData: error?.response?.data
            });
            
            if (error?.isUnauthorized || error?.response?.status === 401) {
              // 这是未认证的情况，可能是 initData hash 验证失败
              console.warn('[Auth] Telegram认证失败 - 可能的原因：');
              console.warn('[Auth] 1. initData hash 验证失败（检查 BOT_TOKEN 配置）');
              console.warn('[Auth] 2. initData 已过期');
              console.warn('[Auth] 3. 后端无法解析 initData');
              console.warn('[Auth] 4. 用户可能尚未在系统中注册');
            } else {
              // 其他错误，记录警告
              console.warn('[Auth] Telegram认证失败，可以使用其他登录方式:', error);
            }
            // 认证失败，设置 loading=false 以便显示登录界面
            // 用户可以通过点击"使用Telegram登录"按钮手动重试
            setAuthState({
              user: null,
              loading: false,
              isAuthenticated: false,
              platform: 'telegram'
            });
            // 不 return，继续执行下面的逻辑（检查 JWT token）
          }
        } else {
          // 在 Telegram 环境中但没有 initData，记录警告但不尝试认证
          console.warn('[Auth] Telegram 环境中 initData 为空，无法自动登录', {
            hasWebApp: !!window.Telegram?.WebApp,
            platform: window.Telegram?.WebApp?.platform,
            version: window.Telegram?.WebApp?.version
          });
          // 不尝试调用 getCurrentUser()，直接继续到下面的逻辑
        }
      }
      
      // Web环境：检查是否有JWT Token
      const token = localStorage.getItem('auth_token');
      console.log('[Auth] Checking JWT token in localStorage...', { 
        hasToken: !!token,
        tokenLength: token?.length || 0,
        platform: platformInfo.platform,
        isInTelegram: isInTelegram()
      });
      
      if (token) {
        try {
          console.log('[Auth] Token found, calling getCurrentUser() to verify...');
          const response = await getCurrentUser();
          console.log('[Auth] getCurrentUser() response:', {
            responseType: typeof response,
            hasData: !!response.data,
            responseKeys: Object.keys(response || {}),
            fullResponse: response
          });
          
          // 确保 response.data 存在且包含必要的字段
          const userData = response.data || response;
          console.log('[Auth] Extracted user data:', {
            userId: userData?.id,
            username: userData?.username,
            hasId: !!userData?.id,
            hasUsername: !!userData?.username,
            allKeys: Object.keys(userData || {})
          });
          
          if (!userData || !userData.id) {
            console.error('[Auth] User data is invalid:', userData);
            throw new Error('Invalid user data received from server');
          }
          
          setAuthState({
            user: userData,
            loading: false,
            isAuthenticated: true,
            platform: platformInfo.platform
          });
          console.log('[Auth] Auth state updated to authenticated=true', {
            userId: userData.id,
            username: userData.username,
            isAuthenticated: true
          });
          return;
        } catch (error: any) {
          // Token无效或已过期，清除
          console.error('[Auth] getCurrentUser() failed:', {
            error: error.message,
            status: error?.response?.status,
            isUnauthorized: error?.isUnauthorized
          });
          if (error?.isUnauthorized || error?.response?.status === 401) {
            console.warn('[Auth] JWT Token无效或已过期，清除token');
          } else {
            console.warn('[Auth] 获取用户信息失败:', error);
          }
          localStorage.removeItem('auth_token');
          console.log('[Auth] Token removed from localStorage');
        }
      } else {
        console.log('[Auth] No token found in localStorage');
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
      console.log(`[useAuth] Starting ${provider} login...`);
      let authData: AuthResponse;
      if (provider === 'google') {
        authData = await googleAuth(credentials);
      } else {
        authData = await walletAuth(credentials);
      }
      
      console.log('[useAuth] Login API response received', { hasToken: !!authData.access_token, hasUser: !!authData.user });
      
      // authData 已经是 AuthResponse 类型，包含 access_token 和 user
      // 保存Token
      if (!authData.access_token) {
        throw new Error('登录响应中缺少 access_token');
      }
      localStorage.setItem('auth_token', authData.access_token);
      console.log('[useAuth] Token saved to localStorage');
      
      // 登录成功后，重新获取完整的用户信息
      try {
        const userResponse = await getCurrentUser();
        console.log('[useAuth] User info retrieved, updating auth state...');
        setAuthState({
          user: userResponse.data,
          loading: false,
          isAuthenticated: true,
          platform: detectPlatform().platform
        });
        console.log('[useAuth] Auth state updated, isAuthenticated=true');
      } catch (userError) {
        // 如果获取用户信息失败，使用登录响应中的用户信息
        console.warn('[useAuth] Failed to get user info, using login response data:', userError);
        setAuthState({
          user: authData.user,
          loading: false,
          isAuthenticated: true,
          platform: detectPlatform().platform
        });
        console.log('[useAuth] Auth state updated with login response data, isAuthenticated=true');
      }
      
      // 等待状态更新完成（React 状态更新是异步的）
      await new Promise(resolve => setTimeout(resolve, 50));
      
      return authData;
    } catch (error) {
      console.error('[useAuth] Login error:', error);
      throw error;
    }
  }, []);

  // Magic Link登录
  const loginWithMagicLink = useCallback(async (token: string) => {
    try {
      const authData = await verifyMagicLink(token);
      
      // authData 已经是 AuthResponse 类型，包含 access_token 和 user
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

