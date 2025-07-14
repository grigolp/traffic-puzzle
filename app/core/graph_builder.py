from typing import List
from models.enums import CellType, Orientation, Direction
from models.graph import RoadGraph, Node, Position

class GraphBuilder:
    """Builds graph structure from grid layout"""
    
    def build_graph(self, width: int, height: int, layout: List[List[str]]) -> RoadGraph:
        """Build graph from grid dimensions and layout"""
        graph = RoadGraph(width, height)
        self._create_nodes(graph, layout)
        self._establish_neighbors(graph)
        return graph
    
    def _create_nodes(self, graph: RoadGraph, layout: List[List[str]]):
        """Create nodes for each grid cell"""
        for y, row in enumerate(layout):
            for x, cell_value in enumerate(row):
                pos = Position(x, y)
                node_id = graph.get_node_id(x, y)
                cell_type = CellType(cell_value)
                node = Node(node_id, pos, cell_type)
                graph.add_node(node)
    
    def _establish_neighbors(self, graph: RoadGraph):
        """Establish neighbor relationships based on explicit road types"""
        for node in graph.nodes.values():
            if not node.cell_type.is_road:
                continue
            
            for orientation in Orientation:
                self._set_neighbors_for_node(graph, node, orientation)
    
    def _set_neighbors_for_node(self, graph: RoadGraph, node: Node, orientation: Orientation):
        """Set neighbors based on node type and orientation"""
        x, y = node.position.x, node.position.y
        
        # Define all possible neighbors
        neighbors_map = self._get_neighbors_map(x, y, orientation)
        
        if node.cell_type == CellType.INTERSECTION:
            # Intersections can connect in all directions
            self._add_all_valid_neighbors(graph, node, orientation, neighbors_map)
            
        elif node.cell_type == CellType.HORIZONTAL_ROAD:
            # Horizontal roads only connect east-west
            if orientation in [Orientation.EAST, Orientation.WEST]:
                self._add_forward_backward_neighbors(graph, node, orientation, neighbors_map)
                
        elif node.cell_type == CellType.VERTICAL_ROAD:
            # Vertical roads only connect north-south
            if orientation in [Orientation.NORTH, Orientation.SOUTH]:
                self._add_forward_backward_neighbors(graph, node, orientation, neighbors_map)
    
    def _get_neighbors_map(self, x: int, y: int, orientation: Orientation) -> dict:
        """Get neighbor positions based on orientation"""
        if orientation == Orientation.NORTH:
            return {
                Direction.FORWARD: (x, y - 1),
                Direction.LEFT: (x - 1, y),
                Direction.RIGHT: (x + 1, y),
                Direction.BACKWARD: (x, y + 1)
            }
        elif orientation == Orientation.SOUTH:
            return {
                Direction.FORWARD: (x, y + 1),
                Direction.LEFT: (x + 1, y),
                Direction.RIGHT: (x - 1, y),
                Direction.BACKWARD: (x, y - 1)
            }
        elif orientation == Orientation.EAST:
            return {
                Direction.FORWARD: (x + 1, y),
                Direction.LEFT: (x, y - 1),
                Direction.RIGHT: (x, y + 1),
                Direction.BACKWARD: (x - 1, y)
            }
        else:  # WEST
            return {
                Direction.FORWARD: (x - 1, y),
                Direction.LEFT: (x, y + 1),
                Direction.RIGHT: (x, y - 1),
                Direction.BACKWARD: (x + 1, y)
            }
    
    def _add_all_valid_neighbors(self, graph: RoadGraph, node: Node, orientation: Orientation, 
                                neighbors_map: dict):
        """Add all valid neighbors (for intersections)"""
        for direction, (nx, ny) in neighbors_map.items():
            if 0 <= nx < graph.width and 0 <= ny < graph.height:
                neighbor = graph.get_node(nx, ny)
                if neighbor and neighbor.cell_type.is_road:
                    node.add_neighbor(orientation, direction, neighbor.id)
    
    def _add_forward_backward_neighbors(self, graph: RoadGraph, node: Node, orientation: Orientation,
                                      neighbors_map: dict):
        """Add only forward and backward neighbors (for road segments)"""
        for direction in [Direction.FORWARD, Direction.BACKWARD]:
            nx, ny = neighbors_map[direction]
            if 0 <= nx < graph.width and 0 <= ny < graph.height:
                neighbor = graph.get_node(nx, ny)
                if neighbor and neighbor.cell_type.is_road:
                    node.add_neighbor(orientation, direction, neighbor.id)