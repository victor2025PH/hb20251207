/**
 * Web登录界面
 * 用于非Telegram环境的登录（Google OAuth, Wallet连接）
 */
import React, { useState } from 'react';
import { googleAuth, walletAuth, verifyMagicLink } from '../utils/api';
import { useAuth } from '../utils/auth/useAuth';

interface WebLoginScreenProps {
  onLoginSuccess?: () => void;
}

export function WebLoginScreen({ onLoginSuccess }: WebLoginScreenProps) {
  const { login, loginWithMagicLink } = useAuth();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [walletAddress, setWalletAddress] = useState('');
  const [magicLinkToken, setMagicLinkToken] = useState('');

  // Google登录
  const handleGoogleLogin = async () => {
    setLoading(true);
    setError(null);
    try {
      // TODO: 集成Google OAuth SDK
      // 这里需要实际的Google OAuth流程
      const mockIdToken = 'mock_google_id_token';
      await login('google', {
        id_token: mockIdToken,
        email: 'user@example.com',
        given_name: 'User',
        family_name: 'Name'
      });
      onLoginSuccess?.();
    } catch (err: any) {
      setError(err.message || 'Google登录失败');
    } finally {
      setLoading(false);
    }
  };

  // Wallet连接
  const handleWalletConnect = async () => {
    if (!walletAddress) {
      setError('请输入钱包地址');
      return;
    }
    
    setLoading(true);
    setError(null);
    try {
      await login('wallet', {
        address: walletAddress,
        network: 'TON'
      });
      onLoginSuccess?.();
    } catch (err: any) {
      setError(err.message || '钱包连接失败');
    } finally {
      setLoading(false);
    }
  };

  // Magic Link登录
  const handleMagicLinkLogin = async () => {
    if (!magicLinkToken) {
      setError('请输入Magic Link Token');
      return;
    }
    
    setLoading(true);
    setError(null);
    try {
      await loginWithMagicLink(magicLinkToken);
      onLoginSuccess?.();
    } catch (err: any) {
      setError(err.message || 'Magic Link验证失败');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="web-login-screen">
      <div className="login-container">
        <h2>登录到红包游戏</h2>
        
        {error && (
          <div className="error-message" style={{ color: 'red', marginBottom: '1rem' }}>
            {error}
          </div>
        )}

        {/* Google登录 */}
        <div className="login-section">
          <h3>Google登录</h3>
          <button 
            onClick={handleGoogleLogin} 
            disabled={loading}
            className="login-button google-button"
          >
            {loading ? '登录中...' : '使用Google登录'}
          </button>
        </div>

        {/* Wallet连接 */}
        <div className="login-section">
          <h3>钱包连接</h3>
          <input
            type="text"
            placeholder="输入钱包地址"
            value={walletAddress}
            onChange={(e) => setWalletAddress(e.target.value)}
            disabled={loading}
            style={{ width: '100%', padding: '0.5rem', marginBottom: '0.5rem' }}
          />
          <button 
            onClick={handleWalletConnect} 
            disabled={loading || !walletAddress}
            className="login-button wallet-button"
          >
            {loading ? '连接中...' : '连接钱包'}
          </button>
        </div>

        {/* Magic Link登录 */}
        <div className="login-section">
          <h3>Magic Link登录</h3>
          <p style={{ fontSize: '0.9rem', color: '#666', marginBottom: '0.5rem' }}>
            从Telegram机器人获取Magic Link后，在此输入Token
          </p>
          <input
            type="text"
            placeholder="输入Magic Link Token"
            value={magicLinkToken}
            onChange={(e) => setMagicLinkToken(e.target.value)}
            disabled={loading}
            style={{ width: '100%', padding: '0.5rem', marginBottom: '0.5rem' }}
          />
          <button 
            onClick={handleMagicLinkLogin} 
            disabled={loading || !magicLinkToken}
            className="login-button magic-link-button"
          >
            {loading ? '验证中...' : '验证Magic Link'}
          </button>
        </div>
      </div>

      <style>{`
        .web-login-screen {
          display: flex;
          justify-content: center;
          align-items: center;
          min-height: 100vh;
          padding: 2rem;
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }
        .login-container {
          background: white;
          padding: 2rem;
          border-radius: 12px;
          box-shadow: 0 10px 40px rgba(0,0,0,0.1);
          max-width: 400px;
          width: 100%;
        }
        .login-container h2 {
          margin: 0 0 1.5rem 0;
          text-align: center;
          color: #333;
        }
        .login-section {
          margin-bottom: 1.5rem;
        }
        .login-section h3 {
          margin: 0 0 0.5rem 0;
          font-size: 1rem;
          color: #555;
        }
        .login-button {
          width: 100%;
          padding: 0.75rem;
          border: none;
          border-radius: 8px;
          font-size: 1rem;
          cursor: pointer;
          transition: all 0.3s;
        }
        .login-button:disabled {
          opacity: 0.6;
          cursor: not-allowed;
        }
        .google-button {
          background: #4285f4;
          color: white;
        }
        .google-button:hover:not(:disabled) {
          background: #357ae8;
        }
        .wallet-button {
          background: #0088cc;
          color: white;
        }
        .wallet-button:hover:not(:disabled) {
          background: #0077b3;
        }
        .magic-link-button {
          background: #9c27b0;
          color: white;
        }
        .magic-link-button:hover:not(:disabled) {
          background: #7b1fa2;
        }
      `}</style>
    </div>
  );
}

