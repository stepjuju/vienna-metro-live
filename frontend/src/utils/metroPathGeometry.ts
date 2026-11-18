export type DistanceMap = Record<string, number>
export type DotPose = { x: number; y: number }

import type { Anchor } from '../data/metroSchematic'

function distanceSquared(path: SVGPathElement, at: number, anchor: Anchor): number {
  const p = path.getPointAtLength(at)
  return (p.x - anchor.x) ** 2 + (p.y - anchor.y) ** 2
}

/** Find the nearest position on a schematic SVG route. Run only on mount. */
function project(path: SVGPathElement, anchor: Anchor): number {
  const total = path.getTotalLength()
  let best = 0
  let bestError = Number.POSITIVE_INFINITY
  const step = 3
  for (let at = 0; at <= total + step; at += step) {
    const distance = Math.min(at, total)
    const error = distanceSquared(path, distance, anchor)
    if (error < bestError) {
      bestError = error
      best = distance
    }
  }
  let left = Math.max(0, best - step)
  let right = Math.min(total, best + step)
  for (let i = 0; i < 18; i += 1) {
    const a = left + (right - left) / 3
    const b = right - (right - left) / 3
    if (distanceSquared(path, a, anchor) < distanceSquared(path, b, anchor)) right = b
    else left = a
  }
  return (left + right) / 2
}


/** Each line's anchors are ordered in the same direction as its route path. */
export function measureStations(
  path: SVGPathElement,
  anchors: readonly Anchor[],
  line: string
): DistanceMap {
  const map: DistanceMap = {}
  let previous = -1

  for (const anchor of anchors) {
    const distance = project(path, anchor)
    const actual = path.getPointAtLength(distance)

    const error = Math.hypot(
      actual.x - anchor.x,
      actual.y - anchor.y
    )

    if (error > 6) {
      console.warn(
        `${line} anchor ${anchor.name} (${anchor.stationId}) is ${error.toFixed(1)} SVG units off the path`
      )
    }

    if (distance <= previous + 0.05) {
      throw new Error(
        `${line}: invalid station order at ${anchor.name}. Check its coordinates.`
      )
    }

    // Check for duplicate station IDs before inserting.
    if (Object.hasOwn(map, anchor.stationId)) {
      throw new Error(
        `${line}: duplicate station ID ${anchor.stationId}`
      )
    }

    // Use stable station IDs instead of normalized names.
    map[anchor.stationId] = distance
    previous = distance
  }

  return map
}


/** Use the path's canonical normal for both directions. */
export function getDotPose(path: SVGPathElement, distance: number, direction: 1 | -1, laneOffset: number): DotPose {
  const total = path.getTotalLength()
  const d = Math.max(0, Math.min(total, distance))
  const point = path.getPointAtLength(d)
  const before = path.getPointAtLength(Math.max(0, d - 2))
  const after = path.getPointAtLength(Math.min(total, d + 2))
  const dx = after.x - before.x
  const dy = after.y - before.y
  const length = Math.hypot(dx, dy) || 1
  const offset = direction * -laneOffset
  return { x: point.x - dy / length * offset, y: point.y + dx / length * offset }
}

export function gtfsSeconds(value: string): number {
  const [hours, minutes, seconds] = value.split(':').map(Number)
  return hours * 3600 + minutes * 60 + seconds
}
export function clamp01(value: number): number { return Math.max(0, Math.min(1, value)) }
