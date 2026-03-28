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
