from dataclasses import dataclass
from typing import List, Set
from enum import Enum
from .graph import Position
from .enums import Orientation, MovementRule


class VehicleType(Enum):
    CAR = "CAR"
    TRUCK = "TRUCK"
    BULLDOZER = "BULLDOZER"


@dataclass
class Vehicle:
    id: str
    type: VehicleType
    length: int  # 2 for CAR/BULLDOZER, 4 for TRUCK
    position: Position  # Head/front position
    orientation: Orientation
    movement_rule: MovementRule
    
    def get_occupied_cells(self) -> List[Position]:
        """
        Calculate all cells this vehicle occupies.
        The head is at self.position, and the body extends backward based on orientation.
        """
        cells = [self.position]

        # Determine the directional offsets based on orientation.
        if self.orientation == Orientation.NORTH:
            delta_x, delta_y = 0, 1
        elif self.orientation == Orientation.SOUTH:
            delta_x, delta_y = 0, -1
        elif self.orientation == Orientation.EAST:
            delta_x, delta_y = -1, 0
        elif self.orientation == Orientation.WEST:
            delta_x, delta_y = 1, 0
        else:
            raise ValueError("Invalid orientation")
        
        # Add cells extending from the head based on vehicle length.
        for i in range(1, self.length):
            cells.append(Position(self.position.x + delta_x * i,
                      self.position.y + delta_y * i))
        
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