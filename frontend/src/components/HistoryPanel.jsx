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
import { useState } from 'react'

function formatRelative(date) {
  const diff = Math.floor((Date.now() - date.getTime()) / 1000)
  if (diff < 60)   return 'just now'
  if (diff < 3600) return `${Math.floor(diff / 60)}m ago`
  if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`
  return date.toLocaleDateString()
}

export default function HistoryPanel({ entries, onSelect }) {
  const [mobileExpanded, setMobileExpanded] = useState(false)

  return (
    <aside
      className="flex-shrink-0 flex flex-col border-t md:border-t-0 md:border-l md:w-72"
      style={{
        background: 'var(--bg-secondary)',
        borderColor: 'var(--border-subtle)',
      }}
    >
      {/* Header — toggles list on mobile, decorative on desktop */}
      <div
        className="flex items-center justify-between px-4 py-3 select-none md:cursor-default cursor-pointer"
        style={{ borderBottom: '1px solid var(--border-subtle)' }}
        onClick={() => setMobileExpanded(e => !e)}
      >
        <div className="flex items-center gap-2">
          <span
            className="font-syne text-xs font-semibold uppercase tracking-widest"
            style={{ color: 'var(--text-secondary)', letterSpacing: '0.1em' }}
          >
            History
          </span>
          {entries.length > 0 && (
            <span
              className="font-mono rounded-full px-1.5 py-0.5"
              style={{
                fontSize: '0.65rem',
                background: 'var(--bg-elevated)',
                color: 'var(--text-muted)',
              }}
            >
              {entries.length}
            </span>
          )}
        </div>
        {/* Chevron — mobile only */}
        <svg
          className="block md:hidden"
          width="14" height="14" viewBox="0 0 24 24"
          fill="none" stroke="currentColor" strokeWidth="2"
          style={{
            color: 'var(--text-muted)',
            transition: 'transform 0.2s ease',
            transform: mobileExpanded ? 'rotate(180deg)' : 'rotate(0deg)',
          }}
        >
          <polyline points="6 9 12 15 18 9" />
        </svg>
      </div>

      {/* Entry list — always visible on desktop, toggleable on mobile */}
      <div
        className={`overflow-y-auto ${mobileExpanded ? 'block' : 'hidden md:block'} md:flex-1 md:min-h-0`}
        style={{ maxHeight: mobileExpanded ? '12rem' : undefined }}
      >
        {entries.length === 0 ? (
          <div className="px-4 py-6 text-center">
            <p
              className="font-outfit text-xs"
              style={{ color: 'var(--text-muted)' }}
            >
              Queries you run will appear here.
            </p>
          </div>
        ) : (
          <div className="flex flex-col">
            {entries.map(entry => (
              <button
                key={entry.id}
                onClick={() => onSelect(entry.query)}
                className="w-full text-left px-4 py-3 flex flex-col gap-1 transition-colors"
                style={{
                  background: 'transparent',
                  border: 'none',
                  borderBottom: '1px solid var(--border-subtle)',
                  cursor: 'pointer',
                }}
                onMouseEnter={e => { e.currentTarget.style.background = 'var(--bg-hover)' }}
                onMouseLeave={e => { e.currentTarget.style.background = 'transparent' }}
              >
                <span
                  className="font-outfit text-xs leading-snug"
                  style={{
                    color: 'var(--text-primary)',
                    display: '-webkit-box',
                    WebkitLineClamp: 2,
                    WebkitBoxOrient: 'vertical',
                    overflow: 'hidden',
                  }}
                >
                  {entry.query}
                </span>
                <span
                  className="font-mono text-xs"
                  style={{ color: 'var(--text-muted)', fontSize: '0.7rem' }}
                >
                  {formatRelative(entry.timestamp)}
                </span>
              </button>
            ))}
          </div>
        )}
      </div>
    </aside>
  )
}
