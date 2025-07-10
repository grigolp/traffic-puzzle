from dataclasses import dataclass
from typing import Dict, Optional, Set
from .enums import CellType, Orientation, Direction, MovementRule


@dataclass
class Position:
    x: int
    y: int
    
    def __hash__(self):
        return hash((self.x, self.y))
    
    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

class Node:
    """Represents a single grid cell"""
    def __init__(self, node_id: str, position: Position, cell_type: CellType):
        self.id = node_id
        self.position = position
        self.cell_type = cell_type
        self.neighbors: Dict[Orientation, Dict[Direction, Optional[str]]] = {}
        
    def add_neighbor(self, from_orientation: Orientation, direction: Direction, neighbor_id: str):
        if from_orientation not in self.neighbors:
            self.neighbors[from_orientation] = {}
        self.neighbors[from_orientation][direction] = neighbor_id

class RoadGraph:
    """Main graph structure for the road network"""
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.nodes: Dict[str, Node] = {}
        self.exit_positions: Set[Position] = set()
        self.path_lookup: Dict[str, Dict[Orientation, Dict[MovementRule, 'PathInfo']]] = {}
    
    def get_node_id(self, x: int, y: int) -> str:
        """Generate consistent node ID from coordinates"""
        return f"n_{x}_{y}"
    
    def get_node(self, x: int, y: int) -> Optional[Node]:
        """Get node by coordinates"""
        node_id = self.get_node_id(x, y)
        return self.nodes.get(node_id)
    
    def is_exit_position(self, pos: Position) -> bool:
        """Check if position is on the grid boundary"""
        return (pos.x == 0 or pos.x == self.width - 1 or 
                pos.y == 0 or pos.y == self.height - 1)
    
    def add_node(self, node: Node):
        """Add node to graph and check if it's an exit"""
        self.nodes[node.id] = node
        if node.cell_type == CellType.ROAD and self.is_exit_position(node.position):
            self.exit_positions.add(node.position)