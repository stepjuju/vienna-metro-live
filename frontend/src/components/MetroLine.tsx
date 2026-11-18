import type { RefObject } from 'react'

type Props = {
  d: string
  pathRef: RefObject<SVGPathElement | null>
}

export function MetroLine({ d, pathRef }: Props) {
  return (
    <g>
      {/* One thick colored route, containing both train lanes. */}
      <path
        ref={pathRef}
        d={d}
        fill="none"
        stroke="#E3000F"
        strokeWidth="30"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      {/* A barely visible center seam helps distinguish the two lanes. */}
      <path
        d={d}
        fill="none"
        stroke="#10151D"
        strokeOpacity="0.17"
        strokeWidth="0.8"
        pointerEvents="none"
      />
    </g>
  )
}
