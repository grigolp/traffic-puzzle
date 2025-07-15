from dataclasses import dataclass
from typing import Optional, Dict, Any
from enum import Enum
from models.graph import Position


class ObstacleType(Enum):
    BOULDER = "BOULDER"
    TRAFFIC_LIGHT = "TRAFFIC_LIGHT"
    PEDESTRIAN = "PEDESTRIAN"


@dataclass
class Obstacle:
    id: str
    type: ObstacleType
    position: Position
    
    def blocks_vehicle(self, vehicle_can_clear: bool) -> bool:
        """Check if this obstacle blocks a vehicle"""
        if self.type == ObstacleType.BOULDER:
            return not vehicle_can_clear
        return False  # Traffic lights and pedestrians should not block (for future implementation)
    
    def to_dict(self) -> dict:
        """Base conversion to JSON"""
        return {
            "id": self.id,
            "type": self.type.value,
            "position": {"x": self.position.x, "y": self.position.y}
        }


@dataclass
class Boulder(Obstacle):
    def __init__(self, id: str, position: Position):
        super().__init__(id, ObstacleType.BOULDER, position)


def obstacle_from_dict(data: dict) -> Obstacle:
    """function to create appropriate obstacle type from JSON"""
    obs_type = ObstacleType(data["type"])
    position = Position(data["position"]["x"], data["position"]["y"])
    
    if obs_type == ObstacleType.BOULDER:
        return Boulder(data["id"], position)
    elif obs_type == ObstacleType.TRAFFIC_LIGHT:
        pass    
    elif obs_type == ObstacleType.PEDESTRIAN:
        pass    
    else:
        raise ValueError(f"Unknown obstacle type: {obs_type}")