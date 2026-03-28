import { useState, useCallback } from 'react'
import { STORAGE_KEYS } from '../constants'

function load(key) {
  try { return localStorage.getItem(key) || '' } catch { return '' }
}
function save(key, value) {
  try { localStorage.setItem(key, value) } catch {}
}

export function useSettings() {
  const [pdbqKey,      setPdbqKeyState]      = useState(() => load(STORAGE_KEYS.PDBQ_KEY))
  const [anthropicKey, setAnthropicKeyState] = useState(() => load(STORAGE_KEYS.ANTHROPIC_KEY))
  const [theme,        setThemeState]        = useState(() => load(STORAGE_KEYS.THEME) || 'dark')

  const setPdbqKey = useCallback((val) => {
    setPdbqKeyState(val)
    save(STORAGE_KEYS.PDBQ_KEY, val)
  }, [])

  const setAnthropicKey = useCallback((val) => {
    setAnthropicKeyState(val)
    save(STORAGE_KEYS.ANTHROPIC_KEY, val)
  }, [])

  const setTheme = useCallback((val) => {
    setThemeState(val)
    save(STORAGE_KEYS.THEME, val)
    document.documentElement.setAttribute('data-theme', val)
  }, [])

  const hasKeys = Boolean(pdbqKey || anthropicKey)

  return { pdbqKey, setPdbqKey, anthropicKey, setAnthropicKey, theme, setTheme, hasKeys }
}
