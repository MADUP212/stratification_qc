#!/usr/bin/env python3
"""Calcule la récurrence, le score pondéré et exporte la grille (CSV/XLSX) + le graphique des 30 lectures.

Score = w_cit * minmax(log1p(citations)) + w_year * minmax(année) + w_pert * minmax(récurrence)
Pondération par défaut : w_cit = 0.35, w_year = 0.25, w_pert = 0.40 (voir Protocole/protocole_snowballing.md).
Les citations manquantes (littérature grise non indexée) sont imputées par la médiane du corpus et signalées
(colonne `citations_imputees`). À remplacer par les comptes Google Scholar avant publication.
"""
import json, os, math, sys
import pandas as pd
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W_CIT, W_YEAR, W_PERT = 0.35, 0.25, 0.40
TOP_N = 30

corpus = json.load(open(os.path.join(ROOT, "Data", "corpus.json"), encoding="utf-8"))
bib = json.load(open(os.path.join(ROOT, "Data", "bibliographies.json"), encoding="utf-8"))

rec = {e["id"]: 0 for e in corpus}
cited_by = {e["id"]: [] for e in corpus}
for citing, cited in bib.items():
    for c in cited:
        if c in rec:
            rec[c] += 1
            cited_by[c].append(citing)

df = pd.DataFrame(corpus)
if "author_short" not in df.columns:
    df["author_short"] = None
df["recurrence"] = df["id"].map(rec)
df["cite_par"] = df["id"].map(lambda i: "; ".join(sorted(cited_by[i])))
df["bibliographie_depouillee"] = df["id"].map(lambda i: int(i in bib))
df["pertinence_thematique"] = df[["c1", "c2", "c3", "c4"]].fillna(0).sum(axis=1)

# citations : imputation par la médiane des valeurs connues
df["number_citations"] = pd.to_numeric(df["number_citations"], errors="coerce")
df["citations_imputees"] = df["number_citations"].isna().astype(int)
med = df["number_citations"].median()
df["citations_utilisees"] = df["number_citations"].fillna(med)

def minmax(x):
    x = x.astype(float)
    if x.max() == x.min():
        return pd.Series(np.zeros(len(x)), index=x.index)
    return (x - x.min()) / (x.max() - x.min())

df["cit_norm"] = minmax(np.log1p(df["citations_utilisees"]))
df["year_norm"] = minmax(df["year"])
df["pert_norm"] = minmax(df["recurrence"])
df["score"] = (W_CIT * df["cit_norm"] + W_YEAR * df["year_norm"] + W_PERT * df["pert_norm"]).round(3)

# Citation auteur-année (style CLESSN)
def cit_auteur_annee(row):
    auteurs = [a.strip() for a in str(row["author"]).split(";") if a.strip()]
    first = auteurs[0].split(",")[0].strip() if auteurs else "?"
    if isinstance(row.get("author_short"), str) and row.get("author_short"):
        return f"({row['author_short']}, {row['year']})"   # forme courte des auteurs institutionnels
    if len(auteurs) == 1:
        return f"({first}, {row['year']})"
    if len(auteurs) == 2:
        second = auteurs[1].split(",")[0].strip()
        return f"({first} et {second}, {row['year']})"
    return f"({first} et al., {row['year']})"

df["citationAuteurAnnee"] = df.apply(cit_auteur_annee, axis=1)
df["titre_court"] = df["title"].str.slice(0, 58).where(df["title"].str.len() <= 58, df["title"].str.slice(0, 55).str.rstrip() + "...")
df["etiquette"] = df["titre_court"] + " " + df["citationAuteurAnnee"]

cols = ["id", "author", "author_short", "year", "title", "journal", "type", "langue", "doi", "url", "number_citations",
        "citations_source", "citations_imputees", "citations_utilisees", "recurrence", "cite_par",
        "bibliographie_depouillee", "round", "direction", "found_via", "statut", "c1", "c2", "c3", "c4",
        "pertinence_thematique", "cit_norm", "year_norm", "pert_norm", "score", "citationAuteurAnnee", "etiquette", "notes"]
df = df[cols].sort_values("score", ascending=False).reset_index(drop=True)
df.insert(0, "rang", range(1, len(df) + 1))

os.makedirs(os.path.join(ROOT, "Data"), exist_ok=True)
df["rang_inclus"] = df["statut"].eq("inclus").cumsum().where(df["statut"].eq("inclus"))
df.to_csv(os.path.join(ROOT, "Data", "grille_snowballing.csv"), index=False, encoding="utf-8-sig")
top = df[df["statut"] == "inclus"].head(TOP_N)  # seules les publications satisfaisant les critères d'inclusion sont classées
top.to_csv(os.path.join(ROOT, "Data", "grille_snowballing_top30.csv"), index=False, encoding="utf-8-sig")

params = pd.DataFrame({
    "parametre": ["w_cit", "w_year", "w_pert", "citations : transformation", "citations manquantes",
                  "année : normalisation", "pertinence : définition", "source des citations", "date"],
    "valeur": [W_CIT, W_YEAR, W_PERT, "log(1 + citations) puis min-max",
               f"imputées par la médiane du corpus ({med:.0f}) et signalées (citations_imputees = 1)",
               "min-max (1 = plus récente, 0 = plus ancienne)",
               "nombre de bibliographies du corpus (98 dépouillées) citant la publication, min-max",
               "Consensus / Semantic Scholar (proxy de Google Scholar, à mettre à jour)", "2026-09-03"]})
with pd.ExcelWriter(os.path.join(ROOT, "Data", "grille_snowballing.xlsx")) as xw:
    df.to_excel(xw, sheet_name="grille", index=False)
    top.to_excel(xw, sheet_name="top30", index=False)
    params.to_excel(xw, sheet_name="parametres", index=False)

# Graphique (rendu Python de secours ; le rendu officiel est dans CodeR/graphique_snowballing.R)
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
plt.rcParams["font.family"] = "serif"
top_plot = top.iloc[::-1]
fig, ax = plt.subplots(figsize=(13, 11))
ax.hlines(y=range(len(top_plot)), xmin=0, xmax=top_plot["score"], color="#9e9e9e", linewidth=1)
ax.plot(top_plot["score"], range(len(top_plot)), "o", color="#1f1f1f", markersize=7)
ax.set_yticks(range(len(top_plot)))
ax.set_yticklabels(top_plot["etiquette"], fontsize=10)
ax.set_xlabel("Indice de pertinence\n(citations 0,35 ; année 0,25 ; récurrence 0,40)", fontsize=11, fontweight="bold")
ax.set_xlim(0, 1)
ax.set_title("Les 30 lectures les plus pertinentes\nÉcart de revenu et de statut francophones/anglophones au Québec, 1961-2021", fontsize=12, fontweight="bold", loc="right")
ax.grid(False)
for s in ["top", "right"]:
    ax.spines[s].set_visible(False)
plt.tight_layout()
os.makedirs(os.path.join(ROOT, "Graphiques"), exist_ok=True)
fig.savefig(os.path.join(ROOT, "Graphiques", "lectures_snowballing_top30.png"), dpi=200)
print(top[["rang", "id", "year", "number_citations", "recurrence", "score"]].to_string(index=False))
print("\nmédiane citations imputée:", med, "| n imputés:", int(df["citations_imputees"].sum()))
