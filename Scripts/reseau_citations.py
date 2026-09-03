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

# Disposition circulaire chronologique : les nœuds sont placés sur un cercle dans l'ordre des années
import math
order = sorted(ids, key=lambda i: (years_ := dict(zip(top["id"], top["year"])))[i])
years = dict(zip(top["id"], top["year"]))
order = sorted(ids, key=lambda i: (years[i], i))
n = len(order)
pos = {i: (math.cos(2 * math.pi * k / n), math.sin(2 * math.pi * k / n)) for k, i in enumerate(order)}
indeg = dict(G.in_degree())
sizes = {i: 120 + 110 * indeg[i] for i in ids}
fig, ax = plt.subplots(figsize=(13, 13))
nx.draw_networkx_edges(G, pos, ax=ax, arrows=True, arrowstyle="-|>", arrowsize=7, edge_color="#9a9a9a", width=0.5, alpha=0.6,
                       connectionstyle="arc3,rad=0.25", node_size=[sizes[i] for i in G.nodes()], min_source_margin=4, min_target_margin=6)
nx.draw_networkx_nodes(G, pos, ax=ax, nodelist=ids, node_size=[sizes[i] for i in ids], node_color="#1f1f1f", alpha=0.9)
for k, i in enumerate(order):
    ang = 360 * k / n
    x, y = pos[i]
    r = 1.13 + 0.004 * indeg[i]
    ha = "left" if math.cos(math.radians(ang)) >= 0 else "right"
    rot = ang if ha == "left" else ang - 180
    ax.text(r * x, r * y, f"{lab[i]}  ({indeg[i]})", rotation=rot, rotation_mode="anchor", ha=ha, va="center", fontsize=9.5, family="serif")
ax.set_xlim(-1.7, 1.7); ax.set_ylim(-1.7, 1.7); ax.set_aspect("equal"); ax.axis("off")
ax.set_title("Réseau de citations entre les 30 lectures les plus pertinentes\nOrdre chronologique sur le cercle ; flèche : « cite » ;\ntaille du point et nombre entre parenthèses : citations reçues des autres lectures du top 30",
             fontsize=11.5, fontweight="bold")
plt.tight_layout()
fig.savefig(os.path.join(ROOT, "Graphiques", "reseau_citations_top30.png"), dpi=200)
print(nodes.sort_values("cite_par_top30", ascending=False).to_string(index=False))
print("arêtes :", len(edges))
