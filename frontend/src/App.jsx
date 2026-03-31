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
import { useState, useEffect, useCallback, useRef } from 'react'
import { useQuery } from './hooks/useQuery'
import { useSettings } from './hooks/useSettings'
import Header from './components/Header'
import Footer from './components/Footer'
import QueryInput from './components/QueryInput'
import StatusIndicator from './components/StatusIndicator'
import AnswerPanel from './components/AnswerPanel'
import DetailPanel from './components/DetailPanel'
import HistoryPanel from './components/HistoryPanel'
import SettingsModal from './components/SettingsModal'

// TEMPORARY: Sentry test — remove after confirming
function ErrorButton() {
  return (
    <button
      onClick={() => {
        Sentry.captureException(new Error('Sentry frontend test'));
        console.log('Event sent to Sentry');
      }}
      style={{ padding: '4px 8px', background: 'red', color: 'white', borderRadius: '4px' }}
    >
      Break the world
    </button>
  );
}

export default function App() {
  const {
    pdbqKey, setPdbqKey,
    anthropicKey, setAnthropicKey,
    theme, setTheme,
    hasKeys,
  } = useSettings()

  const { status, statusMessages, answer, metadata, error, submit, reset } = useQuery()

  const [showSettings, setShowSettings]         = useState(false)
  const [history, setHistory]                   = useState([])
  const [historyInputKey, setHistoryInputKey]   = useState(0)
  const [historyInitialValue, setHistoryInitialValue] = useState('')

  // Apply the saved theme to the document on mount
  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme)
  }, []) // intentionally run once on mount; setTheme handles subsequent changes

  // Add to session history when a query completes successfully
  const prevStatusRef    = useRef('idle')
  const submittedQueryRef = useRef('')

  useEffect(() => {
    const wasActive = prevStatusRef.current === 'loading' || prevStatusRef.current === 'streaming'
    if (wasActive && status === 'done' && submittedQueryRef.current) {
      const q = submittedQueryRef.current
      setHistory(prev => {
        if (prev[0]?.query === q) return prev // skip exact duplicate at top
        return [{ id: Date.now(), query: q, timestamp: new Date() }, ...prev].slice(0, 50)
      })
    }
    prevStatusRef.current = status
  }, [status])

  const handleSubmit = useCallback((q) => {
    submittedQueryRef.current = q
    submit(q, pdbqKey, anthropicKey)
  }, [submit, pdbqKey, anthropicKey])

  // Populate the input and re-submit when a history entry is clicked
  const handleHistorySelect = useCallback((q) => {
    submittedQueryRef.current = q
    setHistoryInitialValue(q)
    setHistoryInputKey(k => k + 1) // re-mounts QueryInput with the history query pre-filled
    submit(q, pdbqKey, anthropicKey)
  }, [submit, pdbqKey, anthropicKey])

  const handleSaveSettings = useCallback((pKey, aKey) => {
    setPdbqKey(pKey)
    setAnthropicKey(aKey)
    setShowSettings(false)
  }, [setPdbqKey, setAnthropicKey])

  const isLoading = status === 'loading' || status === 'streaming'
  const hasResult = Boolean(answer || error)

  // Normalise streaming metadata into the array shape DetailPanel expects
  const normalizedMetadata = metadata ? {
    ...metadata,
    sql_executed: !metadata.sql_executed
      ? []
      : Array.isArray(metadata.sql_executed)
        ? metadata.sql_executed
        : [metadata.sql_executed],
    tool_calls: Array.isArray(metadata.tool_calls) ? metadata.tool_calls : [],
  } : null

  return (
    <div className="flex flex-col" style={{ minHeight: '100vh', background: 'var(--bg-primary)' }}>
      <Header
        theme={theme}
        onToggleTheme={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
        onOpenSettings={() => setShowSettings(true)}
      />

      <main
        className="flex-1 flex flex-col md:flex-row overflow-hidden"
        style={{ minHeight: 0 }}
      >
        {/* Primary content column */}
        <div className="flex-1 min-h-0 overflow-y-auto">
          <div className="max-w-3xl mx-auto px-4 py-8 flex flex-col gap-5">
            <ErrorButton />   {/* TEMPORARY: remove after Sentry test */}
            <QueryInput
              key={historyInputKey}
              initialValue={historyInitialValue}
              onSubmit={handleSubmit}
              isLoading={isLoading}
              onClear={reset}
              hasResult={hasResult}
            />

            <StatusIndicator
              messages={statusMessages}
              visible={status === 'loading'}
            />

            <AnswerPanel answer={answer} status={status} error={error} />

            <DetailPanel
              metadata={normalizedMetadata}
              visible={status === 'done' && Boolean(normalizedMetadata)}
            />
          </div>
        </div>

        {/* Right sidebar — history */}
        <HistoryPanel entries={history} onSelect={handleHistorySelect} />
      </main>

      <Footer />

      {/* Settings modal — required on first visit, optional thereafter */}
      {(!hasKeys || showSettings) && (
        <SettingsModal
          pdbqKey={pdbqKey}
          anthropicKey={anthropicKey}
          onSave={handleSaveSettings}
          onClose={() => setShowSettings(false)}
          isRequired={!hasKeys}
        />
      )}
    </div>
  )
}
