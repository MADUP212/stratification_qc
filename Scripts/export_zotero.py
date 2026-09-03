#!/usr/bin/env python3
"""Exporte le corpus pour Zotero : RIS, BibTeX et CSL-JSON (DOI/URL inclus pour la récupération des PDF).
Fichiers produits : Zotero/corpus_snowballing.{ris,bib,json} et Zotero/top30_snowballing.{ris,bib,json}
"""
import json, os, re
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
df = pd.read_csv(os.path.join(ROOT, "Data", "grille_snowballing.csv"), encoding="utf-8-sig")

RIS_TYPE = {"article": "JOUR", "book": "BOOK", "chapter": "CHAP", "report": "RPRT"}
BIB_TYPE = {"article": "article", "book": "book", "chapter": "incollection", "report": "techreport"}
CSL_TYPE = {"article": "article-journal", "book": "book", "chapter": "chapter", "report": "report"}

def authors(s):
    out = []
    for a in str(s).split(";"):
        a = a.strip()
        if not a:
            continue
        a = re.sub(r"\s*\(dir\.\)", "", a)
        if "," in a:
            fam, giv = [x.strip() for x in a.split(",", 1)]
        else:
            fam, giv = a, ""
        out.append((fam, giv))
    return out

def s(v):
    return "" if (v is None or (isinstance(v, float) and pd.isna(v))) else str(v)

def to_ris(r):
    lines = [f"TY  - {RIS_TYPE.get(r['type'], 'GEN')}"]
    for fam, giv in authors(r["author"]):
        lines.append(f"AU  - {fam}, {giv}".rstrip(", "))
    lines.append(f"TI  - {r['title']}")
    lines.append(f"PY  - {int(r['year'])}")
    if s(r["journal"]):
        lines.append(("JO  - " if r["type"] == "article" else "T2  - ") + s(r["journal"]))
    if s(r["doi"]):
        lines.append(f"DO  - {r['doi']}")
    if s(r["url"]):
        lines.append(f"UR  - {r['url']}")
    lines.append(f"LA  - {s(r['langue'])}")
    lines.append(f"N1  - Snowballing id={r['id']} ; rang={r['rang']} ; score={r['score']} ; récurrence={r['recurrence']} ; citations={s(r['number_citations'])} ({s(r['citations_source'])})")
    if s(r["notes"]):
        lines.append(f"AB  - {r['notes']}")
    lines.append("ER  - ")
    return "\n".join(lines)

def bib_escape(t):
    return s(t).replace("&", "\\&").replace("%", "\\%")

def to_bib(r):
    key = r["id"]
    auth = " and ".join(f"{fam}, {giv}".rstrip(", ") for fam, giv in authors(r["author"]))
    fields = [f"  author = {{{auth}}}", f"  title = {{{bib_escape(r['title'])}}}", f"  year = {{{int(r['year'])}}}"]
    j = bib_escape(r["journal"])
    if j:
        if r["type"] == "article":
            fields.append(f"  journal = {{{j}}}")
        elif r["type"] == "chapter":
            fields.append(f"  booktitle = {{{j}}}")
        elif r["type"] == "report":
            fields.append(f"  institution = {{{j}}}")
        else:
            fields.append(f"  publisher = {{{j}}}")
    if s(r["doi"]):
        fields.append(f"  doi = {{{r['doi']}}}")
    if s(r["url"]):
        fields.append(f"  url = {{{r['url']}}}")
    fields.append(f"  note = {{Snowballing rang {r['rang']}, score {r['score']}, récurrence {r['recurrence']}}}")
    return f"@{BIB_TYPE.get(r['type'], 'misc')}{{{key},\n" + ",\n".join(fields) + "\n}"

def to_csl(r):
    item = {"id": r["id"], "type": CSL_TYPE.get(r["type"], "document"), "title": r["title"],
            "author": [{"family": fam, "given": giv} for fam, giv in authors(r["author"])],
            "issued": {"date-parts": [[int(r["year"])]]}, "language": s(r["langue"]),
            "note": f"Snowballing rang {r['rang']} ; score {r['score']} ; récurrence {r['recurrence']} ; citations {s(r['number_citations'])}"}
    if s(r["journal"]):
        item["container-title" if r["type"] in ("article", "chapter") else "publisher"] = r["journal"]
    if s(r["doi"]):
        item["DOI"] = r["doi"]
    if s(r["url"]):
        item["URL"] = r["url"]
    if s(r["notes"]):
        item["abstract"] = r["notes"]
    return item

os.makedirs(os.path.join(ROOT, "Zotero"), exist_ok=True)
for name, sub in (("corpus_snowballing", df), ("top30_snowballing", df.head(30))):
    with open(os.path.join(ROOT, "Zotero", name + ".ris"), "w", encoding="utf-8") as f:
        f.write("\n\n".join(to_ris(r) for _, r in sub.iterrows()) + "\n")
    with open(os.path.join(ROOT, "Zotero", name + ".bib"), "w", encoding="utf-8") as f:
        f.write("\n\n".join(to_bib(r) for _, r in sub.iterrows()) + "\n")
    with open(os.path.join(ROOT, "Zotero", name + ".json"), "w", encoding="utf-8") as f:
        json.dump([to_csl(r) for _, r in sub.iterrows()], f, ensure_ascii=False, indent=1)
print("exports Zotero écrits :", os.listdir(os.path.join(ROOT, "Zotero")))
print("DOI présents :", int(df["doi"].notna().sum()), "/", len(df), "| URL présentes :", int(df["url"].notna().sum()))
