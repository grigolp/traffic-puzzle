## Traffic Puzzle Graph Representation

### Core Design
- **Every grid cell = one node** (20x20 grid = 400 nodes)
- **Nodes store directional neighbor relationships** (left/right/straight relative to approach)
- **Pre-calculate all possible exit paths** at initialization time

### Pre-Calculated Path Structure
```python
PathLookup[node_id][orientation][movement_rule] = {
    "exit_path": [node_1, node_2, ..., exit_node],  # Full path to exit
    "exit_point": (x, y),                           # Exit coordinates
    "valid": True/False                             # Is move possible
}
```

### Key Benefits
- **O(1) move validation** - No runtime pathfinding needed
- **Fast solvability checking** - Just lookup pre-calculated paths and check if nodes are clear
- **Efficient caching** - Hash road structures to reuse calculations across requests

### Validation Flow
1. Load/retrieve cached road structure
2. For each vehicle state: lookup valid moves instantly
3. Check if path nodes are empty (or contain only boulders for bulldozers)
4. Branch search tree based on available moves

This approach trades initial computation time and memory for extremely fast runtime performance.