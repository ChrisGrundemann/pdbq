import Logo from './Logo'
import SyncStatus from './SyncStatus'
import ThemeToggle from './ThemeToggle'

export default function Header({ theme, onToggleTheme, onOpenSettings }) {
  return (
    <header
      className="flex items-center justify-between px-5 py-3 sticky top-0 z-40"
      style={{
        background: 'var(--bg-secondary)',
        borderBottom: '1px solid var(--border-subtle)',
        backdropFilter: 'blur(8px)',
      }}
    >
      <Logo size="sm" />

      <div className="flex items-center gap-2">
        <SyncStatus />

        <div style={{ width: 1, height: 20, background: 'var(--border)', margin: '0 4px' }} />

        <ThemeToggle theme={theme} onToggle={onToggleTheme} />

        <button
          onClick={onOpenSettings}
          aria-label="Open settings"
          className="btn-ghost rounded-lg flex items-center justify-center"
          style={{ width: 36, height: 36, padding: 0 }}
          title="Settings"
        >
          {/* Settings / key icon */}
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <circle cx="12" cy="12" r="3"/>
            <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/>
          </svg>
        </button>
      </div>
    </header>
  )
}
