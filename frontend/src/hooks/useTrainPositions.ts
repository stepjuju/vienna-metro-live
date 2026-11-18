import { useEffect, useState } from 'react'
import type { TrainsResponse } from '../types/metro'

type Snapshot = { data: TrainsResponse; receivedAt: number }

/** Fetch scheduled train segments; the browser animates between fetches. */
export function useTrainPositions(line = 'U1') {
  const [snapshot, setSnapshot] = useState<Snapshot | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let active = true
    const controller = new AbortController()

    async function refresh() {
      try {
        const response = await fetch(`/api/trains/live?line=${line}`, {
          signal: controller.signal,
        })
        if (!response.ok) throw new Error(`HTTP ${response.status}`)
        const data: TrainsResponse = await response.json()
        if (active) {
          setSnapshot({ data, receivedAt: Date.now() })
          setError(null)
        }
      } catch (unknownError) {
        if (!active || controller.signal.aborted) return
        setError(unknownError instanceof Error ? unknownError.message : 'Network error')
      }
    }

    void refresh()
    const timer = window.setInterval(() => void refresh(), 15_000)
    return () => {
      active = false
      controller.abort()
      window.clearInterval(timer)
    }
  }, [line])

  return { snapshot, error }
}

export function useAnimationClock(): number {
  const [now, setNow] = useState(() => Date.now())
  useEffect(() => {
    let requestId = 0
    function frame() {
      setNow(Date.now())
      requestId = window.requestAnimationFrame(frame)
    }
    requestId = window.requestAnimationFrame(frame)
    return () => window.cancelAnimationFrame(requestId)
  }, [])
  return now
}
