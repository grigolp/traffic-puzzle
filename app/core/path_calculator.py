from typing import Dict, Set, Tuple
from models.enums import Orientation, MovementRule, Direction, CellType
from models.graph import RoadGraph, Node
from models.path import PathInfo

class PathCalculator:
    """Calculates all possible paths for movement rules"""
    
    def __init__(self):
        self.turn_mappings = {
            Orientation.NORTH: {
                Direction.LEFT: Orientation.WEST,
                Direction.RIGHT: Orientation.EAST,
                Direction.BACKWARD: Orientation.SOUTH
            },
            Orientation.SOUTH: {
                Direction.LEFT: Orientation.EAST,
                Direction.RIGHT: Orientation.WEST,
                Direction.BACKWARD: Orientation.NORTH
            },
            Orientation.EAST: {
                Direction.LEFT: Orientation.NORTH,
                Direction.RIGHT: Orientation.SOUTH,
                Direction.BACKWARD: Orientation.WEST
            },
            Orientation.WEST: {
                Direction.LEFT: Orientation.SOUTH,
                Direction.RIGHT: Orientation.NORTH,
                Direction.BACKWARD: Orientation.EAST
            }
        }
    
    def calculate_all_paths(self, graph: RoadGraph):
        """Pre-calculate all possible paths for the graph"""
        for node in graph.nodes.values():
            if not node.cell_type.is_road:
                continue
                
            graph.path_lookup[node.id] = {}
            
            for orientation in Orientation:
                graph.path_lookup[node.id][orientation] = {}
                
                for movement_rule in MovementRule:
                    path_info = self._calculate_path(graph, node, orientation, movement_rule)
                    graph.path_lookup[node.id][orientation][movement_rule] = path_info
    
    def _calculate_path(self, graph: RoadGraph, start_node: Node, 
                       orientation: Orientation, movement_rule: MovementRule) -> PathInfo:
        """Calculate path for a specific movement from a node"""
        if movement_rule == MovementRule.STRAIGHT:
            return self._calculate_straight_path(graph, start_node, orientation)
        elif movement_rule == MovementRule.LEFT:
            return self._calculate_turn_path(graph, start_node, orientation, Direction.LEFT, 1)
        elif movement_rule == MovementRule.RIGHT:
            return self._calculate_turn_path(graph, start_node, orientation, Direction.RIGHT, 1)
        elif movement_rule == MovementRule.LEFT_U_TURN:
            return self._calculate_turn_path(graph, start_node, orientation, Direction.LEFT, 2)
        elif movement_rule == MovementRule.RIGHT_U_TURN:
            return self._calculate_turn_path(graph, start_node, orientation, Direction.RIGHT, 2)
    
    def _calculate_turn_path(self, graph: RoadGraph, start_node: Node, 
                           orientation: Orientation, turn_direction: Direction, 
                           num_turns: int) -> PathInfo:
        """Calculate path that requires making specified number of turns"""
        path = [start_node.id]
        current_node = start_node
        current_orientation = orientation
        visited: Set[Tuple[str, Orientation, int]] = set()
        turns_made = 0
        
        # Make the required number of turns
        while turns_made < num_turns:
            turn_found = False
            
            while not turn_found:
                # Check for loops
                state = (current_node.id, current_orientation, turns_made)
                if state in visited:
                    return PathInfo(exit_path=[], exit_point=None, valid=False)
                visited.add(state)
                
                # Checks if the required turn can be made from the current node.
                #
                # A vehicle must first move one step forward to initiate a turn.
                # Additionally, a turn is prohibited if the previous node was also an intersection.
                # This rule prevents illegal U-turns within the same multi-lane intersection.
                #
                # To check the previous node, we access the path at index -2, because the
                # last element (path[-1]) is the current node.
                if len(path) >= 2 and not graph.nodes[path[-2]].cell_type.is_intersection:
                    if current_orientation in current_node.neighbors:
                        next_node_id = current_node.neighbors[current_orientation].get(turn_direction)
                        if next_node_id:
                            # Make the turn
                            next_node = graph.nodes[next_node_id]
                            current_orientation = self.turn_mappings[current_orientation][turn_direction]
                            path.append(next_node.id)
                            turns_made += 1
                            turn_found = True
                            continue
                
                # Can't turn here, continue straight
                if current_orientation not in current_node.neighbors:
                    return PathInfo(exit_path=[], exit_point=None, valid=False)
                
                next_node_id = current_node.neighbors[current_orientation].get(Direction.FORWARD)
                if not next_node_id:
                    return PathInfo(exit_path=[], exit_point=None, valid=False)
                
                current_node = graph.nodes[next_node_id]
                path.append(current_node.id)
                
                # Check if we've reached an exit before completing turns (Successful exit)
                if graph.is_exit_position(current_node):
                    return PathInfo(exit_path=path, exit_point=current_node.position, valid=True)
        
        # After making all required turns, continue straight to exit
        return self._continue_straight_to_exit(graph, current_node, current_orientation, path)
    
    def _calculate_straight_path(self, graph: RoadGraph, start_node: Node, 
                               orientation: Orientation) -> PathInfo:
        """Calculate straight path from a node"""
        path = []
        current_node = start_node
        current_orientation = orientation
        
        # Move forward from starting position
        if current_orientation not in current_node.neighbors:
            return PathInfo(exit_path=[], exit_point=None, valid=False)
        
        next_node_id = current_node.neighbors[current_orientation].get(Direction.FORWARD)
        if not next_node_id:
            return PathInfo(exit_path=[], exit_point=None, valid=False)
        current_node = graph.nodes[next_node_id]
        path.append(current_node.id)
        
        return self._continue_straight_to_exit(graph, current_node, current_orientation, path)
    
    def _continue_straight_to_exit(self, graph: RoadGraph, current_node: Node,
                                 orientation: Orientation, path: list) -> PathInfo:
        """Continue straight until reaching an exit"""
        visited = set()
        
        while True:
            # Check if we've reached an exit TODO: Fix: Currently it does not check for orientation.
            if graph.is_exit_position(current_node):
                return PathInfo(
                    exit_path=path,
                    exit_point=current_node.position,
                    valid=True
                )
            
            # Prevent infinite loops
            if current_node.id in visited:
                return PathInfo(exit_path=[], exit_point=None, valid=False)
            visited.add(current_node.id)
            
            # Continue straight
            if orientation not in current_node.neighbors:
                return PathInfo(exit_path=[], exit_point=None, valid=False)
            
            next_node_id = current_node.neighbors[orientation].get(Direction.FORWARD)
            if not next_node_id:
                return PathInfo(exit_path=[], exit_point=None, valid=False)
            
            current_node = graph.nodes[next_node_id]
            path.append(current_node.id)
