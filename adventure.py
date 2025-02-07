"""CSC111 Project 1: Text Adventure Game - Game Manager

Instructions (READ THIS FIRST!)
===============================

This Python module contains the code for Project 1. Please consult
the project handout for instructions and details.

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
import json
from typing import Optional

from game_entities import Location, Item
from proj1_event_logger import Event, EventList


# Note: You may add in other import statements here as needed

# Note: You may add helper functions, classes, etc. below as needed


class AdventureGame:
    """A text adventure game class storing all location, item and map data.

    Instance Attributes:
        - # TODO add descriptions of public instance attributes as needed

    Representation Invariants:
        - # TODO add any appropriate representation invariants as needed
    """

    # Private Instance Attributes (do NOT remove these two attributes):
    #   - _locations: a mapping from location id to Location object.
    #                       This represents all the locations in the game.
    #   - _items: a list of Item objects, representing all items in the game.

    _locations: dict[int, Location]
    _items: list[Item]
    current_location_id: int  # Suggested attribute, can be removed
    ongoing: bool  # Suggested attribute, can be removed

    def __init__(self, game_data_file: str, initial_location_id: int) -> None:
        """
        Initialize a new text adventure game, based on the data in the given file, setting starting location of game
        at the given initial location ID.
        (note: you are allowed to modify the format of the file as you see fit)

        Preconditions:
        - game_data_file is the filename of a valid game data JSON file
        """

        # NOTES:
        # You may add parameters/attributes/methods to this class as you see fit.

        # Requirements:
        # 1. Make sure the Location class is used to represent each location.
        # 2. Make sure the Item class is used to represent each item.

        # Suggested helper method (you can remove and load these differently if you wish to do so):
        self._locations, self._items = self._load_game_data(game_data_file)

        # Suggested attributes (you can remove and track these differently if you wish to do so):
        self.current_location_id = initial_location_id  # game begins at this location
        self.ongoing = True  # whether the game is ongoing
        self.inventory = []  # Initialize an empty inventory
        self.score = 0 # starting score of 0
        self.remaining_moves = 5

    @staticmethod
    def _load_game_data(filename: str) -> tuple[dict[int, Location], list[Item]]:
        """Load locations and items from a JSON file with the given filename and
        return a tuple consisting of (1) a dictionary of locations mapping each game location's ID to a Location object,
        and (2) a list of all Item objects."""

        with open(filename, 'r') as f:
            data = json.load(f)  # This loads all the data from the JSON file

        locations = {}
        for loc_data in data['locations']:  # Go through each element associated with the 'locations' key in the file
            location_obj = Location(loc_data['id'], loc_data['brief_description'], loc_data['long_description'],
                                    loc_data['available_commands'], loc_data['items'])
            locations[loc_data['id']] = location_obj

        items = []
        # TODO: Add Item objects to the items list; your code should be structured similarly to the loop above
        # YOUR CODE BELOW
        for item_data in data['items']:
            item_obj = Item(
                name=item_data['name'],
                start_position=item_data['start_position'],
                target_position=item_data['target_position'],
                target_points=item_data['target_points']
            )
            items.append(item_obj)

        return locations, items

    def get_location(self, loc_id: Optional[int] = None) -> Location:
        """Return Location object associated with the provided location ID.
        If no ID is provided, return the Location object associated with the current location.
        """

        # TODO: Complete this method as specified
        # YOUR CODE BELOW
        # If loc_id is None, use the current location ID
        if loc_id is None:
            loc_id = self.current_location_id

        # Retrieve and return the Location object
        return self._locations[loc_id]

    def pick_up_item(self, item_name: str) -> None:
        """Pick up an item if it's at the current location."""
        current_location = self.get_location()

        if item_name in current_location.items:
            self.inventory.append(item_name)  # Add to inventory
            current_location.items.remove(item_name)  # Remove from location
            print(f"You picked up {item_name}!")

            current_location.brief_description = current_location.brief_description.replace(f" {item_name}", "")
            current_location.long_description = current_location.long_description.replace(f" {item_name}", "")

            # Add points for picking up the item
            item = next((i for i in self._items if i.name == item_name), None)
            if item and item.target_points:
                self.score += item.target_points

        else:
            print("There's no such item here.")

    def drop_item(self, item_name: str) -> None:
        """Drop an item from inventory and place it back in the current location."""
        if item_name in self.inventory:
            self.inventory.remove(item_name)  # Remove from inventory
            self.get_location().items.append(item_name)  # Place item at current location
            print(f"You dropped {item_name}.")

            self.get_location().brief_description += f" {item_name}"
            self.get_location().long_description += f" {item_name}"

            # Deduct points for dropping the item
            item = next((i for i in self._items if i.name == item_name), None)
            if item and item.target_points:
                self.score -= item.target_points
        else:
            print("You don't have that item to drop.")

    def display_score(self) -> None:
        """Display the player's current score."""
        print(f"Your current score is: {self.score}")

    def deduct_move(self) -> None:
        """Deduct one move from the remaining moves and check if the game should end."""
        self.remaining_moves -= 1
        print(f"Remaining moves: {self.remaining_moves}")

        if self.remaining_moves <= 0:
            print("You've run out of moves! Game over.")
            self.ongoing = False


if __name__ == "__main__":

    # When you are ready to check your work with python_ta, uncomment the following lines.
    # (Delete the "#" and space before each line.)
    # IMPORTANT: keep this code indented inside the "if __name__ == '__main__'" block
    # import python_ta
    # python_ta.check_all(config={
    #     'max-line-length': 120,
    #     'disable': ['R1705', 'E9998', 'E9999']
    # })

    game_log = EventList()  # This is REQUIRED as one of the baseline requirements
    game = AdventureGame('game_data.json', 1)  # load data, setting initial location ID to 1
    menu = ["look", "inventory", "score", "undo", "log", "quit"]  # Regular menu options available at each location
    choice = None

    # Note: You may modify the code below as needed; the following starter code is just a suggestion
    while game.ongoing:
        # Note: If the loop body is getting too long, you should split the body up into helper functions
        # for better organization. Part of your marks will be based on how well-organized your code is.

        location = game.get_location()

        # TODO: Add new Event to game log to represent current game location
        #  Note that the <choice> variable should be the command which led to this event
        # YOUR CODE HERE
        # Add a new Event for the current location
        # event = Event(
        #     id_num=location.id_num,
        #     description=location.long_description if not location.visited else location.brief_description,
        #     next_command=choice if choice not in ["look", "inventory", "score", "undo", "log"] else None,
        #     prev=game_log.last
        # )
        # game_log.add_event(event)
        if choice not in ["look", "inventory", "score", "undo", "log"]:
            event = Event(
                id_num=location.id_num,
                description=location.long_description if not location.visited else location.brief_description,
                next_command=choice,
                prev=game_log.last
            )
            game_log.add_event(event, command=choice)
          # Mark the location as visited

        # TODO: Depending on whether or not it's been visited before,
        #  print either full description (first time visit) or brief description (every subsequent visit) of location
        # YOUR CODE HERE
        if not location.visited:
            print(location.long_description)
            location.visited = True
        else:
            print(location.brief_description)

        # Display possible actions at this location
        print("What to do? Choose from: look, inventory, score, undo, log, quit")
        print("At this location, you can also:")
        for action in location.available_commands:
            print("-", action)
        for item in location.items:
            print(f"- pick up {item}")

        # Validate choice
        choice = input("\nEnter action: ").lower().strip()
        while (choice not in location.available_commands
               and choice not in menu
               and not choice.startswith("pick up ")
               and not choice.startswith("drop ")):
            print("That was an invalid option; try again.")
            choice = input("\nEnter action: ").lower().strip()

        print("========")
        print("You decided to:", choice)

        # Deduct a move for valid actions
        if choice not in ["look", "inventory", "score", "undo", "log", "quit"]:
            game.deduct_move()

        if choice in menu:
            # TODO: Handle each menu command as appropriate
            # Note: For the "undo" command, remember to manipulate the game_log event list to keep it up-to-date
            if choice == "log":
                game_log.display_events()
            # ENTER YOUR CODE BELOW to handle other menu commands (remember to use helper functions as appropriate)
            elif choice == "inventory":
                if game.inventory:
                    print("Your inventory contains:", ", ".join(game.inventory))
                else:
                    print("Your inventory is empty.")

            elif choice == "look":
                print("You take a moment to look around...")
                print(location.long_description if not location.visited else location.brief_description)


            elif choice == "score":
                # Display the player's current score
                game.display_score()

            elif choice == "undo":
                print("Undoing the last move...")
                if not game_log.is_empty():
                    last_event = game_log.last
                    if last_event.next_command is not None:
                        # Restore location
                        game.current_location_id = last_event.prev.id_num if last_event.prev else 1
                        print(f"Moved back to: {game.get_location().brief_description}")

                        # Reverse item actions
                        if last_event.next_command.startswith("pick up "):
                            item_name = last_event.next_command[len("pick up "):]
                            if item_name in game.inventory:
                                game.inventory.remove(item_name)
                                game.get_location().items.append(item_name)
                                print(f"Undo: Dropped {item_name}.")
                        elif last_event.next_command.startswith("drop "):
                            item_name = last_event.next_command[len("drop "):]
                            if item_name in game.get_location().items:
                                game.get_location().items.remove(item_name)
                                game.inventory.append(item_name)
                                print(f"Undo: Picked up {item_name}.")

                        # Add back the move
                        game.remaining_moves += 1
                        print(f"Move added back. Remaining moves: {game.remaining_moves}")

                        # Remove the event from the log
                        game_log.remove_last_event()
                    else:
                        print("No valid moves to undo.")
                else:
                    print("No moves to undo.")
            elif choice == "quit":
                # End the game
                print("Thanks for playing! Goodbye.")
                game.ongoing = False

        elif choice.startswith("pick up "):
            item_name = choice[len("pick up "):]  # Extract item name
            game.pick_up_item(item_name)

        elif choice.startswith("drop "):
            item_name = choice[len("drop "):]  # Extract item name
            game.drop_item(item_name)

        else:
            # Handle non-menu actions
            result = location.available_commands[choice]
            game.current_location_id = result

            # TODO: Add in code to deal with actions which do not change the location (e.g. taking or using an item)
            # TODO: Add in code to deal with special locations (e.g. puzzles) as needed for your game
