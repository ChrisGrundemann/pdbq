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
import { API_BASE } from '../constants'
import { APIError, extractErrorMessage, friendlyError } from './errors'

function buildHeaders(pdbqKey, anthropicKey) {
  const headers = { 'Content-Type': 'application/json' }
  if (pdbqKey && pdbqKey.trim())           headers['Authorization']   = `Bearer ${pdbqKey}`
  if (anthropicKey && anthropicKey.trim()) headers['X-Anthropic-Key'] = anthropicKey
  return headers
}

export async function* streamQuery(query, pdbqKey, anthropicKey) {
  const response = await fetch(`${API_BASE}/query`, {
    method: 'POST',
    headers: buildHeaders(pdbqKey, anthropicKey),
    body: JSON.stringify({ query, stream: true }),
  })

  if (!response.ok) {
    let body = {}
    try { body = await response.json() } catch {}
    const detail  = extractErrorMessage(body)
    const message = friendlyError(response.status, detail)
    throw new APIError(response.status, message)
  }

  const reader  = response.body.getReader()
  const decoder = new TextDecoder()
  let buffer    = ''

  while (true) {
    const { done, value } = await reader.read()
    if (done) break
    buffer += decoder.decode(value, { stream: true })
    const lines = buffer.split('\n')
    buffer = lines.pop() // retain incomplete line
    for (const line of lines) {
      const trimmed = line.trim()
      if (!trimmed) continue
      try {
        yield JSON.parse(trimmed)
      } catch {
        // malformed line — skip
      }
    }
  }
  // flush remaining buffer
  if (buffer.trim()) {
    try { yield JSON.parse(buffer.trim()) } catch {}
  }
}

export async function fetchHealth() {
  const res = await fetch(`${API_BASE}/health`)
  return res.ok ? res.json() : null
}

export async function fetchSyncStatus() {
  const res = await fetch(`${API_BASE}/sync/status`)
  return res.ok ? res.json() : null
}
