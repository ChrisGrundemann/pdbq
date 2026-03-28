import { useState, useRef, useEffect } from 'react'
import { SUGGESTED_QUERIES } from '../constants'

export default function QueryInput({ onSubmit, isLoading, onClear, hasResult, initialValue = '' }) {
  const [value, setValue] = useState(initialValue)
  const textareaRef = useRef(null)

  // Auto-resize textarea
  useEffect(() => {
    const el = textareaRef.current
    if (!el) return
    el.style.height = 'auto'
    el.style.height = Math.min(el.scrollHeight, 220) + 'px'
  }, [value])

  function handleSubmit() {
    const q = value.trim()
    if (!q || isLoading) return
    onSubmit(q)
  }

  function handleKeyDown(e) {
    if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) {
      e.preventDefault()
      handleSubmit()
    }
  }

  function handleSuggestion(q) {
    setValue(q)
    textareaRef.current?.focus()
  }

  function handleClear() {
    setValue('')
    onClear?.()
    textareaRef.current?.focus()
  }

  const canSubmit = value.trim().length > 0 && !isLoading

  return (
    <div className="flex flex-col gap-3">
      {/* Input box */}
      <div
        className="relative rounded-2xl overflow-hidden transition-all"
        style={{
          background: 'var(--bg-secondary)',
          border: '1px solid var(--border)',
          boxShadow: '0 2px 8px rgba(0,0,0,0.15)',
        }}
      >
        <textarea
          ref={textareaRef}
          value={value}
          onChange={e => setValue(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={'SELECT * FROM networks WHERE question = \'yours\''}
          rows={3}
          className="pdbq-input w-full resize-none font-outfit text-sm px-4 pt-4 pb-12"
          style={{
            background: 'transparent',
            border: 'none',
            color: 'var(--text-primary)',
            lineHeight: 1.65,
            minHeight: 96,
          }}
          disabled={isLoading}
          aria-label="Enter your PeeringDB question"
        />

        {/* Bottom toolbar */}
        <div
          className="absolute bottom-0 left-0 right-0 flex items-center justify-between px-3 py-2"
          style={{ borderTop: '1px solid var(--border-subtle)' }}
        >
          <span className="font-mono text-xs" style={{ color: 'var(--text-muted)' }}>
            ⌘↵ to run
          </span>

          <div className="flex items-center gap-2">
            {(value || hasResult) && (
              <button
                onClick={handleClear}
                className="btn-ghost rounded-lg px-3 py-1.5 text-xs font-syne"
                disabled={isLoading}
                style={{ fontSize: '0.75rem' }}
              >
                Clear
              </button>
            )}
            <button
              onClick={handleSubmit}
              disabled={!canSubmit}
              className="btn-primary rounded-lg px-4 py-1.5 flex items-center gap-2"
              style={{ fontSize: '0.8rem' }}
            >
              {isLoading ? (
                <>
                  <span className="spinner" style={{ borderTopColor: '#090c10', borderColor: 'rgba(9,12,16,0.3)', width: 12, height: 12 }} />
                  <span>Running</span>
                </>
              ) : (
                <>
                  <svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor">
                    <polygon points="5 3 19 12 5 21 5 3"/>
                  </svg>
                  <span>Run Query</span>
                </>
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Suggestion pills — only when input is empty and no result */}
      {!value && !hasResult && !isLoading && (
        <div className="flex flex-col gap-2">
          <span
            className="font-syne text-xs uppercase tracking-wider"
            style={{ color: 'var(--text-muted)', letterSpacing: '0.08em' }}
          >
            Try asking
          </span>
          <div className="flex flex-wrap gap-2">
            {SUGGESTED_QUERIES.map((q, i) => (
              <button
                key={i}
                onClick={() => handleSuggestion(q)}
                className="font-outfit text-xs rounded-lg px-3 py-1.5 text-left transition-all"
                style={{
                  background: 'var(--bg-tertiary)',
                  border: '1px solid var(--border-subtle)',
                  color: 'var(--text-secondary)',
                  cursor: 'pointer',
                  lineHeight: 1.5,
                  maxWidth: '100%',
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
                {q}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
