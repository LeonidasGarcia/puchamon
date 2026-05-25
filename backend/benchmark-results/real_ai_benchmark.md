# Real AI Benchmark

- level_3_weights_source: code_default
- level_3_weights: hp=0.1766, alive=0.1092, damage=0.0643, type=0.1330, speed=0.2153, status=0.0752, effects=0.2265
- manual_weights: hp=0.2500, alive=0.1500, damage=0.2500, type=0.1500, speed=0.0800, status=0.0700, effects=0.0500
- minimax_depths: (1, 2, 3)

| Depth | Matchup | Formato | Batallas | Wins A | Wins B | Empates | Winrate A | Winrate B | Turnos Prom. | HP Restante | Decision ms | Nodos Expl. | Nodos Podados | Mejor IA |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 1 | Facil vs Intermedio | 1v1 | 80 | 22 | 58 | 0 | 27.50% | 72.50% | 2.60 | 57.63% | 0.28 | 3.96 | 0.00 | Intermedio |
| 1 | Facil vs Intermedio | 2v2 | 80 | 13 | 67 | 0 | 16.25% | 83.75% | 6.74 | 51.54% | 0.49 | 4.69 | 0.00 | Intermedio |
| 1 | Facil vs Intermedio | 3v3 | 80 | 8 | 72 | 0 | 10.00% | 90.00% | 10.70 | 48.53% | 0.72 | 5.37 | 0.00 | Intermedio |
| 1 | Intermedio vs Dificil Manual | 1v1 | 80 | 39 | 41 | 0 | 48.75% | 51.25% | 2.01 | 59.25% | 0.64 | 4.00 | 0.00 | Dificil Manual |
| 1 | Intermedio vs Dificil Manual | 2v2 | 80 | 45 | 35 | 0 | 56.25% | 43.75% | 5.67 | 48.50% | 1.06 | 4.69 | 0.00 | Intermedio |
| 1 | Intermedio vs Dificil Manual | 3v3 | 80 | 48 | 32 | 0 | 60.00% | 40.00% | 10.88 | 38.46% | 1.54 | 5.29 | 0.00 | Intermedio |
| 1 | Intermedio vs Dificil GA | 1v1 | 80 | 41 | 39 | 0 | 51.25% | 48.75% | 2.25 | 54.07% | 0.74 | 4.00 | 0.00 | Intermedio |
| 1 | Intermedio vs Dificil GA | 2v2 | 80 | 47 | 33 | 0 | 58.75% | 41.25% | 4.95 | 42.45% | 1.17 | 4.58 | 0.00 | Intermedio |
| 1 | Intermedio vs Dificil GA | 3v3 | 80 | 38 | 42 | 0 | 47.50% | 52.50% | 8.50 | 38.55% | 1.58 | 5.18 | 0.00 | Dificil GA |
| 1 | Dificil Manual vs Dificil GA | 1v1 | 80 | 48 | 32 | 0 | 60.00% | 40.00% | 2.38 | 56.65% | 0.88 | 4.00 | 0.00 | Dificil Manual |
| 1 | Dificil Manual vs Dificil GA | 2v2 | 80 | 40 | 40 | 0 | 50.00% | 50.00% | 6.03 | 41.66% | 1.28 | 4.60 | 0.00 | Empate |
| 1 | Dificil Manual vs Dificil GA | 3v3 | 80 | 31 | 49 | 0 | 38.75% | 61.25% | 9.90 | 41.73% | 1.81 | 5.28 | 0.00 | Dificil GA |
| 1 | Facil vs Dificil GA | 1v1 | 80 | 32 | 47 | 1 | 40.00% | 58.75% | 2.95 | 56.52% | 0.47 | 3.99 | 0.00 | Dificil GA |
| 1 | Facil vs Dificil GA | 2v2 | 80 | 22 | 58 | 0 | 27.50% | 72.50% | 6.59 | 50.88% | 0.69 | 4.74 | 0.00 | Dificil GA |
| 1 | Facil vs Dificil GA | 3v3 | 80 | 11 | 69 | 0 | 13.75% | 86.25% | 10.59 | 50.53% | 1.01 | 5.50 | 0.00 | Dificil GA |
| 1 | Facil vs Dificil Manual | 1v1 | 80 | 24 | 55 | 1 | 30.00% | 68.75% | 3.16 | 53.49% | 0.47 | 3.96 | 0.00 | Dificil Manual |
| 1 | Facil vs Dificil Manual | 2v2 | 80 | 24 | 55 | 1 | 30.00% | 68.75% | 8.47 | 41.09% | 0.72 | 4.70 | 0.00 | Dificil Manual |
| 1 | Facil vs Dificil Manual | 3v3 | 80 | 15 | 65 | 0 | 18.75% | 81.25% | 13.84 | 42.33% | 0.95 | 5.47 | 0.00 | Dificil Manual |
| 2 | Facil vs Intermedio | 1v1 | 80 | 36 | 44 | 0 | 45.00% | 55.00% | 3.08 | 60.88% | 0.80 | 13.03 | 2.09 | Intermedio |
| 2 | Facil vs Intermedio | 2v2 | 80 | 20 | 60 | 0 | 25.00% | 75.00% | 8.18 | 48.47% | 1.50 | 18.11 | 3.18 | Intermedio |
| 2 | Facil vs Intermedio | 3v3 | 80 | 14 | 65 | 1 | 17.50% | 81.25% | 12.39 | 40.03% | 2.53 | 22.84 | 3.92 | Intermedio |
| 2 | Intermedio vs Dificil Manual | 1v1 | 80 | 44 | 36 | 0 | 55.00% | 45.00% | 2.14 | 55.17% | 1.75 | 12.17 | 2.08 | Intermedio |
| 2 | Intermedio vs Dificil Manual | 2v2 | 80 | 34 | 46 | 0 | 42.50% | 57.50% | 6.24 | 49.36% | 3.70 | 18.63 | 3.15 | Dificil Manual |
| 2 | Intermedio vs Dificil Manual | 3v3 | 80 | 37 | 43 | 0 | 46.25% | 53.75% | 10.65 | 46.74% | 6.09 | 24.25 | 3.90 | Dificil Manual |
| 2 | Intermedio vs Dificil GA | 1v1 | 80 | 43 | 37 | 0 | 53.75% | 46.25% | 2.15 | 58.71% | 1.73 | 12.31 | 2.16 | Intermedio |
| 2 | Intermedio vs Dificil GA | 2v2 | 80 | 44 | 35 | 1 | 55.00% | 43.75% | 6.33 | 50.95% | 3.93 | 19.00 | 3.18 | Intermedio |
| 2 | Intermedio vs Dificil GA | 3v3 | 80 | 36 | 44 | 0 | 45.00% | 55.00% | 9.70 | 45.36% | 6.19 | 24.13 | 3.93 | Dificil GA |
| 2 | Dificil Manual vs Dificil GA | 1v1 | 80 | 39 | 41 | 0 | 48.75% | 51.25% | 1.93 | 53.71% | 2.19 | 12.77 | 1.97 | Dificil GA |
| 2 | Dificil Manual vs Dificil GA | 2v2 | 80 | 42 | 38 | 0 | 52.50% | 47.50% | 6.15 | 46.50% | 4.12 | 17.82 | 3.04 | Dificil Manual |
| 2 | Dificil Manual vs Dificil GA | 3v3 | 80 | 43 | 37 | 0 | 53.75% | 46.25% | 10.16 | 46.38% | 6.72 | 22.88 | 3.66 | Dificil Manual |
| 2 | Facil vs Dificil GA | 1v1 | 80 | 28 | 52 | 0 | 35.00% | 65.00% | 2.84 | 60.77% | 1.06 | 12.02 | 2.05 | Dificil GA |
| 2 | Facil vs Dificil GA | 2v2 | 80 | 29 | 51 | 0 | 36.25% | 63.75% | 7.38 | 42.23% | 2.21 | 18.06 | 3.02 | Dificil GA |
| 2 | Facil vs Dificil GA | 3v3 | 80 | 17 | 62 | 1 | 21.25% | 77.50% | 12.32 | 45.03% | 3.51 | 23.04 | 3.79 | Dificil GA |
| 2 | Facil vs Dificil Manual | 1v1 | 80 | 32 | 48 | 0 | 40.00% | 60.00% | 2.69 | 59.79% | 1.11 | 12.27 | 1.97 | Dificil Manual |
| 2 | Facil vs Dificil Manual | 2v2 | 80 | 21 | 59 | 0 | 26.25% | 73.75% | 7.03 | 54.59% | 2.08 | 17.21 | 3.00 | Dificil Manual |
| 2 | Facil vs Dificil Manual | 3v3 | 80 | 20 | 60 | 0 | 25.00% | 75.00% | 12.39 | 42.99% | 3.48 | 23.04 | 3.69 | Dificil Manual |
| 3 | Facil vs Intermedio | 1v1 | 80 | 28 | 51 | 1 | 35.00% | 63.75% | 3.01 | 57.42% | 1.83 | 34.38 | 5.33 | Intermedio |
| 3 | Facil vs Intermedio | 2v2 | 80 | 22 | 57 | 1 | 27.50% | 71.25% | 6.88 | 54.35% | 4.31 | 55.56 | 8.45 | Intermedio |
| 3 | Facil vs Intermedio | 3v3 | 80 | 21 | 59 | 0 | 26.25% | 73.75% | 11.95 | 46.45% | 8.54 | 79.51 | 10.87 | Intermedio |
| 3 | Intermedio vs Dificil Manual | 1v1 | 80 | 40 | 40 | 0 | 50.00% | 50.00% | 2.09 | 56.22% | 4.49 | 33.78 | 5.34 | Empate |
| 3 | Intermedio vs Dificil Manual | 2v2 | 80 | 42 | 38 | 0 | 52.50% | 47.50% | 5.97 | 48.73% | 11.08 | 58.39 | 8.27 | Intermedio |
| 3 | Intermedio vs Dificil Manual | 3v3 | 80 | 34 | 44 | 2 | 42.50% | 55.00% | 11.60 | 46.43% | 18.31 | 71.73 | 9.58 | Dificil Manual |
| 3 | Intermedio vs Dificil GA | 1v1 | 80 | 33 | 47 | 0 | 41.25% | 58.75% | 2.30 | 57.99% | 4.86 | 34.90 | 5.39 | Dificil GA |
| 3 | Intermedio vs Dificil GA | 2v2 | 80 | 38 | 42 | 0 | 47.50% | 52.50% | 5.10 | 57.43% | 11.80 | 57.81 | 8.07 | Dificil GA |
| 3 | Intermedio vs Dificil GA | 3v3 | 80 | 29 | 51 | 0 | 36.25% | 63.75% | 9.65 | 48.26% | 21.46 | 85.49 | 11.21 | Dificil GA |
| 3 | Dificil Manual vs Dificil GA | 1v1 | 80 | 45 | 35 | 0 | 56.25% | 43.75% | 2.09 | 55.66% | 5.49 | 34.02 | 5.32 | Dificil Manual |
| 3 | Dificil Manual vs Dificil GA | 2v2 | 80 | 44 | 36 | 0 | 55.00% | 45.00% | 6.92 | 46.66% | 13.05 | 58.21 | 8.14 | Dificil Manual |
| 3 | Dificil Manual vs Dificil GA | 3v3 | 80 | 35 | 43 | 2 | 43.75% | 53.75% | 11.26 | 44.95% | 23.94 | 81.64 | 10.21 | Dificil GA |
| 3 | Facil vs Dificil GA | 1v1 | 80 | 31 | 46 | 3 | 38.75% | 57.50% | 3.15 | 58.20% | 2.55 | 31.10 | 5.14 | Dificil GA |
| 3 | Facil vs Dificil GA | 2v2 | 80 | 30 | 50 | 0 | 37.50% | 62.50% | 7.29 | 49.43% | 6.77 | 59.57 | 8.21 | Dificil GA |
| 3 | Facil vs Dificil GA | 3v3 | 80 | 24 | 56 | 0 | 30.00% | 70.00% | 12.60 | 46.89% | 13.20 | 89.91 | 11.96 | Dificil GA |
| 3 | Facil vs Dificil Manual | 1v1 | 80 | 30 | 50 | 0 | 37.50% | 62.50% | 2.67 | 62.52% | 2.47 | 29.98 | 5.13 | Dificil Manual |
| 3 | Facil vs Dificil Manual | 2v2 | 80 | 21 | 58 | 1 | 26.25% | 72.50% | 8.91 | 44.79% | 5.77 | 50.18 | 7.07 | Dificil Manual |
| 3 | Facil vs Dificil Manual | 3v3 | 80 | 15 | 64 | 1 | 18.75% | 80.00% | 13.09 | 42.04% | 12.84 | 87.82 | 10.88 | Dificil Manual |
