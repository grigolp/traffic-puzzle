# Traffic Puzzle Level Validator

A high-performance Python tool for validating traffic puzzle levels in mobile games. Determines if puzzle configurations are solvable using advanced pathfinding algorithms and pre-calculated movement rules.

## Overview

This validator analyzes traffic puzzle levels containing vehicles (cars, trucks, bulldozers) on road networks with obstacles (boulders) and determines if all vehicles can successfully exit the grid. It uses predefined movement rules including turn restrictions and multi-lane road support.

### Key Features

- **Fast Validation**: O(1) path lookups using pre-calculated route cache
- **Complex Movement Rules**: Predefined vehicle turning restrictions and intersection logic
- **Multiple Vehicle Types**: Cars, trucks, and bulldozers with different capabilities
- **Obstacle Support**: Boulders that block vehicles (except bulldozers)
- **AWS Lambda Ready**: Deployable as serverless function or run locally
- **Comprehensive Testing**: Test provided with complex scenarios

## Project Structure

```
traffic-puzzle-validator/
├── app/
│   ├── core/                    # Core logic modules
│   │   ├── graph_builder.py     # Builds road network graph
│   │   ├── path_calculator.py   # Pre-calculates all possible paths
│   │   └── solver.py           # BFS/Simple solver for puzzle validation
│   ├── models/                  # Data models and enums
│   │   ├── enums.py            # Cell types, orientations, movement rules
│   │   ├── graph.py            # Graph nodes and road network
│   │   ├── vehicles.py         # Vehicle classes and behavior
│   │   ├── obstacles.py        # Obstacle types and interactions
│   │   ├── game_state.py       # Game state management
│   │   └── path.py             # Path information structures
│   ├── services/               # High-level services
│   │   ├── level_loader.py     # Loads JSON levels into game objects
│   │   └── validator.py        # Main validation orchestration
│   └── lambda_function.py      # AWS Lambda entry point
├── tests/                      # Comprehensive test suite
│   ├── test_graph_builder.py   # Graph construction tests
│   ├── test_path_calculator.py # Path calculation tests
│   ├── test_solver_complex.py  # Complex puzzle scenarios
│   ├── test_movement_calculation.py # Multi-lane movement tests
│   └── test_lambda.py          # Lambda function tests
├── docs/                       # Detailed documentation
│   ├── Traffic Puzzle Level JSON Structure.md
│   ├── Traffic Puzzle Level Validator API.md
│   ├── Road Network Solvability Validator - Project Description.md
│   ├── Graph Representation.md
│   ├── Vehicle Length and Type Specifications.md
│   └── example.json            # Example level configuration
├── requirements.txt            # Corrently no requirements
└── README.md
```

## Quick Start

### Basic Usage

#### Validate a Level (Python)

```python
from services.validator import validate_level

level_data = {
    "levelId": "test_001",
    "metadata": {"difficulty": "easy", "targetMoves": 3},
    "grid": {
        "dimensions": {"width": 5, "height": 3},
        "layout": [
            ["-", "-", "-", "-", "-"],
            ["0", "0", "0", "0", "|"],
            ["-", "-", "+", "-", "+"]
        ]
    },
    "vehicles": [{
        "id": "C01",
        "type": "CAR", 
        "length": 2,
        "position": {"x": 0, "y": 0},
        "orientation": "EAST",
        "movementRule": "STRAIGHT"
    }],
    "obstacles": []
}

result = validate_level(level_data)
print(f"Solvable: {result['solvable']}")
if result['solvable']:
    print(f"Solution: {result['solution']}")
```

#### Run Tests

```bash
# Run all tests
python -m pytest tests/

# Run specific test
python tests/test_lambda.py

# Run with level 116 example
python tests/test_solver_complex.py
```

#### AWS Lambda Deployment

The `lambda_function.py` is ready for AWS Lambda deployment and handles both API Gateway events and direct invocations.

## Vehicle Types & Specifications

| Type | Length | Capabilities | ID Prefix |
|------|--------|-------------|-----------|
| **CAR** | 2 cells | Standard movement | C01, C02... |
| **TRUCK** | 3 cells | Standard movement | T01, T02... |
| **BULLDOZER** | 2 cells | Can clear boulders | B01, B02... |

## Movement Rules

- **STRAIGHT**: Continue forward until exit
- **LEFT/RIGHT**: Move forward, then turn at first available intersection
- **LEFT_U_TURN/RIGHT_U_TURN**: Make two consecutive turns to reverse direction

### Important Restrictions
- Vehicles must move forward ≥1 step before turning
- No consecutive intersection turns (prevents illegal U-turns)
- Horizontal roads: only east/west movement
- Vertical roads: only north/south movement

## Grid Layout

```
"0" = Building/wall (non-passable)
"-" = Horizontal road
"|" = Vertical road  
"+" = Intersection
```

Exit border is automatically added during processing.

## Example Level

See `docs/example.json` for Level 116 - a complex 20x10 grid with 18 vehicles and obstacles.

## Architecture

### Core Components

1. **GraphBuilder**: Converts grid layout to node-based road network
2. **PathCalculator**: Pre-calculates all valid exit paths for each position/orientation/movement combination
3. **Solver**: Uses BFS to find solution sequence, leveraging O(1) path lookups
4. **LevelLoader**: Handles JSON parsing and coordinate system management
5. **Validator**: Orchestrates validation flow and error handling

### Performance Characteristics

- **Path Lookup**: O(1) - pre-calculated at initialization
- **Validation**: O(V × M) where V = vehicles, M = possible moves
- **Memory**: O(N × O × R) where N = nodes, O = orientations, R = movement rules
- **Initialization**: O(N²) for complex path calculations

## API Response Format

### Solvable Level
```json
{
  "solvable": true,
  "solution": ["C01", "T02", "B01"],
  "totalMoves": 3
}
```

### Unsolvable Level
```json
{
  "solvable": false,
  "partialSolution": ["C01"],
  "movesUntilBlock": 1,
  "blockingDetails": [
    {
      "blocked": "C02",
      "blockedBy": "T01", 
      "reason": "Position occupied by another vehicle"
    }
  ],
  "reason": "Deadlock: no remaining exit paths"
}
```

## Development Guidelines

### Adding New Features

1. **New Vehicle Types**: Extend `VehicleType` enum and update `vehicles.py`
2. **New Obstacles**: Implement in `obstacles.py` following `Boulder` pattern
3. **Movement Rules**: Add to `MovementRule` enum and implement in `path_calculator.py`
4. **Validation Rules**: Extend `LevelValidator` class methods

### Running Specific Tests

```bash
# Test path calculation with multi-lane roads
python tests/test_movement_calculation.py

# Test complex scenarios with bulldozers and obstacles  
python tests/test_solver_complex.py

# Test graph building and neighbor relationships
python tests/test_graph_builder.py
```

### Current Limitations

- **Traffic Lights**: Schema defined but not implemented
- **Pedestrians**: Schema defined but not implemented  
- **Dynamic Obstacles**: Only static boulders currently supported

## Documentation

- **[JSON Schema](docs/Traffic%20Puzzle%20Level%20JSON%20Structure.md)**: Complete level format specification
- **[API Reference](docs/Traffic%20Puzzle%20Level%20Validator%20API.md)**: HTTP API documentation  
- **[Algorithm Details](docs/Road%20Network%20Solvability%20Validator%20-%20Project%20Description.md)**: Technical implementation details
- **[Graph Design](docs/Graph%20Representation.md)**: Network representation and pathfinding
- **[Vehicle Specs](docs/Vehicle%20Length%20and%20Type%20Specifications.md)**: Vehicle behavior and constraints