# Traffic Puzzle Level Validator API

**Version:** v1  
**Base URL:** `http://localhost:8000/api/v1`

---

## 1. Validate Level

> **POST** `/validate`  
> Validate a level configuration for solvability.  

### 1.1. Request

**Headers**  
```

Content-Type: application/json

````

**Body Schema**  
```jsonc
{
  "levelId":        "string",               // unique level code
  "metadata": {
    "difficulty":   "easy" | "medium" | "hard",
    "targetMoves":  integer                  // optimal-move benchmark
  },
  "grid": {
    "dimensions": {
      "width":     integer,                  // columns (1–50)
      "height":    integer                   // rows (1–50)
    },
    "layout":       number[][]               // 2D array: 0=non-passable, 1=road
  },
  "vehicles": [
    {
      "id":           "string",              // e.g. “C01”, “T02”, “B01”
      "type":         "CAR" | "TRUCK" | "BULLDOZER",
      "length":       1 | 2,                  // cells occupied
      "position":     { "x": integer, "y": integer },
      "orientation":  "NORTH" | "SOUTH" | "EAST" | "WEST",
      "movementRule": "STRAIGHT" | "LEFT" | "RIGHT" | "U_TURN"
    }
  ],
  "obstacles": [
    //--- BOULDER ---
    {
      "id":       "string",
      "type":     "BOULDER",
      "position": { "x": integer, "y": integer }
    },

    //--- TRAFFIC LIGHT ---
    {
      "id":           "string",
      "type":         "TRAFFIC_LIGHT",
      "position":     { "x": integer, "y": integer },
      "currentState": "RED" | "GREEN",
      "timing": {
        "redDuration":    integer,            // turns per RED
        "greenDuration":  integer,            // turns per GREEN
        "currentTimer":   integer             // turns until state flip
      }
    },

    //--- PEDESTRIAN ---
    {
      "id":               "string",
      "type":             "PEDESTRIAN",
      "position":         { "x": integer, "y": integer },
      "crossingTime":     integer,            // total turns to cross
      "currentProgress":  integer             // progress 0…crossingTime-1
    }
  ]
}
````

---

### 1.2. Responses

#### 1.2.1. 200 OK — Solvable

```json
{
  "solvable":    true,
  "solution":    ["C01", "T02", "B01", "C02", "T01"],  
  "totalMoves":  5
}
```

#### 1.2.2. 200 OK — Unsolvable

```json
{
  "solvable":         false,
  "partialSolution":  ["C01", "T02"],   
  "movesUntilBlock":  2,
  "blockingDetails": [
    {
      "blocked":   "C02",
      "blockedBy": "T01",
      "reason":    "T01 occupies the only exit path for C02"
    },
    {
      "blocked":   "T01",
      "blockedBy": "B01",
      "reason":    "B01 blocks T01’s turning path"
    }
  ],
  "reason":            "Deadlock: no remaining exit paths"
}
```

---

### 1.2.3. 400 Bad Request — Malformed JSON or Missing Fields

```json
{
  "error": {
    "code":    "INVALID_REQUEST",
    "message": "Request body is not valid JSON or is missing required fields"
  }
}
```

---

### 1.2.4. 422 Unprocessable Entity — Schema or Logical Validation Failed

```json
{
  "error": {
    "code":    "VALIDATION_ERROR",
    "message": "Level data failed validation",
    "details": [
      {
        "field":   "vehicles[0].orientation",
        "message": "Expected one of: NORTH, SOUTH, EAST, WEST"
      },
      {
        "field":   "grid.layout[2][5]",
        "message": "Cell value must be 0 or 1"
      }
    ]
  }
}
```

---

### 1.2.5. 500 Internal Server Error

```json
{
  "error": {
    "code":    "SERVER_ERROR",
    "message": "An unexpected error occurred"
  }
}
```

---

## 2. Error Codes Reference

| HTTP | Code                          | Description                                   |
| ---- | ----------------------------- | --------------------------------------------- |
| 400  | `INVALID_REQUEST`             | Malformed JSON or missing required fields     |
| 422  | `VALIDATION_ERROR`            | JSON schema violations or enum mismatches     |
| 422  | `INVALID_LEVEL_DATA`          | Logical inconsistency (e.g. vehicle off-road) |
| 422  | `INVALID_GRID_DIMENSIONS`     | Width/height out of allowed range (1–50)      |
| 422  | `INVALID_VEHICLE_PLACEMENT`   | Vehicle off-road or out of bounds             |
| 422  | `INVALID_OBSTACLE_PLACEMENT`  | Obstacle off-road or out of bounds            |
| 422  | `OVERLAPPING_OBJECTS`         | Two or more objects share the same cell       |
| 422  | `INVALID_VEHICLE_ORIENTATION` | Vehicle initially faces a wall                |
| 500  | `SERVER_ERROR`                | Unexpected server-side failure                |

---

## 3. Usage Examples

#### 3.1. Solvable Level

```bash
curl -X POST http://localhost:8000/api/v1/validate \
  -H "Content-Type: application/json" \
  -d '{
    "levelId": "level_001",
    "metadata": { "difficulty": "easy", "targetMoves": 3 },
    "grid": {
      "dimensions": {"width":5,"height":5},
      "layout": [
        [1,1,1,1,1],
        [1,0,0,0,1],
        [1,1,1,1,1],
        [1,0,0,0,1],
        [1,1,1,1,1]
      ]
    },
    "vehicles": [{
      "id":"C01","type":"CAR","length":1,
      "position":{"x":2,"y":2},
      "orientation":"EAST","movementRule":"STRAIGHT"
    }],
    "obstacles": []
  }'
```

**Response (200 OK):**

```json
{
  "solvable":   true,
  "solution":   ["C01"],
  "totalMoves": 1
}
```

#### 3.2. Unsolvable Level

```bash
curl -X POST http://localhost:8000/api/v1/validate \
  -H "Content-Type: application/json" \
  -d '{
    "levelId": "level_002",
    "metadata": { "difficulty": "hard", "targetMoves": 5 },
    "grid": {
      "dimensions": {"width":5,"height":5},
      "layout": [
        [1,1,1,1,1],
        [1,0,0,0,1],
        [1,1,1,1,1],
        [1,0,0,0,1],
        [1,1,1,1,1]
      ]
    },
    "vehicles": [
      {
        "id":"C01","type":"CAR","length":1,
        "position":{"x":1,"y":2},
        "orientation":"EAST","movementRule":"STRAIGHT"
      },
      {
        "id":"C02","type":"CAR","length":1,
        "position":{"x":3,"y":2},
        "orientation":"WEST","movementRule":"STRAIGHT"
      }
    ],
    "obstacles": []
  }'
```

**Response (200 OK):**

```json
{
  "solvable":        false,
  "partialSolution": [],
  "movesUntilBlock": 0,
  "blockingDetails": [
    {
      "blocked":   "C01",
      "blockedBy": "C02",
      "reason":    "C02 blocks C01’s straight path to exit"
    },
    {
      "blocked":   "C02",
      "blockedBy": "C01",
      "reason":    "C01 blocks C02’s straight path to exit"
    }
  ],
  "reason":          "Deadlock: no alternative paths"
}
```