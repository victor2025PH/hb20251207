import { useQuery } from '@tanstack/react-query'
import { Gift } from 'lucide-react'
import { useTranslation } from '../providers/I18nProvider'
import { listRedPackets, type RedPacket } from '../utils/api'

export default function PacketsPage() {
  const { t } = useTranslation()

  const { data: packets, isLoading } = useQuery({
    queryKey: ['redpackets'],
    queryFn: listRedPackets,
  })

  if (isLoading) {
    return (
      <div className="h-full flex items-center justify-center">
        <div className="w-8 h-8 border-2 border-brand-red border-t-transparent rounded-full animate-spin" />
      </div>
    )
  }

  return (
    <div className="h-full overflow-y-auto scrollbar-hide pb-20 p-4">
      <h1 className="text-xl font-bold mb-4">{t('packets')}</h1>

      {!packets?.length ? (
        <div className="h-64 flex flex-col items-center justify-center text-gray-400">
          <Gift size={48} className="mb-2 opacity-50" />
          <p>{t('no_data')}</p>
        </div>
      ) : (
        <div className="space-y-3">
          {packets.map((packet) => (
            <PacketCard key={packet.id} packet={packet} />
          ))}
        </div>
      )}
    </div>
  )
}

function PacketCard({ packet }: { packet: RedPacket }) {
  const statusColors = {
    active: 'border-green-500/30 bg-green-500/10',
    completed: 'border-gray-500/30 bg-gray-500/10',
    expired: 'border-red-500/30 bg-red-500/10',
  }

  return (
    <div className={`p-4 rounded-2xl border ${statusColors[packet.status]}`}>
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-2">
          <div className="w-10 h-10 rounded-full bg-gradient-to-br from-orange-500 to-red-600 flex items-center justify-center">
            <Gift size={18} className="text-white" />
          </div>
          <div>
            <div className="text-white font-bold">{packet.sender_name}</div>
            <div className="text-gray-400 text-xs">{packet.message || '恭喜發財！'}</div>
          </div>
        </div>
        <div className="text-right">
          <div className="text-white font-bold">{packet.amount} {packet.currency}</div>
          <div className="text-gray-400 text-xs">{packet.remaining}/{packet.quantity} 份</div>
        </div>
      </div>
    </div>
  )
}

