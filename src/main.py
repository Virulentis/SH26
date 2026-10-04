import pandas as pd
import numpy as np 
import networkx as nx
import classes
import scipy
from itertools import combinations
import re



def add_edges(df: pd.DataFrame, Edges: classes.CardGraph, config: dict) -> classes.CardGraph:
    
    
    if "mana_cost" in config:
        for mana_cost, frame in df.groupby('mana_cost')["oracle_id"]:
            for a, b in combinations(frame, 2):
                Edges.add(a, b, config["mana_cost_weight"])
                print(f"Added edge between {a} and {b} with weight {config['mana_cost_weight']} with mana_cost {mana_cost}")

    if "artist" in config:
        for artist, frame in df.groupby('artist')["oracle_id"]:
            for a, b in combinations(frame, 2):
                Edges.add(a, b, config["artist_weight"])
                print(f"Added edge between {a} and {b} with weight {config['artist_weight']} with artist {artist}")

    if "keywords" in config:
        for keyword, frame in df.explode("keywords").groupby("keywords")["oracle_id"]:
            for a, b in combinations(frame, 2):
                Edges.add(a, b, config["keywords_weight"])
                print(f"Added edge between {a} and {b} with weight {config['keywords_weight']} with keyword {keyword}")

    if "creature_types" in config:
        
        temp_df = df[df['type_line'].str.contains('Creature')]
        temp_df['creature_types'] = temp_df['type_line'].str.extract(r'Creature\s*—\s*(.*)')[0].str.split(' ')
        
        for creature_type, frame in temp_df.explode("creature_types").groupby("creature_types")["oracle_id"]:
            for a, b in combinations(frame, 2):
                Edges.add(a, b, config["creature_types_weight"])
                print(f"Added edge between {a} and {b} with weight {config['creature_types_weight']} with creature_type {creature_type}")

    if "type" in config:
        temp_df['type'] = df['type_line'].str.extract(r'^(.*?)(?:\s*—\s*.*)?$')[0].str.split(' ')
        

        for type_, frame in temp_df.explode("type").groupby("type")["oracle_id"]:
            for a, b in combinations(frame, 2):
                Edges.add(a, b, config["type_weight"])
                print(f"Added edge between {a} and {b} with weight {config['type_weight']} with type {type_}")
        
            
    return Edges

def hex_to_rgb(h: str) -> dict:
    h = h.lstrip("#")
    return {"r": int(h[0:2], 16), "g": int(h[2:4], 16), "b": int(h[4:6], 16), "a": 1.0}

def display_color(color_identity: list[str]) -> str:
    if len(color_identity) == 0:
        return "#6e6a6a" # gray for colorless
    if len(color_identity) > 1:
        return "#d4af37" # gold for multicolor
    if color_identity[0] == "W":
        return "#d1c9c9" # white
    if color_identity[0] == "U":
        return "#1e90ff" # blue
    if color_identity[0] == "B":
        return "#000000" # black
    if color_identity[0] == "R":
        return "#ff0000" # red
    if color_identity[0] == "G":
        return "#00ff00" # green
    return "#ff09eb"

def export(Edges: classes.CardGraph, threshold: float = 0.0, df: pd.DataFrame = None   ) -> None:
    nx_graph = nx.Graph()
    Edges_list = Edges.edges(threshold=threshold)
    nx_graph.add_weighted_edges_from(
        [(edge["source"], edge["target"], edge["weight"]) for edge in Edges_list]
    )

    if df is not None:
        for row in df.itertuples(index=False):
            color = display_color(row.color_identity)
            nx_graph.add_node(row.oracle_id, label=row.name, color=color, viz={"color": hex_to_rgb(color)})

    nx_graph.graph["name"] = "Card Graph"

    pr = nx.pagerank(nx_graph, weight="weight")
    pos = nx.spring_layout(nx_graph, weight="weight", seed=42)

    for n, d in nx_graph.nodes(data=True):
        size = 3 + 300 * pr.get(n, 0)
        x, y = float(pos[n][0]) * 1000, float(pos[n][1]) * 1000
        d.update(size=size, x=x, y=y)
        viz = d.setdefault("viz", {})
        viz["size"] = size
        viz["position"] = {"x": x, "y": y, "z": 0.0}
        
    nx.write_gexf(nx_graph, "cards.gexf")



pd.set_option('display.max_columns', None)
df = pd.read_json("./Data/oracle.jsonl", lines=True)
# cut_df = df.sample(n=300, random_state=42)
cut_df = df.sample(n=300, random_state=42)
print(cut_df.head(40)['type_line'])
config = {
    "mana_cost": False,
    "artist": False,
    "keywords": False,
    "creature_types": True,
    "type": True,
    "mana_cost_weight": 1.0,
    "artist_weight": 1.0,
    "keywords_weight": 1.0,
    "creature_types_weight": 1.0,
    "type_weight": 1.0

}




Edges = classes.CardGraph()
Edges = add_edges(cut_df, Edges, config)
export(Edges, threshold=1.0, df=cut_df)