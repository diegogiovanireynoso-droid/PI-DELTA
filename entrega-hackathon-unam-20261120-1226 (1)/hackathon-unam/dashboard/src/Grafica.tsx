import { Bar, BarChart, CartesianGrid, Cell, Label, ReferenceLine, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'

export type Barra = {
  etiqueta: string
  detalle: string
  valor: number
  n: number
  modas?: number[]
  resaltada?: boolean
}

type Props = {
  titulo: string
  ejeY: string
  ejeX: string
  unidad: string
  color: string
  barras: Barra[]
}

function Detalle({ b, unidad }: { b: Barra; unidad: string }) {
  return (
    <div className="rounded border bg-white p-2 text-xs shadow">
      <div className="font-semibold">{b.detalle}</div>
      <div>
        {b.valor} {unidad}
      </div>
      <div>{b.n} jugadas</div>
      {b.modas && b.modas.length > 1 && (
        <div className="mt-1 max-w-[220px] text-amber-700">
          Hay varias modas ({b.modas.join(', ')}). Se muestra la menor.
        </div>
      )}
    </div>
  )
}

export default function Grafica({ titulo, ejeY, ejeX, unidad, color, barras }: Props) {
  const muchas = barras.length > 20
  return (
    <figure className="rounded border bg-white p-3">
      <figcaption className="mb-2 text-sm font-semibold">{titulo}</figcaption>
      {barras.length === 0 ? (
        <p className="py-10 text-center text-sm text-gray-500">Sin datos para este filtro.</p>
      ) : (
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={barras} margin={{ top: 8, right: 12, bottom: 28, left: 8 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="etiqueta" tick={muchas ? false : { fontSize: 11 }} interval={0}>
              <Label value={ejeX} position="insideBottom" offset={-18} fontSize={12} />
            </XAxis>
            <YAxis tick={{ fontSize: 11 }}>
              <Label value={ejeY} angle={-90} position="insideLeft" style={{ textAnchor: 'middle' }} fontSize={12} />
            </YAxis>
            <ReferenceLine y={0} stroke="#999" />
            <Tooltip
              content={(p) => {
                const item = (p.payload as unknown as { payload: Barra }[] | undefined)?.[0]?.payload
                return p.active && item ? <Detalle b={item} unidad={unidad} /> : null
              }}
            />
            <Bar dataKey="valor" isAnimationActive={false}>
              {barras.map((b) => (
                <Cell key={b.detalle} fill={color} fillOpacity={b.resaltada === false ? 0.45 : 1} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      )}
    </figure>
  )
}
