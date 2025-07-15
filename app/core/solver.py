from typing import List, Dict, Set, Tuple, Optional
from collections import deque
from dataclasses import dataclass
from models.graph import RoadGraph
from models.game_state import GameState
from models.vehicles import Vehicle
from models.path import PathInfo


@dataclass
class SolverResult:
    """Result of solving attempt"""
    solvable: bool
    solution: List[str]  # Ordered list of vehicle IDs that exited
    total_moves: int
    blocking_details: List[Dict[str, str]] = None
    reason: str = None


@dataclass
class SearchState:
    """State in the search tree"""
    game_state: GameState
    move_sequence: List[str]  # Vehicle IDs in order of exit
    
    def get_hash(self) -> str:
        """Create unique hash for this state for cycle detection"""
        # Hash based on active vehicles and their positions
        vehicle_parts = []
        for vid in sorted(self.game_state.active_vehicles.keys()):
            v = self.game_state.active_vehicles[vid]
            vehicle_parts.append(f"{vid}:{v.position.x},{v.position.y}")
        
        # Include obstacle positions that can change (traffic lights, pedestrians)
        obstacle_parts = []
        for pos in sorted(self.game_state.obstacles.keys(), key=lambda p: (p.x, p.y)):
            obs = self.game_state.obstacles[pos]
            if obs.type.value == "TRAFFIC_LIGHT":
                obstacle_parts.append(f"TL:{pos.x},{pos.y}:{obs.current_state}")
            elif obs.type.value == "PEDESTRIAN":
                obstacle_parts.append(f"PED:{pos.x},{pos.y}:{obs.current_progress}")
        
        return "|".join(vehicle_parts + obstacle_parts)


class Solver:
    """Determines if a traffic puzzle level is solvable"""
    
    def __init__(self, graph: RoadGraph):
        self.graph = graph
    
    def solve(self, initial_state: GameState) -> SolverResult:
        """
        Attempt to solve the puzzle using breadth-first search.
        Returns detailed results including solution path or blocking reasons.
        """
        # Quick check: if no vehicles, it's already solved
        if initial_state.is_solved():
            return SolverResult(
                solvable=True,
                solution=[],
                total_moves=0
            )
        
        # BFS for finding shortest solution
        queue = deque([SearchState(initial_state, [])])
        visited = {SearchState(initial_state, []).get_hash()}
        
        # Track states for detecting true deadlock
        states_explored = 0
        max_depth = 0
        last_blocking_details = []
        
        while queue:
            current_search_state = queue.popleft()
            current_game_state = current_search_state.game_state
            move_sequence = current_search_state.move_sequence
            
            states_explored += 1
            max_depth = max(max_depth, len(move_sequence))
            
            # Check if solved
            if current_game_state.is_solved():
                return SolverResult(
                    solvable=True,
                    solution=move_sequence,
                    total_moves=len(move_sequence)
                )
            
            # Find all vehicles that can move in current state
            movable_vehicles = self._find_movable_vehicles(current_game_state)
            
            # If no vehicles can move, this branch is blocked
            if not movable_vehicles:
                # Analyze why it's blocked
                blocking_details = self._analyze_blocking(current_game_state)
                last_blocking_details = blocking_details
                continue
            
            # Try moving each movable vehicle
            for vehicle, path_info in movable_vehicles:
                # Apply the move
                new_game_state = current_game_state.apply_vehicle_exit(
                    vehicle.id, 
                    path_info.exit_path,
                    self.graph
                )
                
                new_search_state = SearchState(
                    new_game_state,
                    move_sequence + [vehicle.id]
                )
                
                # Check if we've seen this state before
                state_hash = new_search_state.get_hash()
                if state_hash not in visited:
                    visited.add(state_hash)
                    queue.append(new_search_state)
        
        # No solution found
        return SolverResult(
            solvable=False,
            solution=[],
            total_moves=0,
            blocking_details=last_blocking_details,
            reason=f"Exhausted all possibilities. Explored {states_explored} states up to depth {max_depth}."
        )
    
    def _find_movable_vehicles(self, state: GameState) -> List[Tuple[Vehicle, PathInfo]]:
        """
        Find all vehicles that can move in the current state.
        Returns list of (vehicle, path_info) tuples.
        """
        movable = []
        
        for vehicle in state.active_vehicles.values():
            # Get the pre-calculated path for this vehicle
            node = self.graph.get_node(vehicle.position.x, vehicle.position.y)
            if not node:
                continue
            
            # Look up the path
            if (node.id in self.graph.path_lookup and
                vehicle.orientation in self.graph.path_lookup[node.id] and
                vehicle.movement_rule in self.graph.path_lookup[node.id][vehicle.orientation]):
                
                path_info = self.graph.path_lookup[node.id][vehicle.orientation][vehicle.movement_rule]
                
                # Check if the path is valid and clear
                if path_info.valid:
                    is_clear, blocking_reason = state.is_path_clear(path_info.exit_path, vehicle, self.graph)
                    if is_clear:
                        movable.append((vehicle, path_info))
        
        return movable
    
    def _analyze_blocking(self, state: GameState) -> List[Dict[str, str]]:
        """
        Analyze why no vehicles can move and return detailed blocking information.
        """
        blocking_details = []
        
        for vehicle in state.active_vehicles.values():
            # Get the pre-calculated path
            node = self.graph.get_node(vehicle.position.x, vehicle.position.y)
            if not node:
                blocking_details.append({
                    "blocked": vehicle.id,
                    "blockedBy": "INVALID_POSITION",
                    "reason": f"Vehicle {vehicle.id} is at invalid position ({vehicle.position.x}, {vehicle.position.y})"
                })
                continue
            
            # Check if path exists
            if (node.id not in self.graph.path_lookup or
                vehicle.orientation not in self.graph.path_lookup[node.id] or
                vehicle.movement_rule not in self.graph.path_lookup[node.id][vehicle.orientation]):
                
                blocking_details.append({
                    "blocked": vehicle.id,
                    "blockedBy": "NO_PATH",
                    "reason": f"No valid path exists for {vehicle.id} with {vehicle.movement_rule.value} from current position"
                })
                continue
            
            path_info = self.graph.path_lookup[node.id][vehicle.orientation][vehicle.movement_rule]
            
            if not path_info.valid:
                blocking_details.append({
                    "blocked": vehicle.id,
                    "blockedBy": "INVALID_PATH",
                    "reason": f"Path for {vehicle.id} leads to dead end or cannot complete {vehicle.movement_rule.value}"
                })
            else:
                # Path exists but is blocked
                is_clear, blocking_reason = state.is_path_clear(path_info.exit_path, vehicle, self.graph)
                if not is_clear:
                    # Try to identify what's blocking
                    blocker = self._identify_blocker(path_info.exit_path, vehicle, state)
                    blocking_details.append({
                        "blocked": vehicle.id,
                        "blockedBy": blocker,
                        "reason": blocking_reason or f"{blocker} blocks {vehicle.id}'s path"
                    })
        
        return blocking_details
    
    def _identify_blocker(self, path_node_ids: List[str], blocked_vehicle: Vehicle, 
                         state: GameState) -> str:
        """Identify what's blocking a path"""
        for node_id in path_node_ids:
            position = self.graph.nodes[node_id].position
            
            # Check obstacles
            if position in state.obstacles:
                return state.obstacles[position].id
            
            # Check other vehicles
            for other_vehicle in state.active_vehicles.values():
                if other_vehicle.id != blocked_vehicle.id:
                    if position in other_vehicle.get_occupied_cells():
                        return other_vehicle.id
        
        return "UNKNOWN"