
import { useLayoutEffect, useRef, useState } from 'react'
import metroPaths from '../data/metroPaths.json'
import { LINES, LINE_STATIONS, type LineId } from '../data/metroSchematic'
import type { Train } from '../types/metro'
import { stopKey } from '../utils/stopNames'
import {
  clamp01,
  getDotPose,
  gtfsSeconds,
  measureStations,
  type DistanceMap,
} from '../utils/metroPathGeometry'

type AnimatedTrain = {
  train: Train
  line: LineId
  elapsedSeconds: number
}

type Props = {
  trains: readonly AnimatedTrain[]
}

type Geometry = {
  path: SVGPathElement
  distances: DistanceMap
}

type GeometryMap = Partial<Record<LineId, Geometry>>

const MAP_WIDTH = 1122.5
const MAP_HEIGHT = 793.7

// Keep in sync with frontend/scripts/create_display_map.py.
const TRACK_WIDTH = 5.17 * 2.4
const LANE_OFFSET = TRACK_WIDTH * 0.25
const DOT_RADIUS = TRACK_WIDTH * 0.17
const DOT_STROKE = 0.65

/** Resolve a schematic distance using only the canonical station ID. */
function stationDistance(
  distances: DistanceMap,
  stationId: string | undefined
): number | undefined {
  if (!stationId) return undefined
  return distances[stationId]
}

/**
 * Temporary fallback for the direction of stopped trains.
 *
 * The API provides destination as a name, not an ID.
 * This is used ONLY to choose the lane direction,
 * never to locate a station on the map.
 */
function stoppedTrainDirection(
  train: Train,
  line: LineId
): 1 | -1 {
  const finalStation = LINE_STATIONS[line].at(-1)

  if (
    finalStation &&
    stopKey(train.destination) === stopKey(finalStation.name)
  ) {
    return 1
  }

  return -1
}

function TrainDot({
  item,
  geometry,
}: {
  item: AnimatedTrain
  geometry: Geometry
}) {
  const { train, elapsedSeconds, line } = item
  const { path, distances } = geometry

  let distance: number | undefined
  let direction: 1 | -1

  if (train.status === 'stopped') {
    distance = stationDistance(
      distances,
      train.station_id
    )

    if (distance === undefined) return null

    direction = stoppedTrainDirection(train, line)
  } else {
    const from = stationDistance(
      distances,
      train.from_station_id
    )

    const to = stationDistance(
      distances,
      train.to_station_id
    )

    if (from === undefined || to === undefined) {
      return null
    }

    direction = to >= from ? 1 : -1

    const duration =
      train.departure && train.arrival
        ? gtfsSeconds(train.arrival) -
          gtfsSeconds(train.departure)
        : 0

    const progress = clamp01(
      train.progress +
      (duration > 0 ? elapsedSeconds / duration : 0)
    )

    distance = from + (to - from) * progress
  }

  const dot = getDotPose(
    path,
    distance,
    direction,
    LANE_OFFSET
  )

  const location =
    train.status === 'moving'
      ? `${train.from} → ${train.to}`
      : train.station

  return (
    <circle
      cx={dot.x}
      cy={dot.y}
      r={DOT_RADIUS}
      fill="#ffffff"
      stroke="#17202B"
      strokeWidth={DOT_STROKE}
    >
      <title>
        {`${line} → ${train.destination} · ${location ?? ''}`}
      </title>
    </circle>
  )
}

/**
 * The original SVG is rendered as one image layer.
 * Train markers are drawn above it, so station circles
 * cannot cover moving train dots.
 */
export function MetroMap({ trains }: Props) {
  const pathRefs = useRef<
    Partial<Record<LineId, SVGPathElement>>
  >({})

  const [geometry, setGeometry] =
    useState<GeometryMap>({})

  const [errors, setErrors] =
    useState<string[]>([])

  useLayoutEffect(() => {
    const next: GeometryMap = {}
    const problems: string[] = []

    for (const line of LINES) {
      const path = pathRefs.current[line]

      if (!path) {
        problems.push(`${line}: SVG path unavailable`)
        continue
      }

      try {
        next[line] = {
          path,
          distances: measureStations(
            path,
            LINE_STATIONS[line],
            line
          ),
        }
      } catch (error) {
        problems.push(
          error instanceof Error
            ? error.message
            : `${line}: geometry error`
        )
      }
    }

    setGeometry(next)
    setErrors(problems)
  }, [])

  // Detect API station IDs missing from the line's schematic.
  // Never attempt to recover them by matching station names.
  const unmapped = trains.filter(({ line, train }) => {
    const distances = geometry[line]?.distances

    if (!distances) return false

    if (train.status === 'stopped') {
      return stationDistance(
        distances,
        train.station_id
      ) === undefined
    }

    return (
      stationDistance(
        distances,
        train.from_station_id
      ) === undefined ||
      stationDistance(
        distances,
        train.to_station_id
      ) === undefined
    )
  })

  return (
    <div
      className="map-scroll"
      style={{ background: '#fff' }}
    >
      <svg
        className="metro-svg"
        viewBox={`0 0 ${MAP_WIDTH} ${MAP_HEIGHT}`}
        width="100%"
        role="img"
        aria-label="Vienna U-Bahn schematic with timetable-estimated trains on U1, U2, U3, U4 and U6"
        style={{
          display: 'block',
          width: '100%',
          height: 'auto',
          maxWidth: 'none',
        }}
      >
        <image
          href="/maps/vienna-ubahn-display.svg"
          x={0}
          y={0}
          width={MAP_WIDTH}
          height={MAP_HEIGHT}
        />

        {LINES.map(line => {
          const shape = metroPaths[line]
          const transform =
            shape.transforms?.join(' ') || undefined

          const routeTrains = trains.filter(
            item => item.line === line
          )

          return (
            <g key={line} transform={transform}>
              <path
                ref={(node: SVGPathElement | null) => {
                  if (node) pathRefs.current[line] = node
                }}
                d={shape.d}
                fill="none"
                stroke="none"
                pointerEvents="none"
              />

              <g id={`${line.toLowerCase()}-trains`}>
                {routeTrains.map(item => {
                  const current = geometry[line]

                  return current ? (
                    <TrainDot
                      key={`${line}:${item.train.service_date}:${item.train.trip_id}`}
                      item={item}
                      geometry={current}
                    />
                  ) : null
                })}
              </g>
            </g>
          )
        })}
      </svg>

      {errors.length > 0 && (
        <p className="error">
          Map geometry: {errors.join(' · ')}
        </p>
      )}

      {unmapped.length > 0 && (
        <p className="error">
          {unmapped.length} scheduled trains have unmapped
          station IDs (first examples:{' '}
          {unmapped.slice(0, 3).map(({ line, train }) =>
            train.status === 'stopped'
              ? `${line} ${train.station_id ?? 'missing station_id'}`
              : `${line} ${train.from_station_id ?? 'missing from_station_id'} → ${train.to_station_id ?? 'missing to_station_id'}`
          ).join(' · ')}).
        </p>
      )}
    </div>
  )
}