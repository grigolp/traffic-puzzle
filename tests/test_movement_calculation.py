import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from app.core.graph_builder import GraphBuilder
from app.core.path_calculator import PathCalculator


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
                print("E ", end="")  # Exit
            else:
                print("? ", end="")  # Unknown
        print()

def test_movement_calculations():
    """Test movement calculations with 2-lane roads"""
    
    # 10x10 grid with 2-lane roads
    # - Two horizontal 2-lane roads (rows 2-3 and rows 6-7)
    # - Two vertical 2-lane roads (columns 1-2 and columns 7-8)
    layout =  [
                # 0    1    2    3    4    5    6    7    8    9
                ["0", "|", "|", "0", "0", "0", "0", "|", "|", "0"],  # 0
                ["0", "|", "|", "0", "0", "0", "0", "|", "|", "0"],  # 1
                ["-", "+", "+", "-", "-", "-", "-", "+", "+", "-"],  # 2 - First 2-lane horizontal
                ["-", "+", "+", "-", "-", "-", "-", "+", "+", "-"],  # 3
                ["0", "|", "|", "0", "0", "0", "0", "|", "|", "0"],  # 4
                ["0", "|", "|", "0", "0", "0", "0", "|", "|", "0"],  # 5
                ["-", "+", "+", "-", "-", "-", "-", "+", "+", "-"],  # 6 - Second 2-lane horizontal
                ["-", "+", "+", "-", "-", "-", "-", "+", "+", "-"],  # 7
                ["0", "|", "|", "0", "0", "0", "0", "|", "|", "0"],  # 8
                ["0", "|", "|", "0", "0", "0", "0", "|", "|", "0"],  # 9
            ]
    height = len(layout)       
    width = len(layout[0])
    exit_row = ['E'] * (width + 2)
    layout_with_exits = [exit_row]
    for row in layout:
        layout_with_exits.append(['E'] + row + ['E'])
    layout_with_exits.append(exit_row)

    width_with_exits = width+2
    height_with_exits = height+2
    
    print_grid_visualization(layout_with_exits)
    # Build graph structure
    graph_builder = GraphBuilder()
    graph = graph_builder.build_graph(width_with_exits, height_with_exits, layout_with_exits)

    # Calculate all paths
    calculator = PathCalculator()
    calculator.calculate_all_paths(graph)
    from pprint import pprint
    pprint(graph.path_lookup['n_1_3'])


if __name__ == "__main__":
    test_movement_calculations()
    print("Movement calculations test completed successfully.")