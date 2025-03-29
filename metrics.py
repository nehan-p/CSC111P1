"""CSC111 Final Project: Twitter Network Metrics

Module Description
==================
This module provides analysis functions for computing metrics on a Twitter interaction dataset,
specifically identifying influential users based on PageRank and engagement metrics.

These functions are designed to be used in conjunction with a cleaned Twitter dataset and
a graph-building helper function.

Copyright and Usage Information
===============================

This file is part of a group project submitted for CSC111 at the University of Toronto St. George campus.
It is intended for grading purposes by course instructors and teaching assistants only.

All other forms of distribution, publication, or external use of this code are strictly prohibited
without the explicit written permission of the project group.

This file is Copyright (c) 2025 CSC111 Project Group: Elena Ding, Nehan Punjani, Raphael Ramesar, Joey Lai
"""
import networkx as nx
import pandas as pd
import python_ta
from graph_builder import build_interaction_graph


def compute_pagerank(df: pd.DataFrame, top_n: int = 10) -> None:
    """Compute PageRank scores for users and print the top N most influential users.

    This function builds a cleaned interaction graph from tagged mentions
    and computes PageRank centrality to determine influence.

    Preconditions:
    - `df` must contain a 'user_posted' column with non-null user identifiers.
    - `build_interaction_graph(df)` must return a graph with string-type nodes.
    - `top_n` must be a positive integer.
    """

    df_clean = df[df["user_posted"].notna()].copy()
    df_clean["user_posted"] = df_clean["user_posted"].astype(str).str.strip()

    # Filter out users that look like dictionary strings (bad data)
    df_clean = df_clean[~df_clean["user_posted"].str.contains(r"\{|\}", na=False)]

    graph = build_interaction_graph(df_clean)

    # Remove weird tagged users from nodes too
    cleaned_graph = nx.DiGraph()
    for u, v in graph.edges():
        if isinstance(u, str) and isinstance(v, str) and "{" not in u and "{" not in v:
            cleaned_graph.add_edge(u, v)

    pagerank_scores = nx.pagerank(cleaned_graph)
    top_users = sorted(pagerank_scores.items(), key=lambda x: x[1], reverse=True)[:top_n]

    print("\nTop Influential Users by PageRank:")
    for user, score in top_users:
        print(f"{user}: {score:.4f}")


def show_top_users(df: pd.DataFrame, metric: str, top_n: int = 10) -> None:
    """Print the top top_n number of users by a specified engagement metric.

    This function groups tweets by user and calculates the sum of the given metric
    (e.g., likes, reposts, replies) to identify the most engaged-with users.

    Preconditions:
    - `metric` must be one of the numeric columns in `df`, such as 'likes', 'reposts', or 'replies'.
    - `df` must contain a 'user_posted' column
    - `top_n` >= 0
    """

    if metric not in df.columns:
        print(f"Column '{metric}' not found in dataset.")
        return
    top_users = df.groupby("user_posted")[metric].sum().sort_values(ascending=False).head(top_n)
    print(f"\nTop Users by {metric.capitalize()}:")
    print(top_users)


if __name__ == "__main__":

    python_ta.check_all(config={
        'extra-imports': ['networkx', 'pandas', 'graph_builder'],  # the names (strs) of imported modules
        'allowed-io': ['compute_pagerank', 'show_top_users'],     # the names (strs) of functions that call print/open/input
        'max-line-length': 130
    })
