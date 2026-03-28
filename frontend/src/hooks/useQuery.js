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
import { useState, useCallback, useRef } from 'react'
import { streamQuery } from '../lib/api'

const IDLE = { status: 'idle', statusMessages: [], answer: '', metadata: null, error: null, query: '' }

export function useQuery() {
  const [state, setState] = useState(IDLE)
  const abortRef = useRef(null)

  const submit = useCallback(async (query, pdbqKey, anthropicKey) => {
    // Cancel any in-flight request
    if (abortRef.current) abortRef.current = false

    const token = {}
    abortRef.current = token

    setState({ status: 'loading', statusMessages: [], answer: '', metadata: null, error: null, query })

    try {
      for await (const chunk of streamQuery(query, pdbqKey, anthropicKey)) {
        if (!abortRef.current || abortRef.current !== token) break

        if (chunk.type === 'status') {
          setState(prev => ({
            ...prev,
            status: 'loading',
            statusMessages: [...prev.statusMessages, chunk.text],
          }))
        } else if (chunk.type === 'token') {
          setState(prev => ({
            ...prev,
            status: 'streaming',
            answer: prev.answer + chunk.text,
          }))
        } else if (chunk.type === 'metadata') {
          setState(prev => ({
            ...prev,
            status: 'done',
            metadata: chunk,
          }))
        }
      }

      // Ensure we land in done state even if no metadata chunk
      setState(prev =>
        prev.status === 'streaming' ? { ...prev, status: 'done' } : prev
      )
    } catch (err) {
      setState(prev => ({ ...prev, status: 'error', error: err.message || 'Unknown error' }))
    }
  }, [])

  const reset = useCallback(() => {
    abortRef.current = false
    setState(IDLE)
  }, [])

  return { ...state, submit, reset }
}
