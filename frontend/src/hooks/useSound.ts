import { useCallback, useRef, useEffect, useState } from 'react'

type SoundType = 'click' | 'grab' | 'success' | 'switch' | 'notification' | 'pop' | 'startup'

// 全局狀態，在組件外部持久化
let isGlobalMuted = false
const listeners = new Set<(muted: boolean) => void>()

export const useGlobalAudio = () => {
  const [isMuted, setIsMuted] = useState(isGlobalMuted)

  useEffect(() => {
    const handler = (m: boolean) => setIsMuted(m)
    listeners.add(handler)
    return () => {
      listeners.delete(handler)
    }
  }, [])

  const toggleMute = useCallback(() => {
    isGlobalMuted = !isGlobalMuted
    listeners.forEach(l => l(isGlobalMuted))
  }, [])

  return { isMuted, toggleMute }
}

export const useSound = () => {
  const audioContext = useRef<AudioContext | null>(null)

  useEffect(() => {
    const initAudio = () => {
      if (!audioContext.current) {
        audioContext.current = new (window.AudioContext || (window as any).webkitAudioContext)()
      }
      // 如果暫停則恢復（瀏覽器阻止自動播放）
      if (audioContext.current.state === 'suspended') {
        audioContext.current.resume()
      }
    }
    
    // 在首次交互時初始化以繞過自動播放策略
    window.addEventListener('click', initAudio, { once: true })
    window.addEventListener('touchstart', initAudio, { once: true })
    
    return () => {
      window.removeEventListener('click', initAudio)
      window.removeEventListener('touchstart', initAudio)
    }
  }, [])

  const playSound = useCallback((type: SoundType) => {
    if (isGlobalMuted) return

    if (!audioContext.current) {
      audioContext.current = new (window.AudioContext || (window as any).webkitAudioContext)()
    }

    const ctx = audioContext.current
    
    // 確保上下文正在運行
    if (ctx.state === 'suspended') {
      ctx.resume().catch(() => {})
    }

    const now = ctx.currentTime
    const masterGain = ctx.createGain()
    masterGain.connect(ctx.destination)

    // 輔助函數：創建簡單的提示音
    const playTone = (freq: number, type: OscillatorType, startTime: number, duration: number, volume: number) => {
      const osc = ctx.createOscillator()
      const gain = ctx.createGain()
      osc.type = type
      osc.frequency.setValueAtTime(freq, startTime)
      
      gain.gain.setValueAtTime(0, startTime)
      gain.gain.linearRampToValueAtTime(volume, startTime + 0.02)
      gain.gain.exponentialRampToValueAtTime(0.001, startTime + duration)
      
      osc.connect(gain)
      gain.connect(masterGain)
      
      osc.start(startTime)
      osc.stop(startTime + duration)
    }

    switch (type) {
      case 'click':
        playTone(800, 'sine', now, 0.1, 0.05)
        break

      case 'switch':
        playTone(300, 'triangle', now, 0.15, 0.03)
        break

      case 'pop':
        const oscPop = ctx.createOscillator()
        const gainPop = ctx.createGain()
        oscPop.type = 'sine'
        oscPop.frequency.setValueAtTime(400, now)
        oscPop.frequency.exponentialRampToValueAtTime(800, now + 0.1)
        
        gainPop.gain.setValueAtTime(0.05, now)
        gainPop.gain.exponentialRampToValueAtTime(0.001, now + 0.1)
        
        oscPop.connect(gainPop)
        gainPop.connect(masterGain)
        oscPop.start(now)
        oscPop.stop(now + 0.1)
        break

      case 'grab':
        const oscGrab = ctx.createOscillator()
        const gainGrab = ctx.createGain()
        oscGrab.type = 'sine'
        oscGrab.frequency.setValueAtTime(1200, now)
        oscGrab.frequency.exponentialRampToValueAtTime(2000, now + 0.1)
        
        gainGrab.gain.setValueAtTime(0, now)
        gainGrab.gain.linearRampToValueAtTime(0.1, now + 0.02)
        gainGrab.gain.exponentialRampToValueAtTime(0.001, now + 0.4)
        
        oscGrab.connect(gainGrab)
        gainGrab.connect(masterGain)
        oscGrab.start(now)
        oscGrab.stop(now + 0.4)
        
        playTone(1500, 'sine', now + 0.05, 0.3, 0.05)
        break

      case 'success':
        const chord = [523.25, 659.25, 783.99, 1046.50]
        chord.forEach((freq, i) => {
          playTone(freq, 'sine', now + (i * 0.08), 0.4, 0.05)
        })
        break
      
      case 'notification':
        playTone(523.25, 'sine', now, 0.5, 0.05)
        playTone(783.99, 'sine', now + 0.2, 0.8, 0.04)
        break

      case 'startup':
        const oscStart = ctx.createOscillator()
        const gainStart = ctx.createGain()
        oscStart.type = 'sine'
        oscStart.frequency.setValueAtTime(200, now)
        oscStart.frequency.linearRampToValueAtTime(600, now + 0.8)
        
        gainStart.gain.setValueAtTime(0, now)
        gainStart.gain.linearRampToValueAtTime(0.1, now + 0.4)
        gainStart.gain.exponentialRampToValueAtTime(0.001, now + 1.5)
        
        oscStart.connect(gainStart)
        gainStart.connect(masterGain)
        oscStart.start(now)
        oscStart.stop(now + 1.5)
        
        playTone(1200, 'triangle', now + 0.5, 0.5, 0.02)
        break
    }
  }, [isGlobalMuted])

  return { playSound }
}

