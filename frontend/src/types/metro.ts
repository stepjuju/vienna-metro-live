export type Train = {
  trip_id: string
  line: string
  destination: string
  service_date: string
  status: 'moving' | 'stopped'

  from?: string
  to?: string
  station?: string

  from_stop_id?: string
  to_stop_id?: string
  stop_id?: string

  from_station_id?: string
  to_station_id?: string
  station_id?: string

  departure?: string
  arrival?: string
  progress: number
}

export type TrainsResponse = {
  mode?: string
  line: string
  date: string
  time: string
  count: number
  trains: Train[]
}
