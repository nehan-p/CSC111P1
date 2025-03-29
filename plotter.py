"""CSC111 Final Project: Twitter Data Visualizations

Module Description
==================
This module provides a suite of data visualization functions for analyzing a Twitter dataset.

These visualizations help uncover user behavior patterns, hashtag trends, and influential participants
in the dataset using graph theory and data aggregation techniques.

Copyright and Usage Information
===============================
This file is part of a group project submitted for CSC111 at the University of Toronto St. George campus.
It is intended for grading purposes by course instructors and teaching assistants only.

All other forms of distribution, publication, or external use of this code are strictly prohibited
without the explicit written permission of the project group.

This file is Copyright (c) 2025 CSC111 Project Group: Elena Ding, Nehan Punjani, Raphael Ramesar, Joey Lai
"""
from collections import Counter, defaultdict
import pandas as pd
import matplotlib.pyplot as plt
import python_ta
import networkx as nx
from wordcloud import WordCloud
from matplotlib import widgets

HASHTAG_COL = 'hashtags'
TAGGED_USERS_COL = 'tagged_users'
USER_COL = 'user_posted'
REPLY_COL = 'replies'


def plot_user_hashtag_graph(df: pd.DataFrame, hashtag_limit: int = 20) -> None:
    """Visualize a bipartite graph of users and the top hashtags they use.

    The graph displays relationships between users and their associated hashtags,
    limited to the most frequently used hashtags.

    Preconditions:
    - `df` must contain columns: 'user_posted' and 'hashtags'.
    - `hashtag_limit` > 0
    """
    df_cleaned = df.dropna(subset=[USER_COL, HASHTAG_COL]).copy()
    df_cleaned[HASHTAG_COL] = df_cleaned[HASHTAG_COL].str.lower().str.replace(r'[^a-z0-9_#]', '', regex=True)

    hashtag_counts = df_cleaned[HASHTAG_COL].str.split(',').explode().str.strip().value_counts().head(hashtag_limit)
    top_hashtags = set(hashtag_counts.index)

    bi_graph = nx.Graph()
    user_connections = defaultdict(set)

    for _, row in df_cleaned.iterrows():
        user = row[USER_COL]
        for tag in str(row[HASHTAG_COL]).lower().split(','):
            tag = tag.strip().replace('"', '').replace("'", '')
            tag = ''.join(c for c in tag if c.isalnum() or c in {'#', '_'})
            if tag and tag in top_hashtags:
                user_connections[user].add(tag)

    selected_users = [username for username, tags in user_connections.items() if len(tags) > 0]

    if not selected_users:
        print("No users found with relevant hashtag connections.")
        return

    for user in selected_users:
        for tag in user_connections[user]:
            bi_graph.add_node(user, bipartite=0)
            bi_graph.add_node(tag, bipartite=1)
            bi_graph.add_edge(user, tag)

    pos = nx.spring_layout(bi_graph, seed=42)
    user_nodes = {n for n, d in bi_graph.nodes(data=True) if d.get('bipartite') == 0}
    hashtag_nodes = set(bi_graph) - user_nodes

    plt.figure(figsize=(14, 12))
    nx.draw_networkx_nodes(bi_graph, pos, nodelist=user_nodes, node_color='lightblue', node_size=600, label='Users')
    nx.draw_networkx_nodes(bi_graph, pos, nodelist=hashtag_nodes, node_color='lightcoral', node_size=600, label='Hashtags')
    nx.draw_networkx_edges(bi_graph, pos, alpha=0.5)
    nx.draw_networkx_labels(bi_graph, pos, font_size=9)
    plt.title("User-Hashtag Bipartite Graph (All Connected Users × Top Hashtags)")
    plt.legend()
    plt.axis("off")
    plt.tight_layout()
    plt.show()


def plot_hashtag_cooccurrence(df: pd.DataFrame, max_nodes: int = 25) -> None:
    """Visualize a graph of hashtag co-occurrence based on tweets.

    Edges represent hashtags used together in the same tweet, with edge width
    representing frequency. Only the most connected component is shown.

    Preconditions:
    - `df` must contain a 'hashtags' column with comma-separated hashtags.
    - `max_nodes` > 0
    """
    hashtag_graph = nx.Graph()
    edge_weights = defaultdict(int)

    for hashtags in df[HASHTAG_COL].dropna():
        tags = [tag.strip() for tag in hashtags.split(',') if tag and tag.lower() != 'nan']
        for i in range(len(tags)):
            for j in range(i + 1, len(tags)):
                edge = tuple(sorted([tags[i], tags[j]]))
                edge_weights[edge] += 1

    for (tag1, tag2), weight in edge_weights.items():
        hashtag_graph.add_edge(tag1, tag2, weight=weight)

    if hashtag_graph.number_of_edges() == 0:
        print("No hashtags to form connections.")
        return

    largest_cc = max(nx.connected_components(hashtag_graph), key=len)
    sub_hash_graph = hashtag_graph.subgraph(list(largest_cc)).copy()

    top_nodes = sorted(sub_hash_graph.degree, key=lambda x: x[1], reverse=True)[:max_nodes]
    focus_nodes = [n for n, _ in top_nodes]
    focus_sub_graph = sub_hash_graph.subgraph(focus_nodes)

    edge_widths = [focus_sub_graph[u][v]['weight'] for u, v in focus_sub_graph.edges()]

    plt.figure(figsize=(12, 10))
    pos = nx.spring_layout(focus_sub_graph, seed=42)
    nx.draw_networkx_nodes(focus_sub_graph, pos, node_size=700, node_color='lightgreen')
    nx.draw_networkx_labels(focus_sub_graph, pos, font_size=10)
    nx.draw_networkx_edges(focus_sub_graph, pos, width=edge_widths, edge_color='gray')
    plt.title("Interactive Hashtag Co-occurrence Network (Weighted)")
    plt.axis('off')
    plt.tight_layout()
    plt.show()


def plot_engagement_distribution(df: pd.DataFrame, limit: int) -> None:
    """Show a histogram for tweet engagement (likes, reposts, replies) with clipping.

    Allows switching between metrics using an interactive radio button UI.

    Preconditions:
    - `df` must contain numeric columns: 'likes', 'reposts', and 'replies'.
    - `limit` > 0
    """
    filtered_df = df.copy()
    filtered_df[['likes', 'reposts', 'replies']] = filtered_df[['likes', 'reposts', 'replies']].clip(upper=limit)

    def update(label) -> None:
        """
        Update the histogram plot based on the selected engagement metric.

        Preconditions:
            - label must be one of 'likes', 'reposts', or 'replies'.
            - filtered_df must be a pandas DataFrame accessible in the enclosing scope.
            - ax must be a matplotlib Axes object in the enclosing scope.
        """

        ax.clear()
        ax.hist(filtered_df[label], bins=30, edgecolor='black', alpha=0.7)
        ax.set_title(f"Engagement Distribution: {label.capitalize()})")
        ax.set_xlabel(f"The number of {label}")
        ax.set_ylabel("The amount of tweets")
        plt.draw()

    ax = plt.subplots(figsize=(10, 6))[1]
    plt.subplots_adjust(left=0.3)

    dropdown_ax = plt.axes((0.05, 0.4, 0.15, 0.15))
    dropdown = widgets.RadioButtons(dropdown_ax, ('likes', 'reposts', 'replies'))
    dropdown.on_clicked(update)

    update('likes')
    plt.show()


def plot_reply_leaderboard(df: pd.DataFrame, top_n: int = 15) -> None:
    """Display a bar chart of users who received the most replies.

    Aggregates total replies received per user and visualizes the top N.

    Preconditions:
    - `df` must contain 'user_posted' and 'replies' columns.
    - `top_n` > 0
    """
    reply_sums = df.groupby(USER_COL)['replies'].sum().sort_values(ascending=False).head(top_n)

    if reply_sums.empty:
        print("No reply data available.")
        return

    plt.figure(figsize=(12, 6))
    reply_sums.plot(kind='bar', color='orange')
    plt.title(f"Top {top_n} Users by Total Replies Received")
    plt.ylabel("Replies")
    plt.xlabel("User")
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.show()


def generate_hashtag_wordcloud(df: pd.DataFrame) -> None:
    """Generate and display a word cloud of all hashtags used in the dataset.

    Size of each hashtag is proportional to its frequency. Hashtags are split, stripped, and filtered from nulls.

    Preconditions:
    - `df` must contain a 'hashtags' column with comma-separated values.
    """

    all_hashtags = df[HASHTAG_COL].dropna().str.split(',').explode().str.strip()
    text = ' '.join(tag for tag in all_hashtags if tag.lower() != 'nan')
    if not text:
        print("No hashtags available for word cloud.")
        return

    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text)
    plt.figure(figsize=(10, 6))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis("off")
    plt.title("Hashtag Word Cloud")
    plt.tight_layout()
    plt.show()


def plot_top_mentioned_users(df: pd.DataFrame, top_n: int = 10) -> None:
    """Visualize the most frequently mentioned users in a bar chart.

    Mentions are parsed from the 'tagged_users' column.

    Preconditions:
    - `df` must contain a 'tagged_users' column with comma-separated usernames.
    - `top_n` must be a positive integer.
    """
    mentioned_counts = Counter()

    for tags in df[TAGGED_USERS_COL].dropna():
        for tag in str(tags).split(','):
            tag = tag.strip()
            if tag and tag.lower() != 'nan':
                mentioned_counts[tag] += 1

    if not mentioned_counts:
        print("No mentions found.")
        return

    top_mentions = pd.Series(dict(mentioned_counts)).sort_values(ascending=False).head(top_n)

    plt.figure(figsize=(10, 6))
    top_mentions.plot(kind='bar', color='skyblue')
    plt.title(f"Top {top_n} Most Mentioned Users")
    plt.ylabel("Times Mentioned")
    plt.xlabel("User")
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.show()


def plot_influence_scores(df: pd.DataFrame, top_n: int = 10) -> None:
    """Calculate and plot influence scores (likes + reposts + replies) for users.

    Users are ranked by total engagement to show top influencers.

    Preconditions:
    - `df` must contain columns: 'likes', 'reposts', 'replies', and 'user_posted'.
    - `top_n` > 0
    """
    if not all(col in df.columns for col in ['likes', 'reposts', 'replies']):
        print("Missing one or more engagement columns: likes, reposts, replies.")
        return

    df_copy = df.copy()
    df_copy['influence'] = df_copy[['likes', 'reposts', 'replies']].sum(axis=1)
    influence_scores = df_copy.groupby(USER_COL)['influence'].sum().sort_values(ascending=False).head(top_n)

    if influence_scores.empty:
        print("No influence data available.")
        return

    plt.figure(figsize=(10, 6))
    influence_scores.plot(kind='bar', color='mediumseagreen')
    plt.title(f"Top {top_n} Users by Total Influence Score")
    plt.ylabel("Influence (likes + reposts + replies)")
    plt.xlabel("User")
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":

    python_ta.check_all(config={
        'extra-imports': ['pandas', 'networkx', 'matplotlib.pyplot', 'matplotlib.widgets', 'wordcloud', 'collections'],
        'allowed-io': ['plot_influence_scores', 'plot_top_mentioned_users', 'generate_hashtag_wordcloud',
                       'plot_reply_leaderboard', 'plot_hashtag_cooccurrence', 'plot_user_hashtag_graph'],
        'max-line-length': 160,
        'max-function-name-length': 40
    })
