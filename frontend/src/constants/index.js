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
