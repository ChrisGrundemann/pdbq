export const API_BASE = import.meta.env.VITE_API_BASE_URL || 'https://api.peeringdb.ai'

export const SUGGESTED_QUERIES = [
  'How many new IXes have been started in Asia in the last 5 years?',
  'Which IXes in Africa have more than 10 members, and which data center is each in?',
  'Which networks are present in New Mexico but are not connected to ABQIX? List with facilities.',
]

export const STORAGE_KEYS = {
  PDBQ_KEY:      'pdbq:access_key',
  ANTHROPIC_KEY: 'pdbq:anthropic_key',
  THEME:         'pdbq:theme',
}
