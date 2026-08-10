import pandas as pd
import os

# Project folder
base_folder = r"C:\Users\varsh\OneDrive\Attachments\Desktop\Knowledge_Graph_Project"

node_frames = []
edge_frames = []

subjects = ["ADA", "CN", "DSA", "ML", "OS", "SEPM"]

for subject in subjects:

    subject_folder = os.path.join(base_folder, subject)

    node_file = f"{subject.lower()}_nodes.csv"
    edge_file = f"{subject.lower()}_edges.csv"

    node_path = os.path.join(subject_folder, node_file)
    edge_path = os.path.join(subject_folder, edge_file)

    # ---------- NODES ----------
    if os.path.exists(node_path):

        print(f"Found Nodes: {node_path}")

        try:
            nodes = pd.read_csv(node_path, encoding="utf-8")
        except UnicodeDecodeError:
            nodes = pd.read_csv(node_path, encoding="latin1")

        nodes["subject"] = subject
        node_frames.append(nodes)

    else:
        print(f"Missing Nodes: {node_path}")

    # ---------- EDGES ----------
    if os.path.exists(edge_path):

        print(f"Found Edges: {edge_path}")

        try:
            edges = pd.read_csv(edge_path, encoding="utf-8")
        except UnicodeDecodeError:
            edges = pd.read_csv(edge_path, encoding="latin1")

        edges["subject"] = subject
        edge_frames.append(edges)

    else:
        print(f"Missing Edges: {edge_path}")

# ---------- VALIDATION ----------
if len(node_frames) == 0:
    raise ValueError("No node files found!")

if len(edge_frames) == 0:
    raise ValueError("No edge files found!")

# ---------- MERGE ----------
master_nodes = pd.concat(node_frames, ignore_index=True)
master_edges = pd.concat(edge_frames, ignore_index=True)

# Remove duplicate nodes based on id
if "id" in master_nodes.columns:
    master_nodes = master_nodes.drop_duplicates(subset=["id"])

# Remove duplicate edges
master_edges = master_edges.drop_duplicates()

# ---------- SAVE ----------
merged_folder = os.path.join(base_folder, "MERGED")
os.makedirs(merged_folder, exist_ok=True)

nodes_output = os.path.join(merged_folder, "master_nodes.csv")
edges_output = os.path.join(merged_folder, "master_edges.csv")

master_nodes.to_csv(nodes_output, index=False, encoding="utf-8")
master_edges.to_csv(edges_output, index=False, encoding="utf-8")

print("\n==============================")
print("MERGE COMPLETED SUCCESSFULLY")
print("==============================")
print(f"Total Nodes : {len(master_nodes)}")
print(f"Total Edges : {len(master_edges)}")
print(f"\nSaved:")
print(nodes_output)
print(edges_output)