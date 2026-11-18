import { useEffect, useState } from 'react'
import { LINES, type LineId } from '../data/metroSchematic'
import type { TrainsResponse } from '../types/metro'

export type Snapshot = { data: TrainsResponse; receivedAt: number }
export type SnapshotMap = Partial<Record<LineId, Snapshot>>
export type ErrorMap = Partial<Record<LineId, string>>

/** Five independent timetable requests; one failing line doesn't hide the others. */
export function useAllTrainPositions() {
  const [snapshots, setSnapshots] = useState<SnapshotMap>({})
  const [errors, setErrors] = useState<ErrorMap>({})

  useEffect(() => {
    let active = true
    let refreshing = false
    const controllers = new Set<AbortController>()

    async function refresh() {
      if (refreshing) return
      refreshing = true
      try {
        await Promise.all(LINES.map(async (line) => {
          const controller = new AbortController()
          controllers.add(controller)
          try {
            const response = await fetch(`/api/trains/live?line=${line}`, { signal: controller.signal })
            if (!response.ok) throw new Error(`HTTP ${response.status}`)
            const data: TrainsResponse = await response.json()
            if (!active) return
            setSnapshots(previous => ({ ...previous, [line]: { data, receivedAt: Date.now() } }))
            setErrors(previous => {
              const next = { ...previous }
              delete next[line]
              return next
            })
          } catch (error) {
            if (!active || controller.signal.aborted) return
            setErrors(previous => ({ ...previous, [line]: error instanceof Error ? error.message : 'Network error' }))
          } finally {
            controllers.delete(controller)
          }
        }))
      } finally {
        refreshing = false
      }
    }

    void refresh()
    const timer = window.setInterval(() => void refresh(), 15_000)
    return () => {
      active = false
      window.clearInterval(timer)
      controllers.forEach(controller => controller.abort())
    }
  }, [])

  return { snapshots, errors }
}
