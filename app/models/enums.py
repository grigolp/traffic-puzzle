from enum import Enum

class CellType(Enum):
    NON_PASSABLE = "0"
    HORIZONTAL_ROAD = "-"
    VERTICAL_ROAD = "|"
    INTERSECTION = "+"
    EXIT = "E"
    
    @property
    def is_road(self):
        return self != CellType.NON_PASSABLE
    
    @property
    def is_exit(self):
        return self == CellType.EXIT

class Orientation(Enum):
    NORTH = "NORTH"
    SOUTH = "SOUTH"
    EAST = "EAST"
    WEST = "WEST"

class MovementRule(Enum):
    STRAIGHT = "STRAIGHT"
    LEFT = "LEFT"
    RIGHT = "RIGHT"
    LEFT_U_TURN = "LEFT_U_TURN"
    RIGHT_U_TURN = "RIGHT_U_TURN"

class Direction(Enum):
    """Relative directions from a node"""
    FORWARD = "FORWARD"
    LEFT = "LEFT"
    RIGHT = "RIGHT"
    BACKWARD = "BACKWARD"