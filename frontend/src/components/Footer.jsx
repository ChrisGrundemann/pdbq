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
export default function Footer() {
  return (
    <footer
      className="flex flex-wrap items-center justify-center gap-x-3 gap-y-1 px-4 py-3 text-center"
      style={{
        borderTop: '1px solid var(--border-subtle)',
        background: 'var(--bg-secondary)',
      }}
    >
      <span
        className="font-syne"
        style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}
      >
        pdbq is an unofficial community tool, not affiliated with PeeringDB.
      </span>
      <span style={{ color: 'var(--border)', fontSize: '0.72rem' }}>|</span>
      <a
        href="/terms.html"
        className="font-syne"
        style={{ fontSize: '0.72rem', color: 'var(--text-muted)', textDecoration: 'none' }}
        onMouseEnter={e => { e.currentTarget.style.color = 'var(--text-secondary)' }}
        onMouseLeave={e => { e.currentTarget.style.color = 'var(--text-muted)' }}
      >
        Terms of Service
      </a>
      <span style={{ color: 'var(--border)', fontSize: '0.72rem' }}>|</span>
      <a
        href="/privacy.html"
        className="font-syne"
        style={{ fontSize: '0.72rem', color: 'var(--text-muted)', textDecoration: 'none' }}
        onMouseEnter={e => { e.currentTarget.style.color = 'var(--text-secondary)' }}
        onMouseLeave={e => { e.currentTarget.style.color = 'var(--text-muted)' }}
      >
        Privacy Policy
      </a>
      <span style={{ color: 'var(--border)', fontSize: '0.72rem' }}>|</span>
      <span
        className="font-syne"
        style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}
      >
        pdbq is open source software licensed under{' '}

          href="https://www.gnu.org/licenses/agpl-3.0.html"
          className="font-syne"
          style={{ fontSize: '0.72rem', color: 'var(--text-muted)', textDecoration: 'none' }}
          onMouseEnter={e => { e.currentTarget.style.color = 'var(--text-secondary)' }}
          onMouseLeave={e => { e.currentTarget.style.color = 'var(--text-muted)' }}
          target="_blank"
          rel="noopener noreferrer"
        >
          AGPL v3
        </a>
        {'. Source code available at '}

          href="https://github.com/ChrisGrundemann/pdbq"
          className="font-syne"
          style={{ fontSize: '0.72rem', color: 'var(--text-muted)', textDecoration: 'none' }}
          onMouseEnter={e => { e.currentTarget.style.color = 'var(--text-secondary)' }}
          onMouseLeave={e => { e.currentTarget.style.color = 'var(--text-muted)' }}
          target="_blank"
          rel="noopener noreferrer"
        >
          github.com/ChrisGrundemann/pdbq
        </a>
        {'. Copyright © 2025 Chris Grundemann.'}
      </span>
    </footer>
  )
}
