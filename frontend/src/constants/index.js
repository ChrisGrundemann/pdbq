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

export const EXAMPLE_QUERIES = [
  { category: 'IXes',       query: 'How many IXes are in Africa?' },
  { category: 'IXes',       query: 'IXes in Africa with more than 10 members' },
  { category: 'IXes',       query: 'Top 10 IXes by member count globally' },
  { category: 'IXes',       query: 'All IXes in Ukraine' },
  { category: 'IXes',       query: 'Which IXes are at Equinix AM3?' },
  { category: 'IXes',       query: 'IXes added to PeeringDB in the last 12 months' },
  { category: 'Networks',   query: 'Which networks peer at more than 10 IXes in Europe?' },
  { category: 'Networks',   query: 'What ASes are present at CoreSite DE1?' },
  { category: 'Networks',   query: 'All networks registered in Japan' },
  { category: 'Networks',   query: 'Networks with IPv6 enabled in South America' },
  { category: 'Networks',   query: 'Top 10 networks by self-reported IPv4 prefix count' },
  { category: 'Networks',   query: 'Which networks joined PeeringDB in 2024?' },
  { category: 'Facilities', query: 'All facilities in Singapore' },
  { category: 'Facilities', query: 'Which facilities host the most networks?' },
  { category: 'Facilities', query: 'Facilities operated by Digital Realty in the US' },
  { category: 'Facilities', query: 'How many data centers are in each country in Asia Pacific?' },
  { category: 'Peering',    query: 'Which networks peer with AS15169 (Google)?' },
  { category: 'Peering',    query: 'What IXes do AS15169 (Google) and AS32934 (Meta) have in common?' },
  { category: 'Peering',    query: 'Networks present at both SFMIX and DE-CIX Frankfurt' },
  { category: 'Peering',    query: 'Which networks at BBIX Thailand have an open peering policy?' },
  { category: 'Carriers',   query: 'Carriers present at Equinix SP4 São Paulo' },
  { category: 'Carriers',   query: 'Which carriers are most widely deployed globally?' },
  { category: 'Historical', query: 'How has the number of IXes in Africa grown year by year since 2010?' },
  { category: 'Historical', query: 'What was the quarterly growth of IX members at AR-IX over the last 5 years?' },
  { category: 'Historical', query: 'How many facilities existed in Asia Pacific in 2015 vs today?' },
]

export const STORAGE_KEYS = {
  PDBQ_KEY:      'pdbq:access_key',
  ANTHROPIC_KEY: 'pdbq:anthropic_key',
  THEME:         'pdbq:theme',
}
