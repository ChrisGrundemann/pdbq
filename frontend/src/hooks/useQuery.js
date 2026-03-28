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
