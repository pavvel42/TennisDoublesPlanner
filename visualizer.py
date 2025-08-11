import matplotlib.pyplot as plt
import networkx as nx
import seaborn as sns
import pandas as pd

def visualize_schedule(schedule, player_map):
    G = nx.Graph()
    G.add_nodes_from(player_map.values())

    colors = plt.cm.get_cmap('hsv', len(schedule) + 1)
    pos = nx.circular_layout(G)
    
    plt.figure(figsize=(10, 8))
    for i, match_teams in enumerate(schedule): # match_teams is ((name1, name2), (name3, name4))
        team1 = match_teams[0]
        team2 = match_teams[1]
        
        # Draw team 1
        nx.draw_networkx_edges(G, pos, edgelist=[team1], edge_color=colors(i), width=2.0, label=f'Match {i+1} Team 1')
        # Draw team 2 with a slightly different color or style
        nx.draw_networkx_edges(G, pos, edgelist=[team2], edge_color=colors(i + 0.5), width=2.0, label=f'Match {i+1} Team 2')

    nx.draw_networkx_nodes(G, pos, node_color='lightblue', node_size=700)
    nx.draw_networkx_labels(G, pos, font_size=10)
    plt.title("Tournament Schedule - Match Teams")
    plt.legend()
    plt.show(block=False)
    plt.pause(3)
    plt.close()

def visualize_frequency_matrices(player_names, partner_counts, opponent_counts):
    # Partner Counts Heatmap
    plt.figure(figsize=(8, 6))
    df_partner = pd.DataFrame(partner_counts, index=player_names, columns=player_names)
    sns.heatmap(df_partner, annot=True, cmap='Blues', fmt='g')
    plt.title("Partnering Frequency")
    plt.show(block=False)
    plt.pause(3)
    plt.close()

    # Opponent Counts Heatmap
    plt.figure(figsize=(8, 6))
    df_opponent = pd.DataFrame(opponent_counts, index=player_names, columns=player_names)
    sns.heatmap(df_opponent, annot=True, cmap='Reds', fmt='g')
    plt.title("Opponent Frequency")
    plt.show(block=False)
    plt.pause(3)
    plt.close()
