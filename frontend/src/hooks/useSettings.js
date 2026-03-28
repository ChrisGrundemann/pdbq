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
