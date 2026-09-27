# RayCastMazeGame

A first-person raycasted maze game built in pure Python with [pygame](https://www.pygame.org/), using the DDA (Digital Differential Analyzer) algorithm for real-time wall rendering.

## Overview

Each playthrough generates a new 21x21 maze using a randomized depth-first search (recursive backtracker), then renders it in real time from a first-person perspective. The scene is lit by a flashlight effect that fades with distance, and walls are rendered with several hand-painted procedural textures (brick, metal, stone, hazard stripes, and a distinct "exit" texture marking the goal). Reach the exit tile to win — press R to generate and explore a brand new maze.

## Features

- **DDA raycasting** for efficient, accurate wall-distance calculation per screen column
- **Procedurally generated mazes** — a new layout every playthrough via randomized recursive backtracking
- **Textured walls** with per-tile material variation, rendered with perspective-correct texture mapping
- **Dynamic flashlight lighting** with distance-based falloff and a radial vignette mask
- **Strafing movement** (WASD/arrow keys to move and turn, Q/E to strafe) with wall collision detection

## Controls

| Key | Action |
|---|---|
| `W` / `↑` | Move forward |
| `S` / `↓` | Move backward |
| `A` / `←` | Turn left |
| `D` / `→` | Turn right |
| `Q` | Strafe left |
| `E` | Strafe right |
| `R` | Generate a new maze (after escaping) |
| `Esc` | Quit |

## Requirements

- Python 3.10+
- [pygame](https://www.pygame.org/)

Install the dependency with:

```bash
pip install pygame
```

## Running the game

```bash
python main.py
```

## Project structure
RayCastMazeGame/
├── main.py     # Maze generation, DDA raycasting, rendering, and game loop
└── player.py   # Player state and camera plane calculation


## How it works

The renderer casts one ray per screen column using the DDA algorithm to find the nearest wall intersection, then scales a vertical wall slice based on the perpendicular distance to create the 3D perspective effect. Wall side (north/south vs. east/west) and tile type determine which texture and shading are applied, and a flashlight falloff function darkens surfaces the further they are from the player.
