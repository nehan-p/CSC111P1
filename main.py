"""CSC111 Final Project: Twitter Data Analysis

Module Description
==================
This module defines the graphical user interface (GUI) for interacting with the Twitter
data analysis toolkit. It uses the Tkinter library to display a menu of visual and
text-based data analysis options.

Copyright and Usage Information
===============================

This file is part of a group project submitted for CSC111 at the University of Toronto St. George campus.
It is intended for grading purposes by course instructors and teaching assistants only.

All other forms of distribution, publication, or external use of this code are strictly prohibited
without the explicit written permission of the project group.

This file is Copyright (c) 2025 CSC111 Project Group: Elena Ding, Nehan Punjani, Raphael Ramesar, Joey Lai
"""

import tkinter as tk
from tkinter import simpledialog, messagebox, scrolledtext
import sys
from io import StringIO
import python_ta
from pandas import DataFrame
from data_loader import load_dataset
from metrics import (
    compute_pagerank,
)
from plotter import (
    plot_user_hashtag_graph,
    plot_hashtag_cooccurrence,
    plot_engagement_distribution,
    generate_hashtag_wordcloud
)


def show_output_window(title: str, content: str) -> None:
    """Display a new window with scrollable text content."""

    output_win = tk.Toplevel(root)
    output_win.title(title)
    text_area = scrolledtext.ScrolledText(output_win, wrap=tk.WORD, width=60, height=20)
    text_area.pack(padx=10, pady=10)
    text_area.insert(tk.END, content)
    text_area.config(state=tk.DISABLED)


def run_analysis(choice: str, df: DataFrame) -> None:
    """Run the selected analysis option based on user input.

    Preconditions:
    - `df` is a non-empty pandas DataFrame with valid Twitter data and
      includes at least the following columns: "user_posted", "likes",
      "reposts", "replies", and "hashtags".
    """

    if choice == "1":
        top_users = df.groupby("user_posted")["likes"].sum().sort_values(ascending=False).head(10)
        show_output_window("Top Users by Likes", top_users.to_string())
    elif choice == "2":
        top_users = df.groupby("user_posted")["reposts"].sum().sort_values(ascending=False).head(10)
        show_output_window("Top Users by Retweets", top_users.to_string())
    elif choice == "3":
        top_users = df.groupby("user_posted")["replies"].sum().sort_values(ascending=False).head(10)
        show_output_window("Top Users by Replies", top_users.to_string())
    elif choice == "4":
        buffer = StringIO()
        sys.stdout = buffer
        compute_pagerank(df)
        sys.stdout = sys.__stdout__
        show_output_window("PageRank Influencers", buffer.getvalue())
    elif choice == "5":
        messagebox.showinfo("Notice", "This option has been removed.")
    elif choice == "6":
        plot_user_hashtag_graph(df)
    elif choice == "7":
        plot_hashtag_cooccurrence(df)
    elif choice == "8":
        limit_str = simpledialog.askstring("Input", "Enter limit (e.g., 1000):")
        if limit_str is None:
            return  # User cancelled the input
        try:
            limit = int(limit_str)
            plot_engagement_distribution(df, limit)
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number.")
    elif choice == "9":
        generate_hashtag_wordcloud(df)
    elif choice == "0":
        root.destroy()
    else:
        messagebox.showwarning("Warning", "Invalid choice. Please try again.")


if __name__ == "__main__":
    # GUI root initialization
    root = tk.Tk()
    root.title("Twitter Data Analysis")
    root.geometry("400x500")

    # Load dataset
    dataframe = load_dataset("twitter-posts.csv")

    # Button configuration
    options = [
        ("1", "Show top users by likes"),
        ("2", "Show top users by retweets"),
        ("3", "Show top users by replies"),
        ("4", "Compute PageRank and show top influencers"),
        ("6", "Show User-Hashtag Bipartite Graph"),
        ("7", "Visualize hashtag co-occurrence"),
        ("8", "Show engagement distribution"),
        ("9", "Generate hashtag word cloud"),
        ("0", "Exit")
    ]

    # Create button UI
    tk.Label(root, text="Twitter Data Analysis Menu", font=("Arial", 14)).pack(pady=10)

    for val, label in options:
        tk.Button(root, text=label, width=40, command=lambda v=val: run_analysis(v, dataframe)).pack(pady=5)

    python_ta.check_all(config={
        'extra-imports': ['tkinter', 'data_loader', 'metrics', 'pandas', 'plotter', 'io', 'sys'],  # the names (strs) of imported modules
        'allowed-io': ['compute_pagerank', 'show_top_users'],
        # the names (strs) of functions that call print/open/input
        'max-line-length': 150,
        'max-branches': 13
    })

    root.mainloop()
