from dataclasses import dataclass, field
from typing import List, Set, Optional
from enum import Enum
from models.graph import Position
from models.enums import Orientation, MovementRule


class VehicleType(Enum):
    CAR = "CAR"
    TRUCK = "TRUCK"
    BULLDOZER = "BULLDOZER"


@dataclass
class Vehicle:
    id: str
    type: VehicleType
    length: int
    position: Position  # Head/front position
    orientation: Orientation
    movement_rule: MovementRule
    _occupied_cells_cache: Optional[List[Position]] = field(default=None, init=False, compare=False)
    
    def get_occupied_cells(self) -> List[Position]:
        """Calculate all cells this vehicle occupies."""
        if self._occupied_cells_cache is not None:
            return self._occupied_cells_cache
        
        cells = [self.position]
        
        # Pre-compute directional offsets
        if self.orientation == Orientation.NORTH:
            delta_x, delta_y = 0, 1
        elif self.orientation == Orientation.SOUTH:
            delta_x, delta_y = 0, -1
        elif self.orientation == Orientation.EAST:
            delta_x, delta_y = -1, 0
        else:  # WEST
            delta_x, delta_y = 1, 0
        
        # Add cells extending from the head
        for i in range(1, self.length):
            cells.append(Position(
                self.position.x + delta_x * i,
                self.position.y + delta_y * i
            ))
        
        self._occupied_cells_cache = cells
        return cells
    
    def can_clear_obstacles(self) -> bool:
        """Check if this vehicle can clear obstacles (only bulldozers)"""
        return self.type == VehicleType.BULLDOZER
    
    def to_dict(self) -> dict:
        """Convert to JSON-serializable format"""
        return {
            "id": self.id,
            "type": self.type.value,
            "length": self.length,
            "position": {"x": self.position.x, "y": self.position.y},
            "orientation": self.orientation.value,
            "movementRule": self.movement_rule.value
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Vehicle':
        """Create Vehicle from JSON data"""
        return cls(
            id=data["id"],
            type=VehicleType(data["type"]),
            length=data["length"],
            position=Position(data["position"]["x"], data["position"]["y"]),
            orientation=Orientation(data["orientation"]),
            movement_rule=MovementRule(data["movementRule"])
        )