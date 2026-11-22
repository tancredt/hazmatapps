import { apiFetch } from '@/utils/api'

/**
 * Shared label verification for the transfer pages.
 *
 * Outcomes are deliberately three-valued:
 *   found   -> the record exists, carry on
 *   missing -> the register answered and there is no such label  -> 404 panel
 *   error   -> we could not ask (network / server)               -> retry panel
 *
 * "error" is never reported as "missing", so a dropout can't tell a crew that
 * a real asset doesn't exist.
 */

const TTL_MS = 60 * 1000
const cache = new Map()

const cacheKey = (kind, label) => `${kind}:${String(label).trim().toUpperCase()}`

const readCache = (key) => {
  const hit = cache.get(key)
  if (!hit) return null
  if (Date.now() - hit.at > TTL_MS) {
    cache.delete(key)
    return null
  }
  return hit.result
}

const writeCache = (key, result) => cache.set(key, { result, at: Date.now() })

const toList = (payload) => {
  if (Array.isArray(payload)) return payload
  if (Array.isArray(payload?.results)) return payload.results
  return []
}

export const normalizeCylinderLabel = (value) => {
  const cleaned = String(value ?? '').trim().toUpperCase().replace(/\s+/g, '')
  const match = cleaned.match(/^CYL0*(\d+)$/) || cleaned.match(/^0*(\d+)$/)
  return match ? `CYL${match[1].padStart(5, '0')}` : cleaned
}

export const firstParam = (raw) =>
  String(Array.isArray(raw) ? (raw[0] ?? '') : (raw ?? '')).trim()

export async function lookupDetector(rawLabel, { force = false } = {}) {
  const label = firstParam(rawLabel)
  if (!label) return { state: 'idle', label: '', record: null }

  const key = cacheKey('detector', label)
  if (!force) {
    const hit = readCache(key)
    if (hit) return hit
  }

  try {
    const payload = await apiFetch(`/detector-labels/?label=${encodeURIComponent(label)}`)
    const target = label.toUpperCase()
    // Backend filter is `icontains`, so confirm an exact case-insensitive match.
    const record =
      toList(payload).find(
        (d) => String(d?.label ?? '').trim().toUpperCase() === target
      ) || null

    const result = record
      ? { state: 'found', label, record }
      : { state: 'missing', label, record: null }

    writeCache(key, result)
    return result
  } catch (error) {
    console.error('[labelLookup] detector lookup failed', error)
    return { state: 'error', label, record: null, error }
  }
}

export async function lookupCylinder(rawLabel, { force = false } = {}) {
  const label = normalizeCylinderLabel(rawLabel)
  if (!label) return { state: 'idle', label: '', record: null }

  const key = cacheKey('cylinder', label)
  if (!force) {
    const hit = readCache(key)
    if (hit) return hit
  }

  // Canonical form first, then the bare number in case the register indexes ids.
  const queries = [label]
  const digits = label.match(/^CYL(\d+)$/)
  if (digits) queries.push(String(Number(digits[1])))

  let lastError = null

  for (const query of queries) {
    try {
      const payload = await apiFetch(`/cylinders/?label=${encodeURIComponent(query)}`)
      const record =
        toList(payload).find((c) => normalizeCylinderLabel(c?.label) === label) || null

      if (record) {
        const result = { state: 'found', label, record }
        writeCache(key, result)
        return result
      }
    } catch (error) {
      lastError = error
    }
  }

  if (lastError) {
    console.error('[labelLookup] cylinder lookup failed', lastError)
    return { state: 'error', label, record: null, error: lastError }
  }

  const result = { state: 'missing', label, record: null }
  writeCache(key, result)
  return result
}

export const DISTRICT_WORDS = {
  CC: 'Central',
  E1: 'Eastern',
  N1: 'Northern',
  S1: 'Southern 1',
  S2: 'Southern 2',
  W1: 'Western 1',
  W2: 'Western 2',
  W3: 'Western 3',
  LA: 'Latrobe Valley'
}

export const DETECTOR_STATUS_WORDS = {
  OO: 'On Order',
  OF: 'Offline Repair',
  IS: 'In Stock',
  OP: 'Operational',
  DC: 'Decommissioned',
  MI: 'Missing',
  TR: 'In Transit'
}

export const CYLINDER_STATUS_WORDS = {
  OO: 'On Order',
  IS: 'In Stock',
  OP: 'Operational',
  MT: 'Empty'
}

export const formatDay = (value) => {
  if (!value) return ''
  const d = new Date(value)
  if (Number.isNaN(d.getTime())) return ''
  return d.toLocaleDateString('en-AU', { day: '2-digit', month: 'short', year: 'numeric' })
}
