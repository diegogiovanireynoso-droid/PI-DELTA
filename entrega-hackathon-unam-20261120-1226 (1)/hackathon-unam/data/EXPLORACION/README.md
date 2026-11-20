# Exploración de datos y supuestos del dashboard

Notas de la exploración que sustenta el dashboard. El README de la raíz resume el proyecto.

## Hallazgos

1. **El visitante domina el 3er quarter.** Es el único quarter regular donde el visitante supera al local en yardas totales (6,559 contra 6,125) y en promedio por jugada (7.11 contra 6.69). Además tuvo más jugadas (922 contra 915). En el resto de los quarters, el local suma más yardas. Es una diferencia descriptiva de las semanas 1 a 8 de 2021 y todavía no está probada estadísticamente.
2. **El 3er quarter es el más productivo por jugada** (6.91 yardas de promedio), aunque el 2º suma más yardas totales (16,027) porque tiene más jugadas.
3. **Los quarters 2 y 4 concentran el volumen:** 2,441 y 2,446 jugadas, frente a 1,735 del 1º y 1,837 del 3º.
4. **Las yardas por jugada tienen cola larga:** la mediana es de 4 a 5 yardas por quarter y la media de 6.4 a 6.9. Las jugadas largas suben el promedio.
5. **Los castigos son poco frecuentes en los datos:** `penaltyYards` y `foulName1` son nulos en más del 91% de las jugadas.
6. **`playId` no identifica una jugada por sí solo:** se repite entre partidos. La llave es (`gameId`, `playId`).

## data/EXPLORACION

Carpeta de exploración de datos. Su objetivo es entender los 4 CSV de `data/` (`games`, `plays`, `players`, `pffScoutingData`) y encontrar algo que ayude a un coach de la NFL o que cuente una historia de la liga a través de los datos.

- Usa solo el stack permitido (Python en `.venv`, pandas y numpy).
- Es solo lectura: los CSV originales nunca se modifican.
- Tarea 1 (hecha): estructura de cada archivo (filas, columnas, tipos, nulos, temporadas). Script: `tarea1_estructura.py`, salida: `tarea1_salida.txt`.
- Tarea 2 (pendiente): limpieza, nulos, valores atípicos (media vs. mediana), relaciones y dispersión; se crearán DataFrames derivados sin columnas poco útiles.

### Análisis de plays.csv (notas para el resumen final)

Script: `data/EXPLORACION/plays_analisis.py`, salida: `plays_analisis_salida.txt`. Solo lectura.

- **Tipos:** 17 columnas numéricas y 15 no numéricas. `gameId`, `playId` y `foulNFLId1/2/3` son numéricas pero funcionan como identificadores.
- **Nulos:** `foulName3`/`foulNFLId3` 99.99%, `foulName2`/`foulNFLId2` 99.65%, `foulName1`/`foulNFLId1` 91.40%, `penaltyYards` 91.17% (nulo = jugada sin castigo), `dropBackType` 6.17%, `yardlineSide` 1.46%, `offenseFormation` y `defendersInBox` 0.08%, `absoluteYardlineNumber`, `personnelO` y `personnelD` 1 fila cada una. El resto no tiene nulos.
- **Filas por `gameId`:** no es constante. Hay 122 partidos con entre 47 (`2021100301`) y 97 (`2021090900`) jugadas, media 70.14 y mediana 70 (40 cantidades distintas).
- **`playId`:** solo 3,762 únicos en 8,557 filas. Se repite entre partidos (un mismo `playId` llega a aparecer en 15), pero no dentro de un mismo partido. El par (`gameId`, `playId`) es único, así que esa es la llave de la jugada.
- **Quarter con más jugadas:** el 4 con 2,446, casi igual que el 2 con 2,441. El 5 (tiempo extra) tiene 98.
- **Yardas por quarter** (suma de `playResult`): el 2 lidera con 16,027 yardas. Por promedio por jugada gana el 3 (6.91). Las medianas son 4 o 5 yardas (3 en el tiempo extra), menores que las medias.
- **Local vs. visitante** (`possessionTeam` comparado con `homeTeamAbbr` de `games.csv`): el local suma más yardas en los quarters 1, 2, 4 y 5. El visitante suma más en el 3 (6,559 contra 6,125). En total, local 28,785 yardas y visitante 27,383. Por promedio por jugada, el visitante gana en los quarters 1 y 3, y el local en el 2, 4 y 5.
- **Limitación:** `playResult` es el resultado neto de la jugada (incluye castigos). Los datos solo cubren las semanas 1 a 8 de 2021 y la diferencia entre local y visitante no se ha probado estadísticamente.

### Análisis de cuartos: por qué el visitante domina el 3er cuarto (notas para el resumen final)

Script: `data/EXPLORACION/cuartos_analisis.py`, salida: `cuartos_analisis_salida.txt`. Solo lectura. "Local defiende" son las jugadas con `possessionTeam` = visitante.

- **Moda, media y mediana (visitante atacando, `playResult`):** Q3 tiene media 7.11, mediana 4 y moda 0. La moda 0 son pases incompletos. En todos los cuartos la media supera a la mediana.
- **Sin diferencia en lo más frecuente:** en todos los cuartos la defensa local usa `4 DL, 2 LB, 5 DB`, Cover-3 (Zone) y 6 defensores en la caja. El visitante ataca con SHOTGUN, `1 RB, 1 TE, 3 WR`, dropback TRADITIONAL y sin play action. Las modas no explican el Q3. La única diferencia de moda es el tiempo extra (Q5), donde hay empate entre Cover-1 y Cover-3 con solo 54 jugadas.
- **Posiciones alineadas:** la moda de posición en `pffScoutingData` es poco informativa. En la ofensiva sale LT/RT/LG porque están en todas las jugadas. En la defensa salen RCB/LCB/ROLB en todos los cuartos.
- **Diferencias pequeñas en Q3 contra Q1, Q2 y Q4:** la defensa local usa menos `2 DL, 3 LB, 6 DB` (6.7% contra 11.3%) y menos Cover-2 (10.6% contra 13.7%). El visitante usa más play action (26.4% contra 22.6%) y menos SHOTGUN (61.3% contra 65.6%). No se probó significancia estadística.
- **Por partido:** en 37 de 122 el local cambia su cobertura más frecuente en Q3, en 50 no cambia y en 35 hay empate en la moda. El visitante cambia su formación más frecuente en 10, no cambia en 93 y hay empate en 19.
- **Lo que sí distingue al Q3:** más jugadas largas. El 11.8% de las jugadas del visitante en Q3 gana 20 o más yardas (9.5% a 10.3% en Q1, Q2 y Q4), con un máximo de 82 yardas. Con las yardas recortadas al percentil 95, el promedio de Q3 sigue siendo mayor (6.40 contra 5.76 a 5.94).
- **Conclusión provisional:** con estos datos no se encontró un cambio de estrategia que explique el Q3. Lo que se ve es más jugadas explosivas, y la causa no se puede determinar con las columnas actuales.

#### Archivos relacionados con el avance del visitante y la defensa local

- `plays.csv`: yardas (`playResult`, `prePenaltyPlayResult`, `yardsToGo`, `yardlineNumber`), formación y decisiones (`offenseFormation`, `personnelO`, `dropBackType`, `pff_playAction`), defensa (`personnelD`, `defendersInBox`, `pff_passCoverage`, `pff_passCoverageType`), contexto (`quarter`, `down`, marcador previo, `gameClock`, castigos).
- `pffScoutingData.csv`: jugador por jugada con rol, posición alineada y presión (`pff_hit`, `pff_hurry`, `pff_sack`) o bloqueo. Es el único archivo con datos por jugador.
- `players.csv`: características (`height`, `weight`, `birthDate`, `collegeName`, `officialPosition`). Se une con `pffScoutingData` por `nflId`.
- `games.csv`: identifica local y visitante, semana y horario. No tiene datos de jugadas.
- **No existe:** lista de jugadores por equipo ni cambios de plantilla, lesiones, sustituciones ni datos de movimiento. El equipo de un jugador solo puede inferirse por su rol en la jugada y `possessionTeam`.

#### Cambios de plantilla (indirecto)

Script: `data/EXPLORACION/cambios_plantilla.py`, salida: `cambios_plantilla_salida.txt`. Solo lectura.

- **Método:** en `pffScoutingData` cada jugada trae 11 `nflId` ofensivos (roles Pass, Pass Block, Pass Route) y 11 defensivos (Coverage, Pass Rush). La unidad ofensiva es del `possessionTeam` y la defensiva del `defensiveTeam`. Se ordenan las jugadas de cada unidad por cuarto y reloj, y se comparan los conjuntos de `nflId` entre jugadas consecutivas (entran = en la nueva y no en la anterior; salen = al revés).
- **Límites:** `plays.csv` solo trae pases, así que la "jugada anterior" es el pase anterior y pueden faltar sustituciones entre medias. Un cambio de ids puede ser una sustitución o un cambio de formación (por ejemplo, un TE por un WR). Los datos no distinguen lesión de decisión técnica. El orden usa cuarto y reloj, porque `playId` solo coincide con el orden cronológico en 90.2% de los partidos.
- **Q2 a Q3 (medio tiempo), visitante ofensiva:** entran en promedio 1.79 jugadores, y en 106 de 122 partidos hay al menos uno nuevo. Es casi igual que en Q1 a Q2 (1.74) y Q3 a Q4 (1.74).
- **Q2 a Q3, local defensiva:** entran en promedio 2.52 jugadores, en 120 de 122 partidos. Es menos que en Q1 a Q2 (2.89) y similar a Q3 a Q4 (2.62). No hay un ajuste de plantilla local que destaque en el medio tiempo.
- **Dentro del Q3:** entran más jugadores entre jugadas que en Q2 y Q4 (ofensiva visitante 1.58 contra 1.38 y 1.23, defensiva local 2.21 contra 1.90 y 1.76). La misma tendencia aparece en el equipo contrario, así que es una característica del cuarto y no de un solo equipo. Las causas no se pueden determinar con estos datos.
- **Quién entra en el Q3:** en la ofensiva visitante, TE (75), WR (61) y RB (58). En la defensiva local, DT (73), DE (61) y OLB (50).
- **Conclusión provisional:** los cambios de jugadores existen y son medibles, pero con estos datos no se ve un cambio de plantilla que explique la ventaja del visitante en el Q3.
- **Contraste en el medio tiempo (Q2 a Q3):** la ofensiva visitante tiene la entrada promedio más alta entre las transiciones de cuarto (1.79), y la defensa local la segunda más baja (2.52, solo por encima de Q4 a Q5 con 2.18 y 11 pares). Pareado por partido, el visitante supera a Q1 a Q2 por 0.05 (error estándar 0.13) y a Q3 a Q4 por 0.06 (0.15), así que no es distinguible de cero. La defensa local entra 0.38 menos que en Q1 a Q2 (error estándar 0.15, unas 2.6 veces), pero solo 0.09 menos que en Q3 a Q4 (0.17). Es una pista débil, no una conclusión.


#### Investigación del cambio de jugadores del 3er cuarto

- **Por qué había dos cifras distintas para la ofensiva:** eran dos agrupaciones del mismo cálculo. Las transiciones comparan solo la primera jugada del cuarto nuevo con la última del anterior (ofensiva visitante Q2→Q3 = 1.79). La agrupación por cuarto mezcla esa transición con las jugadas consecutivas dentro del cuarto (ofensiva visitante Q3 = 1.58). Los datos no cambiaron. Ahora se muestran tres agrupaciones separadas: A (transiciones), B (dentro del cuarto) y C (todos los pares, por cuarto de la jugada nueva).
- **Cálculo y gráficas con el stack permitido:** `backend/exploracion.py` calcula en memoria con pandas y expone `GET /api/exploracion/cambios`. El dashboard (`dashboard/src/App.tsx`) las grafica con Recharts. Las tablas completas, con n, media, mediana y moda, están en `data/EXPLORACION/estadisticas_cambios_salida.txt` (script `estadisticas_cambios.py`).
- **Ofensiva visitante (media / mediana / moda):** Q1→Q2 1.74 / 2 / 2, **Q2→Q3 1.79 / 2 / 1 o 2**, Q3→Q4 1.74 / 2 / 2, Q4→Q5 1.64 / 2 / 2. Dentro del Q3: 1.54 / 1 / 1. Todos los pares con Q3 como cuarto de la jugada nueva: 1.58 / 2 / 1.
- **Posiciones defensivas:** no hubo cambios relevantes entre cuartos. La moda es la misma (RCB en cobertura, DRT en pass rush).
- **Entrada de jugadores:** sí se vio una variante, pequeña y casi toda en la media. Las medianas y modas cambian poco (1 a 3 jugadores).
- **Posiciones en el Q3 (moda):** en la ofensiva hay empate entre QB, C, LG, RG, LT y RT porque aparecen en todas las jugadas. En la defensa local y visitante la moda es RCB (887 y 882 registros).
- **Para ver las gráficas:** `uvicorn backend.main:app --reload` en la raíz y `npm run dev` en `dashboard/`.

#### Tipo de jugador que entra y sale en el 3er cuarto

Script: `data/EXPLORACION/tabla_tercer_cuarto.py`, salida: `tabla_tercer_cuarto_salida.txt`, gráficas y CSV en `data/EXPLORACION/graficas/`. El tipo de jugador es `officialPosition` de `players.csv`, unida por `nflId`.

- **Del Q2 al Q3 (primera jugada del Q3 contra la última del Q2), ambos equipos:** salen más WR de los que entran (visitante 107 contra 61, local 86 contra 52) y entran más TE (visitante 75 contra 36 que salen, local 64 contra 42). En defensa salen más CB (62 contra 21 en el local, 60 contra 22 en el visitante) y safeties, y entran más DT, NT e ILB.
- **Durante el Q3:** las entradas y salidas se compensan casi exactamente, con WR, TE y RB en ofensiva y DE, DT y OLB en defensa como posiciones más rotadas. No hay un movimiento neto por posición.
- **Lectura:** el patrón del medio tiempo es igual en local y visitante, así que no explica por sí solo la ventaja del visitante. Que la última jugada del Q2 suela ser de formación con más receptores y defensivos de pase es una hipótesis que no se verificó con los datos.

#### Yardas del visitante en el Q3 según el cambio de jugadores

Script: `data/EXPLORACION/yardas_por_cambio.py`, salida: `yardas_por_cambio_salida.txt`. Se unen por (`gameId`, `playId`) las 922 jugadas del visitante en el Q3 con los jugadores que entran en su ofensiva y en la defensa local.

- **Cambio del visitante (ofensiva):** con al menos 30 jugadas, ninguna posición que entra supera a las jugadas sin ese cambio. WR, TE y RB promedian 6.5 a 6.6 yardas contra 7.5 a 7.6 sin el cambio. Los promedios más altos son de muestras pequeñas (C 12.18 con 11 jugadas, T 8.64 con 22, FB 8.29 con 28).
- **Cambio del local (defensa):** las jugadas donde entra un OLB (318) promedian 7.70 yardas contra 6.80 sin él, pero la mediana es 4 en ambos casos. Cuando entra un DT (356) el visitante promedia 6.20 contra 7.69 sin él.
- **Coincidencia:** no coinciden. La mejor posición del lado visitante (TE o WR, empatados) y la del lado local (OLB) no son las mismas. Con entrada de OLB local y sin TE visitante el promedio es 8.53 (159 jugadas). Con ambos cambios es 6.87.
- **Cantidad de cambios:** el visitante promedia más yardas con 0 jugadores nuevos (8.38) que con 2 (5.75). La relación es descriptiva, no causal.

#### Gráficas de respuesta (yardas por cuarto y moda de posiciones en el Q3)

Script: `data/EXPLORACION/graficas_respuestas.py`, salida: `graficas_respuestas_salida.txt`, SVG en `data/EXPLORACION/graficas/`.

- **Yardas:** el visitante promedia más yardas por jugada en el Q3 (7.11, contra 6.41, 6.44, 6.30 y 5.89 en Q1, Q2, Q4 y tiempo extra). Es el único cuarto regular donde supera al local (6.69).
- **Moda de posiciones que entran y salen durante el Q3:** WR en ofensiva y DE en defensa, para local y visitante, tanto al entrar como al salir. Entran y salen casi los mismos jugadores de cada posición (por ejemplo, ofensiva visitante: 491 WR entran y 457 salen), lo que indica rotación y no un cambio de composición.

## Supuestos y decisiones del dashboard final

- **Yardas:** `playResult` de `plays.csv` en jugadas del Q3 cuyo `possessionTeam` es el visitante de `games.csv`. Son solo jugadas de pase, como en toda la exploración.
- **Cambios en la defensa local:** jugadores que entran a la defensa local (roles Coverage y Pass Rush de `pffScoutingData.csv`) respecto a la jugada anterior de esa unidad, en las jugadas del Q3. Incluye la primera jugada del Q3, que se compara con la última del Q2 (agrupación C de la exploración, media 2.21). La defensa siempre tiene 11 jugadores, así que entran = salen.
- **Moda:** valores enteros; si hay varias se muestra la menor y el tooltip lista todas.
- **Por temporada:** los datos solo tienen la temporada 2021 (semanas 1 a 8), así que cada gráfica muestra una sola temporada. Se agrupan todas las jugadas de la temporada, no promedios de promedios. Con un equipo elegido se agrega su barra (solo sus partidos como visitante) junto a la de todos.
- **Por partido:** una barra por partido (122), ordenada por semana y fecha. Los partidos con varias modas lo indican en el tooltip.
- **Datos en el repositorio:** los CSV de `data/` se ignoran en git (`data/*.csv`), porque son datos de una competencia con licencia restringida. Solo se suben los JSON agregados de `dashboard/public/data/`, que genera `backend/export_static.py`.
