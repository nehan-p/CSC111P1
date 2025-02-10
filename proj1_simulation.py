"""CSC111 Project 1: Text Adventure Game - Simulator

Instructions (READ THIS FIRST!)
===============================

This Python module contains code for Project 1 that allows a user to simulate an entire
playthrough of the game. Please consult the project handout for instructions and details.

You can copy/paste your code from the ex1_simulation file into this one, and modify it as needed
to work with your game.

Copyright and Usage Information
===============================

This file is provided solely for the personal and private use of students
taking CSC111 at the University of Toronto St. George campus. All forms of
distribution of this code, whether as given or with any changes, are
expressly prohibited. For more information on copyright for CSC111 materials,
please consult our Course Syllabus.

This file is Copyright (c) 2025 CSC111 Teaching Team
"""
from __future__ import annotations
from proj1_event_logger import Event, EventList
from adventure import AdventureGame
from game_entities import Location


class AdventureGameSimulation:
    """A simulation of an adventure game playthrough.
    """
    # Private Instance Attributes:
    #   - _game: The AdventureGame instance that this simulation uses.
    #   - _events: A collection of the events to process during the simulation.
    _game: AdventureGame
    _events: EventList

    def __init__(self, game_data_file: str, initial_location_id: int, commands: list[str]) -> None:
        """Initialize a new game simulation based on the given game data, that runs through the given commands.

        Preconditions:
        - len(commands) > 0
        - all commands in the given list are valid commands at each associated location in the game
        """
        self._events = EventList()
        self._game = AdventureGame(game_data_file, initial_location_id)


        # Hint: self._game.get_location() gives you back the current location


        # Hint: Call self.generate_events with the appropriate arguments

        initial_location = self._game.get_location()
        first_event = Event(initial_location_id, initial_location.long_description, commands[0], None, None)
        self._events.add_event(first_event)

        # Hint: self._game.get_location() gives you back the current location

        # Hint: Call self.generate_events with the appropriate arguments
        self.generate_events(commands, initial_location)

    def generate_events(self, commands: list[str], initial_location) -> None:
        """Generate all events in this simulation, handling both movement and non-movement commands."""
        current_location = self._game.get_location()
        visited_locations = set()

        for command in commands:
            # Check if command results in location change
            if command in current_location.available_commands:
                next_loc_id = current_location.available_commands[command]
                new_location = self._game.get_location(next_loc_id)

                # Update visited status and description
                if next_loc_id not in visited_locations:
                    description = new_location.long_description
                    visited_locations.add(next_loc_id)
                else:
                    description = new_location.brief_description

                current_location = new_location
            else:
                # For non-movement commands, use current location's description
                description = current_location.brief_description
                next_loc_id = current_location.id_num

            # Create and add event
            new_event = Event(
                next_loc_id,
                description,
                command,
                None,
                self._events.last
            )
            self._events.add_event(new_event)
        # Hint: current_location.available_commands[command] will return the next location ID
        # which executing <command> while in <current_location_id> leads to

    def get_id_log(self) -> list[int]:
        """
        Get back a list of all location IDs in the order that they are visited within a game simulation
        that follows the given commands.

        >>> sim = AdventureGameSimulation('game_data.json', 1, ["go east"])
        >>> sim.get_id_log()
        [1, 2]

        >>> sim = AdventureGameSimulation('game_data.json', 7, ["go east", "go south", "pick up lost student card"])
        >>> sim.get_id_log()
        [7, 2, 6, 6]
        """

        # Note: We have completed this method for you. Do NOT modify it for ex1.

        return self._events.get_id_log()

    def run(self) -> None:
        """Run the game simulation and log location descriptions."""

        # Note: We have completed this method for you. Do NOT modify it for ex1.

        current_event = self._events.first  # Start from the first event in the list

        while current_event:
            print(current_event.description)
            if current_event is not self._events.last:
                print("You choose:", current_event.next_command)

            # Move to the next event in the linked list
            current_event = current_event.next


if __name__ == "__main__":
    # When you are ready to check your work with python_ta, uncomment the following lines.
    # (Delete the "#" and space before each line.)
    # IMPORTANT: keep this code indented inside the "if __name__ == '__main__'" block
    # import python_ta
    # python_ta.check_all(config={
    #     'max-line-length': 120,
    #     'disable': ['R1705', 'E9998', 'E9999']
    # })

    # TODO: Modify the code below to provide a walkthrough of commands needed to win and lose the game
    win_walkthrough = [
        "go east",  # 7 → 2 (Dorm → St. George St)
        "go west",  # 2 → 1 (Bahen Center)
        "pick up uoft mug",
        "go east",  # 1 → 2
        "go south",  # 2 → 6 (Wallberg)
        "pick up lost student card",
        "pick up old notebook",
        "read old notebook",  # Reveal lab code 3842
        "go north",  # 6 → 5 (Front Campus)
        "go north",  # 5 → 3 (Robarts Library)
        "examine door frame",  # Get study room code 7291
        "go west",  # 3 → 8 (Study Room) WITH CODE
        7291,
        "pick up laptop charger",
        "piano",
        "exit",  # 8 → 3
        "go east",  # 3 → 2
        "go east",  # 2 → 4 (Myhal Basement)
        "go south",  # 4 → 9 (Computer Lab)
        3842,
        "pick up usb drive",
        "exit",  # 9 → 4
        "go west",  # 4 → 2
        "go north"  # 2 → 7 (Dorm) - WIN!
    ]

    expected_win_log = [7, 2, 1, 1, 2, 6, 6, 6, 6, 5, 3, 3, 8, 8, 8, 8, 3, 2, 4, 9, 9, 9, 4, 2, 7]
    sim = AdventureGameSimulation('game_data.json', 7, win_walkthrough)
    actual_win_log = sim.get_id_log()
    assert expected_win_log == sim.get_id_log()

    # Create a list of all the commands needed to walk through your game to reach a 'game over' state
    # Use a cycle that goes from dorm to St. George St and back:
    lose_walkthrough = ["go east", "go north"] * 23  # 46 moves
    expected_lose_log = [7] + [2, 7] * 23  # Total 47 locations (46 moves)
    # Uncomment the line below to test your demo
    sim = AdventureGameSimulation('game_data.json', 7, lose_walkthrough)
    assert expected_lose_log == sim.get_id_log()

    # TODO: Add code below to provide walkthroughs that show off certain features of the game
    # TODO: Create a list of commands involving visiting locations, picking up items, and then
    #   checking the inventory, your list must include the "inventory" command at least once
    # inventory_demo = [..., "inventory", ...]
    # expected_log = []
    # assert expected_log == AdventureGameSimulation(...)

    # scores_demo = [..., "score", ...]
    # expected_log = []
    # assert expected_log == AdventureGameSimulation(...)

    # Add more enhancement_demos if you have more enhancements
    # enhancement1_demo = [...]
    # expected_log = []
    # assert expected_log == AdventureGameSimulation(...)

    # Inventory demonstration
    inventory_demo = [
        "go east",  # 7 → 2
        "go south",  # 2 → 6
        "inventory",  # Empty
        "pick up lost student card",
        "inventory",  # Show card
        "pick up old notebook",
        "inventory"  # Show both
    ]
    expected_inventory_log = [7, 2, 6, 6, 6, 6, 6, 6]
    sim = AdventureGameSimulation('game_data.json', 7, inventory_demo)
    actual_inventory_log = sim.get_id_log()
    assert expected_inventory_log == sim.get_id_log()

    # Score demonstration
    score_demo = [
        "go east",  # 7 → 2
        "go west",  # 2 → 1 (Bahen)
        "pick up engineering calculator",
        "score",  # 0 (not placed)
        "go east",  # 1 → 2
        "go east",  # 2 → 4 (Myhal)
        "drop engineering calculator",  # +5 points
        "score"  # 5
    ]
    expected_score_log = [7, 2, 1, 1, 1, 2, 4, 4, 4]
    sim = AdventureGameSimulation('game_data.json', 7, score_demo)
    actual_score_log = sim.get_id_log()
    assert expected_score_log == sim.get_id_log()

    # Puzzle demonstration (USB access)
    usb_puzzle_demo = [
        "go east",  # 7 → 2
        "go south",  # 2 → 6
        "pick up old notebook",
        "read old notebook",  # Get code
        "go north",  # 6 → 5
        "go north",  # 5 → 3
        "go east",  # 3 → 2
        "go east",  # 2 → 4
        "go south",  # 4 → 9 (With code)
        "pick up usb drive"
    ]
    expected_usb_log = [7, 2, 6, 6, 6, 5, 3, 2, 4, 9, 9]
    sim = AdventureGameSimulation('game_data.json', 7, usb_puzzle_demo)
    actual_usb_log = sim.get_id_log()
    assert expected_usb_log == sim.get_id_log()

    laptop_charger_demo = [
        "go east",  # 7 → 2
        "go south",  # 2 → 6
        "pick up lost student card",
        "go north",  # 6 → 5
        "go north",  # 5 → 3
        "go west",  # Try study room (fail)
        "examine door frame",  # Get code
        "go west"  # Success with code
    ]
    expected_laptop_log = [7, 2, 6, 6, 5, 3, 8, 8, 8]
    sim = AdventureGameSimulation('game_data.json', 7, laptop_charger_demo)
    actual_laptop_log = sim.get_id_log()
    assert expected_laptop_log == sim.get_id_log()

    # Note: You can add more code below for your own testing purposes
