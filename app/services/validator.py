from typing import List, Tuple, Optional, Set
from ..models.graph import RoadGraph, Position
from ..models.game_state import GameState
from ..models.vehicles import Vehicle
from ..models.enums import CellType


class LevelValidator:
    """Validates level configurations"""
    
    def validate_initial_state(self, graph: RoadGraph, state: GameState) -> Tuple[bool, List[str]]:
        """
        Validate the initial state of a level.
        Returns (is_valid, list_of_errors)
        """
        errors = []
        
        # 1. Check all vehicles are on road cells
        for vehicle in state.active_vehicles.values():
            errors.extend(self._validate_vehicle_placement(vehicle, graph))
        
        # 2. Check for vehicle overlaps
        errors.extend(self._check_vehicle_overlaps(state))
        
        # 3. Check obstacles are on road cells
        for obstacle in state.obstacles.values():
            errors.extend(self._validate_obstacle_placement(obstacle, graph))
        
        # 4. Check each vehicle can theoretically reach an exit
        for vehicle in state.active_vehicles.values():
            errors.extend(self._validate_vehicle_path_exists(vehicle, graph))
        
        return len(errors) == 0, errors
    
    def _validate_vehicle_placement(self, vehicle: Vehicle, graph: RoadGraph) -> List[str]:
        """Check if vehicle is placed on valid road cells"""
        errors = []
        
        for position in vehicle.get_occupied_cells():
            node = graph.get_node(position.x, position.y)
            
            if not node:
                errors.append(
                    f"Vehicle {vehicle.id} occupies non-existent position ({position.x}, {position.y})"
                )
            elif not node.cell_type.is_road or node.cell_type.is_exit:
                errors.append(
                    f"Vehicle {vehicle.id} at ({position.x}, {position.y}) is not on a road cell"
                )
            
            # Check orientation compatibility
            if node and node.cell_type.is_road and not node.cell_type.is_exit:
                if not self._is_orientation_valid_for_cell(vehicle.orientation, node.cell_type):
                    errors.append(
                        f"Vehicle {vehicle.id} orientation {vehicle.orientation.value} "
                        f"incompatible with {node.cell_type.name} at ({position.x}, {position.y})"
                    )
        
        return errors
    
    def _is_orientation_valid_for_cell(self, orientation, cell_type: CellType) -> bool:
        """Check if orientation is valid for cell type"""
        if cell_type == CellType.INTERSECTION:
            return True  # All orientations valid at intersections
        elif cell_type == CellType.HORIZONTAL_ROAD:
            return orientation.value in ["EAST", "WEST"]
        elif cell_type == CellType.VERTICAL_ROAD:
            return orientation.value in ["NORTH", "SOUTH"]
        return False
    
    def _check_vehicle_overlaps(self, state: GameState) -> List[str]:
        """Check for overlapping vehicles"""
        errors = []
        position_map = {}
        
        for vehicle in state.active_vehicles.values():
            for position in vehicle.get_occupied_cells():
                if position in position_map:
                    errors.append(
                        f"Vehicles {position_map[position]} and {vehicle.id} "
                        f"overlap at position ({position.x}, {position.y})"
                    )
                else:
                    position_map[position] = vehicle.id
        
        return errors
    
    def _validate_obstacle_placement(self, obstacle, graph: RoadGraph) -> List[str]:
        """Check if obstacle is placed on valid road cell"""
        errors = []
        position = obstacle.position
        node = graph.get_node(position.x, position.y)
        
        if not node:
            errors.append(
                f"Obstacle {obstacle.id} at non-existent position ({position.x}, {position.y})"
            )
        elif not node.cell_type.is_road or node.cell_type.is_exit:
            errors.append(
                f"Obstacle {obstacle.id} at ({position.x}, {position.y}) is not on a road cell"
            )
        
        return errors
    
    def _validate_vehicle_path_exists(self, vehicle: Vehicle, graph: RoadGraph) -> List[str]:
        """Check if vehicle has at least one theoretical path to exit"""
        errors = []
        
        # Get the node at vehicle's head position
        node = graph.get_node(vehicle.position.x, vehicle.position.y)
        if not node:
            return errors  # Already caught by placement validation
        
        # Check if path exists in lookup
        if node.id not in graph.path_lookup:
            errors.append(f"No paths calculated for vehicle {vehicle.id} at ({vehicle.position.x}, {vehicle.position.y})")
            return errors
        
        if vehicle.orientation not in graph.path_lookup[node.id]:
            errors.append(f"No paths for orientation {vehicle.orientation.value} for vehicle {vehicle.id}")
            return errors
        
        if vehicle.movement_rule not in graph.path_lookup[node.id][vehicle.orientation]:
            errors.append(
                f"No path for movement rule {vehicle.movement_rule.value} "
                f"for vehicle {vehicle.id} facing {vehicle.orientation.value}"
            )
            return errors
        
        # Check if the path is theoretically valid
        path_info = graph.path_lookup[node.id][vehicle.orientation][vehicle.movement_rule]
        if not path_info.valid:
            errors.append(
                f"Vehicle {vehicle.id} has no valid exit path with "
                f"movement rule {vehicle.movement_rule.value} from current position"
            )
        
        return errors