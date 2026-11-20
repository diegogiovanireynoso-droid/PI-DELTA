# Hackathon NFL Big Data Bowl UNAM


## Objetivo
Encontrar en los datos de las semanas 1 a 8 de la temporada 2021 de la NFL algo que ayude a un coach a entender por qué el equipo visitante rinde más en el 3er cuarto, y mostrarlo en un dashboard claro.

## Proceso
Primero se hizo una exploración de los cuatro CSV en `data/EXPLORACION/` (estructura, nulos, yardas por cuarto, formaciones, coberturas y cambios de jugadores entre jugadas), sin modificar los datos. Con esos hallazgos se construyó la app con el stack permitido: pandas y numpy en Python para calcular, FastAPI para servir las métricas, y React con Recharts para graficarlas por partido y por temporada. También se exportan JSON estáticos para publicar el dashboard en GitHub Pages sin necesidad de backend.

## Resultado
El equipo visitante domina el 3er cuarto: promedia 7.11 yardas por jugada, contra 6.69 del local y entre 5.89 y 6.44 del visitante en los demás cuartos. No se encontró un cambio de estrategia que lo explique, pues las formaciones, coberturas y rotación de jugadores son parecidas en ambos equipos; lo que destaca es una mayor proporción de jugadas largas, de 20 yardas o más.
