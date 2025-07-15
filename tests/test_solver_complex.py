import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

app_dir = project_root / 'app'
sys.path.append(str(app_dir))


from services.level_loader import LevelLoader # type: ignore
from services.validator import LevelValidator # type: ignore
from core.solver import Solver # type: ignore
from models.graph import Position # type: ignore
from models.enums import Orientation, MovementRule # type: ignore
from models.vehicles import Vehicle, VehicleType # type: ignore
from models.obstacles import Boulder # type: ignore
from models.game_state import GameState # type: ignore


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


def visualize_solution_state(layout, vehicles, obstacles, exited_vehicles=None):
    """Visualize current state with vehicles and obstacles"""
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
    
    # Mark obstacles
    for pos, obstacle in obstacles.items():
        if 0 <= pos.y < len(viz_grid) and 0 <= pos.x < len(viz_grid[0]):
            viz_grid[pos.y][pos.x] = "●"  # Boulder
    
    # Mark vehicles
    for vehicle_id, vehicle in vehicles.items():
        for i, pos in enumerate(vehicle.get_occupied_cells()):
            if 0 <= pos.y < len(viz_grid) and 0 <= pos.x < len(viz_grid[0]):
                if i == 0:  # Head
                    viz_grid[pos.y][pos.x] = vehicle_id[0]  # First letter (C, T, B)
                else:  # Body (for trucks)
                    viz_grid[pos.y][pos.x] = vehicle_id[0].lower()
    
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
    
    print("\nLegend: C/c=Car, T/t=Truck, B=Bulldozer, ●=Boulder, ◊=Exit")
    if exited_vehicles:
        print(f"Exited: {', '.join(exited_vehicles)}")

def test_actual_level_116():
    
    print("\n" + "="*70)
    print("TEST LV. 116: MULTIPLE VEHICLES and BOLDER")
    print("="*70)
    
    level_data =     {
    "levelId": "level_116",
    "metadata": {
        "difficulty": "___",
        "targetMoves": 28
    },
    "grid": {
        "dimensions": {"width": 10, "height": 20},
        "layout": [
            ["0","|","0","0","0","0","0","0","|","0"],
            ["0","|","0","0","0","0","0","0","|","0"],
            ["-","+","-","-","-","-","-","-","+","-"],
            ["0","|","0","0","0","0","0","0","|","0"],
            ["0","|","0","0","0","0","0","0","|","0"],
            ["0","|","0","0","0","0","0","0","|","0"],
            ["0","|","0","0","0","0","0","0","|","0"],
            ["0","|","0","0","0","0","0","0","|","0"],
            ["0","|","0","0","0","0","0","0","|","0"],
            ["-","+","-","-","-","-","-","-","+","-"],
            ["0","|","0","0","0","0","0","0","|","0"],
            ["0","|","0","0","0","0","0","0","|","0"],
            ["0","|","0","0","0","0","0","0","|","0"],
            ["-","+","-","-","-","-","-","-","+","-"],
            ["0","|","0","0","0","0","0","0","|","0"],
            ["0","|","0","0","0","0","0","0","|","0"],
            ["0","|","0","0","0","0","0","0","|","0"],
            ["-","+","-","-","-","-","-","-","+","-"],
            ["0","|","0","0","0","0","0","0","|","0"],
            ["0","|","0","0","0","0","0","0","|","0"]
        ]
    },
    "vehicles": [
        {
            "id": "C01",
            "type": "CAR",
            "length": 2,
            "position": {"x": 2, "y": 2},
            "orientation": "WEST",
            "movementRule": "RIGHT"
        },
        {
            "id": "C02",
            "type": "CAR",
            "length": 2,
            "position": {"x": 7, "y": 2},
            "orientation": "EAST",
            "movementRule": "LEFT"
        },
        {
            "id": "C03",
            "type": "CAR",
            "length": 2,
            "position": {"x": 1, "y": 3},
            "orientation": "NORTH",
            "movementRule": "RIGHT_U_TURN"
        },
        {
            "id": "C04",
            "type": "CAR",
            "length": 2,
            "position": {"x": 8, "y": 3},
            "orientation": "NORTH",
            "movementRule": "LEFT"
        },
        {
            "id": "B01",
            "type": "BULLDOZER",
            "length": 2,
            "position": {"x": 1, "y": 8},
            "orientation": "SOUTH",
            "movementRule": "STRAIGHT"
        },
        {
            "id": "C05",
            "type": "CAR",
            "length": 2,
            "position": {"x": 8, "y": 8},
            "orientation": "SOUTH",
            "movementRule": "STRAIGHT"
        },
        {
            "id": "C06",
            "type": "CAR",
            "length": 2,
            "position": {"x": 2, "y": 9},
            "orientation": "WEST",
            "movementRule": "LEFT"
        },
        {
            "id": "C07",
            "type": "CAR",
            "length": 2,
            "position": {"x": 7, "y": 9},
            "orientation": "WEST",
            "movementRule": "STRAIGHT"
        },
        {
            "id": "C08",
            "type": "CAR",
            "length": 2,
            "position": {"x": 1, "y": 12},
            "orientation": "SOUTH",
            "movementRule": "STRAIGHT"
        },
        {
            "id": "C09",
            "type": "CAR",
            "length": 2,
            "position": {"x": 8, "y": 10},
            "orientation": "NORTH",
            "movementRule": "LEFT"
        },
        {
            "id": "T01",
            "type": "TRUCK",
            "length": 3,
            "position": {"x": 1, "y": 13},
            "orientation": "WEST",
            "movementRule": "STRAIGHT"
        },
        {
            "id": "C10",
            "type": "CAR",
            "length": 2,
            "position": {"x": 6, "y": 13},
            "orientation": "EAST",
            "movementRule": "STRAIGHT"
        },
        {
            "id": "C11",
            "type": "CAR",
            "length": 2,
            "position": {"x": 1, "y": 14},
            "orientation": "NORTH",
            "movementRule": "RIGHT"
        },
        {
            "id": "C12",
            "type": "CAR",
            "length": 2,
            "position": {"x": 8, "y": 14},
            "orientation": "NORTH",
            "movementRule": "LEFT_U_TURN"
        },
        {
            "id": "C13",
            "type": "CAR",
            "length": 2,
            "position": {"x": 2, "y": 17},
            "orientation": "WEST",
            "movementRule": "LEFT"
        },
        {
            "id": "C14",
            "type": "CAR",
            "length": 2,
            "position": {"x": 6, "y": 17},
            "orientation": "WEST",
            "movementRule": "RIGHT"
        },
        {
            "id": "C15",
            "type": "CAR",
            "length": 2,
            "position": {"x": 1, "y": 18},
            "orientation": "SOUTH",
            "movementRule": "STRAIGHT"
        },
        {
            "id": "C16",
            "type": "CAR",
            "length": 2,
            "position": {"x": 8, "y": 18},
            "orientation": "SOUTH",
            "movementRule": "STRAIGHT"
        }
    ],
    "obstacles": [
        {
            "id": "OB1",
            "type": "BOULDER",
            "position": {"x": 1, "y": 9}
        }
    ]
}
    run_complex_test(level_data)


def test_complex_scenario_1():
    """Test: Multiple vehicles with crossing paths"""
    print("\n" + "="*70)
    print("TEST 1: MULTIPLE VEHICLES WITH CROSSING PATHS")
    print("="*70)
    
    level_data = {
        "levelId": "complex_001",
        "metadata": {"difficulty": "hard", "targetMoves": 4},
        "grid": {
            "dimensions": {"width": 11, "height": 10},
            "layout": [
                ["0", "|", "|", "0", "0", "0", "0", "|", "|", "|", "0"],
                ["0", "|", "|", "0", "0", "0", "0", "|", "|", "|", "0"],
                ["-", "+", "+", "-", "-", "-", "-", "+", "+", "+", "-"],
                ["-", "+", "+", "-", "-", "-", "-", "+", "+", "+", "-"],
                ["0", "|", "|", "0", "0", "0", "0", "|", "|", "|", "0"],
                ["0", "|", "|", "0", "0", "0", "0", "|", "|", "|", "0"],
                ["-", "+", "+", "-", "-", "-", "-", "+", "+", "+", "-"],
                ["-", "+", "+", "-", "-", "-", "-", "+", "+", "+", "-"],
                ["-", "+", "+", "-", "-", "-", "-", "+", "+", "+", "-"],
                ["0", "|", "|", "0", "0", "0", "0", "|", "|", "|", "0"],
            ]
        },
        "vehicles": [
            {
                "id": "C01",
                "type": "CAR",
                "length": 1,
                "position": {"x": 0, "y": 2},
                "orientation": "EAST",
                "movementRule": "STRAIGHT"
            },
            {
                "id": "C02",
                "type": "CAR",
                "length": 1,
                "position": {"x": 5, "y": 3},
                "orientation": "WEST",
                "movementRule": "LEFT"
            },
            {
                "id": "T01",
                "type": "TRUCK",
                "length": 2,
                "position": {"x": 8, "y": 0},
                "orientation": "SOUTH",
                "movementRule": "RIGHT"
            },
            {
                "id": "C03",
                "type": "CAR",
                "length": 1,
                "position": {"x": 1, "y": 9},
                "orientation": "NORTH",
                "movementRule": "STRAIGHT"
            }
        ],
        "obstacles": []
    }
    
    run_complex_test(level_data)


def test_complex_scenario_2():
    """Test: Bulldozer clearing path for other vehicles"""
    print("\n" + "="*70)
    print("TEST 2: BULLDOZER CLEARING PATH")
    print("="*70)
    
    level_data = {
        "levelId": "complex_002",
        "metadata": {"difficulty": "hard", "targetMoves": 3},
        "grid": {
            "dimensions": {"width": 11, "height": 10},
            "layout": [
                ["0", "|", "|", "0", "0", "0", "0", "|", "|", "|", "0"],
                ["0", "|", "|", "0", "0", "0", "0", "|", "|", "|", "0"],
                ["-", "+", "+", "-", "-", "-", "-", "+", "+", "+", "-"],
                ["-", "+", "+", "-", "-", "-", "-", "+", "+", "+", "-"],
                ["0", "|", "|", "0", "0", "0", "0", "|", "|", "|", "0"],
                ["0", "|", "|", "0", "0", "0", "0", "|", "|", "|", "0"],
                ["-", "+", "+", "-", "-", "-", "-", "+", "+", "+", "-"],
                ["-", "+", "+", "-", "-", "-", "-", "+", "+", "+", "-"],
                ["-", "+", "+", "-", "-", "-", "-", "+", "+", "+", "-"],
                ["0", "|", "|", "0", "0", "0", "0", "|", "|", "|", "0"],
            ]
        },
        "vehicles": [
            {
                "id": "B01",
                "type": "BULLDOZER",
                "length": 1,
                "position": {"x": 0, "y": 2},
                "orientation": "EAST",
                "movementRule": "STRAIGHT"
            },
            {
                "id": "C01",
                "type": "CAR",
                "length": 1,
                "position": {"x": 0, "y": 3},
                "orientation": "EAST",
                "movementRule": "STRAIGHT"
            },
            {
                "id": "C02",
                "type": "CAR",
                "length": 1,
                "position": {"x": 8, "y": 5},
                "orientation": "NORTH",
                "movementRule": "LEFT"
            }
        ],
        "obstacles": [
            {"id": "OB1", "type": "BOULDER", "position": {"x": 5, "y": 2}},
            {"id": "OB2", "type": "BOULDER", "position": {"x": 5, "y": 3}},
            {"id": "OB3", "type": "BOULDER", "position": {"x": 2, "y": 7}}
        ]
    }
    
    run_complex_test(level_data)


def test_complex_scenario_3():
    """Test: Deadlock scenario with partial solution"""
    print("\n" + "="*70)
    print("TEST 3: DEADLOCK WITH PARTIAL SOLUTION")
    print("="*70)
    
    level_data = {
        "levelId": "complex_003",
        "metadata": {"difficulty": "hard", "targetMoves": 5},
        "grid": {
            "dimensions": {"width": 11, "height": 10},
            "layout": [
                ["0", "|", "|", "0", "0", "0", "0", "|", "|", "|", "0"],
                ["0", "|", "|", "0", "0", "0", "0", "|", "|", "|", "0"],
                ["-", "+", "+", "-", "-", "-", "-", "+", "+", "+", "-"],
                ["-", "+", "+", "-", "-", "-", "-", "+", "+", "+", "-"],
                ["0", "|", "|", "0", "0", "0", "0", "|", "|", "|", "0"],
                ["0", "|", "|", "0", "0", "0", "0", "|", "|", "|", "0"],
                ["-", "+", "+", "-", "-", "-", "-", "+", "+", "+", "-"],
                ["-", "+", "+", "-", "-", "-", "-", "+", "+", "+", "-"],
                ["-", "+", "+", "-", "-", "-", "-", "+", "+", "+", "-"],
                ["0", "|", "|", "0", "0", "0", "0", "|", "|", "|", "0"],
            ]
        },
        "vehicles": [
            {
                "id": "C01",
                "type": "CAR",
                "length": 1,
                "position": {"x": 2, "y": 2},
                "orientation": "EAST",
                "movementRule": "STRAIGHT"
            },
            {
                "id": "C02",
                "type": "CAR",
                "length": 1,
                "position": {"x": 3, "y": 3},
                "orientation": "WEST",
                "movementRule": "STRAIGHT"
            },
            {
                "id": "T01",
                "type": "TRUCK",
                "length": 2,
                "position": {"x": 7, "y": 2},
                "orientation": "SOUTH",
                "movementRule": "LEFT"
            },
            {
                "id": "C03",
                "type": "CAR",
                "length": 1,
                "position": {"x": 8, "y": 8},
                "orientation": "NORTH",
                "movementRule": "STRAIGHT"
            }
        ],
        "obstacles": [
            {"id": "OB1", "type": "BOULDER", "position": {"x": 1, "y": 3}},
            {"id": "OB2", "type": "BOULDER", "position": {"x": 4, "y": 2}}
        ]
    }
    
    run_complex_test(level_data)


def test_complex_scenario_4():
    """Test: U-turn movements with obstacles"""
    print("\n" + "="*70)
    print("TEST 4: U-TURN MOVEMENTS WITH OBSTACLES")
    print("="*70)
    
    level_data = {
        "levelId": "complex_004",
        "metadata": {"difficulty": "hard", "targetMoves": 3},
        "grid": {
            "dimensions": {"width": 11, "height": 10},
            "layout": [
                ["0", "|", "|", "0", "0", "0", "0", "|", "|", "|", "0"],
                ["0", "|", "|", "0", "0", "0", "0", "|", "|", "|", "0"],
                ["-", "+", "+", "-", "-", "-", "-", "+", "+", "+", "-"],
                ["-", "+", "+", "-", "-", "-", "-", "+", "+", "+", "-"],
                ["0", "|", "|", "0", "0", "0", "0", "|", "|", "|", "0"],
                ["0", "|", "|", "0", "0", "0", "0", "|", "|", "|", "0"],
                ["-", "+", "+", "-", "-", "-", "-", "+", "+", "+", "-"],
                ["-", "+", "+", "-", "-", "-", "-", "+", "+", "+", "-"],
                ["-", "+", "+", "-", "-", "-", "-", "+", "+", "+", "-"],
                ["0", "|", "|", "0", "0", "0", "0", "|", "|", "|", "0"],
            ]
        },
        "vehicles": [
            {
                "id": "C01",
                "type": "CAR",
                "length": 1,
                "position": {"x": 5, "y": 2},
                "orientation": "EAST",
                "movementRule": "LEFT_U_TURN"
            },
            {
                "id": "T01",
                "type": "TRUCK",
                "length": 2,
                "position": {"x": 3, "y": 7},
                "orientation": "WEST",
                "movementRule": "RIGHT_U_TURN"
            },
            {
                "id": "C02",
                "type": "CAR",
                "length": 1,
                "position": {"x": 8, "y": 8},
                "orientation": "WEST",
                "movementRule": "STRAIGHT"
            }
        ],
        "obstacles": [
            {"id": "OB1", "type": "BOULDER", "position": {"x": 9, "y": 2}},
            {"id": "OB2", "type": "BOULDER", "position": {"x": 1, "y": 7}}
        ]
    }
    
    run_complex_test(level_data)


def test_complex_scenario_5():
    """Test: Multi-lane traffic jam"""
    print("\n" + "="*70)
    print("TEST 5: MULTI-LANE TRAFFIC JAM")
    print("="*70)
    
    level_data = {
        "levelId": "complex_005",
        "metadata": {"difficulty": "hard", "targetMoves": 6},
        "grid": {
            "dimensions": {"width": 11, "height": 10},
            "layout": [
                ["0", "|", "|", "0", "0", "0", "0", "|", "|", "|", "0"],
                ["0", "|", "|", "0", "0", "0", "0", "|", "|", "|", "0"],
                ["-", "+", "+", "-", "-", "-", "-", "+", "+", "+", "-"],
                ["-", "+", "+", "-", "-", "-", "-", "+", "+", "+", "-"],
                ["0", "|", "|", "0", "0", "0", "0", "|", "|", "|", "0"],
                ["0", "|", "|", "0", "0", "0", "0", "|", "|", "|", "0"],
                ["-", "+", "+", "-", "-", "-", "-", "+", "+", "+", "-"],
                ["-", "+", "+", "-", "-", "-", "-", "+", "+", "+", "-"],
                ["-", "+", "+", "-", "-", "-", "-", "+", "+", "+", "-"],
                ["0", "|", "|", "0", "0", "0", "0", "|", "|", "|", "0"],
            ]
        },
        "vehicles": [
            # 3-lane horizontal road traffic
            {
                "id": "C01",
                "type": "CAR",
                "length": 1,
                "position": {"x": 0, "y": 6},
                "orientation": "EAST",
                "movementRule": "STRAIGHT"
            },
            {
                "id": "C02",
                "type": "CAR",
                "length": 1,
                "position": {"x": 1, "y": 7},
                "orientation": "EAST",
                "movementRule": "STRAIGHT"
            },
            {
                "id": "T01",
                "type": "TRUCK",
                "length": 2,
                "position": {"x": 3, "y": 8},
                "orientation": "EAST",
                "movementRule": "STRAIGHT"
            },
            # Blocking vehicles
            {
                "id": "C03",
                "type": "CAR",
                "length": 1,
                "position": {"x": 8, "y": 6},
                "orientation": "WEST",
                "movementRule": "STRAIGHT"
            },
            {
                "id": "C04",
                "type": "CAR",
                "length": 1,
                "position": {"x": 7, "y": 7},
                "orientation": "WEST",
                "movementRule": "STRAIGHT"
            },
            {
                "id": "B01",
                "type": "BULLDOZER",
                "length": 1,
                "position": {"x": 8, "y": 1},
                "orientation": "SOUTH",
                "movementRule": "STRAIGHT"
            }
        ],
        "obstacles": [
            {"id": "OB1", "type": "BOULDER", "position": {"x": 5, "y": 6}},
            {"id": "OB2", "type": "BOULDER", "position": {"x": 5, "y": 7}}
        ]
    }
    
    run_complex_test(level_data)


def run_complex_test(level_data):
    """Run a complex test case with visualization"""
    # Load and build
    loader = LevelLoader()
    graph, initial_state = loader.load_level(level_data)
    
    # Get layout with exits for visualization
    grid_data = level_data["grid"]
    original_layout = grid_data["layout"]
    layout_with_exits = loader._add_exit_border(original_layout)
    
    print(f"\nLevel: {level_data['levelId']}")
    print(f"Target moves: {level_data['metadata']['targetMoves']}")
    
    # Show initial state
    print("\nINITIAL STATE:")
    print_grid_visualization(layout_with_exits)
    print("\nVehicles and obstacles overlay:")
    visualize_solution_state(layout_with_exits, initial_state.active_vehicles, initial_state.obstacles)
    
    # Validate
    validator = LevelValidator()
    # is_valid, errors = validator.validate_initial_state(graph, initial_state)
    
    # if not is_valid:
    #     print("\nVALIDATION ERRORS:")
    #     for error in errors:
    #         print(f"  - {error}")
    #     return
    
    # Solve
    solver = Solver(graph)
    result = solver.solve(initial_state)
    
    print("\n" + "-"*70)
    print("SOLUTION RESULT:")
    print(f"Solvable: {result.solvable}")
    
    if result.solvable:
        print(f"Solution: {' → '.join(result.solution)}")
        print(f"Total moves: {result.total_moves}")
        
        # Show final state
        print("\nFINAL STATE (all vehicles exited):")
        final_state = initial_state
        for vehicle_id in result.solution:
            # Simulate the moves to show final state
            vehicle = final_state.active_vehicles[vehicle_id]
            node = graph.get_node(vehicle.position.x, vehicle.position.y)
            path_info = graph.path_lookup[node.id][vehicle.orientation][vehicle.movement_rule]
            final_state = final_state.apply_vehicle_exit(vehicle_id, path_info.exit_path, graph)
        
        visualize_solution_state(layout_with_exits, final_state.active_vehicles, 
                               final_state.obstacles, result.solution)
    else:
        print(f"Partial solution: {' → '.join(result.solution) if result.solution else 'None'}")
        print(f"Moves until block: {result.total_moves}")
        print(f"Reason: {result.reason}")
        
        # Show state after partial solution
        if result.solution:
            print("\nSTATE AFTER PARTIAL SOLUTION:")
            partial_state = initial_state
            for vehicle_id in result.solution:
                vehicle = partial_state.active_vehicles[vehicle_id]
                node = graph.get_node(vehicle.position.x, vehicle.position.y)
                path_info = graph.path_lookup[node.id][vehicle.orientation][vehicle.movement_rule]
                partial_state = partial_state.apply_vehicle_exit(vehicle_id, path_info.exit_path, graph)
            
            visualize_solution_state(layout_with_exits, partial_state.active_vehicles,
                                   partial_state.obstacles, result.solution)
        
        # Show blocking details
        if result.blocking_details:
            print("\nBLOCKING ANALYSIS:")
            for detail in result.blocking_details:
                print(f"  - {detail['blocked']} blocked by {detail['blockedBy']}")
                print(f"    Reason: {detail['reason']}")


if __name__ == "__main__":
    test_actual_level_116()
    # test_complex_scenario_1()  # Multiple vehicles
    # test_complex_scenario_2()  # Bulldozer clearing
    # test_complex_scenario_3()  # Deadlock
    # test_complex_scenario_4()  # U-turns
    # test_complex_scenario_5()  # Traffic jam