import { useState } from 'react'

function MetaRow({ label, value }) {
  return (
    <div className="flex items-center justify-between py-2" style={{ borderBottom: '1px solid var(--border-subtle)' }}>
      <span className="font-syne text-xs uppercase tracking-wider" style={{ color: 'var(--text-muted)', letterSpacing: '0.08em' }}>
        {label}
      </span>
      <span className="font-mono text-sm" style={{ color: 'var(--text-primary)' }}>
        {value}
      </span>
    </div>
  )
}

function SqlTab({ statements }) {
  if (!statements?.length) {
    return (
      <p className="font-mono text-sm" style={{ color: 'var(--text-muted)' }}>No SQL executed.</p>
    )
  }
  return (
    <div className="flex flex-col gap-3">
      {statements.map((sql, i) => (
        <div key={i}>
          {statements.length > 1 && (
            <span className="font-syne text-xs uppercase tracking-wider mb-1.5 block" style={{ color: 'var(--text-muted)' }}>
              Query {i + 1}
            </span>
          )}
          <pre
            className="rounded-lg p-4 overflow-x-auto text-sm"
            style={{
              background: 'var(--bg-primary)',
              border: '1px solid var(--border-subtle)',
              color: 'var(--violet)',
              fontFamily: '"JetBrains Mono", monospace',
              lineHeight: 1.65,
              margin: 0,
            }}
          >
            <code>{sql}</code>
          </pre>
        </div>
      ))}
    </div>
  )
}

function ToolCallsTab({ toolCalls }) {
  if (!toolCalls?.length) {
    return (
      <p className="font-mono text-sm" style={{ color: 'var(--text-muted)' }}>No tool calls recorded.</p>
    )
  }
  return (
    <div className="flex flex-col gap-3">
      {toolCalls.map((tc, i) => (
        <div key={i}>
          <span className="font-syne text-xs uppercase tracking-wider mb-1.5 block" style={{ color: 'var(--text-muted)' }}>
            Call {i + 1}{tc.name ? ` — ${tc.name}` : ''}
          </span>
          <pre
            className="rounded-lg p-4 overflow-x-auto text-xs"
            style={{
              background: 'var(--bg-primary)',
              border: '1px solid var(--border-subtle)',
              color: 'var(--text-secondary)',
              fontFamily: '"JetBrains Mono", monospace',
              lineHeight: 1.65,
              margin: 0,
            }}
          >
            <code>{JSON.stringify(tc, null, 2)}</code>
          </pre>
        </div>
      ))}
    </div>
  )
}

function MetaTab({ metadata }) {
  if (!metadata) return null
  return (
    <div className="flex flex-col">
      <MetaRow label="Elapsed"       value={`${metadata.elapsed_ms?.toLocaleString() ?? '—'} ms`} />
      <MetaRow label="SQL queries"   value={metadata.sql_executed?.length ?? 0} />
      <MetaRow label="Tool calls"    value={metadata.tool_calls?.length ?? 0} />
      {metadata.model && <MetaRow label="Model" value={metadata.model} />}
    </div>
  )
}

const TABS = ['SQL', 'Tool Calls', 'Meta']

export default function DetailPanel({ metadata, visible }) {
  const [activeTab, setActiveTab] = useState('SQL')

  if (!visible || !metadata) return null

  return (
    <div
      className="fade-in rounded-xl overflow-hidden"
      style={{ border: '1px solid var(--border-subtle)', background: 'var(--bg-tertiary)' }}
    >
      {/* Tab bar */}
      <div
        className="flex items-center gap-0 px-4"
        style={{ borderBottom: '1px solid var(--border-subtle)' }}
      >
        {TABS.map(tab => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`font-syne text-xs font-semibold py-3 px-3 mr-1 transition-all ${
              activeTab === tab ? 'tab-active' : 'tab-inactive'
            }`}
            style={{
              background: 'none',
              border: 'none',
              borderBottom: activeTab === tab ? '2px solid var(--accent)' : '2px solid transparent',
              color: activeTab === tab ? 'var(--accent)' : 'var(--text-secondary)',
              cursor: 'pointer',
              letterSpacing: '0.06em',
              textTransform: 'uppercase',
            }}
          >
            {tab}
            {tab === 'SQL' && metadata.sql_executed?.length > 0 && (
              <span
                className="ml-1.5 rounded-full px-1.5 py-0.5 text-xs"
                style={{ background: 'var(--accent-glow)', color: 'var(--accent)', fontSize: '0.65rem' }}
              >
                {metadata.sql_executed.length}
              </span>
            )}
          </button>
        ))}

        {/* Elapsed badge — always visible in tab bar */}
        <div className="ml-auto flex items-center gap-1.5">
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="var(--text-muted)" strokeWidth="2">
            <circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>
          </svg>
          <span className="font-mono text-xs" style={{ color: 'var(--text-muted)' }}>
            {metadata.elapsed_ms != null ? `${(metadata.elapsed_ms / 1000).toFixed(1)}s` : '—'}
          </span>
        </div>
      </div>

      {/* Tab content */}
      <div className="p-4">
        {activeTab === 'SQL'        && <SqlTab       statements={metadata.sql_executed} />}
        {activeTab === 'Tool Calls' && <ToolCallsTab toolCalls={metadata.tool_calls} />}
        {activeTab === 'Meta'       && <MetaTab      metadata={metadata} />}
      </div>
    </div>
  )
}
