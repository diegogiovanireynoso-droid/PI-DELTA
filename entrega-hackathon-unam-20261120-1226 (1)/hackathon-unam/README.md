# Hackathon NFL Big Data Bowl UNAM


## Objetivo
Encontrar en los datos de las semanas 1 a 8 de la temporada 2021 de la NFL algo que ayude a un coach a entender por qué el equipo visitante rinde más en el 3er cuarto, y mostrarlo en un dashboard claro.

## Proceso
Primero se hizo una exploración de los cuatro CSV en `data/EXPLORACION/` (estructura, nulos, yardas por cuarto, formaciones, coberturas y cambios de jugadores entre jugadas), sin modificar los datos. Con esos hallazgos se construyó la app con el stack permitido: pandas y numpy en Python para calcular, FastAPI para servir las métricas, y React con Recharts para graficarlas por partido y por temporada. También se exportan JSON estáticos para publicar el dashboard en GitHub Pages sin necesidad de backend.

## Resultado
El equipo visitante domina el 3er cuarto: promedia 7.11 yardas por jugada,contra 6.69 del local y entre 5.89 y 6.44 del propio visitante en los demáscuartos. 
Esa ventaja no viene de avanzar con más constancia, sino de la explosividad: el visitante tiene una mayor proporción de jugadas largas (20 yardas o más), que elevan el promedio, aunque la mediana y la moda se mantengan cerca de las de otros cuartos. 

Como las formaciones, coberturas y rotación de jugadores son parecidas en ambos equipos, la hipótesis más razonable es que las defensas locales se desgastan o pierden ajustes tras elmedio tiempo y dejan más jugadas largas, no que el visitante cambie su estrategia. 

En términos prácticos, el 3er cuarto es la ventana donde el
visitante más aprovecha las jugadas grandes, y una defensa local que quiera
frenarlo debería priorizar evitarlas.
