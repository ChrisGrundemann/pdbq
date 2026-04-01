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
import { useState, forwardRef, useImperativeHandle } from 'react'

const PILLS = [
  {
    label: '208k+ records',
    description: 'Full PeeringDB mirror, updated nightly.',
    icon: (
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <ellipse cx="12" cy="5" rx="9" ry="3"/>
        <path d="M3 5v14c0 1.66 4.03 3 9 3s9-1.34 9-3V5"/>
        <path d="M3 12c0 1.66 4.03 3 9 3s9-1.34 9-3"/>
      </svg>
    ),
  },
  {
    label: 'Claude-powered',
    description: 'Natural language → SQL → answer.',
    icon: (
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>
      </svg>
    ),
  },
  {
    label: 'Shareable queries',
    description: 'Every query gets a linkable URL.',
    icon: (
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/>
        <path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/>
      </svg>
    ),
  },
]

const HeroPanel = forwardRef(function HeroPanel({ onGetStarted }, ref) {
  const [expanded, setExpanded] = useState(() => localStorage.getItem('pdbq_visited') !== '1')

  useImperativeHandle(ref, () => ({
    collapse() {
      setExpanded(false)
      localStorage.setItem('pdbq_visited', '1')
    },
  }))

  return (
    <div
      className="network-grid fade-in"
      style={{
        background: 'var(--bg-secondary)',
        borderRadius: 12,
        border: '1px solid var(--border)',
        padding: '20px 24px',
      }}
    >
      {/* Toggle bar — always visible */}
      <div
        onClick={() => setExpanded(v => !v)}
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          paddingBottom: expanded ? 8 : 0,
          borderBottom: expanded ? '1px solid var(--border-subtle)' : 'none',
          cursor: 'pointer',
          userSelect: 'none',
        }}
      >
        <span className="font-outfit text-xs" style={{ color: 'var(--text-muted)' }}>
          pdbq — natural-language queries over PeeringDB
        </span>
        <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
          <span className="font-syne text-xs" style={{ color: 'var(--text-secondary)' }}>About</span>
          <svg
            width="12"
            height="12"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            style={{
              color: 'var(--text-secondary)',
              transform: expanded ? 'rotate(180deg)' : 'rotate(0deg)',
              transition: 'transform 200ms ease',
            }}
          >
            <polyline points="6 9 12 15 18 9"/>
          </svg>
        </div>
      </div>

      {/* Collapsible hero content */}
      <div
        style={{
          maxHeight: expanded ? 800 : 0,
          overflow: 'hidden',
          transition: 'max-height 300ms ease',
        }}
      >
        <div style={{ paddingTop: 20 }}>
          {/* Headline */}
          <h1
            className="font-syne"
            style={{ fontWeight: 700, fontSize: '1.5rem', color: 'var(--text-primary)', margin: 0 }}
          >
            Ask PeeringDB anything.
          </h1>

          {/* Subhead */}
          <p
            className="font-outfit"
            style={{
              fontSize: '0.9375rem',
              color: 'var(--text-secondary)',
              maxWidth: 520,
              marginTop: 8,
              marginBottom: 0,
              lineHeight: 1.6,
            }}
          >
            pdbq is a natural-language query agent over the full PeeringDB dataset —
            200k+ records across IXes, networks, facilities, ASNs, peering sessions,
            and carriers. Powered by Claude. No SQL required.
          </p>

          {/* Feature pills */}
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 12, marginTop: 20 }}>
            {PILLS.map(({ label, description, icon }) => (
              <div
                key={label}
                style={{
                  background: 'var(--bg-tertiary)',
                  border: '1px solid var(--border-subtle)',
                  borderRadius: 8,
                  padding: '12px 16px',
                  display: 'flex',
                  flexDirection: 'row',
                  gap: 10,
                  alignItems: 'center',
                }}
              >
                <div
                  style={{
                    width: 28,
                    height: 28,
                    borderRadius: 6,
                    background: 'var(--accent-glow)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    flexShrink: 0,
                    color: 'var(--accent)',
                  }}
                >
                  {icon}
                </div>
                <div>
                  <div className="font-syne text-sm" style={{ fontWeight: 600, color: 'var(--text-primary)' }}>
                    {label}
                  </div>
                  <div className="font-outfit text-xs" style={{ color: 'var(--text-muted)', marginTop: 2 }}>
                    {description}
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* CTA row */}
          <div style={{ display: 'flex', flexDirection: 'row', gap: 12, alignItems: 'center', flexWrap: 'wrap', marginTop: 20 }}>
            <button
              onClick={onGetStarted}
              className="btn-primary"
              style={{ borderRadius: 8, padding: '10px 20px', fontSize: '0.875rem' }}
            >
              Get started →
            </button>
            <span className="font-outfit text-sm" style={{ color: 'var(--text-muted)' }}>
              or paste your Anthropic key into ⚙ above
            </span>
          </div>

          {/* Disclaimer */}
          <div
            style={{
              marginTop: 16,
              paddingTop: 16,
              borderTop: '1px solid var(--border-subtle)',
            }}
          >
            <p
              className="font-outfit text-xs"
              style={{ color: 'var(--text-muted)', fontStyle: 'italic', margin: 0 }}
            >
              pdbq is an unofficial community tool, not affiliated with PeeringDB.
              Data use is subject to the{' '}
              <a
                href="https://www.peeringdb.com/aup"
                target="_blank"
                rel="noopener noreferrer"
                style={{ color: 'var(--accent)' }}
              >
                PeeringDB Acceptable Use Policy
              </a>
              .
            </p>
          </div>
        </div>
      </div>
    </div>
  )
})

export default HeroPanel
