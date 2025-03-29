"""CSC111 Final Project: Twitter Graph Builder

Module Description
==================
This module provides functions for constructing different types of graphs based on
user interaction data from a Twitter dataset.

These graphs form the backbone of the network analysis conducted in the rest of the project.

Copyright and Usage Information
===============================

This file is part of a group project submitted for CSC111 at the University of Toronto St. George campus.
It is intended for grading purposes by course instructors and teaching assistants only.

All other forms of distribution, publication, or external use of this code are strictly prohibited
without the explicit written permission of the project group.

This file is Copyright (c) 2025 CSC111 Project Group: Elena Ding, Nehan Punjani, Raphael Ramesar, Joey Lai
"""
import json
import networkx as nx
import python_ta
import pandas as pd

USER_COL = "user_posted"
TAGGED_USERS_COL = "tagged_users"


def build_interaction_graph(df: pd.DataFrame) -> nx.Graph:
    """
    Build an undirected interaction graph from tagged mentions.
    Nodes are users; edges represent mentions.
    """
    interaction_graph = nx.Graph()

    for _, row in df.iterrows():
        user = row[USER_COL]

        raw_mentions = row[TAGGED_USERS_COL]
        try:
            mentions = json.loads(raw_mentions)
            if isinstance(mentions, list):
                for m in mentions:
                    if isinstance(m, dict) and 'profile_name' in m:
                        tag_name = m['profile_name']
                        interaction_graph.add_edge(user, tag_name)
        except TypeError:
            continue  # skip malformed entries

    return interaction_graph


def build_retweet_graph(df: pd.DataFrame) -> nx.DiGraph:
    """
    Build a directed graph from retweet-like behavior.
    Assumes 'tagged_users' column includes retweet mentions.
    """
    retweet_graph = nx.DiGraph()

    for _, row in df.iterrows():
        user = row[USER_COL]
        tagged = str(row[TAGGED_USERS_COL]).split(',')

        for tagged_user in tagged:
            tagged_user = tagged_user.strip()
            if tagged_user and tagged_user != 'nan':
                retweet_graph.add_edge(tagged_user, user)

    return retweet_graph


def build_reply_graph(df: pd.DataFrame) -> nx.DiGraph:
    """
    Build a directed graph for reply trees (parent -> reply).
    Since we don't have reply IDs, we'll simulate using 'replies' field.
    """
    reply_graph = nx.DiGraph()

    for _, row in df.iterrows():
        user = row[USER_COL]
        replies = str(row['replies']).split(',')

        for reply in replies:
            reply = reply.strip()
            if reply and reply != 'nan':
                reply_graph.add_edge(user, reply)

    return reply_graph


if __name__ == "__main__":

    python_ta.check_all(config={
        'extra-imports': ['pandas', 'networkx', 'json'],  # the names (strs) of imported modules
        'allowed-io': [],     # the names (strs) of functions that call print/open/input
        'max-line-length': 130
    })
