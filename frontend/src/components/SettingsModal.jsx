import { useState } from 'react'

export default function SettingsModal({ pdbqKey, anthropicKey, onSave, onClose, isRequired }) {
  const [localPdbq,      setLocalPdbq]      = useState(pdbqKey || '')
  const [localAnthropic, setLocalAnthropic] = useState(anthropicKey || '')
  const [showPdbq,       setShowPdbq]       = useState(false)
  const [showAnthropic,  setShowAnthropic]  = useState(false)
  const [saveError, setSaveError] = useState('')

  function validate() {
    if (!localPdbq.trim() && !localAnthropic.trim()) {
      setSaveError('Please enter at least one key')
      return false
    }
    setSaveError('')
    return true
  }

  function handleSave() {
    if (!validate()) return
    onSave(localPdbq.trim(), localAnthropic.trim())
  }

  function handleKeyDown(e) {
    if (e.key === 'Enter') handleSave()
    if (e.key === 'Escape' && !isRequired) onClose?.()
  }


  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4"
      style={{ background: 'rgba(9, 12, 16, 0.85)', backdropFilter: 'blur(4px)' }}
      onClick={(e) => { if (!isRequired && e.target === e.currentTarget) onClose?.() }}
    >
      <div
        className="w-full max-w-md fade-in rounded-2xl"
        style={{
          background: 'var(--bg-secondary)',
          border: '1px solid var(--border)',
          boxShadow: '0 24px 64px rgba(0,0,0,0.5), 0 0 0 1px rgba(34,211,238,0.05)',
        }}
        onKeyDown={handleKeyDown}
      >
        {/* Header */}
        <div className="flex items-center justify-between p-6 pb-4">
          <div>
            <h2 className="font-syne font-bold text-lg" style={{ color: 'var(--text-primary)' }}>
              Configure pdbq
            </h2>
            <p className="font-outfit text-sm mt-0.5" style={{ color: 'var(--text-secondary)' }}>
              You need two keys to query PeeringDB data.
            </p>
          </div>
          {!isRequired && (
            <button onClick={onClose} className="btn-ghost rounded-lg p-1.5" aria-label="Close">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <line x1="18" y1="6" x2="6" y2="18"/>
                <line x1="6" y1="6" x2="18" y2="18"/>
              </svg>
            </button>
          )}
        </div>

        <div className="px-6 pb-6 flex flex-col gap-5">
          {/* pdbq Access Key */}
          <div className="flex flex-col gap-1.5">
            <label className="font-syne font-600 text-sm" style={{ color: 'var(--text-primary)', fontWeight: 600 }}>
              pdbq Access Key <span className="font-outfit" style={{ color: 'var(--text-muted)', fontWeight: 400 }}>(optional)</span>
            </label>
            <div className="relative">
              <input
                type={showPdbq ? 'text' : 'password'}
                value={localPdbq}
                onChange={e => { setLocalPdbq(e.target.value); setSaveError('') }}
                placeholder="pdbq-..."
                className="pdbq-input w-full font-mono text-sm rounded-lg px-3 py-2.5 pr-10"
                style={{
                  background: 'var(--bg-tertiary)',
                  border: '1px solid var(--border)',
                  color: 'var(--text-primary)',
                }}
                autoFocus
                autoComplete="off"
                spellCheck={false}
              />
              <button
                type="button"
                onClick={() => setShowPdbq(v => !v)}
                className="absolute right-2.5 top-1/2 -translate-y-1/2"
                style={{ color: 'var(--text-muted)' }}
                tabIndex={-1}
                aria-label={showPdbq ? 'Hide key' : 'Show key'}
              >
                {showPdbq ? (
                  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94"/>
                    <path d="M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19"/>
                    <line x1="1" y1="1" x2="23" y2="23"/>
                  </svg>
                ) : (
                  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
                    <circle cx="12" cy="12" r="3"/>
                  </svg>
                )}
              </button>
            </div>
            <span className="font-outfit text-xs" style={{ color: 'var(--text-muted)' }}>
              Distributed by the pdbq maintainer. Grants access using the community Anthropic key.
            </span>
          </div>

          {/* Anthropic API Key */}
          <div className="flex flex-col gap-1.5">
            <label className="font-syne font-600 text-sm" style={{ color: 'var(--text-primary)', fontWeight: 600 }}>
              Anthropic API Key <span className="font-outfit" style={{ color: 'var(--text-muted)', fontWeight: 400 }}>(optional)</span>
            </label>
            <div className="relative">
              <input
                type={showAnthropic ? 'text' : 'password'}
                value={localAnthropic}
                onChange={e => { setLocalAnthropic(e.target.value); setSaveError('') }}
                placeholder="sk-ant-..."
                className="pdbq-input w-full font-mono text-sm rounded-lg px-3 py-2.5 pr-10"
                style={{
                  background: 'var(--bg-tertiary)',
                  border: '1px solid var(--border)',
                  color: 'var(--text-primary)',
                }}
                autoComplete="off"
                spellCheck={false}
              />
              <button
                type="button"
                onClick={() => setShowAnthropic(v => !v)}
                className="absolute right-2.5 top-1/2 -translate-y-1/2"
                style={{ color: 'var(--text-muted)' }}
                tabIndex={-1}
                aria-label={showAnthropic ? 'Hide key' : 'Show key'}
              >
                {showAnthropic ? (
                  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94"/>
                    <path d="M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19"/>
                    <line x1="1" y1="1" x2="23" y2="23"/>
                  </svg>
                ) : (
                  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
                    <circle cx="12" cy="12" r="3"/>
                  </svg>
                )}
              </button>
            </div>
            <span className="font-outfit text-xs" style={{ color: 'var(--text-muted)' }}>
              Your own Anthropic key — never stored on our servers.
            </span>
          </div>

          {/* Save error */}
          {saveError && (
            <span className="font-outfit text-xs text-center" style={{ color: 'var(--red)' }}>
              {saveError}
            </span>
          )}

          {/* Save button */}
          <button
            onClick={handleSave}
            className="btn-primary w-full rounded-lg py-2.5 text-sm"
            style={{ letterSpacing: '0.04em' }}
          >
            Save & Continue
          </button>

          {!isRequired && (
            <button
              onClick={onClose}
              className="text-center font-outfit text-sm"
              style={{ color: 'var(--text-muted)', background: 'none', border: 'none', cursor: 'pointer' }}
            >
              Cancel
            </button>
          )}
        </div>
      </div>
    </div>
  )
}
