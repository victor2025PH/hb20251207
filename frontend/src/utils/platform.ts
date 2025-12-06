/**
 * 平台检测工具
 * 用于检测当前运行环境（Telegram, Web, iOS, Android等）
 */

export type Platform = 'telegram' | 'web' | 'ios' | 'android' | 'unknown';

export interface PlatformInfo {
  platform: Platform;
  isTelegram: boolean;
  isWeb: boolean;
  isMobile: boolean;
  isIOS: boolean;
  isAndroid: boolean;
  userAgent: string;
}

/**
 * 检测当前平台
 */
export function detectPlatform(): PlatformInfo {
  const userAgent = navigator.userAgent || '';
  const isTelegram = typeof window !== 'undefined' && 
    (window as any).Telegram?.WebApp !== undefined;
  
  const isIOS = /iPad|iPhone|iPod/.test(userAgent) && !(window as any).MSStream;
  const isAndroid = /Android/.test(userAgent);
  const isMobile = isIOS || isAndroid;
  
  let platform: Platform = 'unknown';
  if (isTelegram) {
    platform = 'telegram';
  } else if (isIOS) {
    platform = 'ios';
  } else if (isAndroid) {
    platform = 'android';
  } else {
    platform = 'web';
  }
  
  return {
    platform,
    isTelegram,
    isWeb: !isTelegram && !isMobile,
    isMobile,
    isIOS,
    isAndroid,
    userAgent
  };
}

/**
 * 获取平台规则（用于合规和UI显示）
 */
export function getPlatformRules() {
  const platformInfo = detectPlatform();
  
  return {
    // iOS平台：隐藏金融功能
    hideFinancialFeatures: platformInfo.isIOS,
    // 显示的功能
    showDeposit: !platformInfo.isIOS,
    showWithdraw: !platformInfo.isIOS,
    showExchange: !platformInfo.isIOS,
    showStars: true,
    showGame: true,
    // 平台信息
    ...platformInfo
  };
}

/**
 * 检查是否在Telegram环境中
 */
export function isInTelegram(): boolean {
  return typeof window !== 'undefined' && 
    (window as any).Telegram?.WebApp !== undefined;
}

