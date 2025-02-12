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
from typing import Any, Optional
from game_entities import Location, Item
from proj1_event_logger import Event, EventList


class AdventureGame:
    """A text adventure game class storing all location, item and map data.

    Instance Attributes:
        - _locations: A mapping from location id to Location object.
        - _items: A list of Item objects, representing all items in the game.
        - current_location_id: An integer tracking the id number of the current location of the player
        - ongoing: A boolean determining the game's status

    Representation Invariants:
        - all(id_num >= 0 for id_num in self._locations)
        - all(isinstance(loc, Location) for loc in self._locations.values())
        - all(isinstance(item, Item) for item in self._items)
        - self.current_location_id in self._locations
    """

    _locations: dict[int, Location]
    _items: list[Item]
    current_location_id: int
    ongoing: bool
    player_data: dict[str, Any]
    game_flags: dict[str, bool]

    def __init__(self, game_data_file: str, initial_location_id: int) -> None:
        """
        Initialize a new text adventure game, based on the data in the given file, setting starting location of game
        at the given initial location ID.
        (note: you are allowed to modify the format of the file as you see fit)

        Preconditions:
        - game_data_file is the filename of a valid game data JSON file
        - initial_location_id is a valid location ID present in the game data file.
        - initial_location_id is a non-negative integer.
        """

        self._locations, self._items = self._load_game_data(game_data_file)
        self.current_location_id = initial_location_id
        self.ongoing = True

        # Grouping player-related data into a single dictionary
        self.player_data = {
            'inventory': [],
            'score': 0,
            'remaining_moves': 40,
            'known_codes': set()
        }

        # Grouping puzzle/flag-related data into another dictionary
        self.game_flags = {
            'study_room': False,
            'lab_door': False,
            'scored': False,
            'used_card': False
        }

    @staticmethod
    def _load_game_data(filename: str) -> tuple[dict[int, Location], list[Item]]:
        """Load game data from a JSON file and initialize game locations in a dictionary and items in a list."""

        with open(filename, 'r') as f:
            data = json.load(f)

        locations = {}
        for loc_data in data["locations"]:
            location_obj = Location(
                location_id=loc_data["id"],
                brief_description=loc_data["brief_description"],
                long_description=loc_data["long_description"],
                available_commands=loc_data["available_commands"],
                items=loc_data["items"],
                examinables=loc_data.get("examinables", {})
            )
            locations[loc_data["id"]] = location_obj

        items = []
        for item_data in data["items"]:
            item_obj = Item(
                name=item_data["name"],
                description=item_data["description"],
                start_position=item_data["start_position"],
                target_position=item_data["target_position"],
                target_points=item_data["target_points"]
            )
            items.append(item_obj)

        return locations, items

    def get_location(self, loc_id: Optional[int] = None) -> Location:
        """ Return Location object associated with the provided location ID.
        If no ID is provided, return the Location object associated with the current location.
        """

        # If loc_id is None, use the current location ID
        if loc_id is None:
            loc_id = self.current_location_id

        # Retrieve and return the Location object
        return self._locations[loc_id]

    def get_item_by_name(self, item_name: str) -> Optional[Item]:
        """Return the Item object with the given name, or None if not found."""

        return next((item for item in self._items if item.name == item_name), None)

    def pick_up_item(self, item_name: str) -> None:
        """Pick up an item if it's at the current location."""

        current_location = self.get_location()

        if item_name == "laptop charger":  # Laptop charger riddle to pick up laptop charger
            print("As you reach for the charger, a librarian stops you.")
            print("She says, 'There's a computer science sticker on this laptop charger. To prove you're a computer "
                  "science student, solve this riddle to take the charger:'")
            print("What has keys but can't open locks?")
            answer = input("Your answer: a __________").strip().lower()
            if answer != "dictionary":
                print("Incorrect. The charger remains on the table.")
                print("Would you like a hint? Enter 'yes' or 'no'")
                hint = input().strip().lower()
                if hint == "yes":
                    print("Think about python data types!")
                return  # Exit without picking up

        if item_name in current_location.items:  # Picking up other items
            # Add to inventory
            self.player_data["inventory"].append(item_name)
            # Remove from location
            current_location.items.remove(item_name)

            item = self.get_item_by_name(item_name)
            if item:
                print(f"{item.description}")

            print(f"You picked up {item_name}!")

            # Update location descriptions
            current_location.brief_description = current_location.brief_description.replace(f" {item_name}", "")
            current_location.long_description = current_location.long_description.replace(f" {item_name}", "")

        else:  # If player tries to pick up an item not in the current location
            print("There's no such item here.")

    def drop_item(self, item_name: str) -> None:
        """Drop an item from inventory and place it back in the current location."""

        if item_name in self.player_data["inventory"]:
            # Special check: lost student card
            if item_name == "lost student card" and self.game_flags["used_card"] is False:
                print("Hmmm... maybe you should hang on to the student card for a minute before dropping it off at "
                      "Lost & Found, in case you need it to access something in the library and considering you left "
                      "your student card at your parents' house.")
                return
            self.player_data["inventory"].remove(item_name)
            current_location = self.get_location()
            current_location.items.append(item_name)
            print(f"You dropped {item_name}.")

            current_location.brief_description += f" {item_name}"
            current_location.long_description += f" {item_name}"

            # Check if the item is in its target position and add points
            item = next((i for i in self._items if i.name == item_name), None)
            if item and current_location.id_num == item.target_position:
                if not item.scored:
                    item.scored = True
                    self.player_data["score"] += item.target_points
                    print(f"You placed {item_name} in the correct location! +{item.target_points} points.")
        else:
            print("You don't have that item to drop.")

    def display_score(self) -> None:
        """Display the player's current score."""

        print(f"Your current score is: {self.player_data['score']}")

    def deduct_move(self) -> None:
        """Deduct one move from the remaining moves and check if the game should end."""

        self.player_data["remaining_moves"] -= 1
        print(f"Remaining moves: {self.player_data['remaining_moves']}")

        if self.player_data["remaining_moves"] <= 0:  # If the player has run out of moves, end the game
            print("It's 4 PM! The project deadline has passed, and you didn’t find all your items in time. "
                  "You scramble to submit, but it's too late... You have failed to meet the deadline.")
            self.ongoing = False

    def check_win_condition(self) -> None:
        """Check if the player has won the game."""

        # Check if the player is in their dorm and has all the required items
        inventory = self.player_data["inventory"]

        if (self.current_location_id == 7
                and "usb drive" in inventory
                and "uoft mug" in inventory
                and "laptop charger" in inventory):
            print("Your laptop is charging, your game is backed up, and your lucky mug is right where it belongs.")
            print("With everything set, you're ready to finish your project and submit it on time. Well done!")
            print(f"Your final score was: {self.player_data['score']}")
            self.ongoing = False  # End the game

    def display_actions(self) -> None:
        """Display possible actions for the player at this location."""

        location = self.get_location()  # Get the current location

        print("What to do? Choose from: look, inventory, score, undo, log, quit")

        print("At this location, you can also:")
        for action in location.available_commands:
            print(f"- {action}")

        for item in location.items:
            print(f"- pick up {item}")

        # If player is in the study room and the puzzle is activated, show examinable objects
        if location.id_num == 3 and self.game_flags["study_room"]:
            print("You can examine:")
            for obj in location.examinables:
                print(f"- examine {obj}")

        # If the player has an old notebook item in their inventory, provide the option to read it
        if "old notebook" in self.player_data["inventory"]:
            print("- read old notebook")

    def get_valid_action(self, location: Location, menu: list[str]) -> str:
        """
        Prompt the user to enter an action, checks if it's a valid option, and deducts a move for
        commands that don't cost moves.
        """

        choice = input("\nEnter action: ").lower().strip()

        while (choice not in location.available_commands
               and choice not in menu
               and not choice.startswith("pick up ")
               and not choice.startswith("drop ")
               and not choice.startswith("examine ")
               and not (choice == "read old notebook"
                        and "old notebook" in self.player_data["inventory"])):
            print("That was an invalid option; try again.")
            choice = input("\nEnter action: ").lower().strip()

        # Deduct a move for valid actions except menu choices, pick up, drop, or read
        if (choice not in menu
                and not choice.startswith("pick up ")
                and not choice.startswith("drop ")
                and not choice.startswith("read ")):
            self.deduct_move()

        return choice

    def handle_menu_action(self, choice: str, events_log: EventList) -> None:
        """Handle player actions from the menu (inventory, look, score, undo, log, quit)."""
        if choice == "log":
            events_log.display_events()

        elif choice == "inventory":
            if self.player_data["inventory"]:
                print("Your inventory contains:", ", ".join(self.player_data["inventory"]))
            else:
                print("Your inventory is empty.")

        elif choice == "look":
            print("You take a moment to look around...")

        elif choice == "score":
            self.display_score()

        elif choice == "undo":
            self.undo_last_action(events_log)

        elif choice == "quit":
            print("Thanks for playing! Goodbye.")
            self.ongoing = False

    def undo_last_action(self, events_log: EventList) -> None:
        """Undo the last action and restore the previous game state."""
        print("Undoing the last move...")
        if events_log.is_empty():
            print("No moves to undo.")
            return

        last_event = events_log.last
        if last_event.next_command is not None:
            self.current_location_id = last_event.prev.id_num if last_event.prev else 1
            print(f"Moved back to: {self.get_location().brief_description}")

            # Reverse item actions
            if last_event.next_command.startswith("pick up "):
                item_name = last_event.next_command[len("pick up "):]
                if item_name in self.player_data["inventory"]:
                    self.player_data["inventory"].remove(item_name)
                    self.get_location().items.append(item_name)
                    print(f"Undo: Dropped {item_name}.")
                elif last_event.next_command.startswith("drop "):
                    item_name = last_event.next_command[len("drop "):]
                if item_name in self.get_location().items:
                    self.get_location().items.remove(item_name)
                    self.player_data["inventory"].append(item_name)
                    print(f"Undo: Picked up {item_name}.")

            # Restore move count
            self.player_data["remaining_moves"] += 1
            print(f"Move added back. Remaining moves: {self.player_data['remaining_moves']}")

            # *** Reset puzzle flags for locked door puzzles ***
            # For the Robarts Study Room puzzle (location id 3), reset the flags so that the examine options disappear.
            if (self.current_location_id == 3
                    and self.game_flags["study_room"]):
                self.game_flags["study_room"] = False
                self.game_flags["used_card"] = False
            elif self.current_location_id == 4:
                self.game_flags["lab_door"] = False

            game_log.remove_last_event()

        else:
            print("No valid moves to undo.")

    def handle_item_actions(self, choice: str) -> None:
        """Handle item interactions such as picking up, dropping, or reading."""
        if choice.startswith("pick up "):
            item_name = choice[len("pick up "):]

            # Check if the item is in the current location
            if item_name in self.get_location().items:
                self.pick_up_item(item_name)
            else:
                print("There's no such item here.")

        elif choice.startswith("drop "):
            item_name = choice[len("drop "):]
            self.drop_item(item_name)

        elif choice.startswith("read "):
            item_name = choice[len("read "):]
            if (item_name == "old notebook"
                    and item_name in self.player_data["inventory"]):
                print("You flip through the notebook...")
                print("On the top-left of page 42: '3842 - remember to submit assignment!'")
                self.player_data["known_codes"].add("3842")
            else:
                print(f"You don't have {item_name} to read.")

    def handle_examine(self, choice: str) -> None:
        """Handle 'examine' actions for objects at the current location."""
        object_name = choice[len("examine "):].strip().lower()
        current_loc = self.get_location()

        if object_name in current_loc.examinables:
            print(f"\n{current_loc.examinables[object_name]}")

            # Special case for discovering the code
            if current_loc.id_num == 3 and object_name == "door frame":
                self.player_data["known_codes"].add(7291)
        else:
            print("\nLooks like there's nothing to examine!")

    def handle_locked_doors(self, choice: str) -> bool:
        """Handle special movement cases (locked doors requiring codes)."""
        current_location = self.get_location()

        if choice == "go south" and current_location.id_num == 4:  # Myhal Lab Door
            print("The lab door has a keypad. A sign says: 'Enter 4-digit code:'")
            if "3842" not in self.player_data["known_codes"]:  # If the player hasn't encountered the code yet, give them the hint
                print("You need an access code! Maybe there's a code written on a notebook somewhere...")
                self.game_flags["lab_door"] = True
                return True  # Door stays locked
            else:
                # If the player has encountered the code, hint at that
                print("You need an access code! Where have might you find a four digit code written...")
                attempt = input("Enter 4-digit code: ").strip()
                if attempt == "3842":
                    self.current_location_id = 9  # Move to Computer Lab
                    print("Access granted! The door clicks open.")
                    return False
                else:
                    print("Incorrect code! The keypad flashes red.")
                    self.deduct_move()
                    return True  # Door stays locked

        elif choice == "go west" and current_location.id_num == 3:  # Robarts Study Room
            return self._handle_study_room_door()
        return False

    def _handle_study_room_door(self) -> bool:
        """Handle logic for the locked Robarts Study Room door (location id=3).
        Return True if the door remains locked (i.e., no movement), False if unlocked."""
        if "lost student card" not in self.player_data["inventory"]:
            print("\nThe study room door has a card reader blinking red.")
            print("'ACCESS LIMITED TO UOFT STUDENTS - TAP CARD TO ENTER'")
            print("\nHmmm, looks like you need a student card to enter! Unfortunately you left yours "
                  "at your parents' house over the weekend. Maybe there's one somewhere on campus...")
            self.game_flags["study_room"] = True
            self.deduct_move()
            return True

        else:
            print("\nYou tap the lost student card. The reader flashes green!")
            if 7291 not in self.player_data["known_codes"]:
                print("A hidden keypad slides out from the wall with a prompt:")
                print("'ENTER 4-DIGIT MAINTENANCE CODE'")
                print("You don't know the code! Maybe there's a clue nearby...")
                self.game_flags["study_room"] = True
                self.deduct_move()
                return True

            else:
                code_attempt = input("Enter 4-digit code: ").strip()
                if code_attempt == "7291":
                    print("\nThe door mechanism clicks open! You slip inside.")
                    self.game_flags["used_card"] = True
                    self.current_location_id = 8
                    return False
                else:
                    print("\nIncorrect code! The keypad flashes red and retracts.")
                    self.deduct_move()
                    return True

    def handle_movement(self, choice: str, location: Location) -> None:
        """Handle standard movement between locations."""
        if choice in location.available_commands:
            self.current_location_id = location.available_commands[choice]
            self.check_win_condition()


if __name__ == "__main__":

    import python_ta

    python_ta.check_all(config={
        'max-line-length': 212,
        'disable': ['R1705', 'E9998', 'E9999']
    })

    game_log = EventList()
    game = AdventureGame('game_data.json', 7)  # load data, setting initial location ID to 7
    game_menu = ["look", "inventory", "score", "undo", "log", "quit"]  # Regular menu options available at each location
    game_choice = None

    while game.ongoing:
        game_location = game.get_location()

        if game_choice not in ["look", "inventory", "score", "undo", "log"]:
            event = Event(
                id_num=game_location.id_num,
                description=game_location.long_description if not game_location.visited else game_location.brief_description,
                next_command=game_choice,
                prev=game_log.last
            )
            game_log.add_event(event, command=game_choice)

        # Display descriptions
        if not game_location.visited:
            print(game_location.long_description)
            game_location.visited = True
        else:
            print(game_location.brief_description)

        # Display actions
        game.display_actions()

        # Get a valid action from the player
        game_choice = game.get_valid_action(game_location, game_menu)

        # Handle menu actions
        if game_choice in game_menu:
            game.handle_menu_action(game_choice, game_log)

        # Handle item actions, ie. pick up, drop, read
        elif game_choice.startswith("pick up ") or game_choice.startswith("drop ") or game_choice.startswith("read "):
            game.handle_item_actions(game_choice)

        # Handle examine actions
        elif game_choice.startswith("examine "):
            game.handle_examine(game_choice)

        # Handle locked doors or restricted areas
        elif game.handle_locked_doors(game_choice):
            continue  # Skip movement if user entered wrong code

        # Handle normal movement (ONLY if it’s a valid movement command)
        elif game_choice in game_location.available_commands:
            game.handle_movement(game_choice, game_location)

        else:
            print("Invalid action.")
