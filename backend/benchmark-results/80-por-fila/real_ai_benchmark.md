# Real AI Benchmark

- level_3_weights_source: code_default
- level_3_weights: hp=0.1707, alive=0.1192, damage=0.1381, type=0.1233, speed=0.1066, status=0.1315, effects=0.2105
- manual_weights: hp=0.2500, alive=0.1500, damage=0.2500, type=0.1500, speed=0.0800, status=0.0700, effects=0.0500
- minimax_depths: (1, 2, 3, 4)
- battles_per_row: 80
- total_battles: 5760
- expected_total_battles: 5760
- concurrency: 4
- max_turns: 80
- started_at: 2026-06-17T23:49:23.708268+00:00
- finished_at: 2026-06-18T00:09:41.602728+00:00
- elapsed_seconds: 1217.8944569319992
- elapsed_minutes: 20.298240948866653

| Depth | Matchup | Formato | Batallas | Wins A | Wins B | Empates | Winrate A | Winrate B | Turnos Prom. | HP Restante | Decision ms | Nodos Expl. | Nodos Podados | Mejor IA |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 1 | Facil vs Intermedio | 1v1 | 80 | 21 | 56 | 3 | 26.25% | 70.00% | 2.90 | 62.28% | 0.25 | 3.99 | 0.00 | Intermedio |
| 1 | Facil vs Intermedio | 2v2 | 80 | 9 | 71 | 0 | 11.25% | 88.75% | 6.41 | 55.60% | 0.39 | 4.43 | 0.00 | Intermedio |
| 1 | Facil vs Intermedio | 3v3 | 80 | 9 | 71 | 0 | 11.25% | 88.75% | 10.69 | 52.68% | 0.59 | 5.11 | 0.00 | Intermedio |
| 1 | Intermedio vs Dificil Manual | 1v1 | 80 | 47 | 33 | 0 | 58.75% | 41.25% | 1.89 | 60.07% | 0.68 | 4.00 | 0.00 | Intermedio |
| 1 | Intermedio vs Dificil Manual | 2v2 | 80 | 50 | 30 | 0 | 62.50% | 37.50% | 6.05 | 45.14% | 0.98 | 4.21 | 0.00 | Intermedio |
| 1 | Intermedio vs Dificil Manual | 3v3 | 80 | 49 | 30 | 1 | 61.25% | 37.50% | 10.71 | 36.24% | 1.38 | 4.74 | 0.00 | Intermedio |
| 1 | Intermedio vs Dificil GA | 1v1 | 80 | 40 | 40 | 0 | 50.00% | 50.00% | 2.15 | 60.21% | 0.69 | 4.00 | 0.00 | Empate |
| 1 | Intermedio vs Dificil GA | 2v2 | 80 | 49 | 31 | 0 | 61.25% | 38.75% | 4.78 | 46.21% | 0.97 | 4.11 | 0.00 | Intermedio |
| 1 | Intermedio vs Dificil GA | 3v3 | 80 | 32 | 48 | 0 | 40.00% | 60.00% | 7.54 | 40.52% | 1.40 | 4.59 | 0.00 | Dificil GA |
| 1 | Dificil Manual vs Dificil GA | 1v1 | 80 | 40 | 40 | 0 | 50.00% | 50.00% | 2.23 | 56.63% | 0.88 | 4.00 | 0.00 | Empate |
| 1 | Dificil Manual vs Dificil GA | 2v2 | 80 | 35 | 45 | 0 | 43.75% | 56.25% | 6.40 | 45.52% | 1.22 | 4.25 | 0.00 | Dificil GA |
| 1 | Dificil Manual vs Dificil GA | 3v3 | 80 | 26 | 52 | 2 | 32.50% | 65.00% | 11.15 | 34.34% | 1.72 | 4.79 | 0.00 | Dificil GA |
| 1 | Facil vs Dificil GA | 1v1 | 80 | 28 | 52 | 0 | 35.00% | 65.00% | 2.74 | 59.65% | 0.52 | 4.00 | 0.00 | Dificil GA |
| 1 | Facil vs Dificil GA | 2v2 | 80 | 15 | 65 | 0 | 18.75% | 81.25% | 6.29 | 51.76% | 0.70 | 4.49 | 0.00 | Dificil GA |
| 1 | Facil vs Dificil GA | 3v3 | 80 | 12 | 67 | 1 | 15.00% | 83.75% | 10.79 | 49.91% | 0.93 | 5.30 | 0.00 | Dificil GA |
| 1 | Facil vs Dificil Manual | 1v1 | 80 | 33 | 46 | 1 | 41.25% | 57.50% | 3.06 | 52.95% | 0.46 | 4.00 | 0.00 | Dificil Manual |
| 1 | Facil vs Dificil Manual | 2v2 | 80 | 24 | 54 | 2 | 30.00% | 67.50% | 7.80 | 50.34% | 0.64 | 4.42 | 0.00 | Dificil Manual |
| 1 | Facil vs Dificil Manual | 3v3 | 80 | 15 | 65 | 0 | 18.75% | 81.25% | 12.96 | 45.15% | 0.91 | 5.26 | 0.00 | Dificil Manual |
| 2 | Facil vs Intermedio | 1v1 | 80 | 23 | 55 | 2 | 28.75% | 68.75% | 2.96 | 62.96% | 0.67 | 12.11 | 2.11 | Intermedio |
| 2 | Facil vs Intermedio | 2v2 | 80 | 27 | 53 | 0 | 33.75% | 66.25% | 7.39 | 46.45% | 1.34 | 16.46 | 2.91 | Intermedio |
| 2 | Facil vs Intermedio | 3v3 | 80 | 15 | 64 | 1 | 18.75% | 80.00% | 13.35 | 39.23% | 2.31 | 21.18 | 3.62 | Intermedio |
| 2 | Intermedio vs Dificil Manual | 1v1 | 80 | 41 | 38 | 1 | 51.25% | 47.50% | 1.96 | 62.79% | 1.65 | 11.84 | 2.12 | Intermedio |
| 2 | Intermedio vs Dificil Manual | 2v2 | 80 | 24 | 56 | 0 | 30.00% | 70.00% | 6.58 | 49.29% | 3.29 | 16.95 | 2.75 | Dificil Manual |
| 2 | Intermedio vs Dificil Manual | 3v3 | 80 | 17 | 63 | 0 | 21.25% | 78.75% | 9.90 | 51.48% | 5.58 | 22.04 | 3.44 | Dificil Manual |
| 2 | Intermedio vs Dificil GA | 1v1 | 80 | 38 | 41 | 1 | 47.50% | 51.25% | 2.17 | 54.17% | 1.58 | 11.45 | 2.26 | Dificil GA |
| 2 | Intermedio vs Dificil GA | 2v2 | 80 | 23 | 57 | 0 | 28.75% | 71.25% | 5.81 | 55.85% | 3.36 | 16.97 | 2.87 | Dificil GA |
| 2 | Intermedio vs Dificil GA | 3v3 | 80 | 23 | 57 | 0 | 28.75% | 71.25% | 9.26 | 50.74% | 5.66 | 22.06 | 3.50 | Dificil GA |
| 2 | Dificil Manual vs Dificil GA | 1v1 | 80 | 42 | 38 | 0 | 52.50% | 47.50% | 2.34 | 55.50% | 2.07 | 11.98 | 1.90 | Dificil Manual |
| 2 | Dificil Manual vs Dificil GA | 2v2 | 80 | 40 | 40 | 0 | 50.00% | 50.00% | 5.38 | 54.38% | 3.77 | 15.84 | 2.59 | Empate |
| 2 | Dificil Manual vs Dificil GA | 3v3 | 80 | 38 | 41 | 1 | 47.50% | 51.25% | 9.65 | 54.23% | 6.16 | 20.04 | 3.16 | Dificil GA |
| 2 | Facil vs Dificil GA | 1v1 | 80 | 27 | 52 | 1 | 33.75% | 65.00% | 2.95 | 59.13% | 1.13 | 12.08 | 2.13 | Dificil GA |
| 2 | Facil vs Dificil GA | 2v2 | 80 | 18 | 62 | 0 | 22.50% | 77.50% | 6.79 | 56.51% | 1.92 | 16.08 | 2.91 | Dificil GA |
| 2 | Facil vs Dificil GA | 3v3 | 80 | 8 | 72 | 0 | 10.00% | 90.00% | 10.69 | 57.47% | 3.19 | 21.56 | 3.68 | Dificil GA |
| 2 | Facil vs Dificil Manual | 1v1 | 80 | 27 | 53 | 0 | 33.75% | 66.25% | 2.67 | 60.95% | 1.03 | 11.29 | 2.31 | Dificil Manual |
| 2 | Facil vs Dificil Manual | 2v2 | 80 | 15 | 65 | 0 | 18.75% | 81.25% | 7.39 | 55.30% | 1.98 | 16.44 | 2.76 | Dificil Manual |
| 2 | Facil vs Dificil Manual | 3v3 | 80 | 11 | 69 | 0 | 13.75% | 86.25% | 10.31 | 58.42% | 3.08 | 20.99 | 3.60 | Dificil Manual |
| 3 | Facil vs Intermedio | 1v1 | 80 | 20 | 59 | 1 | 25.00% | 73.75% | 3.05 | 64.45% | 1.53 | 28.45 | 5.31 | Intermedio |
| 3 | Facil vs Intermedio | 2v2 | 80 | 18 | 62 | 0 | 22.50% | 77.50% | 7.05 | 51.27% | 3.61 | 45.28 | 7.75 | Intermedio |
| 3 | Facil vs Intermedio | 3v3 | 80 | 14 | 66 | 0 | 17.50% | 82.50% | 10.12 | 52.55% | 7.14 | 65.78 | 10.12 | Intermedio |
| 3 | Intermedio vs Dificil Manual | 1v1 | 80 | 33 | 47 | 0 | 41.25% | 58.75% | 1.99 | 63.73% | 4.38 | 31.20 | 5.51 | Dificil Manual |
| 3 | Intermedio vs Dificil Manual | 2v2 | 80 | 39 | 41 | 0 | 48.75% | 51.25% | 5.49 | 52.72% | 8.86 | 43.45 | 7.01 | Dificil Manual |
| 3 | Intermedio vs Dificil Manual | 3v3 | 80 | 43 | 36 | 1 | 53.75% | 45.00% | 10.60 | 45.36% | 15.86 | 59.80 | 9.24 | Intermedio |
| 3 | Intermedio vs Dificil GA | 1v1 | 80 | 42 | 38 | 0 | 52.50% | 47.50% | 2.12 | 55.09% | 3.72 | 28.04 | 5.18 | Intermedio |
| 3 | Intermedio vs Dificil GA | 2v2 | 80 | 33 | 46 | 1 | 41.25% | 57.50% | 5.11 | 52.52% | 8.84 | 43.89 | 7.48 | Dificil GA |
| 3 | Intermedio vs Dificil GA | 3v3 | 80 | 38 | 42 | 0 | 47.50% | 52.50% | 7.79 | 56.99% | 17.23 | 64.84 | 9.83 | Dificil GA |
| 3 | Dificil Manual vs Dificil GA | 1v1 | 80 | 33 | 44 | 3 | 41.25% | 55.00% | 2.14 | 59.00% | 4.83 | 28.52 | 5.28 | Dificil GA |
| 3 | Dificil Manual vs Dificil GA | 2v2 | 80 | 37 | 42 | 1 | 46.25% | 52.50% | 5.39 | 56.26% | 10.60 | 44.46 | 7.19 | Dificil GA |
| 3 | Dificil Manual vs Dificil GA | 3v3 | 80 | 44 | 36 | 0 | 55.00% | 45.00% | 9.07 | 44.10% | 22.28 | 63.44 | 8.97 | Dificil Manual |
| 3 | Facil vs Dificil GA | 1v1 | 80 | 20 | 59 | 1 | 25.00% | 73.75% | 2.73 | 61.76% | 3.00 | 29.57 | 5.01 | Dificil GA |
| 3 | Facil vs Dificil GA | 2v2 | 80 | 15 | 65 | 0 | 18.75% | 81.25% | 6.79 | 54.51% | 6.78 | 49.86 | 7.54 | Dificil GA |
| 3 | Facil vs Dificil GA | 3v3 | 80 | 13 | 67 | 0 | 16.25% | 83.75% | 10.15 | 53.44% | 13.04 | 73.83 | 9.96 | Dificil GA |
| 3 | Facil vs Dificil Manual | 1v1 | 80 | 28 | 50 | 2 | 35.00% | 62.50% | 3.38 | 63.22% | 3.07 | 30.72 | 5.05 | Dificil Manual |
| 3 | Facil vs Dificil Manual | 2v2 | 80 | 24 | 56 | 0 | 30.00% | 70.00% | 7.60 | 49.93% | 7.01 | 49.34 | 7.41 | Dificil Manual |
| 3 | Facil vs Dificil Manual | 3v3 | 80 | 11 | 67 | 2 | 13.75% | 83.75% | 13.56 | 47.43% | 12.96 | 69.38 | 8.84 | Dificil Manual |
| 4 | Facil vs Intermedio | 1v1 | 80 | 24 | 56 | 0 | 30.00% | 70.00% | 2.58 | 59.83% | 3.39 | 53.69 | 14.57 | Intermedio |
| 4 | Facil vs Intermedio | 2v2 | 80 | 22 | 57 | 1 | 27.50% | 71.25% | 7.36 | 50.70% | 10.15 | 106.19 | 24.34 | Intermedio |
| 4 | Facil vs Intermedio | 3v3 | 80 | 13 | 67 | 0 | 16.25% | 83.75% | 12.06 | 48.78% | 23.16 | 175.32 | 37.72 | Intermedio |
| 4 | Intermedio vs Dificil Manual | 1v1 | 80 | 45 | 34 | 1 | 56.25% | 42.50% | 2.51 | 54.14% | 9.98 | 57.60 | 15.17 | Intermedio |
| 4 | Intermedio vs Dificil Manual | 2v2 | 80 | 42 | 38 | 0 | 52.50% | 47.50% | 6.15 | 54.93% | 27.13 | 120.90 | 26.28 | Intermedio |
| 4 | Intermedio vs Dificil Manual | 3v3 | 80 | 35 | 45 | 0 | 43.75% | 56.25% | 8.95 | 52.52% | 56.56 | 178.88 | 36.27 | Dificil Manual |
| 4 | Intermedio vs Dificil GA | 1v1 | 80 | 44 | 36 | 0 | 55.00% | 45.00% | 2.25 | 52.32% | 7.32 | 50.87 | 14.91 | Intermedio |
| 4 | Intermedio vs Dificil GA | 2v2 | 80 | 41 | 38 | 1 | 51.25% | 47.50% | 6.67 | 54.16% | 26.22 | 111.17 | 24.75 | Intermedio |
| 4 | Intermedio vs Dificil GA | 3v3 | 80 | 48 | 32 | 0 | 60.00% | 40.00% | 9.90 | 49.55% | 62.43 | 193.65 | 39.35 | Intermedio |
| 4 | Dificil Manual vs Dificil GA | 1v1 | 80 | 43 | 36 | 1 | 53.75% | 45.00% | 2.30 | 56.25% | 9.36 | 53.54 | 14.27 | Dificil Manual |
| 4 | Dificil Manual vs Dificil GA | 2v2 | 80 | 37 | 42 | 1 | 46.25% | 52.50% | 5.30 | 58.52% | 31.81 | 114.98 | 26.41 | Dificil GA |
| 4 | Dificil Manual vs Dificil GA | 3v3 | 80 | 40 | 40 | 0 | 50.00% | 50.00% | 8.96 | 50.17% | 69.36 | 191.39 | 38.96 | Empate |
| 4 | Facil vs Dificil GA | 1v1 | 80 | 31 | 49 | 0 | 38.75% | 61.25% | 2.90 | 59.87% | 5.16 | 55.02 | 15.37 | Dificil GA |
| 4 | Facil vs Dificil GA | 2v2 | 80 | 18 | 62 | 0 | 22.50% | 77.50% | 6.22 | 53.67% | 14.36 | 107.43 | 26.45 | Dificil GA |
| 4 | Facil vs Dificil GA | 3v3 | 80 | 13 | 65 | 2 | 16.25% | 81.25% | 9.75 | 55.15% | 33.43 | 192.15 | 41.83 | Dificil GA |
| 4 | Facil vs Dificil Manual | 1v1 | 80 | 23 | 57 | 0 | 28.75% | 71.25% | 2.61 | 59.41% | 4.70 | 54.78 | 14.73 | Dificil Manual |
| 4 | Facil vs Dificil Manual | 2v2 | 80 | 15 | 64 | 1 | 18.75% | 80.00% | 6.19 | 55.11% | 14.17 | 104.63 | 24.68 | Dificil Manual |
| 4 | Facil vs Dificil Manual | 3v3 | 80 | 15 | 64 | 1 | 18.75% | 80.00% | 11.59 | 50.93% | 31.45 | 179.48 | 38.07 | Dificil Manual |
