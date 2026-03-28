export default function StatusIndicator({ messages, visible }) {
  if (!visible) return null

  return (
    <div
      className="fade-in rounded-xl px-4 py-3 flex flex-col gap-2"
      style={{
        background: 'var(--bg-tertiary)',
        border: '1px solid var(--border-subtle)',
      }}
    >
      {messages.length === 0 ? (
        <div className="flex items-center gap-2.5">
          <span className="spinner" />
          <span className="font-mono text-xs" style={{ color: 'var(--text-secondary)' }}>
            Connecting to PeeringDB agent...
          </span>
        </div>
      ) : (
        messages.map((msg, i) => {
          const isLast = i === messages.length - 1
          return (
            <div key={i} className="flex items-center gap-2.5 fade-in">
              {isLast ? (
                <span className="spinner flex-shrink-0" />
              ) : (
                /* Checkmark for completed steps */
                <svg
                  width="14" height="14" viewBox="0 0 14 14" fill="none"
                  className="flex-shrink-0"
                  style={{ color: 'var(--green)' }}
                >
                  <circle cx="7" cy="7" r="6.5" stroke="currentColor" strokeOpacity="0.3" />
                  <path
                    d="M4.5 7L6.2 8.7L9.5 5.3"
                    stroke="currentColor" strokeWidth="1.4"
                    strokeLinecap="round" strokeLinejoin="round"
                  />
                </svg>
              )}
              <span
                className="font-mono text-xs"
                style={{ color: isLast ? 'var(--text-secondary)' : 'var(--text-muted)' }}
              >
                {msg}
              </span>
            </div>
          )
        })
      )}
    </div>
  )
}
