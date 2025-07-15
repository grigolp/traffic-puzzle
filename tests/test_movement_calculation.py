import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

app_dir = project_root / 'app'
sys.path.append(str(app_dir))

from core.graph_builder import GraphBuilder # type: ignore
from core.path_calculator import PathCalculator # type: ignore
from models.graph import Position # type: ignore
from models.enums import Orientation, MovementRule # type: ignore

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
            elif cell == 'E':
                print("◊ ", end="")  # Exit
            else:
                print("? ", end="")  # Unknown
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
            elif cell == "E":
                viz_row.append("◊")
            else:
                viz_row.append("?")
        viz_grid.append(viz_row)
    
    # Mark start position
    viz_grid[start_pos.y][start_pos.x] = "S"
    
    # Mark path
    for i, node_id in enumerate(path_nodes):
        _, x, y = node_id.split('_')
        x, y = int(x), int(y)
        if (x, y) != (start_pos.x, start_pos.y):
            if viz_grid[y][x] == "◊":
                viz_grid[y][x] = "X"  # Exit reached
            else:
                viz_grid[y][x] = str((i) % 10)
    
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
    print("\nLegend: S=Start, X=Exit reached, ◊=Exit not used, Numbers=Path order")

def add_exits_to_layout(layout):
    """Add exit nodes around the perimeter of the layout"""
    height = len(layout)       
    width = len(layout[0])
    exit_row = ['E'] * (width + 2)
    layout_with_exits = [exit_row]
    for row in layout:
        layout_with_exits.append(['E'] + row + ['E'])
    layout_with_exits.append(exit_row)
    return layout_with_exits, width + 2, height + 2

def test_path_calculator_with_multi_lane_roads():
    """Test path calculation with 2-lane and 3-lane roads"""
    
    # Modified layout with both 2-lane and 3-lane roads
    layout = [
        # 0    1    2    3    4    5    6    7    8    9   10
        ["0", "|", "|", "0", "0", "0", "0", "|", "|", "|", "0"],  # 0 - 3-lane vertical on right
        ["0", "|", "|", "0", "0", "0", "0", "|", "|", "|", "0"],  # 1
        ["-", "+", "+", "-", "-", "-", "-", "+", "+", "+", "-"],  # 2 - 2-lane meets 3-lane
        ["-", "+", "+", "-", "-", "-", "-", "+", "+", "+", "-"],  # 3
        ["0", "|", "|", "0", "0", "0", "0", "|", "|", "|", "0"],  # 4
        ["0", "|", "|", "0", "0", "0", "0", "|", "|", "|", "0"],  # 5
        ["-", "+", "+", "-", "-", "-", "-", "+", "+", "+", "-"],  # 6 - 3-lane horizontal
        ["-", "+", "+", "-", "-", "-", "-", "+", "+", "+", "-"],  # 7
        ["-", "+", "+", "-", "-", "-", "-", "+", "+", "+", "-"],  # 8
        ["0", "|", "|", "0", "0", "0", "0", "|", "|", "|", "0"],  # 9
    ]
    
    # Add exits around the perimeter
    layout_with_exits, width, height = add_exits_to_layout(layout)
    
    print("=== PATH CALCULATOR TEST WITH 2-LANE AND 3-LANE ROADS ===\n")
    print(f"Grid dimensions (with exits): {width}x{height}")
    print("Road configuration:")
    print("- 2-lane vertical road: columns 1-2")
    print("- 3-lane vertical road: columns 7-9") 
    print("- 2-lane horizontal road: rows 2-3")
    print("- 3-lane horizontal road: rows 6-8")
    
    # Visualize the grid with exits
    print_grid_visualization(layout_with_exits)
    
    # Build graph and calculate paths
    graph_builder = GraphBuilder()
    graph = graph_builder.build_graph(width, height, layout_with_exits)
    
    calculator = PathCalculator()
    calculator.calculate_all_paths(graph)
    
    print(f"\nTotal nodes: {len(graph.nodes)}")
    print(f"Road nodes: {sum(1 for n in graph.nodes.values() if n.cell_type.is_road and not n.cell_type.is_exit)}")
    print(f"Exit nodes: {sum(1 for n in graph.nodes.values() if n.cell_type.is_exit)}")
    
    # Test cases focusing on multi-lane behavior
    test_cases = [
        {
            "name": "2-lane road straight movement",
            "position": Position(5, 3),  # Adjusted for exit border
            "orientation": Orientation.EAST,
            "movement": MovementRule.STRAIGHT,
            "expected": "Should continue east through 2-lane/3-lane intersection"
        },
        {
            "name": "3-lane road middle lane straight",
            "position": Position(9, 5),  # Middle lane of 3-lane vertical road
            "orientation": Orientation.NORTH,
            "movement": MovementRule.STRAIGHT,
            "expected": "Should go straight north to exit"
        },
        {
            "name": "LEFT turn from 2-lane to 3-lane road",
            "position": Position(5, 3),
            "orientation": Orientation.EAST,
            "movement": MovementRule.LEFT,
            "expected": "Should turn north into 3-lane road"
        },
        {
            "name": "Test RIGHT turns on intersections",
            "position": Position(8, 4),
            "orientation": Orientation.NORTH,
            "movement": MovementRule.RIGHT,
            "expected": "Should go straight"
        },
        {
            "name": "RIGHT turn from 3-lane to 2-lane road",
            "position": Position(8, 5),
            "orientation": Orientation.NORTH,
            "movement": MovementRule.RIGHT,
            "expected": "Should turn east into 2-lane road"
        },
        {
            "name": "RIGHT turn from 3-lane to 2-lane road",
            "position": Position(8, 6),
            "orientation": Orientation.NORTH,
            "movement": MovementRule.RIGHT,
            "expected": "Should turn east into 2-lane road"
        },
        {
            "name": "LEFT_U_TURN on 3-lane road",
            "position": Position(5, 7),  # Middle row of 3-lane horizontal
            "orientation": Orientation.EAST,
            "movement": MovementRule.LEFT_U_TURN,
            "expected": "Should make two left turns using 3-lane width"
        },
        {
            "name": "Parallel movement on 3-lane road (top lane)",
            "position": Position(4, 7),  # Top lane of 3-lane horizontal
            "orientation": Orientation.WEST,
            "movement": MovementRule.STRAIGHT,
            "expected": "Should go straight west to exit"
        },
        {
            "name": "Parallel movement on 3-lane road (bottom lane)",
            "position": Position(4, 9),  # Bottom lane of 3-lane horizontal
            "orientation": Orientation.WEST,
            "movement": MovementRule.STRAIGHT,
            "expected": "Should go straight west to exit"
        },
        {
            "name": "Complex turn through multiple intersections",
            "position": Position(2, 3),
            "orientation": Orientation.EAST,
            "movement": MovementRule.RIGHT_U_TURN,
            "expected": "Should navigate through 2-lane intersection for U-turn"
        },
        {
            "name": "Complex turn through multiple intersections",
            "position": Position(2, 3),
            "orientation": Orientation.EAST,
            "movement": MovementRule.LEFT_U_TURN,
            "expected": "Should navigate through 2-lane intersection for U-turn"
        }
    ]
    
    print("\n" + "="*70)
    print("PATH CALCULATION TESTS")
    print("="*70)
    
    for test in test_cases:
        print(f"\nTest: {test['name']}")
        print(f"Start: ({test['position'].x}, {test['position'].y}) facing {test['orientation'].value}")
        print(f"Movement: {test['movement'].value}")
        print(f"Expected: {test['expected']}")
        print("-" * 50)
        
        # Get the node
        node = graph.get_node(test['position'].x, test['position'].y)
        if not node:
            print("ERROR: No node at this position!")
            continue
        
        if not node.cell_type.is_road:
            print(f"ERROR: Not a road cell! Type: {node.cell_type.name}")
            continue
        
        # Check if path was calculated
        if node.id not in graph.path_lookup:
            print("ERROR: No paths calculated for this node!")
            continue
        
        if test['orientation'] not in graph.path_lookup[node.id]:
            print("ERROR: No paths calculated for this orientation!")
            print(f"Available orientations: {list(graph.path_lookup[node.id].keys())}")
            continue
        
        if test['movement'] not in graph.path_lookup[node.id][test['orientation']]:
            print("ERROR: No path calculated for this movement rule!")
            print(f"Available movements: {list(graph.path_lookup[node.id][test['orientation']].keys())}")
            continue
        
        # Get the path
        path_info = graph.path_lookup[node.id][test['orientation']][test['movement']]
        
        print(f"Result: {'VALID' if path_info.valid else 'INVALID'}")
        
        if path_info.valid:
            print(f"Exit point: ({path_info.exit_point.x}, {path_info.exit_point.y})")
            print(f"Path length: {len(path_info.exit_path)} cells")
            
            # Show path summary
            if len(path_info.exit_path) > 10:
                path_summary = f"{' → '.join(path_info.exit_path[:3])} → ... → {' → '.join(path_info.exit_path[-3:])}"
            else:
                path_summary = ' → '.join(path_info.exit_path)
            print(f"Path: {path_summary}")
            
            # Visualize the path
            print("\nPath visualization:")
            visualize_path(layout_with_exits, test['position'], path_info.exit_path, path_info.exit_point)
        else:
            if path_info.exit_path:
                print(f"Partial path length: {len(path_info.exit_path)} cells")
                print("Path visualization (incomplete):")
                visualize_path(layout_with_exits, test['position'], path_info.exit_path)
            else:
                print("No path generated")
    
    # Test parallel lane independence on 3-lane road
    print("\n" + "="*70)
    print("3-LANE ROAD PARALLEL MOVEMENT TEST")
    print("="*70)
    
    print("\nTesting parallel lane independence on 3-lane road:")
    positions = [
        (Position(5, 7), "Top lane"),     # Row 6 (0-indexed) + 1 for exit border
        (Position(5, 8), "Middle lane"),  # Row 7 + 1
        (Position(5, 9), "Bottom lane")   # Row 8 + 1
    ]
    
    for pos, lane_name in positions:
        node = graph.get_node(pos.x, pos.y)
        if node and node.id in graph.path_lookup:
            if Orientation.EAST in graph.path_lookup[node.id]:
                if MovementRule.STRAIGHT in graph.path_lookup[node.id][Orientation.EAST]:
                    path_info = graph.path_lookup[node.id][Orientation.EAST][MovementRule.STRAIGHT]
                    print(f"{lane_name} at ({pos.x},{pos.y}): {'VALID' if path_info.valid else 'INVALID'}")
                    if path_info.valid:
                        print(f"  → Exits at ({path_info.exit_point.x}, {path_info.exit_point.y})")
    
    # Statistics
    print("\n" + "="*70)
    print("PATH STATISTICS SUMMARY")
    print("="*70)
    
    stats = {rule: {"valid": 0, "invalid": 0} for rule in MovementRule}
    
    for node_id, orientations in graph.path_lookup.items():
        node = graph.nodes[node_id]
        # Only count non-exit road nodes
        if node.cell_type.is_road and not node.cell_type.is_exit:
            for orientation, movements in orientations.items():
                for movement_rule, path_info in movements.items():
                    if path_info.valid:
                        stats[movement_rule]["valid"] += 1
                    else:
                        stats[movement_rule]["invalid"] += 1
    
    print("\nMovement success rates:")
    for movement_rule, counts in stats.items():
        total = counts["valid"] + counts["invalid"]
        if total > 0:
            success_rate = (counts["valid"] / total) * 100
            print(f"{movement_rule.value:15} - Valid: {counts['valid']:4}, "
                  f"Invalid: {counts['invalid']:4}, "
                  f"Success rate: {success_rate:5.1f}%")

if __name__ == "__main__":
    test_path_calculator_with_multi_lane_roads()