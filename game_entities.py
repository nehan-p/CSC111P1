"""CSC111 Project 1: Text Adventure Game - Game Entities

Instructions (READ THIS FIRST!)
===============================

This Python module contains the entity classes for Project 1, to be imported and used by
 the `adventure` module.
 Please consult the project handout for instructions and details.

Copyright and Usage Information
===============================

This file is provided solely for the personal and private use of students
taking CSC111 at the University of Toronto St. George campus. All forms of
distribution of this code, whether as given or with any changes, are
expressly prohibited. For more information on copyright for CSC111 materials,
please consult our Course Syllabus.

This file is Copyright (c) 2025 CSC111 Teaching Team
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class Location:
    """A location in our text adventure game world.

    Instance Attributes:
    - id_num: The unique identifier for this location.
    - name: The name of the location.
    - brief_description: A short description of the location for revisits.
    - long_description: A detailed description of the location for first-time visits.
    - available_commands: A dictionary mapping commands (e.g., "go east") to the corresponding location ID.
    - items: A list of item names present at this location.
    - visited: A boolean indicating whether the player has visited this location before.
    - examinables: A dictionary of objects that can be examined with their descriptions.

    Representation Invariants:
    - id_num > 0
    """

    def __init__(self, location_id: int, brief_description: str, long_description: str, available_commands: dict[str, int], items: list[str], visited: bool = False, examinables: Optional[dict[str, str]] = None) -> None:
        self.id_num = location_id
        self.brief_description = brief_description
        self.long_description = long_description
        self.available_commands = available_commands
        self.items = items
        self.visited = visited
        self.examinables = examinables if examinables is not None else {}

@dataclass
class Item:
    """An item in our text adventure game world.

    Instance Attributes:
    - name: The name of the item.
    - description: A brief description of the item.
    - start_position: The location ID where the item starts.
    - target_position: The location ID where the item is intended to be used.
    - target_points: The number of points awarded if the item is used correctly.

    Representation Invariants:
    - start_position > 0
    - target_position > 0
    - target_points >= 0
    """

    # NOTES:
    # This is just a suggested starter class for Item.
    # You may change these parameters and the data available for each Item object as you see fit.
    # (The current parameters correspond to the example in the handout).
    #
    # The only thing you must NOT change is the name of this class: Item.
    # All item objects in your game MUST be represented as an instance of this class.

    name: str
    description: str
    start_position: int
    target_position: int
    target_points: int


# Note: Other entities you may want to add, depending on your game plan:
# - Puzzle class to represent special locations (could inherit from Location class if it seems suitable)
# - Player class
# etc.

if __name__ == "__main__":
    pass
    # When you are ready to check your work with python_ta, uncomment the following lines.
    # (Delete the "#" and space before each line.)
    # IMPORTANT: keep this code indented inside the "if __name__ == '__main__'" block
    # import python_ta
    # python_ta.check_all(config={
    #     'max-line-length': 120,
    #     'disable': ['R1705', 'E9998', 'E9999']
    # })
