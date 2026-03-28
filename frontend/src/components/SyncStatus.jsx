// pdbq - Natural language query agent for PeeringDB
// Copyright (C) 2025 Chris Grundemann
//
// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU Affero General Public License as
// published by the Free Software Foundation, either version 3 of the
// License, or (at your option) any later version.
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
// GNU Affero General Public License for more details.
//
// You should have received a copy of the GNU Affero General Public License
// along with this program. If not, see <https://www.gnu.org/licenses/>.
import { useState, useEffect } from 'react'
import { fetchSyncStatus } from '../lib/api'

function timeAgo(dateStr) {
  if (!dateStr) return null
  const diff = Date.now() - new Date(dateStr).getTime()
  const mins  = Math.floor(diff / 60_000)
  const hours = Math.floor(diff / 3_600_000)
  const days  = Math.floor(diff / 86_400_000)
  if (mins  <  1)  return 'just now'
  if (mins  < 60)  return `${mins}m ago`
  if (hours < 24)  return `${hours}h ago`
  return `${days}d ago`
}

export default function SyncStatus() {
  const [status, setStatus] = useState(null)
  const [stale,  setStale]  = useState(false)

  useEffect(() => {
    let mounted = true
    async function poll() {
      try {
        const data = await fetchSyncStatus()
        if (!mounted) return
        setStatus(data)
        // Consider stale if last sync > 25 hours ago
        if (data?.last_sync) {
          const hours = (Date.now() - new Date(data.last_sync).getTime()) / 3_600_000
          setStale(hours > 25)
        }
      } catch {}
    }
    poll()
    const interval = setInterval(poll, 5 * 60_000) // poll every 5 min
    return () => { mounted = false; clearInterval(interval) }
  }, [])

  if (!status) return null

  const ago   = timeAgo(status.last_sync)
  const color = stale ? 'var(--amber)' : 'var(--green)'
  const label = stale ? `Data may be stale — synced ${ago}` : `Synced ${ago}`

  return (
    <div
      className="flex items-center gap-1.5"
      title={label}
      style={{ cursor: 'default' }}
    >
      <span
        className="status-pulse inline-block rounded-full"
        style={{ width: 7, height: 7, background: color, flexShrink: 0 }}
      />
      <span
        className="font-syne hidden sm:inline-block"
        style={{ fontSize: '0.72rem', color: stale ? 'var(--amber)' : 'var(--text-muted)', letterSpacing: '0.04em' }}
      >
        {ago}
      </span>
    </div>
  )
}
