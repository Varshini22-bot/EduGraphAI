import pandas as pd

nodes = pd.read_csv(r"C:\Users\varsh\OneDrive\Attachments\Desktop\Knowledge_Graph_Project\MERGED\master_nodes.csv")
edges = pd.read_csv(r"C:\Users\varsh\OneDrive\Attachments\Desktop\Knowledge_Graph_Project\MERGED\master_edges.csv")

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