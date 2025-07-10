# Road Network Solvability Validator: Project Description

The Road Network Solvability Validator is a deterministic software tool designed to ascertain if a given traffic puzzle level is solvable. It operates on a discrete, turn-based state-space model where a single "move" consists of one vehicle exiting the map completely. The validator takes an initial level configuration as input and performs a systematic search to determine if a valid sequence of vehicle exits exists, leading to a state where all vehicles have successfully left the network.

## 2. Core Functionality: Solvability Validator

### 2.1. Input Definition (Level Data)

The validator will accept level data in a structured JSON format.

**grid:**
- `dimensions`: `{ "width": <int>, "height": <int> }`
- `layout`: A 2D array where each cell defines its static type:
  - `"0"`: non-passable (sidewalks, walls, buildings)
  - `"-"`: horizontal road
  - `"|"`: vertical road  
  - `"+"`: intersection (where roads meet)

Exit points are handled by adding a border of exit nodes around the grid during processing.

**vehicles:** An array of vehicle objects, each with:
- `id`: A unique string identifier (e.g., "C01", "T02", "B01")
- `type`: CAR, TRUCK, or BULLDOZER
- `length`: 1 for CAR/BULLDOZER, 2 for TRUCK
- `position`: A single {x, y} coordinate representing the head/front position
- `orientation`: NORTH, SOUTH, EAST, or WEST
- `movementRule`: STRAIGHT, LEFT, RIGHT, LEFT_U_TURN, or RIGHT_U_TURN

**obstacles:** An array of obstacle objects including:
- `BOULDER` (static): blocks all vehicles except BULLDOZER
- `TRAFFIC_LIGHT` (dynamic): with currentState (RED/GREEN) and timing
- `PEDESTRIAN` (dynamic): with crossingTime and currentProgress
- `position`: An {x, y} coordinate

### 2.2. Internal Path Calculation

The validator uses a pre-calculated graph representation where all possible paths are computed at initialization:

**Graph Representation:**
- Every grid cell becomes a node
- Each node stores neighbor relationships based on orientation
- All possible exit paths are pre-calculated for O(1) lookup

**Path Lookup Structure:**
```
PathLookup[node_id][orientation][movement_rule] = {
    "exit_path": [node_1, node_2, ..., exit_node],
    "exit_point": (x, y),
    "valid": True/False
}
```

**Path Constraints:**
- The generated path must conform to the vehicle's specified `movementRule`
- Horizontal roads only allow east/west movement
- Vertical roads only allow north/south movement
- Intersections allow turns in any direction
- All cells in the path must be clear of other vehicles

**Movement Rules:**
- `STRAIGHT`: Continue forward until exit
- `LEFT`: Continue until first available left turn, take it, then continue to exit
- `RIGHT`: Continue until first available right turn, take it, then continue to exit
- `LEFT_U_TURN`: Make two consecutive left turns to reverse direction
- `RIGHT_U_TURN`: Make two consecutive right turns to reverse direction

**Obstacle Interaction:**
- For CAR and TRUCK vehicles, the path must also be clear of any BOULDERs
- For BULLDOZER vehicles, the path can traverse a cell with a BOULDER

**Failure Condition:** If no valid path can be found for a vehicle that satisfies all its constraints, that vehicle cannot move in the current state.

### 2.3. State Representation

A "State" is a complete snapshot of the puzzle at a specific moment, defined by the positions of all dynamic elements.

- **Active Vehicles:** The set of vehicles currently on the grid (ID, Type, current position, orientation)
- **Active Obstacles:** The current state of all obstacles:
  - **Boulders:** coordinates of remaining boulders
  - **Traffic Lights:** current state (RED/GREEN) and timing counters
  - **Pedestrians:** current crossing progress

### 2.4. Actions (State Transitions)

A state transition occurs when one vehicle successfully exits the grid.

1. **Identify Possible Moves:** From a given state S, lookup pre-calculated paths for each active vehicle
2. **Check Path Validity:** Verify all cells in the path are clear (or only contain boulders for bulldozers)
3. **Generate New States (Branching):** For each vehicle V that has a clear exit path, create a new state S':
   - In S', V is removed from the set of active vehicles
   - If V was a BULLDOZER and its path crossed a BOULDER, that boulder is removed in S'
   - Each new state S' represents a branch in the search

### 2.5. Solvability Determination

The validator determines solvability by exploring the state-space graph with efficient path lookups.

- **Initial State:** The configuration defined by the input level data
- **Goal State:** Any state where the set of active vehicles is empty

**Search Process:**
1. Start with the initialState
2. For each vehicle, lookup its pre-calculated exit path (O(1) operation)
3. Check if the path is clear in the current state
4. If no vehicles can move, this branch is a dead end
5. If vehicles can move, create new states for each possibility
6. Track visited states to prevent loops
7. If any branch reaches the goalState, the level is SOLVABLE
8. If all branches are explored without reaching goalState, level is UNSOLVABLE

**Output:**
- `status`: SOLVABLE or UNSOLVABLE
- `solutionPath`: If solvable, an ordered list of vehicle IDs that exited
- `reason`: If unsolvable (e.g., "Deadlock reached: Vehicles A, B, C are blocked")
```