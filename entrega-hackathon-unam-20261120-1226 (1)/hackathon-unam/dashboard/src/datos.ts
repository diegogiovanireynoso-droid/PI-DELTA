export type Estadisticos = { n: number; media: number; mediana: number; moda: number; modas: number[] }
export type Partido = { gameId: number; season: number; week: number; fecha: string; visitante: string; local: string }
export type FilaPartido = Partido & Estadisticos
export type FilaTemporada = Estadisticos & { season: number; equipo: string }
export type Meta = {
  temporadas: number[]
  equipos_visitantes: string[]
  partidos: Partido[]
  jugadas_yardas: number
  jugadas_cambios: number
  notas: string[]
}

type Nombre = 'meta' | 'yardas_por_partido' | 'yardas_por_temporada' | 'cambios_por_partido' | 'cambios_por_temporada'

// Rutas relativas y sin diagonal inicial (el sitio se publica en una subruta).
const API: Record<Nombre, string> = {
  meta: 'api/q3/meta',
  yardas_por_partido: 'api/q3/yardas/partido',
  yardas_por_temporada: 'api/q3/yardas/temporada',
  cambios_por_partido: 'api/q3/cambios/partido',
  cambios_por_temporada: 'api/q3/cambios/temporada',
}

export type Origen = 'API' | 'JSON estático'

/** Usa el API si responde JSON; si no, lee public/data/<nombre>.json. */
export async function cargar<T>(nombre: Nombre): Promise<{ datos: T; origen: Origen }> {
  try {
    const r = await fetch(API[nombre])
    if (r.ok && (r.headers.get('content-type') ?? '').includes('application/json')) {
      return { datos: (await r.json()) as T, origen: 'API' }
    }
  } catch {
    // sin API: se usa el JSON estático
  }
  const r = await fetch(`data/${nombre}.json`)
  if (!r.ok) throw new Error(`No se pudo leer data/${nombre}.json (HTTP ${r.status})`)
  return { datos: (await r.json()) as T, origen: 'JSON estático' }
}
