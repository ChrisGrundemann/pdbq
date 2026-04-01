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
import { EXAMPLE_QUERIES } from '../constants'

const CATEGORIES = ['All', ...Array.from(new Set(EXAMPLE_QUERIES.map(e => e.category)))]

const TAB_BASE = {
  fontFamily: "'Syne', sans-serif",
  fontSize: '0.75rem',
  padding: '4px 10px',
  borderRadius: 6,
  background: 'transparent',
  border: 'none',
  cursor: 'pointer',
  fontWeight: 500,
}

export default function ExamplePanel({ onSelect, onDismiss }) {
  const [activeCategory, setActiveCategory] = useState('All')

  const filtered = activeCategory === 'All'
    ? EXAMPLE_QUERIES
    : EXAMPLE_QUERIES.filter(e => e.category === activeCategory)

  return (
    <div
      className="fade-in"
      style={{
        background: 'var(--bg-secondary)',
        border: '1px solid var(--border)',
        borderRadius: 12,
        padding: '16px 20px',
      }}
    >
      {/* Header row */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
        <div style={{ display: 'flex', flexDirection: 'row', gap: 8, alignItems: 'center' }}>
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="var(--accent)" strokeWidth="2">
            <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>
          </svg>
          <span className="font-syne text-sm" style={{ fontWeight: 700, color: 'var(--text-primary)' }}>
            Example Queries
          </span>
          <span className="font-outfit text-xs" style={{ color: 'var(--text-muted)' }}>
            · Click any to run
          </span>
        </div>
        <button
          onClick={onDismiss}
          className="btn-ghost"
          style={{ borderRadius: 6, padding: '4px 8px', fontSize: '0.75rem' }}
        >
          ✕ Dismiss
        </button>
      </div>

      {/* Category tabs */}
      <div style={{ display: 'flex', flexDirection: 'row', gap: 4, flexWrap: 'wrap', marginBottom: 16, paddingBottom: 12, borderBottom: '1px solid var(--border-subtle)' }}>
        {CATEGORIES.map(cat => (
          <button
            key={cat}
            onClick={() => setActiveCategory(cat)}
            className={activeCategory === cat ? 'tab-active' : 'tab-inactive'}
            style={TAB_BASE}
          >
            {cat}
          </button>
        ))}
      </div>

      {/* Example pills */}
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
        {filtered.map((entry, i) => (
          <button
            key={i}
            onClick={() => onSelect(entry.query)}
            className="font-outfit"
            style={{
              background: 'var(--bg-tertiary)',
              border: '1px solid var(--border-subtle)',
              borderRadius: 8,
              padding: '8px 12px',
              fontSize: '0.75rem',
              textAlign: 'left',
              color: 'var(--text-secondary)',
              cursor: 'pointer',
              maxWidth: 280,
              lineHeight: 1.5,
            }}
            onMouseEnter={e => {
              e.currentTarget.style.borderColor = 'var(--accent)'
              e.currentTarget.style.color = 'var(--text-primary)'
              e.currentTarget.style.background = 'var(--accent-glow)'
            }}
            onMouseLeave={e => {
              e.currentTarget.style.borderColor = 'var(--border-subtle)'
              e.currentTarget.style.color = 'var(--text-secondary)'
              e.currentTarget.style.background = 'var(--bg-tertiary)'
            }}
          >
            {entry.query}
          </button>
        ))}
      </div>
    </div>
  )
}
