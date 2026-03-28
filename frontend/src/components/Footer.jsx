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
        href="#"
        className="font-syne"
        style={{ fontSize: '0.72rem', color: 'var(--text-muted)', textDecoration: 'none' }}
        onMouseEnter={e => { e.currentTarget.style.color = 'var(--text-secondary)' }}
        onMouseLeave={e => { e.currentTarget.style.color = 'var(--text-muted)' }}
      >
        Terms of Service
      </a>
      <span style={{ color: 'var(--border)', fontSize: '0.72rem' }}>|</span>
      <a
        href="#"
        className="font-syne"
        style={{ fontSize: '0.72rem', color: 'var(--text-muted)', textDecoration: 'none' }}
        onMouseEnter={e => { e.currentTarget.style.color = 'var(--text-secondary)' }}
        onMouseLeave={e => { e.currentTarget.style.color = 'var(--text-muted)' }}
      >
        Privacy Policy
      </a>
    </footer>
  )
}
