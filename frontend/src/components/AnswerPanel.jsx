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
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import rehypeHighlight from 'rehype-highlight'
import 'highlight.js/styles/github-dark.css'

export default function AnswerPanel({ answer, status, error }) {
  if (error) {
    return (
      <div
        className="fade-in rounded-xl px-4 py-3 flex items-start gap-3"
        style={{ background: 'var(--red-dim)', border: '1px solid var(--red)', borderOpacity: 0.3 }}
      >
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="var(--red)" strokeWidth="2" className="flex-shrink-0 mt-0.5">
          <circle cx="12" cy="12" r="10"/>
          <line x1="12" y1="8" x2="12" y2="12"/>
          <line x1="12" y1="16" x2="12.01" y2="16"/>
        </svg>
        <div>
          <p className="font-syne font-semibold text-sm" style={{ color: 'var(--red)', margin: 0 }}>
            Query failed
          </p>
          <p className="font-outfit text-sm mt-0.5" style={{ color: 'var(--text-secondary)', margin: 0 }}>
            {error}
          </p>
        </div>
      </div>
    )
  }

  if (!answer) return null

  return (
    <div className="fade-in flex flex-col gap-3">
      {/* Answer label */}
      <div className="flex items-center gap-2">
        <span
          className="font-syne text-xs font-semibold uppercase tracking-widest"
          style={{ color: 'var(--accent)', letterSpacing: '0.1em' }}
        >
          Answer
        </span>
        {(status === 'streaming') && (
          <span
            className="inline-block rounded-full status-pulse"
            style={{ width: 5, height: 5, background: 'var(--accent)' }}
          />
        )}
      </div>

      {/* Markdown content */}
      <div
        className="rounded-xl px-5 py-4"
        style={{
          background: 'var(--bg-secondary)',
          border: '1px solid var(--border-subtle)',
          boxShadow: '0 1px 3px rgba(0,0,0,0.12)',
        }}
      >
        <div className="markdown-answer">
          <ReactMarkdown
            remarkPlugins={[remarkGfm]}
            rehypePlugins={[rehypeHighlight]}
          >
            {answer}
          </ReactMarkdown>
        </div>

        {/* Streaming cursor at end of text */}
        {status === 'streaming' && (
          <span className="font-mono cursor-blink" style={{ fontSize: '0.9rem' }}>▮</span>
        )}
      </div>
    </div>
  )
}
