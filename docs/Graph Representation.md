## Traffic Puzzle Graph Representation

### Core Design
- **Every grid cell = one node** (original grid + exit border)
- **Exit border automatically added** around original grid during processing
- **Nodes store directional neighbor relationships** (left/right/straight relative to approach)
- **Pre-calculate all possible exit paths** at initialization time with complex movement rules

### Coordinate System
- **Input coordinates**: 0-indexed relative to original grid dimensions
- **Internal coordinates**: Shifted by +1 in both directions due to exit border
- **Path calculations**: Use internal coordinate system
- **Output coordinates**: Converted back to original grid reference

### Pre-Calculated Path Structure
```python
PathLookup[node_id][orientation][movement_rule] = {
    "exit_path": [node_1, node_2, ..., exit_node],  # Full path to exit
    "exit_point": (x, y),                           # Exit coordinates (internal system)
    "valid": True/False                             # Is move possible
}
```

### Advanced Movement Rules Implementation
- **Turn Restrictions**: Vehicles must move forward at least one step before turning
- **Intersection Logic**: Consecutive intersection turns prohibited (prevents illegal U-turns)
- **State Tracking**: Visited states tracked to prevent infinite loops during path calculation
- **Multi-step Turns**: U-turns require two consecutive turn actions with validation at each step

### Key Benefits
- **O(1) move validation** - No runtime pathfinding needed
- **Fast solvability checking** - Just lookup pre-calculated paths and check if nodes are clear
- **Complex movement rule support** - All turn restrictions pre-calculated and validated
- **Efficient caching** - Hash road structures to reuse calculations across requests

### Validation Flow
1. Load level data and add exit border (+1 coordinate shift)
2. Build graph with neighbor relationships based on road types
3. Pre-calculate all valid paths considering movement restrictions
4. For each vehicle state: lookup valid moves instantly (O(1))
5. Check if path nodes are clear (or contain only boulders for bulldozers)
6. Branch search tree based on available moves
7. Track visited states to prevent cycles

This approach trades initial computation time and memory for extremely fast runtime performance while supporting complex, realistic traffic movement rules.