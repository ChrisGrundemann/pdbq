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
export function extractErrorMessage(body) {
  if (!body) return 'Unknown error'
  if (typeof body.detail === 'string') return body.detail
  if (Array.isArray(body.detail)) return body.detail.map(e => e.msg).join(', ')
  return body.message || 'Unknown error'
}

export function friendlyError(status, detail) {
  if (status === 401) {
    if (detail && detail.includes('Invalid API key')) {
      return 'Invalid API key — check your settings'
    }
    return 'API key required — open settings to add your keys'
  }
  if (status === 422) {
    if (detail && detail.includes('Field required')) {
      return 'Please enter a question'
    }
    return detail || 'Invalid request'
  }
  if (status >= 500) {
    return 'Something went wrong on our end — try again in a moment'
  }
  return detail || `Error ${status}`
}

export class APIError extends Error {
  constructor(status, message) {
    super(message)
    this.status = status
    this.name = 'APIError'
  }
}
