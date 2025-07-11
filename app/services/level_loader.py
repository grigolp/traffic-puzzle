from typing import Dict, List, Tuple
from ..models.graph import RoadGraph, Position
from ..models.vehicles import Vehicle
from ..models.obstacles import obstacle_from_dict
from ..models.game_state import GameState
from ..core.graph_builder import GraphBuilder
from ..core.path_calculator import PathCalculator


class LevelLoader:
    """Loads and processes level data from JSON format"""
    
    def __init__(self):
        self.graph_builder = GraphBuilder()
        self.path_calculator = PathCalculator()
    
    def load_level(self, level_data: dict) -> Tuple[RoadGraph, GameState]:
        """
        Load level from JSON data and return graph and initial state.
        Adds exit border around the grid as specified in the docs.
        """
        # Extract grid data
        grid_data = level_data["grid"]
        original_width = grid_data["dimensions"]["width"]
        original_height = grid_data["dimensions"]["height"]
        original_layout = grid_data["layout"]
        
        # Add exit border
        layout_with_exits = self._add_exit_border(original_layout)
        width = original_width + 2
        height = original_height + 2
        
        # Build graph
        graph = self.graph_builder.build_graph(width, height, layout_with_exits)
        
        # Calculate all paths
        self.path_calculator.calculate_all_paths(graph)
        
        # Load vehicles (adjust positions for border)
        vehicles = []
        for vehicle_data in level_data.get("vehicles", []):
            vehicle = Vehicle.from_dict(vehicle_data)
            # Adjust position for exit border
            vehicle.position = Position(
                vehicle.position.x + 1,
                vehicle.position.y + 1
            )
            vehicles.append(vehicle)
        
        # Load obstacles (adjust positions for border)
        obstacles = {}
        for obstacle_data in level_data.get("obstacles", []):
            obstacle = obstacle_from_dict(obstacle_data)
            # Adjust position for exit border
            adjusted_pos = Position(
                obstacle.position.x + 1,
                obstacle.position.y + 1
            )
            obstacle.position = adjusted_pos
            obstacles[adjusted_pos] = obstacle
        
        # Create initial game state
        initial_state = GameState(
            active_vehicles={v.id: v for v in vehicles},
            obstacles=obstacles,
            exited_vehicles=[]
        )
        
        return graph, initial_state
    
    def _add_exit_border(self, layout: List[List[str]]) -> List[List[str]]:
        """Add 'E' exit nodes around the entire grid"""
        height = len(layout)
        width = len(layout[0]) if height > 0 else 0
        
        # Create new layout with border
        bordered_layout = []
        
        # Top border
        bordered_layout.append(['E'] * (width + 2))
        
        # Original rows with side borders
        for row in layout:
            bordered_layout.append(['E'] + row + ['E'])
        
        # Bottom border
        bordered_layout.append(['E'] * (width + 2))
        
        return bordered_layout