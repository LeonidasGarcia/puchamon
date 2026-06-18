# Real AI Benchmark

- level_3_weights_source: code_default
- level_3_weights: hp=0.1707, alive=0.1192, damage=0.1381, type=0.1233, speed=0.1066, status=0.1315, effects=0.2105
- manual_weights: hp=0.2500, alive=0.1500, damage=0.2500, type=0.1500, speed=0.0800, status=0.0700, effects=0.0500
- minimax_depths: (1, 2, 3, 4)
- battles_per_row: 150
- total_battles: 10800
- expected_total_battles: 10800
- concurrency: 4
- max_turns: 80
- started_at: 2026-06-17T23:54:41.142473+00:00
- finished_at: 2026-06-18T00:33:29.766530+00:00
- elapsed_seconds: 2328.6240544830007
- elapsed_minutes: 38.81040090805001

| Depth | Matchup | Formato | Batallas | Wins A | Wins B | Empates | Winrate A | Winrate B | Turnos Prom. | HP Restante | Decision ms | Nodos Expl. | Nodos Podados | Mejor IA |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 1 | Facil vs Intermedio | 1v1 | 150 | 49 | 99 | 2 | 32.67% | 66.00% | 2.73 | 57.01% | 0.26 | 3.98 | 0.00 | Intermedio |
| 1 | Facil vs Intermedio | 2v2 | 150 | 32 | 117 | 1 | 21.33% | 78.00% | 6.33 | 48.58% | 0.41 | 4.37 | 0.00 | Intermedio |
| 1 | Facil vs Intermedio | 3v3 | 150 | 15 | 134 | 1 | 10.00% | 89.33% | 10.77 | 47.58% | 0.63 | 5.07 | 0.00 | Intermedio |
| 1 | Intermedio vs Dificil Manual | 1v1 | 150 | 80 | 69 | 1 | 53.33% | 46.00% | 2.36 | 50.68% | 0.71 | 4.00 | 0.00 | Intermedio |
| 1 | Intermedio vs Dificil Manual | 2v2 | 150 | 80 | 69 | 1 | 53.33% | 46.00% | 5.72 | 40.73% | 1.00 | 4.15 | 0.00 | Intermedio |
| 1 | Intermedio vs Dificil Manual | 3v3 | 150 | 91 | 56 | 3 | 60.67% | 37.33% | 10.87 | 38.00% | 1.58 | 4.72 | 0.00 | Intermedio |
| 1 | Intermedio vs Dificil GA | 1v1 | 150 | 84 | 66 | 0 | 56.00% | 44.00% | 2.13 | 53.03% | 0.74 | 4.00 | 0.00 | Intermedio |
| 1 | Intermedio vs Dificil GA | 2v2 | 150 | 84 | 65 | 1 | 56.00% | 43.33% | 5.31 | 41.34% | 1.06 | 4.14 | 0.00 | Intermedio |
| 1 | Intermedio vs Dificil GA | 3v3 | 150 | 62 | 87 | 1 | 41.33% | 58.00% | 7.99 | 40.25% | 1.65 | 4.60 | 0.00 | Dificil GA |
| 1 | Dificil Manual vs Dificil GA | 1v1 | 150 | 71 | 77 | 2 | 47.33% | 51.33% | 2.31 | 48.96% | 1.04 | 3.99 | 0.00 | Dificil GA |
| 1 | Dificil Manual vs Dificil GA | 2v2 | 150 | 65 | 84 | 1 | 43.33% | 56.00% | 5.73 | 42.27% | 1.42 | 4.20 | 0.00 | Dificil GA |
| 1 | Dificil Manual vs Dificil GA | 3v3 | 150 | 61 | 88 | 1 | 40.67% | 58.67% | 10.93 | 35.45% | 2.07 | 4.79 | 0.00 | Dificil GA |
| 1 | Facil vs Dificil GA | 1v1 | 150 | 44 | 104 | 2 | 29.33% | 69.33% | 2.81 | 60.51% | 0.59 | 4.00 | 0.00 | Dificil GA |
| 1 | Facil vs Dificil GA | 2v2 | 150 | 40 | 110 | 0 | 26.67% | 73.33% | 6.45 | 50.50% | 0.81 | 4.54 | 0.00 | Dificil GA |
| 1 | Facil vs Dificil GA | 3v3 | 150 | 17 | 133 | 0 | 11.33% | 88.67% | 10.07 | 54.97% | 1.16 | 5.35 | 0.00 | Dificil GA |
| 1 | Facil vs Dificil Manual | 1v1 | 150 | 50 | 95 | 5 | 33.33% | 63.33% | 3.24 | 58.59% | 0.60 | 3.99 | 0.00 | Dificil Manual |
| 1 | Facil vs Dificil Manual | 2v2 | 150 | 47 | 103 | 0 | 31.33% | 68.67% | 8.55 | 45.53% | 0.82 | 4.43 | 0.00 | Dificil Manual |
| 1 | Facil vs Dificil Manual | 3v3 | 150 | 30 | 119 | 1 | 20.00% | 79.33% | 12.95 | 48.40% | 1.17 | 5.27 | 0.00 | Dificil Manual |
| 2 | Facil vs Intermedio | 1v1 | 150 | 48 | 97 | 5 | 32.00% | 64.67% | 2.75 | 61.61% | 0.78 | 11.85 | 2.15 | Intermedio |
| 2 | Facil vs Intermedio | 2v2 | 150 | 36 | 114 | 0 | 24.00% | 76.00% | 7.41 | 47.11% | 1.74 | 16.62 | 2.84 | Intermedio |
| 2 | Facil vs Intermedio | 3v3 | 150 | 33 | 117 | 0 | 22.00% | 78.00% | 12.61 | 41.99% | 3.09 | 22.13 | 3.68 | Intermedio |
| 2 | Intermedio vs Dificil Manual | 1v1 | 150 | 76 | 72 | 2 | 50.67% | 48.00% | 2.12 | 54.43% | 2.08 | 11.71 | 2.14 | Intermedio |
| 2 | Intermedio vs Dificil Manual | 2v2 | 150 | 63 | 87 | 0 | 42.00% | 58.00% | 6.37 | 51.04% | 4.32 | 16.99 | 2.91 | Dificil Manual |
| 2 | Intermedio vs Dificil Manual | 3v3 | 150 | 59 | 91 | 0 | 39.33% | 60.67% | 9.87 | 49.92% | 7.07 | 21.38 | 3.40 | Dificil Manual |
| 2 | Intermedio vs Dificil GA | 1v1 | 150 | 69 | 79 | 2 | 46.00% | 52.67% | 2.05 | 55.60% | 2.03 | 11.88 | 2.12 | Dificil GA |
| 2 | Intermedio vs Dificil GA | 2v2 | 150 | 56 | 93 | 1 | 37.33% | 62.00% | 5.76 | 54.16% | 3.66 | 17.09 | 2.80 | Dificil GA |
| 2 | Intermedio vs Dificil GA | 3v3 | 150 | 41 | 109 | 0 | 27.33% | 72.67% | 9.55 | 49.33% | 6.92 | 21.83 | 3.49 | Dificil GA |
| 2 | Dificil Manual vs Dificil GA | 1v1 | 150 | 76 | 71 | 3 | 50.67% | 47.33% | 2.08 | 56.19% | 2.61 | 11.76 | 2.22 | Dificil Manual |
| 2 | Dificil Manual vs Dificil GA | 2v2 | 150 | 67 | 82 | 1 | 44.67% | 54.67% | 5.70 | 51.43% | 4.83 | 15.85 | 2.58 | Dificil GA |
| 2 | Dificil Manual vs Dificil GA | 3v3 | 150 | 70 | 80 | 0 | 46.67% | 53.33% | 8.83 | 53.38% | 7.80 | 20.31 | 3.20 | Dificil GA |
| 2 | Facil vs Dificil GA | 1v1 | 150 | 51 | 96 | 3 | 34.00% | 64.00% | 3.11 | 54.28% | 1.31 | 12.37 | 2.03 | Dificil GA |
| 2 | Facil vs Dificil GA | 2v2 | 150 | 32 | 117 | 1 | 21.33% | 78.00% | 6.52 | 52.78% | 2.30 | 16.31 | 2.83 | Dificil GA |
| 2 | Facil vs Dificil GA | 3v3 | 150 | 20 | 130 | 0 | 13.33% | 86.67% | 10.73 | 52.19% | 4.01 | 21.36 | 3.66 | Dificil GA |
| 2 | Facil vs Dificil Manual | 1v1 | 150 | 44 | 102 | 4 | 29.33% | 68.00% | 2.63 | 59.71% | 1.30 | 11.43 | 2.22 | Dificil Manual |
| 2 | Facil vs Dificil Manual | 2v2 | 150 | 26 | 124 | 0 | 17.33% | 82.67% | 6.81 | 53.57% | 2.36 | 15.89 | 2.74 | Dificil Manual |
| 2 | Facil vs Dificil Manual | 3v3 | 150 | 19 | 129 | 2 | 12.67% | 86.00% | 12.09 | 53.10% | 3.98 | 20.57 | 3.38 | Dificil Manual |
| 3 | Facil vs Intermedio | 1v1 | 150 | 48 | 98 | 4 | 32.00% | 65.33% | 2.77 | 59.02% | 1.89 | 28.98 | 5.10 | Intermedio |
| 3 | Facil vs Intermedio | 2v2 | 150 | 40 | 109 | 1 | 26.67% | 72.67% | 6.93 | 54.26% | 4.48 | 45.60 | 7.85 | Intermedio |
| 3 | Facil vs Intermedio | 3v3 | 150 | 17 | 132 | 1 | 11.33% | 88.00% | 9.79 | 60.93% | 8.58 | 66.13 | 10.20 | Intermedio |
| 3 | Intermedio vs Dificil Manual | 1v1 | 150 | 78 | 72 | 0 | 52.00% | 48.00% | 2.22 | 58.51% | 4.65 | 28.58 | 5.12 | Intermedio |
| 3 | Intermedio vs Dificil Manual | 2v2 | 150 | 75 | 75 | 0 | 50.00% | 50.00% | 5.69 | 54.14% | 10.68 | 43.93 | 7.37 | Empate |
| 3 | Intermedio vs Dificil Manual | 3v3 | 150 | 70 | 80 | 0 | 46.67% | 53.33% | 9.62 | 47.05% | 20.49 | 63.41 | 9.57 | Dificil Manual |
| 3 | Intermedio vs Dificil GA | 1v1 | 150 | 75 | 73 | 2 | 50.00% | 48.67% | 2.05 | 57.45% | 4.83 | 29.15 | 5.21 | Intermedio |
| 3 | Intermedio vs Dificil GA | 2v2 | 150 | 73 | 77 | 0 | 48.67% | 51.33% | 4.91 | 57.16% | 10.64 | 43.79 | 7.29 | Dificil GA |
| 3 | Intermedio vs Dificil GA | 3v3 | 150 | 77 | 73 | 0 | 51.33% | 48.67% | 7.88 | 52.82% | 21.14 | 64.29 | 9.81 | Intermedio |
| 3 | Dificil Manual vs Dificil GA | 1v1 | 150 | 73 | 77 | 0 | 48.67% | 51.33% | 2.27 | 59.05% | 5.59 | 27.87 | 5.10 | Dificil GA |
| 3 | Dificil Manual vs Dificil GA | 2v2 | 150 | 69 | 78 | 3 | 46.00% | 52.00% | 5.99 | 52.22% | 12.94 | 45.19 | 7.08 | Dificil GA |
| 3 | Dificil Manual vs Dificil GA | 3v3 | 150 | 73 | 76 | 1 | 48.67% | 50.67% | 10.21 | 44.91% | 22.98 | 62.39 | 9.16 | Dificil GA |
| 3 | Facil vs Dificil GA | 1v1 | 150 | 54 | 93 | 3 | 36.00% | 62.00% | 3.31 | 57.46% | 3.02 | 29.49 | 5.26 | Dificil GA |
| 3 | Facil vs Dificil GA | 2v2 | 150 | 35 | 115 | 0 | 23.33% | 76.67% | 6.72 | 51.54% | 6.69 | 51.28 | 7.79 | Dificil GA |
| 3 | Facil vs Dificil GA | 3v3 | 150 | 24 | 125 | 1 | 16.00% | 83.33% | 10.33 | 53.30% | 12.58 | 76.35 | 10.42 | Dificil GA |
| 3 | Facil vs Dificil Manual | 1v1 | 150 | 51 | 97 | 2 | 34.00% | 64.67% | 3.07 | 59.02% | 2.48 | 28.62 | 4.86 | Dificil Manual |
| 3 | Facil vs Dificil Manual | 2v2 | 150 | 35 | 115 | 0 | 23.33% | 76.67% | 7.51 | 49.61% | 6.62 | 53.21 | 7.62 | Dificil Manual |
| 3 | Facil vs Dificil Manual | 3v3 | 150 | 22 | 127 | 1 | 14.67% | 84.67% | 11.98 | 44.21% | 12.90 | 76.73 | 10.03 | Dificil Manual |
| 4 | Facil vs Intermedio | 1v1 | 150 | 50 | 98 | 2 | 33.33% | 65.33% | 2.91 | 61.56% | 3.29 | 57.13 | 15.20 | Intermedio |
| 4 | Facil vs Intermedio | 2v2 | 150 | 34 | 115 | 1 | 22.67% | 76.67% | 7.67 | 46.30% | 9.82 | 110.47 | 25.23 | Intermedio |
| 4 | Facil vs Intermedio | 3v3 | 150 | 15 | 134 | 1 | 10.00% | 89.33% | 11.59 | 51.88% | 20.50 | 171.97 | 37.26 | Intermedio |
| 4 | Intermedio vs Dificil Manual | 1v1 | 150 | 66 | 83 | 1 | 44.00% | 55.33% | 2.20 | 54.98% | 8.47 | 58.49 | 15.76 | Dificil Manual |
| 4 | Intermedio vs Dificil Manual | 2v2 | 150 | 75 | 75 | 0 | 50.00% | 50.00% | 5.84 | 55.82% | 23.96 | 109.56 | 24.73 | Empate |
| 4 | Intermedio vs Dificil Manual | 3v3 | 150 | 71 | 79 | 0 | 47.33% | 52.67% | 9.74 | 49.31% | 56.08 | 189.10 | 37.84 | Dificil Manual |
| 4 | Intermedio vs Dificil GA | 1v1 | 150 | 73 | 75 | 2 | 48.67% | 50.00% | 2.33 | 55.14% | 8.91 | 58.31 | 15.82 | Dificil GA |
| 4 | Intermedio vs Dificil GA | 2v2 | 150 | 71 | 79 | 0 | 47.33% | 52.67% | 5.04 | 59.55% | 25.54 | 115.75 | 25.95 | Dificil GA |
| 4 | Intermedio vs Dificil GA | 3v3 | 150 | 72 | 78 | 0 | 48.00% | 52.00% | 9.61 | 50.88% | 60.37 | 199.85 | 40.17 | Dificil GA |
| 4 | Dificil Manual vs Dificil GA | 1v1 | 150 | 84 | 65 | 1 | 56.00% | 43.33% | 2.17 | 58.01% | 10.02 | 57.37 | 15.39 | Dificil Manual |
| 4 | Dificil Manual vs Dificil GA | 2v2 | 150 | 58 | 92 | 0 | 38.67% | 61.33% | 5.65 | 55.53% | 30.65 | 116.71 | 26.62 | Dificil GA |
| 4 | Dificil Manual vs Dificil GA | 3v3 | 150 | 74 | 76 | 0 | 49.33% | 50.67% | 8.91 | 53.37% | 64.18 | 189.79 | 39.32 | Dificil GA |
| 4 | Facil vs Dificil GA | 1v1 | 150 | 43 | 106 | 1 | 28.67% | 70.67% | 2.73 | 57.85% | 5.27 | 58.30 | 15.25 | Dificil GA |
| 4 | Facil vs Dificil GA | 2v2 | 150 | 22 | 127 | 1 | 14.67% | 84.67% | 6.93 | 56.73% | 14.47 | 114.90 | 28.59 | Dificil GA |
| 4 | Facil vs Dificil GA | 3v3 | 150 | 22 | 128 | 0 | 14.67% | 85.33% | 10.35 | 56.48% | 29.11 | 201.58 | 44.56 | Dificil GA |
| 4 | Facil vs Dificil Manual | 1v1 | 150 | 47 | 99 | 4 | 31.33% | 66.00% | 2.76 | 60.44% | 4.44 | 57.20 | 15.86 | Dificil Manual |
| 4 | Facil vs Dificil Manual | 2v2 | 150 | 38 | 112 | 0 | 25.33% | 74.67% | 6.83 | 52.32% | 13.51 | 119.88 | 27.20 | Dificil Manual |
| 4 | Facil vs Dificil Manual | 3v3 | 150 | 20 | 129 | 1 | 13.33% | 86.00% | 11.44 | 53.16% | 26.69 | 187.00 | 40.82 | Dificil Manual |
