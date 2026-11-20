import { useEffect, useMemo, useState, type ReactNode } from 'react'
import Grafica, { type Barra } from './Grafica'
import { cargar, FilaPartido, FilaTemporada, Meta, Origen } from './datos'

type Stat = 'moda' | 'media' | 'mediana'
const STATS: { clave: Stat; nombre: string }[] = [
  { clave: 'moda', nombre: 'Moda' },
  { clave: 'media', nombre: 'Media' },
  { clave: 'mediana', nombre: 'Mediana' },
]

type Datos = {
  meta: Meta
  yardasPartido: FilaPartido[]
  yardasTemporada: FilaTemporada[]
  cambiosPartido: FilaPartido[]
  cambiosTemporada: FilaTemporada[]
  origen: Origen
}

async function cargarTodo(): Promise<Datos> {
  const [m, yp, yt, cp, ct] = await Promise.all([
    cargar<Meta>('meta'),
    cargar<FilaPartido[]>('yardas_por_partido'),
    cargar<FilaTemporada[]>('yardas_por_temporada'),
    cargar<FilaPartido[]>('cambios_por_partido'),
    cargar<FilaTemporada[]>('cambios_por_temporada'),
  ])
  const origenes = new Set([m, yp, yt, cp, ct].map((x) => x.origen))
  return {
    meta: m.datos,
    yardasPartido: yp.datos,
    yardasTemporada: yt.datos,
    cambiosPartido: cp.datos,
    cambiosTemporada: ct.datos,
    origen: origenes.size === 1 ? m.origen : 'JSON estático',
  }
}

function barrasPartido(filas: FilaPartido[], stat: Stat, unidad: string): Barra[] {
  return filas.map((f) => ({
    etiqueta: `S${f.week} ${f.visitante}@${f.local}`,
    detalle: `Semana ${f.week} (${f.fecha}): ${f.visitante} visita a ${f.local}. ${STATS.find((s) => s.clave === stat)!.nombre} en ${unidad}`,
    valor: f[stat],
    n: f.n,
    modas: stat === 'moda' ? f.modas : undefined,
  }))
}

function barrasTemporada(filas: FilaTemporada[], stat: Stat, equipo: string): Barra[] {
  return filas
    .filter((f) => f.equipo === 'TODOS' || f.equipo === equipo)
    .map((f) => ({
      etiqueta: `${f.season} · ${f.equipo === 'TODOS' ? 'Todos' : f.equipo}`,
      detalle: `Temporada ${f.season}, ${f.equipo === 'TODOS' ? 'todos los visitantes' : `${f.equipo} como visitante`}`,
      valor: f[stat],
      n: f.n,
      modas: stat === 'moda' ? f.modas : undefined,
      resaltada: f.equipo === 'TODOS' ? equipo === 'TODOS' : true,
    }))
}

function Select({ etiqueta, valor, onChange, children }: { etiqueta: string; valor: string; onChange: (v: string) => void; children: ReactNode }) {
  return (
    <label className="flex flex-col text-sm">
      <span className="mb-1 font-medium">{etiqueta}</span>
      <select className="rounded border bg-white px-2 py-1" value={valor} onChange={(e) => onChange(e.target.value)}>
        {children}
      </select>
    </label>
  )
}

export default function App() {
  const [datos, setDatos] = useState<Datos | null>(null)
  const [error, setError] = useState('')
  const [temporada, setTemporada] = useState('TODAS')
  const [equipo, setEquipo] = useState('TODOS')
  const [partido, setPartido] = useState('TODOS')

  useEffect(() => {
    cargarTodo().then(setDatos).catch((e: Error) => setError(e.message))
  }, [])

  const partidosFiltro = useMemo(
    () =>
      datos
        ? datos.meta.partidos.filter(
            (p) => (temporada === 'TODAS' || p.season === Number(temporada)) && (equipo === 'TODOS' || p.visitante === equipo),
          )
        : [],
    [datos, temporada, equipo],
  )

  if (error) return <main className="p-6 text-red-700">No se pudieron cargar los datos: {error}</main>
  if (!datos) return <main className="p-6">Cargando…</main>

  const permitido = (f: FilaPartido) =>
    (temporada === 'TODAS' || f.season === Number(temporada)) &&
    (equipo === 'TODOS' || f.visitante === equipo) &&
    (partido === 'TODOS' || f.gameId === Number(partido))
  const yp = datos.yardasPartido.filter(permitido)
  const cp = datos.cambiosPartido.filter(permitido)
  const porTemporada = (filas: FilaTemporada[]) => filas.filter((f) => temporada === 'TODAS' || f.season === Number(temporada))

  const seccion = (
    titulo: string,
    descripcion: string,
    color: string,
    unidad: string,
    ejeY: string,
    partidoFilas: FilaPartido[],
    temporadaFilas: FilaTemporada[],
  ) => (
    <section className="mb-10">
      <h2 className="text-xl font-bold">{titulo}</h2>
      <p className="mb-4 text-sm text-gray-600">{descripcion}</p>
      <h3 className="mb-2 font-semibold">Por partido</h3>
      <div className="mb-6 grid gap-4 lg:grid-cols-3">
        {STATS.map((s) => (
          <Grafica
            key={s.clave}
            titulo={`${s.nombre} por partido`}
            ejeY={ejeY}
            ejeX="Partidos (por semana; pasa el cursor para ver detalle)"
            unidad={unidad}
            color={color}
            barras={barrasPartido(partidoFilas, s.clave, unidad)}
          />
        ))}
      </div>
      <h3 className="mb-2 font-semibold">Por temporada</h3>
      <div className="grid gap-4 lg:grid-cols-3">
        {STATS.map((s) => (
          <Grafica
            key={s.clave}
            titulo={`${s.nombre} por temporada`}
            ejeY={ejeY}
            ejeX="Temporada y equipo visitante"
            unidad={unidad}
            color={color}
            barras={barrasTemporada(temporadaFilas, s.clave, equipo)}
          />
        ))}
      </div>
    </section>
  )

  return (
    <main className="mx-auto max-w-7xl p-6">
      <h1 className="text-2xl font-bold">NFL 2021: el visitante en el 3er cuarto</h1>
      <p className="mb-4 text-sm text-gray-600">
        Ofensiva del equipo visitante y cambios de jugadores en la defensa local durante el 3er cuarto. Datos: semanas 1 a 8 de 2021
        (jugadas de pase). Fuente de datos en uso: <strong>{datos.origen}</strong>.
      </p>
      <div className="mb-6 flex flex-wrap gap-4 rounded border bg-gray-50 p-3">
        <Select etiqueta="Temporada" valor={temporada} onChange={(v) => { setTemporada(v); setPartido('TODOS') }}>
          <option value="TODAS">Todas</option>
          {datos.meta.temporadas.map((t) => <option key={t} value={t}>{t}</option>)}
        </Select>
        <Select etiqueta="Equipo visitante" valor={equipo} onChange={(v) => { setEquipo(v); setPartido('TODOS') }}>
          <option value="TODOS">Todos</option>
          {datos.meta.equipos_visitantes.map((e) => <option key={e} value={e}>{e}</option>)}
        </Select>
        <Select etiqueta="Partido" valor={partido} onChange={setPartido}>
          <option value="TODOS">Todos ({partidosFiltro.length})</option>
          {partidosFiltro.map((p) => (
            <option key={p.gameId} value={p.gameId}>S{p.week} {p.visitante} @ {p.local}</option>
          ))}
        </Select>
      </div>

      {seccion(
        'Dominio ofensivo del visitante (yardas)',
        `Yardas por jugada (playResult) del visitante en el 3er cuarto. ${datos.meta.jugadas_yardas} jugadas en total.`,
        '#e5534b',
        'yardas por jugada',
        'Yardas por jugada',
        yp,
        porTemporada(datos.yardasTemporada),
      )}
      {seccion(
        'Cambios en la defensa local contra la ofensiva visitante',
        `Jugadores que entran a la defensa local respecto a la jugada anterior, por jugada del visitante en el 3er cuarto. ${datos.meta.jugadas_cambios} jugadas en total.`,
        '#1f6feb',
        'jugadores nuevos por jugada',
        'Jugadores nuevos por jugada',
        cp,
        porTemporada(datos.cambiosTemporada),
      )}

      <footer className="border-t pt-3 text-xs text-gray-600">
        <ul className="list-disc pl-5">{datos.meta.notas.map((n) => <li key={n}>{n}</li>)}</ul>
      </footer>
    </main>
  )
}
