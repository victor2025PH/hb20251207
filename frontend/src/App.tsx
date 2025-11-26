import { lazy, Suspense } from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import BottomNav from './components/BottomNav'
import TopToolbar from './components/TopToolbar'
import Loading from './components/Loading'

// 懒加载页面
const WalletPage = lazy(() => import('./pages/WalletPage'))
const PacketsPage = lazy(() => import('./pages/PacketsPage'))
const EarnPage = lazy(() => import('./pages/EarnPage'))
const GamePage = lazy(() => import('./pages/GamePage'))
const ProfilePage = lazy(() => import('./pages/ProfilePage'))
const SendRedPacket = lazy(() => import('./pages/SendRedPacket'))
const Recharge = lazy(() => import('./pages/Recharge'))
const Withdraw = lazy(() => import('./pages/Withdraw'))

export default function App() {
  return (
    <div className="fixed inset-0 bg-brand-dark text-white flex flex-col overflow-hidden">
      <TopToolbar />
      
      <main className="flex-1 overflow-hidden">
        <Suspense fallback={<Loading />}>
          <Routes>
            <Route path="/" element={<WalletPage />} />
            <Route path="/packets" element={<PacketsPage />} />
            <Route path="/send" element={<SendRedPacket />} />
            <Route path="/earn" element={<EarnPage />} />
            <Route path="/game" element={<GamePage />} />
            <Route path="/profile" element={<ProfilePage />} />
            <Route path="/recharge" element={<Recharge />} />
            <Route path="/withdraw" element={<Withdraw />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </Suspense>
      </main>
      
      <BottomNav />
    </div>
  )
}

