# Road Network Solvability Validator: Project Description

The Road Network Solvability Validator is a deterministic software tool designed to ascertain if a given traffic puzzle level is solvable. It operates on a discrete, turn-based state-space model where a single "move" consists of one vehicle exiting the map completely. The validator takes an initial level configuration as input and performs a systematic search to determine if a valid sequence of vehicle exits exists, leading to a state where all vehicles have successfully left the network.

## 2. Core Functionality: Solvability Validator

### 2.1. Input Definition (Level Data)

The validator will accept level data in a structured JSON format.

**grid:**
- `dimensions`: `{ "width": <int>, "height": <int> }`
- `layout`: A 2D array where each cell defines its static type:
  - `0`: non-passable (sidewalks, walls)
  - `1`: road (vehicles may occupy and travel on)

Exit cells are any road cell (`1`) on the outermost row or column.

**vehicles:** An array of vehicle objects, each with:
- `id`: A unique string identifier (e.g., "C01", "T02", "B01")
- `type`: CAR, TRUCK, or BULLDOZER
- `length`: 1 for CAR/BULLDOZER, 2 for TRUCK
- `position`: A single {x, y} coordinate representing the head/front position
- `orientation`: NORTH, SOUTH, EAST, or WEST
- `movementRule`: STRAIGHT, LEFT, RIGHT, or U_TURN

**obstacles:** An array of obstacle objects including:
- `BOULDER` (static): blocks all vehicles except BULLDOZER
- `TRAFFIC_LIGHT` (dynamic): with currentState (RED/GREEN) and timing
- `PEDESTRIAN` (dynamic): with crossingTime and currentProgress
- `position`: An {x, y} coordinate

### 2.2. Internal Path Calculation

For any vehicle to exit, a complete, cell-by-cell path must be calculated from its current position to an EXIT_POINT.

**Pathfinding Logic:** A pathfinding algorithm will find a route to a valid EXIT_POINT.

**Path Constraints:**
- The generated path must conform to the vehicle's specified `movementRule`
- All cells in the path must be traversable (ROAD or EXIT_POINT)
- All cells in the path must be clear of other vehicles

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

1. **Identify Possible Moves:** From a given state S, check every active vehicle to see if it has a valid, clear exit path according to the rules in Section 2.2
2. **Generate New States (Branching):** For each vehicle V that has a valid exit path, a new potential state S' is created:
   - In S', V is removed from the set of active vehicles
   - If V was a BULLDOZER and its path crossed a BOULDER, that boulder is removed from the set of active boulders in S'
   - Each new state S' represents a branch in the search for a solution

### 2.5. Solvability Determination

The validator determines solvability by exploring the state-space graph, starting from the initial configuration. The core logic is that if multiple vehicles can exit from a single state, each choice creates a different future reality for the puzzle, and we must be prepared to explore them.

- **Initial State:** The configuration defined by the input level data
- **Goal State:** Any state where the set of active vehicles is empty

**Search Process:**
1. Start with the initialState
2. In the current state, find all vehicles that can make a valid exit move
3. If no vehicles can move, this branch of the search is a dead end
4. If one or more vehicles can move, this creates multiple branches. The process is applied recursively to each new state generated
5. To prevent infinite loops (e.g., returning to a previous board layout, thiis should not be possible for current problem statement), the validator must keep track of states it has already analyzed
6. If any branch leads to the goalState, the level is SOLVABLE
7. If all possible branches have been explored and none lead to the goalState, the level is UNSOLVABLE

**Output:**
- `status`: SOLVABLE or UNSOLVABLE
- `solutionPath`: If solvable, an ordered list of vehicle IDs that exited
- `reason`: If unsolvable (e.g., "Deadlock reached: Vehicles A, B, C are blocked")
