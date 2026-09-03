#!/usr/bin/env python3
"""Gestion de la grille de snowballing.

Usage :
  python3 Scripts/grille.py add   < fragment.json   # liste d'entrées (dict) ; fusion par id
  python3 Scripts/grille.py cite  < fragment.json   # {"id_citant": ["id_cité", ...]}
  python3 Scripts/grille.py show  [id ...]
  python3 Scripts/grille.py stats
  python3 Scripts/grille.py missing                 # champs manquants
"""
import json, sys, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CORPUS = os.path.join(ROOT, "Data", "corpus.json")
BIBLIO = os.path.join(ROOT, "Data", "bibliographies.json")

FIELDS = ["id", "author", "year", "title", "journal", "type", "doi", "url",
          "number_citations", "citations_source", "round", "direction", "found_via",
          "c1", "c2", "c3", "c4", "statut", "notes", "langue"]

def load(path, default):
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return default

def save(path, obj):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)

def cmd_add():
    corpus = load(CORPUS, [])
    byid = {e["id"]: e for e in corpus}
    new = json.load(sys.stdin)
    added, updated = [], []
    for e in new:
        if "id" not in e:
            sys.exit("entrée sans id: %r" % e)
        if e["id"] in byid:
            byid[e["id"]].update({k: v for k, v in e.items() if v not in (None, "")})
            updated.append(e["id"])
        else:
            for k in FIELDS:
                e.setdefault(k, None)
            corpus.append(e)
            byid[e["id"]] = e
            added.append(e["id"])
    save(CORPUS, corpus)
    print("ajoutés:", added)
    if updated:
        print("mis à jour:", updated)
    print("total corpus:", len(corpus))

def cmd_cite():
    corpus = load(CORPUS, [])
    ids = {e["id"] for e in corpus}
    bib = load(BIBLIO, {})
    new = json.load(sys.stdin)
    for citing, cited in new.items():
        if citing not in ids:
            print("AVERTISSEMENT: citant inconnu", citing)
        bad = [c for c in cited if c not in ids]
        if bad:
            print("AVERTISSEMENT: cités inconnus pour", citing, ":", bad)
        cur = set(bib.get(citing, []))
        cur.update(c for c in cited if c in ids and c != citing)
        bib[citing] = sorted(cur)
    save(BIBLIO, bib)
    print("bibliographies enregistrées:", len(bib))

def recurrence():
    corpus = load(CORPUS, [])
    bib = load(BIBLIO, {})
    rec = {e["id"]: 0 for e in corpus}
    for citing, cited in bib.items():
        for c in cited:
            if c in rec:
                rec[c] += 1
    return rec

def cmd_show(ids):
    corpus = load(CORPUS, [])
    rec = recurrence()
    for e in corpus:
        if ids and e["id"] not in ids:
            continue
        print(f'{e["id"]:28s} {str(e.get("year")):5s} rec={rec[e["id"]]:2d} cit={e.get("number_citations")} | {e.get("author")} — {str(e.get("title"))[:80]}')

def cmd_stats():
    corpus = load(CORPUS, [])
    bib = load(BIBLIO, {})
    rec = recurrence()
    print("corpus:", len(corpus), "| bibliographies dépouillées:", len(bib))
    from collections import Counter
    print("par ronde/direction:", Counter((e.get("round"), e.get("direction")) for e in corpus))
    print("par statut:", Counter(e.get("statut") for e in corpus))
    top = sorted(rec.items(), key=lambda x: -x[1])[:15]
    print("récurrence max:", top)

def cmd_missing():
    corpus = load(CORPUS, [])
    for e in corpus:
        miss = [k for k in ("author", "year", "title", "number_citations", "doi") if e.get(k) in (None, "")]
        if miss:
            print(e["id"], "manque:", miss)

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "stats"
    if cmd == "add": cmd_add()
    elif cmd == "cite": cmd_cite()
    elif cmd == "show": cmd_show(sys.argv[2:])
    elif cmd == "stats": cmd_stats()
    elif cmd == "missing": cmd_missing()
    else: sys.exit(__doc__)
