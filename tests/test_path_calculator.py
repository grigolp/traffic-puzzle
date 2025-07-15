import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

app_dir = project_root / 'app'
sys.path.append(str(app_dir))

from core.graph_builder import GraphBuilder # type: ignore
from core.path_calculator import PathCalculator # type: ignore
from models.graph import Position # type: ignore
from models.enums import Orientation, MovementRule, CellType # type: ignore

def print_grid_visualization(layout):
    """Print the grid in a readable format"""
    print("\nGrid Layout:")
    print("  ", end="")
    for x in range(len(layout[0])):
        print(f"{x:2}", end="")
    print()
    
    for y, row in enumerate(layout):
        print(f"{y:2} ", end="")
        for cell in row:
            if cell == "0":
                print("■ ", end="")  # Building/obstacle
            elif cell == "-":
                print("─ ", end="")  # Horizontal road
            elif cell == "|":
                print("│ ", end="")  # Vertical road
            elif cell == "+":
                print("┼ ", end="")  # Intersection
        print()

def visualize_path(layout, start_pos, path_nodes, exit_point=None):
    """Visualize a specific path on the grid"""
    # Create a copy of the layout for visualization
    viz_grid = []
    for row in layout:
        viz_row = []
        for cell in row:
            if cell == "0":
                viz_row.append("■")
            elif cell == "-":
                viz_row.append("─")
            elif cell == "|":
                viz_row.append("│")
            elif cell == "+":
                viz_row.append("┼")
        viz_grid.append(viz_row)
    
    # Mark start position
    viz_grid[start_pos.y][start_pos.x] = "S"
    
    # Mark path
    for i, node_id in enumerate(path_nodes):
        _, x, y = node_id.split('_')
        x, y = int(x), int(y)
        if (x, y) != (start_pos.x, start_pos.y) and (not exit_point or (x, y) != (exit_point.x, exit_point.y)):
            viz_grid[y][x] = str((i + 1) % 10)
    
    # Mark exit
    if exit_point:
        viz_grid[exit_point.y][exit_point.x] = "E"
    
    # Print visualization
    print("  ", end="")
    for x in range(len(viz_grid[0])):
        print(f"{x:2}", end="")
    print()
    
    for y, row in enumerate(viz_grid):
        print(f"{y:2} ", end="")
        for cell in row:
            print(f"{cell} ", end="")
        print()

def test_path_calculator():
    """Test path calculation with various scenarios"""
    
    # 8x8 grid with clear road structure
    layout = [
        # 0    1    2    3    4    5    6    7
        ["-", "-", "-", "+", "-", "-", "-", "-"],  # 0 - Horizontal road with intersection
        ["0", "0", "0", "|", "0", "0", "0", "0"],  # 1
        ["0", "0", "0", "|", "0", "0", "0", "0"],  # 2
        ["-", "-", "-", "+", "-", "-", "+", "-"],  # 3 - Main horizontal road
        ["0", "0", "0", "|", "0", "0", "|", "0"],  # 4
        ["0", "0", "0", "|", "0", "0", "|", "0"],  # 5
        ["0", "0", "0", "+", "-", "-", "+", "0"],  # 6 - Bottom connection
        ["0", "0", "0", "|", "0", "0", "|", "0"],  # 7
    ]
    
    # Build graph
    builder = GraphBuilder()
    graph = builder.build_graph(8, 8, layout)
    
    # Calculate paths
    calculator = PathCalculator()
    calculator.calculate_all_paths(graph)
    
    print("=== PATH CALCULATOR TEST ===\n")
    print(f"Grid dimensions: {graph.width}x{graph.height}")
    print(f"Road nodes: {sum(1 for n in graph.nodes.values() if n.cell_type.is_road)}")
    print(f"Exit positions: {len(graph.exit_positions)}")
    
    # Visualize the grid
    print_grid_visualization(layout)
    
    # Test cases
    test_cases = [
        {
            "name": "STRAIGHT from horizontal road",
            "position": Position(1, 0),
            "orientation": Orientation.EAST,
            "movement": MovementRule.STRAIGHT,
            "description": "Should go straight east to exit"
        },
        {
            "name": "LEFT turn at intersection",
            "position": Position(2, 3),
            "orientation": Orientation.EAST,
            "movement": MovementRule.LEFT,
            "description": "Should turn left (north) at intersection (3,3)"
        },
        {
            "name": "RIGHT turn at intersection",
            "position": Position(2, 3),
            "orientation": Orientation.EAST,
            "movement": MovementRule.RIGHT,
            "description": "Should turn right (south) at intersection (3,3)"
        },
        {
            "name": "STRAIGHT through intersection",
            "position": Position(2, 3),
            "orientation": Orientation.EAST,
            "movement": MovementRule.STRAIGHT,
            "description": "Should continue straight through intersection"
        },
        {
            "name": "LEFT_U_TURN requiring two left turns",
            "position": Position(1, 3),
            "orientation": Orientation.EAST,
            "movement": MovementRule.LEFT_U_TURN,
            "description": "Should make two left turns to reverse direction"
        },
        {
            "name": "RIGHT_U_TURN requiring two right turns",
            "position": Position(5, 3),
            "orientation": Orientation.WEST,
            "movement": MovementRule.RIGHT_U_TURN,
            "description": "Should make two right turns to reverse direction"
        },
        {
            "name": "Vertical road going north",
            "position": Position(3, 5),
            "orientation": Orientation.NORTH,
            "movement": MovementRule.STRAIGHT,
            "description": "Should go straight north to exit"
        },
        {
            "name": "Dead-end detection",
            "position": Position(6, 5),
            "orientation": Orientation.SOUTH,
            "movement": MovementRule.STRAIGHT,
            "description": "Should be invalid - leads to dead end"
        }
    ]
    
    print("\n" + "="*70)
    print("PATH CALCULATION TESTS")
    print("="*70)
    
    for test in test_cases:
        print(f"\nTest: {test['name']}")
        print(f"Start: ({test['position'].x}, {test['position'].y}) facing {test['orientation'].value}")
        print(f"Movement: {test['movement'].value}")
        print(f"Expected: {test['description']}")
        print("-" * 50)
        
        # Get the node
        node = graph.get_node(test['position'].x, test['position'].y)
        if not node:
            print("ERROR: No node at this position!")
            continue
        
        # Check if path was calculated
        if node.id not in graph.path_lookup:
            print("ERROR: No paths calculated for this node!")
            continue
        
        if test['orientation'] not in graph.path_lookup[node.id]:
            print("ERROR: No paths calculated for this orientation!")
            continue
        
        if test['movement'] not in graph.path_lookup[node.id][test['orientation']]:
            print("ERROR: No path calculated for this movement rule!")
            continue
        
        # Get the path
        path_info = graph.path_lookup[node.id][test['orientation']][test['movement']]
        
        print(f"Result: {'VALID' if path_info.valid else 'INVALID'}")
        
        if path_info.valid:
            print(f"Exit point: ({path_info.exit_point.x}, {path_info.exit_point.y})")
            print(f"Path length: {len(path_info.exit_path)} cells")
            
            # Show first few and last few nodes of path
            if len(path_info.exit_path) <= 8:
                path_str = " → ".join(path_info.exit_path)
            else:
                path_str = " → ".join(path_info.exit_path[:4]) + " ... " + " → ".join(path_info.exit_path[-2:])
            print(f"Path: {path_str}")
            
            # Visualize the path
            print("\nPath visualization:")
            visualize_path(layout, test['position'], path_info.exit_path, path_info.exit_point)
        else:
            if path_info.exit_path:
                print(f"Partial path length: {len(path_info.exit_path)} cells")
                print(f"Path ended at: {path_info.exit_path[-1] if path_info.exit_path else 'N/A'}")
    
    # Statistics
    print("\n" + "="*70)
    print("PATH STATISTICS")
    print("="*70)
    
    # Count valid/invalid paths by movement type
    stats = {rule: {"valid": 0, "invalid": 0, "total": 0} for rule in MovementRule}
    
    for node_id, orientations in graph.path_lookup.items():
        for orientation, movements in orientations.items():
            for movement_rule, path_info in movements.items():
                stats[movement_rule]["total"] += 1
                if path_info.valid:
                    stats[movement_rule]["valid"] += 1
                else:
                    stats[movement_rule]["invalid"] += 1
    
    print("\nPaths by movement type:")
    for movement_rule, counts in stats.items():
        if counts["total"] > 0:
            success_rate = (counts["valid"] / counts["total"]) * 100
            print(f"{movement_rule.value:15} - Valid: {counts['valid']:3}, "
                  f"Invalid: {counts['invalid']:3}, "
                  f"Success rate: {success_rate:5.1f}%")
    
    # Test specific intersection behavior
    print("\n" + "="*70)
    print("INTERSECTION BEHAVIOR TEST")
    print("="*70)
    
    intersection_pos = Position(3, 3)
    print(f"\nTesting all movements from intersection at ({intersection_pos.x}, {intersection_pos.y}):")
    
    for orientation in Orientation:
        print(f"\n  Facing {orientation.value}:")
        node = graph.get_node(intersection_pos.x, intersection_pos.y)
        
        if node.id in graph.path_lookup and orientation in graph.path_lookup[node.id]:
            for movement in MovementRule:
                if movement in graph.path_lookup[node.id][orientation]:
                    path_info = graph.path_lookup[node.id][orientation][movement]
                    status = "VALID" if path_info.valid else "INVALID"
                    exit_info = f"exit at ({path_info.exit_point.x}, {path_info.exit_point.y})" if path_info.valid else "no exit"
                    print(f"    {movement.value:15} -> {status:7} ({exit_info})")

if __name__ == "__main__":
    test_path_calculator()