# Vehicle Length and Type Specifications

## Vehicle Types and Dimensions

### CAR
- **Length**: 2 cells
- **Capabilities**: Standard movement, blocked by all obstacles
- **ID Prefix**: C (e.g., C01, C02)

### TRUCK  
- **Length**: 3 cells
- **Capabilities**: Standard movement, blocked by all obstacles
- **ID Prefix**: T (e.g., T01, T02)
- **Special Considerations**: Longer length requires more planning for turns and intersections

### BULLDOZER
- **Length**: 2 cells  
- **Capabilities**: Can clear boulders while moving
- **ID Prefix**: B (e.g., B01, B02)
- **Special Behavior**: When a bulldozer's path crosses a boulder, the boulder is removed from the game state

## Implementation Notes

### Cell Occupation
All vehicles occupy multiple cells extending backward from their head position:
- **Head**: Always at the `position` coordinate specified in vehicle data
- **Body**: Extends opposite to the vehicle's orientation

### Validation
- Vehicle length should match type specifications
- All occupied cells must be on valid road segments
- No two vehicles can occupy the same cell
- Vehicle orientation must be compatible with road type (horizontal/vertical roads have restrictions)

### Boulder Interaction
- **Cars and Trucks**: Cannot move through boulders
- **Bulldozers**: Can move through boulders, removing them in the process
- **Path Planning**: Bulldozer paths can include boulder positions; other vehicles cannot