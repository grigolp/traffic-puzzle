import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import json
from app.lambda_function import lambda_handler


def test_lambda_with_level_116():
    """Test with the actual Level 116"""
    level_data =     {
    "levelId": "level_116",
    "metadata": {
        "difficulty": "___",
        "targetMoves": 28
    },
    "grid": {
        "dimensions": {"width": 10, "height": 20},
        "layout": [
            ["0","|","0","0","0","0","0","0","|","0"],
            ["0","|","0","0","0","0","0","0","|","0"],
            ["-","+","-","-","-","-","-","-","+","-"],
            ["0","|","0","0","0","0","0","0","|","0"],
            ["0","|","0","0","0","0","0","0","|","0"],
            ["0","|","0","0","0","0","0","0","|","0"],
            ["0","|","0","0","0","0","0","0","|","0"],
            ["0","|","0","0","0","0","0","0","|","0"],
            ["0","|","0","0","0","0","0","0","|","0"],
            ["-","+","-","-","-","-","-","-","+","-"],
            ["0","|","0","0","0","0","0","0","|","0"],
            ["0","|","0","0","0","0","0","0","|","0"],
            ["0","|","0","0","0","0","0","0","|","0"],
            ["-","+","-","-","-","-","-","-","+","-"],
            ["0","|","0","0","0","0","0","0","|","0"],
            ["0","|","0","0","0","0","0","0","|","0"],
            ["0","|","0","0","0","0","0","0","|","0"],
            ["-","+","-","-","-","-","-","-","+","-"],
            ["0","|","0","0","0","0","0","0","|","0"],
            ["0","|","0","0","0","0","0","0","|","0"]
        ]
    },
    "vehicles": [
        {
            "id": "C01",
            "type": "CAR",
            "length": 2,
            "position": {"x": 2, "y": 2},
            "orientation": "WEST",
            "movementRule": "RIGHT"
        },
        {
            "id": "C02",
            "type": "CAR",
            "length": 2,
            "position": {"x": 7, "y": 2},
            "orientation": "EAST",
            "movementRule": "LEFT"
        },
        {
            "id": "C03",
            "type": "CAR",
            "length": 2,
            "position": {"x": 1, "y": 3},
            "orientation": "NORTH",
            "movementRule": "RIGHT_U_TURN"
        },
        {
            "id": "C04",
            "type": "CAR",
            "length": 2,
            "position": {"x": 8, "y": 3},
            "orientation": "NORTH",
            "movementRule": "LEFT"
        },
        {
            "id": "B01",
            "type": "BULLDOZER",
            "length": 2,
            "position": {"x": 1, "y": 8},
            "orientation": "SOUTH",
            "movementRule": "STRAIGHT"
        },
        {
            "id": "C05",
            "type": "CAR",
            "length": 2,
            "position": {"x": 8, "y": 8},
            "orientation": "SOUTH",
            "movementRule": "STRAIGHT"
        },
        {
            "id": "C06",
            "type": "CAR",
            "length": 2,
            "position": {"x": 2, "y": 9},
            "orientation": "WEST",
            "movementRule": "LEFT"
        },
        {
            "id": "C07",
            "type": "CAR",
            "length": 2,
            "position": {"x": 7, "y": 9},
            "orientation": "WEST",
            "movementRule": "STRAIGHT"
        },
        {
            "id": "C08",
            "type": "CAR",
            "length": 2,
            "position": {"x": 1, "y": 12},
            "orientation": "SOUTH",
            "movementRule": "STRAIGHT"
        },
        {
            "id": "C09",
            "type": "CAR",
            "length": 2,
            "position": {"x": 8, "y": 10},
            "orientation": "NORTH",
            "movementRule": "LEFT"
        },
        {
            "id": "T01",
            "type": "TRUCK",
            "length": 4,
            "position": {"x": 1, "y": 13},
            "orientation": "WEST",
            "movementRule": "STRAIGHT"
        },
        {
            "id": "C10",
            "type": "CAR",
            "length": 2,
            "position": {"x": 6, "y": 13},
            "orientation": "EAST",
            "movementRule": "STRAIGHT"
        },
        {
            "id": "C11",
            "type": "CAR",
            "length": 2,
            "position": {"x": 1, "y": 14},
            "orientation": "NORTH",
            "movementRule": "RIGHT"
        },
        {
            "id": "C12",
            "type": "CAR",
            "length": 2,
            "position": {"x": 8, "y": 14},
            "orientation": "NORTH",
            "movementRule": "LEFT_U_TURN"
        },
        {
            "id": "C13",
            "type": "CAR",
            "length": 2,
            "position": {"x": 2, "y": 17},
            "orientation": "WEST",
            "movementRule": "LEFT"
        },
        {
            "id": "C14",
            "type": "CAR",
            "length": 2,
            "position": {"x": 6, "y": 17},
            "orientation": "WEST",
            "movementRule": "RIGHT"
        },
        {
            "id": "C15",
            "type": "CAR",
            "length": 2,
            "position": {"x": 1, "y": 18},
            "orientation": "SOUTH",
            "movementRule": "STRAIGHT"
        },
        {
            "id": "C16",
            "type": "CAR",
            "length": 2,
            "position": {"x": 8, "y": 18},
            "orientation": "SOUTH",
            "movementRule": "STRAIGHT"
        }
    ],
    "obstacles": [
        {
            "id": "OB1",
            "type": "BOULDER",
            "position": {"x": 1, "y": 9}
        }
    ]
}
    # Test as API Gateway event
    event = {
        'body': json.dumps(level_data),
        'headers': {'Content-Type': 'application/json'}
    }
    
    response = lambda_handler(event, {})
    # print("API Gateway Event Response:")
    # print(f"Status: {response['statusCode']}")
    # print(f"Body: {response['body']}")
    
    # Test as direct invocation
    # print("\n\nDirect Invocation Response:")
    response = lambda_handler(level_data, {})
    # print(f"Status: {response['statusCode']}")
    # print(f"Body: {response['body']}")


def test_invalid_json():
    """Test with invalid JSON"""
    event = {
        'body': '{"invalid": json',
        'headers': {'Content-Type': 'application/json'}
    }
    
    response = lambda_handler(event, {})
    print("\n\nInvalid JSON Response:")
    print(f"Status: {response['statusCode']}")
    print(f"Body: {response['body']}")


if __name__ == "__main__":
    import time
    print("Running Lambda tests...")
    start_time = time.time()
    test_lambda_with_level_116()
    end_time = time.time()
    print(f"\nTests completed in {end_time - start_time:.2f} seconds")
    