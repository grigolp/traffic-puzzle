# Traffic Puzzle Level JSON Schema

This document defines the JSON structure used to represent the state of a single level in the traffic-puzzle mobile game. It covers level metadata, the road grid, all vehicle types, and all obstacle types, along with a full example.

---

## 1. Root Structure

```json
{
  "levelId":         "string",
  "metadata":        { … },
  "grid":            { … },
  "vehicles":        [ … ],
  "obstacles":       [ … ]
}
```

* **levelId**: Unique identifier for the level (e.g. `"level_001"`).
* **metadata**: Level configuration parameters.
* **grid**: Road network definition.
* **vehicles**: Array of all movable vehicles on this level.
* **obstacles**: Array of all static and dynamic obstacles.

---

## 2. Metadata

```json
"metadata": {
  "difficulty":   "easy" | "medium" | "hard",
  "targetMoves":  integer
}
```

* **difficulty**: Intended complexity tier of the puzzle.
* **targetMoves**: Optimal number of moves for a perfect score.

---

## 3. Grid Definition

```json
"grid": {
  "dimensions": {
    "width":   integer,
    "height":  integer
  },
  "layout": [
    ["0", "-", "-", "+", …],
    ["0", "0", "0", "|", …],
    …
  ]
}
```

* **dimensions.width** / **.height**: Grid size in cells (columns × rows).
* **layout**: 2D array of strings defining road structure:

  * `"0"` = non-passable (sidewalks, walls, buildings)
  * `"-"` = horizontal road (allows east/west movement only)
  * `"|"` = vertical road (allows north/south movement only)
  * `"+"` = intersection (allows movement in all directions)

**Exit handling**: Exit nodes are automatically added as a border around the grid during processing. Vehicles exit when they reach these border nodes.

---

## 4. Vehicles

Each vehicle entry:

```json
{
  "id":           "C01" | "T02" | "B01",
  "type":         "CAR" | "TRUCK" | "BULLDOZER",
  "length":       2 | 3,
  "position":     { "x": integer, "y": integer },
  "orientation":  "NORTH" | "SOUTH" | "EAST" | "WEST",
  "movementRule": "STRAIGHT" | "LEFT" | "RIGHT" | "LEFT_U_TURN" | "RIGHT_U_TURN"
}
```

* **id**: Unique code (prefix by type: `C`=Car, `T`=Truck, `B`=Bulldozer + two-digit index).
* **type**: Vehicle category.
* **length**: Number of grid cells occupied:
  * **CAR**: 2 cells
  * **TRUCK**: 3 cells  
  * **BULLDOZER**: 2 cells
* **position**: Head/front coordinate (0-indexed, relative to original grid before exit border).
* **orientation**: Facing direction of the head.
* **movementRule**: Path constraint determining how the vehicle navigates:
  * `STRAIGHT`: Continues forward until exit
  * `LEFT`: Takes first available left turn (after moving at least one cell forward), then continues to exit
  * `RIGHT`: Takes first available right turn (after moving at least one cell forward), then continues to exit
  * `LEFT_U_TURN`: Makes two consecutive left turns to reverse direction
  * `RIGHT_U_TURN`: Makes two consecutive right turns to reverse direction

**Important Movement Restrictions:**
- Vehicles must move forward at least one step before making a turn
- Turns cannot be made at consecutive intersections (prevents illegal U-turns within multi-lane intersections)
- These restrictions significantly affect path planning and solvability

**Coordinate System:**
- Input coordinates are relative to the original grid (0-indexed)
- During processing, a border of exit nodes is added around the grid
- Internal coordinates are shifted by +1 in both directions to accommodate the exit border
- This shift is handled automatically and doesn't affect input/output formats

**Occupied cells** are computed by extending from the head position opposite to orientation:

| Orientation | Length=2 (cells)         | Length=4 (cells)                    |
| ----------- | ------------------------ | ----------------------------------- |
| **NORTH**   | `[{x,y}, {x, y+1}]`     | `[{x,y}, {x,y+1}, {x,y+2}, {x,y+3}]` |
| **SOUTH**   | `[{x,y}, {x, y-1}]`     | `[{x,y}, {x,y-1}, {x,y-2}, {x,y-3}]` |
| **EAST**    | `[{x,y}, {x-1, y}]`     | `[{x,y}, {x-1,y}, {x-2,y}, {x-3,y}]` |
| **WEST**    | `[{x,y}, {x+1, y}]`     | `[{x,y}, {x+1,y}, {x+2,y}, {x+3,y}]` |

---

## 5. Obstacles

All obstacles share these base fields:

```json
{
  "id":       string,
  "type":     string,
  "position": { "x": integer, "y": integer }
}
```

**Coordinate System:** Input coordinates are relative to the original grid (0-indexed, before exit border addition).

### 5.1. Boulder (Implemented)

```json
{
  "id":   "OB01",
  "type": "BOULDER",
  "position": { "x": 6, "y": 4 }
}
```

* Blocks all vehicles except **BULLDOZER**, which may traverse/remove it.

### 5.2. Traffic Light (Future Implementation)

```json
{
  "id":           "OTL01",
  "type":         "TRAFFIC_LIGHT",
  "position":     { "x": 4, "y": 2 },
  "currentState": "RED" | "GREEN",
  "timing": {
    "redDuration":    integer,
    "greenDuration":  integer,
    "currentTimer":   integer
  }
}
```

**Note:** Currently not implemented in the validator. Schema provided for future development.

### 5.3. Pedestrian (Future Implementation)

```json
{
  "id":               "OP01",
  "type":             "PEDESTRIAN",
  "position":         { "x": 3, "y": 5 },
  "crossingTime":     integer,
  "currentProgress":  integer
}
```

**Note:** Currently not implemented in the validator. Schema provided for future development.

---

## 6. Complete Example

```json
{
    "levelId": "level_001",
    "metadata": {
        "difficulty": "medium",
        "targetMoves": 12
    },
    "grid": {
        "dimensions": { "width": 10, "height": 8 },
        "layout": [
            ["0","|","|","0","0","0","|","|","|","0"],
            ["0","|","|","0","0","0","|","|","|","0"],
            ["-","+","+","-","-","-","+","+","+","-"],
            ["-","+","+","-","-","-","+","+","+","-"],
            ["0","|","|","0","0","0","|","|","|","0"],
            ["0","|","|","0","0","0","|","|","|","0"],
            ["-","+","+","-","-","-","+","+","+","-"],
            ["0","|","|","0","0","0","|","|","|","0"]
        ]
    },
    "vehicles": [
        {
            "id": "C01",
            "type": "CAR",
            "length": 2,
            "position": {"x": 2, "y": 2},
            "orientation": "EAST",
            "movementRule": "STRAIGHT"
        },
        {
            "id": "T01",
            "type": "TRUCK",
            "length": 3,
            "position": {"x": 7, "y": 4},
            "orientation": "NORTH",
            "movementRule": "LEFT"
        },
        {
            "id": "B01",
            "type": "BULLDOZER",
            "length": 2,
            "position": {"x": 1, "y": 6},
            "orientation": "SOUTH",
            "movementRule": "RIGHT_U_TURN"
        }
    ],
    "obstacles": [
        {
            "id": "OB1",
            "type": "BOULDER",
            "position": {"x": 5, "y": 3}
        }
    ]
}
```