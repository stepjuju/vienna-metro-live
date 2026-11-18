
/**
 * Temporary GTFS station-name compatibility layer.
 *
 * Keeps naming differences out of schematic geometry.
 *
 * This module will no longer be needed for train positioning
 * once the backend returns stable internal station IDs.
 */

const STOP_ALIASES: Record<string, string> = {
  mittelandstrasse: 'landstrasse',
  wienmittelandstrasse: 'landstrasse',
}

/**
 * Convert a station name into a comparison key.
 * Not suitable as a permanent station identifier.
 */
export function stopKey(value: string): string {
  let key = value
    .toLowerCase()
    .normalize('NFKD')
    .replace(/[\u0300-\u036f]/g, '')
    .replace(/ß/g, 'ss')
    .replace(/[^a-z0-9]/g, '')

  key = key.replace(/^wien(?=[a-z])/, '')

  // Known timetable / schematic naming differences
  key = STOP_ALIASES[key] ?? key

  if (key.startsWith('sudtiroler')) {
    return 'sudtirolerplhbf'
  }

  if (key.startsWith('kaisermuhlen')) {
    return 'kaisermuhlenvic'
  }

  if (key.startsWith('landstrasse')) {
    return 'landstrasse'
  }

  if (key.startsWith('meidlinghaupt')) {
    return 'meidlinghauptstrasse'
  }

  if (key.startsWith('bahnhofmeidling') || key === 'meidling') {
    return 'bahnhofmeidling'
  }

  if (key.startsWith('wahringerstrasse')) {
    return 'wahringerstrassevolksoper'
  }

  if (key.startsWith('michelbeuern')) {
    return 'michelbeuernakh'
  }

  if (key.startsWith('burggassestadthalle')) {
    return 'burggassestadthalle'
  }

  if (key.startsWith('margaretengurtel')) {
    return 'margaretengurtel'
  }

  return key
}
