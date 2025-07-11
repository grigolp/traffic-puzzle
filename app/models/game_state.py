from typing import Dict, List, Set, Optional, Tuple
from dataclasses import dataclass
from .vehicles import Vehicle
from .obstacles import Obstacle
from .graph import Position, RoadGraph


@dataclass
class GameState:
    """Represents the current state of all vehicles and obstacles"""
    active_vehicles: Dict[str, Vehicle]
    obstacles: Dict[Position, Obstacle]
    exited_vehicles: List[str]
    turn_number: int = 0
    
    def get_occupied_positions(self, exclude_vehicle_id: Optional[str] = None) -> Set[Position]:
        """Get all positions occupied by vehicles (optionally excluding one)"""
        occupied = set()
        for vehicle_id, vehicle in self.active_vehicles.items():
            if vehicle_id != exclude_vehicle_id:
                occupied.update(vehicle.get_occupied_cells())
        return occupied
    
    def get_obstacle_positions(self) -> Set[Position]:
        """Get all positions with obstacles"""
        return set(self.obstacles.keys())
    
    def is_position_blocked(self, position: Position, vehicle: Vehicle) -> Tuple[bool, Optional[str]]:
        """
        Check if a position is blocked for a given vehicle.
        Returns (is_blocked, reason)
        """
        # Check for other vehicles
        occupied = self.get_occupied_positions(exclude_vehicle_id=vehicle.id)
        if position in occupied:
            return True, "Position occupied by another vehicle"
        
        # Check for obstacles
        if position in self.obstacles:
            obstacle = self.obstacles[position]
            
            # Bulldozers can clear boulders
            if obstacle.type.value == "BOULDER" and vehicle.can_clear_obstacles():
                return False, None
            else:
                return True, f"{obstacle.type.value} blocks path"
        
        return False, None
    
    def is_path_clear(self, path_node_ids: List[str], vehicle: Vehicle, graph: RoadGraph) -> Tuple[bool, Optional[str]]:
        """
        Check if an entire path is clear for a vehicle.
        Returns (is_clear, blocking_reason)
        """
        for node_id in path_node_ids:
            position = graph.nodes[node_id].position     
            is_blocked, reason = self.is_position_blocked(position, vehicle)
            if is_blocked:
                return False, reason
        
        return True, None
    
    def apply_vehicle_exit(self, vehicle_id: str, path_node_ids: List[str], graph: RoadGraph) -> 'GameState':
        """
        Create a new state with the vehicle removed and any obstacles cleared.
        """
        if vehicle_id not in self.active_vehicles:
            raise ValueError(f"Vehicle {vehicle_id} not in active vehicles")
        
        vehicle = self.active_vehicles[vehicle_id]
        
        # Create new state
        new_vehicles = self.active_vehicles.copy()
        del new_vehicles[vehicle_id]
        
        new_obstacles = self.obstacles.copy()
        new_exited = self.exited_vehicles + [vehicle_id]
        
        # If bulldozer, remove boulders on path
        if vehicle.can_clear_obstacles():
            for node_id in path_node_ids:
                position = graph.nodes[node_id].position 
                
                if position in new_obstacles:
                    obstacle = new_obstacles[position]
                    if obstacle.type.value == "BOULDER":
                        del new_obstacles[position]
                
        return GameState(
            active_vehicles=new_vehicles,
            obstacles=new_obstacles,
            exited_vehicles=new_exited,
            turn_number=self.turn_number + 1
        )
    
    def is_solved(self) -> bool:
        """Check if all vehicles have exited"""
        return len(self.active_vehicles) == 0
    
    def copy(self) -> 'GameState':
        """Create a deep copy of the state"""
        return GameState(
            active_vehicles=self.active_vehicles.copy(),
            obstacles=self.obstacles.copy(),
            exited_vehicles=self.exited_vehicles.copy(),
            turn_number=self.turn_number
        )