export default function Logo({ size = 'md', showTagline = false }) {
  const scales = { sm: 0.75, md: 1, lg: 1.35 }
  const s = scales[size] || 1

  return (
    <div className="flex items-center gap-3" style={{ userSelect: 'none' }}>
      {/* Peering topology mark */}
      <svg
        width={Math.round(40 * s)}
        height={Math.round(32 * s)}
        viewBox="0 0 40 32"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        aria-hidden="true"
      >
        {/* Edge: node A ↔ node B */}
        <line x1="7" y1="10" x2="33" y2="10" stroke="var(--accent)" strokeWidth="1.5" strokeOpacity="0.6" />
        {/* Edge: node B → node C */}
        <line x1="33" y1="10" x2="26" y2="24" stroke="var(--accent)" strokeWidth="1.5" strokeOpacity="0.4" />
        {/* Edge: node A → node C */}
        <line x1="7" y1="10" x2="26" y2="24" stroke="var(--accent)" strokeWidth="1" strokeOpacity="0.25" />

        {/* Node A — left (primary) */}
        <circle cx="7" cy="10" r="4.5" fill="var(--accent)" fillOpacity="0.15" stroke="var(--accent)" strokeWidth="1.5" />
        <circle cx="7" cy="10" r="2" fill="var(--accent)" />

        {/* Node B — right (primary) */}
        <circle cx="33" cy="10" r="4.5" fill="var(--accent)" fillOpacity="0.15" stroke="var(--accent)" strokeWidth="1.5" />
        <circle cx="33" cy="10" r="2" fill="var(--accent)" />

        {/* Node C — bottom (secondary) */}
        <circle cx="26" cy="24" r="3.5" fill="var(--accent)" fillOpacity="0.1" stroke="var(--accent)" strokeWidth="1" strokeOpacity="0.5" />
        <circle cx="26" cy="24" r="1.5" fill="var(--accent)" fillOpacity="0.7" />

        {/* Subtle glow on primary nodes */}
        <circle cx="7"  cy="10" r="7" fill="var(--accent)" fillOpacity="0.04" />
        <circle cx="33" cy="10" r="7" fill="var(--accent)" fillOpacity="0.04" />
      </svg>

      {/* Wordmark */}
      <div className="flex flex-col leading-none">
        <div className="flex items-baseline" style={{ gap: '1px' }}>
          <span
            className="font-mono font-bold tracking-tight"
            style={{
              fontSize: `${Math.round(22 * s)}px`,
              color: 'var(--text-primary)',
              letterSpacing: '-0.03em',
            }}
          >
            pdbq
          </span>
          <span
            className="font-mono font-bold cursor-blink"
            style={{
              fontSize: `${Math.round(22 * s)}px`,
              color: 'var(--accent)',
              marginLeft: '1px',
            }}
            aria-hidden="true"
          >
            _
          </span>
        </div>
        {showTagline && (
          <span
            className="font-syne"
            style={{
              fontSize: `${Math.round(10 * s)}px`,
              color: 'var(--text-muted)',
              letterSpacing: '0.08em',
              textTransform: 'uppercase',
              marginTop: '2px',
            }}
          >
            PeeringDB Query Agent
          </span>
        )}
      </div>
    </div>
  )
}
