#!/usr/bin/env python3
"""Réseau de citations entre les 30 lectures les plus pertinentes.

Nœud = publication (étiquette auteur-année) ; arête orientée = « cite » (citant -> cité), d'après Data/bibliographies.json ;
taille du point proportionnelle au nombre de fois où la publication est citée par les autres membres du top 30 (degré entrant).
Produit Data/reseau_citations_top30_noeuds.csv, Data/reseau_citations_top30_aretes.csv et Graphiques/reseau_citations_top30.png.
"""
import os, json
import pandas as pd
import networkx as nx
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
top = pd.read_csv(os.path.join(ROOT, "Data", "grille_snowballing_top30.csv"), encoding="utf-8-sig")
bib = json.load(open(os.path.join(ROOT, "Data", "bibliographies.json"), encoding="utf-8"))
ids = list(top["id"])
lab = dict(zip(top["id"], top["citationAuteurAnnee"].str.strip("()")))

G = nx.DiGraph()
for i in ids:
    G.add_node(i)
edges = [(citant, cite) for citant in ids for cite in bib.get(citant, []) if cite in ids and cite != citant]
G.add_edges_from(edges)

nodes = pd.DataFrame({"id": ids, "etiquette": [lab[i] for i in ids], "annee": top["year"].values,
                      "cite_par_top30": [G.in_degree(i) for i in ids], "cite_top30": [G.out_degree(i) for i in ids],
                      "recurrence_corpus": top["recurrence"].values, "indice": top["score"].values})
nodes.to_csv(os.path.join(ROOT, "Data", "reseau_citations_top30_noeuds.csv"), index=False, encoding="utf-8-sig")
pd.DataFrame(edges, columns=["citant", "cite"]).assign(citant_etiquette=lambda d: d["citant"].map(lab), cite_etiquette=lambda d: d["cite"].map(lab)) \
  .to_csv(os.path.join(ROOT, "Data", "reseau_citations_top30_aretes.csv"), index=False, encoding="utf-8-sig")

# Disposition en réseau (force-directed, Fruchterman-Reingold) : les publications qui se citent sont rapprochées
indeg = dict(G.in_degree())
pos = nx.spring_layout(G.to_undirected(), seed=11, k=1.6, iterations=800, weight=None)
sizes = [70 + 62 * indeg[i] for i in ids]                    # plus grand point = plus cité dans le top 30
fig, ax = plt.subplots(figsize=(16, 13))
nx.draw_networkx_edges(G, pos, ax=ax, arrows=True, arrowstyle="-|>", arrowsize=8, edge_color="#8c8c8c", alpha=0.35, width=0.5,
                       connectionstyle="arc3,rad=0.12", node_size=sizes, min_source_margin=4, min_target_margin=6)
nx.draw_networkx_nodes(G, pos, ax=ax, node_size=sizes, node_color="#1f1f1f", alpha=0.92)
import math
for k, i in enumerate(ids):
    x, y = pos[i]
    dy = 5 + math.sqrt(sizes[k]) / 2.2
    ax.annotate(f"{lab[i]} ({indeg[i]})", (x, y), xytext=(0, dy), textcoords="offset points", ha="center", va="bottom",
                fontsize=8, family="serif",
                bbox=dict(boxstyle="round,pad=0.12", fc="white", ec="none", alpha=0.7))
ax.set_axis_off()
ax.set_title("Réseau de citations entre les 30 lectures les plus pertinentes\n"
             "Disposition force-directed : les publications qui se citent sont rapprochées ; flèche : « cite » ;\n"
             "taille du point et nombre entre parenthèses : citations reçues des autres lectures du top 30",
             fontsize=11.5, fontweight="bold")
ax.margins(0.08)
plt.tight_layout()
fig.savefig(os.path.join(ROOT, "Graphiques", "reseau_citations_top30.png"), dpi=200)
print(nodes.sort_values("cite_par_top30", ascending=False).to_string(index=False))
print("arêtes :", len(edges))
