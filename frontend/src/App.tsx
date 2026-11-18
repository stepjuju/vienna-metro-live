import './App.css'
import { MetroMap } from './components/MetroMap'
import { LINES, type LineId } from './data/metroSchematic'
import { useAllTrainPositions } from './hooks/useAllTrainPositions'
import { useAnimationClock } from './hooks/useTrainPositions'
import type { Train } from './types/metro'

function App() {
  const { snapshots, errors } = useAllTrainPositions()
  const now = useAnimationClock()

  const trains: { line: LineId; train: Train; elapsedSeconds: number }[] = []
  for (const line of LINES) {
    const snapshot = snapshots[line]
    if (!snapshot) continue
    const elapsedSeconds = Math.max(0, (now - snapshot.receivedAt) / 1000)
    for (const train of snapshot.data.trains) {
      trains.push({ line, train, elapsedSeconds })
    }
  }

  const lineErrors = LINES.filter(line => errors[line]).map(line => `${line}: ${errors[line]}`)
  const loadedLines = LINES.filter(line => snapshots[line]).length
  const snapshotTimes = LINES.map(line => snapshots[line]?.data.time).filter(Boolean)

  return (
    <main className="app">
      <header className="page-header">
        <div>
          <p className="eyebrow">VIENNA / TRANSIT DISPLAY</p>
          <h1>Vienna Metro Live</h1>
          <p className="subtitle">Scheduled movement · all five U-Bahn lines</p>
        </div>
        <span className="live-badge"><span className="live-dot" /> LIVE SIMULATION</span>
      </header>
      <section className="panel">
        <div className="panel-heading">
          <div className="line-heading"><h2>U1 · U2 · U3 · U4 · U6</h2></div>
          <span className="muted">{trains.length} scheduled trains · {loadedLines}/5 lines loaded</span>
        </div>
        {lineErrors.length > 0 && <p className="error">Timetable refresh: {lineErrors.join(' · ')}</p>}
        {loadedLines === 0 && lineErrors.length === 0 && <p className="muted">Loading train positions…</p>}
        <MetroMap trains={trains} />
        <footer className="panel-footer">
          <span>Latest schedule snapshot: {snapshotTimes[0] ?? '—'}</span>
          <span>Positions estimated from GTFS · 15 s refresh</span>
        </footer>
      </section>
    </main>
  )
}

export default App
