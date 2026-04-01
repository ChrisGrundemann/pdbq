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

          {/* How to use */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: 12, marginTop: 20 }}>

            {/* Option 1 — BYOC */}
            <div style={{
              background: 'var(--bg-tertiary)',
              border: '1px solid var(--border-subtle)',
              borderRadius: 8,
              padding: '14px 16px',
            }}>
              <div className="font-syne text-sm" style={{ fontWeight: 600, color: 'var(--text-primary)', marginBottom: 4 }}>
                Option 1 — Bring your own Claude key
              </div>
              <p className="font-outfit text-xs" style={{ color: 'var(--text-secondary)', lineHeight: 1.6, margin: 0 }}>
                You have an Anthropic API key. Click ⚙ above, paste it in, and
                start querying immediately. Your key is used directly and never
                stored on our servers.
              </p>
              <a
                href="https://console.anthropic.com/"
                target="_blank"
                rel="noopener noreferrer"
                className="font-outfit text-xs"
                style={{ color: 'var(--accent)', display: 'inline-block', marginTop: 6 }}
              >
                Get a key at console.anthropic.com →
              </a>
            </div>

            {/* Option 2 — Community key */}
            <div style={{
              background: 'var(--bg-tertiary)',
              border: '1px solid var(--border-subtle)',
              borderRadius: 8,
              padding: '14px 16px',
            }}>
              <div className="font-syne text-sm" style={{ fontWeight: 600, color: 'var(--text-primary)', marginBottom: 4 }}>
                Option 2 — Request a community key
              </div>
              <p className="font-outfit text-xs" style={{ color: 'var(--text-secondary)', lineHeight: 1.6, margin: 0 }}>
                Don't have an Anthropic key? Request a free pdbq community key
                on GitHub. Community requests are rate-limited to manage costs.
              </p>
              <a
                href="https://github.com/ChrisGrundemann/pdbq"
                target="_blank"
                rel="noopener noreferrer"
                className="font-outfit text-xs"
                style={{ color: 'var(--accent)', display: 'inline-block', marginTop: 6 }}
              >
                Request a key on GitHub →
              </a>
            </div>

          </div>

          {/* CTA */}
          <div style={{ marginTop: 16 }}>
            <button
              onClick={onGetStarted}
              className="btn-primary"
              style={{ borderRadius: 8, padding: '10px 20px', fontSize: '0.875rem' }}
            >
              I have a key — get started →
            </button>
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
