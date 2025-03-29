"""CSC111 Final Project: Twitter Data Loader

Module Description
==================
This module loads a local Twitter dataset from a CSV file into a pandas DataFrame.
It includes basic error handling to inform the user if the dataset file is not found in the expected location.

This module is intended to be used as a foundational utility for all other analysis
modules in the project.

Copyright and Usage Information
===============================

This file is part of a group project submitted for CSC111 at the University of Toronto St. George campus.
It is intended for grading purposes by course instructors and teaching assistants only.

All other forms of distribution, publication, or external use of this code are strictly prohibited
without the explicit written permission of the project group.

This file is Copyright (c) 2025 CSC111 Project Group: Elena Ding, Nehan Punjani, Raphael Ramesar, Joey Lai
"""
import python_ta
import pandas as pd


def load_dataset(file_path: str = "twitter-posts.csv") -> pd.DataFrame:
    """
    Load the Twitter dataset from a local file.
    Assumes that the file 'twitter-posts.csv' is present in the same folder.
    """
    try:
        df = pd.read_csv(file_path)
        print("Dataset loaded successfully.")
        return df
    except FileNotFoundError:
        raise FileNotFoundError(
            f"The dataset file '{file_path}' does not exist. Please ensure it is downloaded and in the correct folder."
        )


if __name__ == "__main__":

    python_ta.check_all(config={
        'extra-imports': ['pandas'],  # the names (strs) of imported modules
        'allowed-io': ['load_dataset'],     # the names (strs) of functions that call print/open/input
        'max-line-length': 130
    })
