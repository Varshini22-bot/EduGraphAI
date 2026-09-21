import os
import pandas as pd

script_dir = os.path.dirname(os.path.abspath(__file__))
base_folder = os.path.abspath(os.path.join(script_dir, ".."))

merged_folder = os.path.join(base_folder, "MERGED")
if not os.path.exists(os.path.join(merged_folder, "master_nodes.csv")):
    merged_folder = os.path.join(base_folder, "data", "MERGED")

nodes = pd.read_csv(os.path.join(merged_folder, "master_nodes.csv"))
edges = pd.read_csv(os.path.join(merged_folder, "master_edges.csv"))

node_ids = set(nodes["id"])

missing = []

for _, row in edges.iterrows():

    if row["source"] not in node_ids:
        missing.append(row["source"])

    if row["target"] not in node_ids:
        missing.append(row["target"])

missing = sorted(set(missing))

print("\nMissing Nodes:")
print(missing)
print(f"\nTotal Missing = {len(missing)}")