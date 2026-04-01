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

const TAB_STYLE = {
  fontFamily: "'Syne', sans-serif",
  fontSize: '0.7rem',
  padding: '2px 8px',
  borderRadius: 6,
  background: 'transparent',
  border: 'none',
  cursor: 'pointer',
  whiteSpace: 'nowrap',
}

export default function ExamplePanel({ onSelect }) {
  const [mobileExpanded, setMobileExpanded] = useState(false)
  const [activeCategory, setActiveCategory] = useState('All')

  const filtered = activeCategory === 'All'
    ? EXAMPLE_QUERIES
    : EXAMPLE_QUERIES.filter(e => e.category === activeCategory)

  return (
    <aside
      className="flex-shrink-0 flex flex-col border-b md:border-b-0 md:border-r md:w-64"
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
          <svg
            width="12"
            height="12"
            viewBox="0 0 24 24"
            fill="none"
            stroke="var(--accent)"
            strokeWidth="2"
            style={{ flexShrink: 0 }}
          >
            <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>
          </svg>
          <span
            className="font-syne text-xs font-semibold uppercase tracking-widest"
            style={{ color: 'var(--text-secondary)', letterSpacing: '0.1em' }}
          >
            Examples
          </span>
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

      {/* Category tabs */}
      <div
        className={`flex gap-1 px-4 pt-3 pb-2 overflow-x-auto ${mobileExpanded ? 'block' : 'hidden md:flex'}`}
        style={{ borderBottom: '1px solid var(--border-subtle)', flexShrink: 0 }}
      >
        {CATEGORIES.map(cat => (
          <button
            key={cat}
            onClick={() => setActiveCategory(cat)}
            className={activeCategory === cat ? 'tab-active' : 'tab-inactive'}
            style={TAB_STYLE}
          >
            {cat}
          </button>
        ))}
      </div>

      {/* Example list — always visible on desktop, toggleable on mobile */}
      <div
        className={`overflow-y-auto ${mobileExpanded ? 'block' : 'hidden md:block'} md:flex-1 md:min-h-0`}
        style={{ maxHeight: mobileExpanded ? '16rem' : undefined }}
      >
        {filtered.length === 0 ? (
          <div className="px-4 py-6 text-center">
            <p className="font-outfit text-xs" style={{ color: 'var(--text-muted)' }}>
              No examples in this category.
            </p>
          </div>
        ) : (
          <div className="flex flex-col">
            {filtered.map((entry, i) => (
              <button
                key={i}
                onClick={() => onSelect(entry.query)}
                className="w-full text-left px-4 py-2.5 font-outfit transition-colors"
                style={{
                  background: 'transparent',
                  border: 'none',
                  borderBottom: '1px solid var(--border-subtle)',
                  cursor: 'pointer',
                  fontSize: '0.75rem',
                  lineHeight: 1.5,
                  color: 'var(--text-secondary)',
                }}
                onMouseEnter={e => {
                  e.currentTarget.style.background = 'var(--bg-hover)'
                  e.currentTarget.style.color = 'var(--text-primary)'
                }}
                onMouseLeave={e => {
                  e.currentTarget.style.background = 'transparent'
                  e.currentTarget.style.color = 'var(--text-secondary)'
                }}
              >
                {entry.query}
              </button>
            ))}
          </div>
        )}
      </div>
    </aside>
  )
}
