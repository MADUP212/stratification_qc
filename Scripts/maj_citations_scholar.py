#!/usr/bin/env python3
"""Injecte des comptes de citations Google Scholar dans le corpus, puis relance le score.

Usage :
  1. Remplir Data/citations_google_scholar.csv (colonnes : id, citations_google_scholar, date) — par exemple à partir de
     l'extension Zotero « Citation Counts Manager » (colonne « Citation count ») ou de Publish or Perish.
  2. python3 Scripts/maj_citations_scholar.py
  3. python3 Scripts/score_snowballing.py && python3 Scripts/reseau_citations.py && python3 Scripts/export_zotero.py
"""
import csv, json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV = os.path.join(ROOT, "Data", "citations_google_scholar.csv")
CORPUS = os.path.join(ROOT, "Data", "corpus.json")

if not os.path.exists(CSV):
    sys.exit(f"fichier absent : {CSV}")
corpus = json.load(open(CORPUS, encoding="utf-8"))
byid = {e["id"]: e for e in corpus}
n = 0
with open(CSV, encoding="utf-8-sig") as f:
    for row in csv.DictReader(f):
        i = row["id"].strip()
        val = row.get("citations_google_scholar", "").strip()
        if i in byid and val:
            byid[i]["number_citations"] = int(float(val))
            byid[i]["citations_source"] = f"Google Scholar {row.get('date', '').strip()}".strip()
            n += 1
        elif i not in byid:
            print("id inconnu :", i)
json.dump(corpus, open(CORPUS, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"{n} comptes Google Scholar injectés ; relancer Scripts/score_snowballing.py")
