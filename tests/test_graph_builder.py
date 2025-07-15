import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

app_dir = project_root / 'app'
sys.path.append(str(app_dir))

from core.graph_builder import GraphBuilder
from models.graph import Position
from models.enums import Orientation, Direction, CellType

def test_graph_building():
    """Test graph building and neighbor relationships"""
    
    # Simple test grid
    layout = [
        ["0", "-", "-", "+", "-", "-", "0"],  # Row 0
        ["0", "0", "0", "|", "0", "0", "0"],  # Row 1
        ["-", "-", "-", "+", "-", "-", "-"],  # Row 2
        ["0", "0", "0", "|", "0", "0", "0"],  # Row 3
        ["0", "0", "0", "|", "0", "0", "0"],  # Row 4
    ]
    
    builder = GraphBuilder()
    graph = builder.build_graph(7, 5, layout)
    
    print("=== GRAPH BUILDER TEST ===\n")
    print("Grid Layout:")
    for y, row in enumerate(layout):
        print(f"Row {y}: {' '.join(row)}")
    
    print(f"\nTotal nodes: {len(graph.nodes)}")
    print(f"Road nodes: {sum(1 for n in graph.nodes.values() if n.cell_type.is_road)}")
    
    # Test specific nodes
    test_cases = [
        # Horizontal road cell
        {"pos": (1, 0), "type": "HORIZONTAL_ROAD"},
        {"pos": (2, 2), "type": "HORIZONTAL_ROAD"},
        
        # Vertical road cell
        {"pos": (3, 1), "type": "VERTICAL_ROAD"},
        {"pos": (3, 4), "type": "VERTICAL_ROAD"},
        
        # Intersection
        {"pos": (3, 0), "type": "INTERSECTION"},
        {"pos": (3, 2), "type": "INTERSECTION"},
        
        # Non-road
        {"pos": (0, 0), "type": "NON_PASSABLE"},
    ]
    
    print("\n" + "="*60)
    print("NODE TYPE VERIFICATION")
    print("="*60)
    
    for test in test_cases:
        x, y = test["pos"]
        node = graph.get_node(x, y)
        if node:
            print(f"\nPosition ({x}, {y}):")
            print(f"  Expected type: {test['type']}")
            print(f"  Actual type: {node.cell_type.name}")
            print(f"  Match: {'✓' if node.cell_type.name == test['type'] else '✗'}")
        else:
            print(f"\nPosition ({x}, {y}): Node not found!")
    
    print("\n" + "="*60)
    print("NEIGHBOR RELATIONSHIPS")
    print("="*60)
    
    # Test neighbor relationships for key nodes
    neighbor_tests = [
        {
            "pos": (1, 0),
            "name": "Horizontal road at (1,0)",
            "orientations": [Orientation.EAST, Orientation.WEST, Orientation.NORTH, Orientation.SOUTH]
        },
        {
            "pos": (3, 1),
            "name": "Vertical road at (3,1)",
            "orientations": [Orientation.NORTH, Orientation.SOUTH, Orientation.EAST, Orientation.WEST]
        },
        {
            "pos": (3, 0),
            "name": "Intersection at (3,0)",
            "orientations": [Orientation.NORTH, Orientation.SOUTH, Orientation.EAST, Orientation.WEST]
        },
        {
            "pos": (3, 2),
            "name": "Intersection at (3,2)",
            "orientations": [Orientation.NORTH, Orientation.SOUTH, Orientation.EAST, Orientation.WEST]
        }
    ]
    
    for test in neighbor_tests:
        x, y = test["pos"]
        node = graph.get_node(x, y)
        
        if not node:
            print(f"\n{test['name']}: Node not found!")
            continue
            
        print(f"\n{test['name']} (type: {node.cell_type.name}):")
        
        for orientation in test["orientations"]:
            print(f"\n  When facing {orientation.value}:")
            
            if orientation in node.neighbors:
                neighbors = node.neighbors[orientation]
                if neighbors:
                    for direction, neighbor_id in neighbors.items():
                        if neighbor_id:
                            # Extract coordinates from node ID
                            _, nx, ny = neighbor_id.split('_')
                            print(f"    {direction.value:8} -> ({nx}, {ny})")
                else:
                    print(f"    No neighbors defined")
            else:
                print(f"    Orientation not in neighbors dict")
    
    # Test edge cases
    print("\n" + "="*60)
    print("EDGE CASE TESTS")
    print("="*60)
    
    # Test exit positions
    print(f"\nExit positions ({len(graph.exit_positions)} total):")
    for pos in sorted(graph.exit_positions, key=lambda p: (p.y, p.x)):
        node = graph.get_node(pos.x, pos.y)
        print(f"  ({pos.x}, {pos.y}) - Type: {node.cell_type.name}")
    
    # Test that non-road cells have no neighbors
    print("\nNon-road cell neighbor check:")
    non_road = graph.get_node(0, 0)
    if non_road:
        has_neighbors = any(non_road.neighbors.values())
        print(f"  Non-road at (0,0) has neighbors: {has_neighbors} {'✗' if has_neighbors else '✓'}")
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    # Count total neighbor connections
    total_connections = 0
    for node in graph.nodes.values():
        if node.cell_type.is_road:
            for orientation in node.neighbors:
                for direction, neighbor_id in node.neighbors[orientation].items():
                    if neighbor_id:
                        total_connections += 1
    
    print(f"Total neighbor connections: {total_connections}")
    
    # Verify specific expected connections
    expected_connections = [
        ("Horizontal roads connect east-west", 
         lambda n: n.cell_type == CellType.HORIZONTAL_ROAD and 
         any(Direction.FORWARD in n.neighbors.get(o, {}) for o in [Orientation.EAST, Orientation.WEST])),
        
        ("Vertical roads connect north-south",
         lambda n: n.cell_type == CellType.VERTICAL_ROAD and
         any(Direction.FORWARD in n.neighbors.get(o, {}) for o in [Orientation.NORTH, Orientation.SOUTH])),
        
        ("Intersections have multiple connections",
         lambda n: n.cell_type == CellType.INTERSECTION and
         sum(1 for o in n.neighbors.values() for d in o.values() if d) > 2)
    ]
    
    print("\nConnection validation:")
    for desc, check in expected_connections:
        matching_nodes = sum(1 for n in graph.nodes.values() if n.cell_type.is_road and check(n))
        total_type = sum(1 for n in graph.nodes.values() if n.cell_type.is_road)
        print(f"  {desc}: {matching_nodes} nodes {'✓' if matching_nodes > 0 else '✗'}")

if __name__ == "__main__":
    test_graph_building()