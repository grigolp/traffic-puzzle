from dataclasses import dataclass
from typing import List, Optional
from models.graph import Position

@dataclass
class PathInfo:
    """Pre-calculated path information"""
    exit_path: List[str]  # List of node IDs to traverse
    exit_point: Optional[Position]  # Where the vehicle exits the grid
    valid: bool  # Whether this movement is possible