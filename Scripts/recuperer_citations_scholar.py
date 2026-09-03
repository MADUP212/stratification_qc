#!/usr/bin/env python3
"""Récupère les comptes de citations Google Scholar des références du corpus (à lancer sur votre poste).

Même mécanisme que le serveur MCP JackKuo666/Google-Scholar-MCP-Server (bibliothèque `scholarly`), mais en lot :
pour chaque publication de Data/corpus.json, recherche du titre dans Google Scholar, choix du meilleur résultat
(similarité de titre + année) et écriture de `num_citations` dans Data/citations_google_scholar.csv, que
Scripts/maj_citations_scholar.py injecte ensuite dans le corpus.

Installation :  pip install scholarly            (Python >= 3.8 ; si bibtexparser refuse de se compiler :
                pip install "bibtexparser<2" puis pip install --no-deps scholarly)
Usage :         python3 Scripts/recuperer_citations_scholar.py [--seulement-manquants] [--top30] [--pause 8]
                --reprendre : ne réinterroge pas les ids déjà remplis dans le CSV.
Google Scholar n'a pas de quota officiel mais bloque une adresse IP après 20 à 50 requêtes rapprochées (blocage de
15 min à plusieurs heures) : le script s'arrête au premier blocage ; attendre, changer de réseau ou utiliser --proxy,
puis relancer avec --reprendre. Rien n'est envoyé ailleurs que vers Google Scholar (et le proxy choisi).
"""
import argparse, csv, datetime, difflib, json, os, re, sys, time, unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CORPUS = os.path.join(ROOT, "Data", "corpus.json")
CSV = os.path.join(ROOT, "Data", "citations_google_scholar.csv")
TOP30 = os.path.join(ROOT, "Data", "grille_snowballing_top30.csv")


def normaliser(t):
    t = unicodedata.normalize("NFKD", str(t)).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9 ]+", " ", t.lower()).strip()


def meilleur_resultat(resultats, titre, annee):
    """Choisit le résultat dont le titre ressemble le plus (>= 0,6) au titre cherché ; l'année départage."""
    meilleur, score_max = None, 0.0
    for r in resultats:
        bib = r.get("bib", {}) if isinstance(r, dict) else {}
        s = difflib.SequenceMatcher(None, normaliser(bib.get("title", "")), normaliser(titre)).ratio()
        try:
            if annee and abs(int(str(bib.get("pub_year", "0"))[:4]) - int(annee)) <= 1:
                s += 0.1
        except ValueError:
            pass
        if s > score_max:
            meilleur, score_max = r, s
    return (meilleur, round(score_max, 2)) if score_max >= 0.6 else (None, round(score_max, 2))


def chercher(titre, annee, n=5):
    from scholarly import scholarly
    q = scholarly.search_pubs(titre)
    out = []
    for _ in range(n):
        try:
            out.append(next(q))
        except StopIteration:
            break
    return meilleur_resultat(out, titre, annee)


def sauvegarder(deja, corpus, byid):
    with open(CSV, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["id", "citations_google_scholar", "date", "author", "year", "title", "titre_scholar", "similarite"])
        w.writeheader()
        for j in [e["id"] for e in corpus]:
            w.writerow({c: deja.get(j, {"id": j, "author": byid[j]["author"], "year": byid[j]["year"], "title": byid[j]["title"]}).get(c, "") for c in w.fieldnames})


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seulement-manquants", action="store_true", help="ids sans number_citations dans corpus.json")
    ap.add_argument("--top30", action="store_true", help="seulement les 30 lectures classées")
    ap.add_argument("--reprendre", action="store_true", help="ne pas réinterroger les ids déjà remplis dans le CSV")
    ap.add_argument("--pause", type=float, default=20.0, help="secondes entre deux requêtes (20 s par défaut)")
    ap.add_argument("--proxy", choices=["aucun", "free", "scraperapi", "tor"], default="aucun",
                    help="passer par un proxy : free (proxies publics gratuits, instables), scraperapi (clé requise, --cle), tor (Tor Browser lancé, port 9150)")
    ap.add_argument("--cle", default=os.environ.get("SCRAPERAPI_KEY", ""), help="clé API ScraperAPI (ou variable SCRAPERAPI_KEY)")
    ap.add_argument("--test", action="store_true", help="test hors ligne de l'appariement des titres")
    a = ap.parse_args()

    if a.test:
        faux = [{"bib": {"title": "The wage gap between Francophones and Anglophones: a Canadian perspective, 1970–2000", "pub_year": "2008"}, "num_citations": 61},
                {"bib": {"title": "Wage gaps in Canada", "pub_year": "2001"}, "num_citations": 999}]
        r, s = meilleur_resultat(faux, "The wage gap between Francophones and Anglophones: a Canadian perspective, 1970-2000", 2008)
        assert r and r["num_citations"] == 61, (r, s)
        r2, s2 = meilleur_resultat(faux, "Language and Ethnic Relations in Canada", 1970)
        assert r2 is None, (r2, s2)
        print("test appariement OK :", s, s2)
        return

    if a.proxy != "aucun":
        from scholarly import scholarly, ProxyGenerator
        pg = ProxyGenerator()
        ok = {"free": lambda: pg.FreeProxies(), "scraperapi": lambda: pg.ScraperAPI(a.cle),
              "tor": lambda: pg.Tor_External(tor_sock_port=9150, tor_control_port=9151, tor_password="")}[a.proxy]()
        if not ok:
            sys.exit("proxy indisponible : vérifier la clé, la connexion ou Tor Browser")
        scholarly.use_proxy(pg)
        print("proxy activé :", a.proxy)

    corpus = json.load(open(CORPUS, encoding="utf-8"))
    ids = [e["id"] for e in corpus]
    if a.top30 and os.path.exists(TOP30):
        with open(TOP30, encoding="utf-8-sig") as f:
            ids = [r["id"] for r in csv.DictReader(f)]
    if a.seulement_manquants:
        ids = [i for i in ids if next(e for e in corpus if e["id"] == i).get("number_citations") is None]

    deja = {}
    if os.path.exists(CSV):
        with open(CSV, encoding="utf-8-sig") as f:
            for r in csv.DictReader(f):
                deja[r["id"]] = r
    byid = {e["id"]: e for e in corpus}
    aujourdhui = datetime.date.today().isoformat()
    for k, i in enumerate(ids, 1):
        e = byid[i]
        if a.reprendre and deja.get(i, {}).get("citations_google_scholar"):
            continue
        try:
            r, s = chercher(e["title"], e["year"])
            if r is None:
                print(f"[{k}/{len(ids)}] {i}: aucun résultat assez proche (similarité {s})")
                deja[i] = {"id": i, "citations_google_scholar": "", "date": aujourdhui, "author": e["author"], "year": e["year"], "title": e["title"], "titre_scholar": "", "similarite": s}
            else:
                n = r.get("num_citations", 0)
                print(f"[{k}/{len(ids)}] {i}: {n} citations (similarité {s}) — {r['bib'].get('title', '')[:70]}")
                deja[i] = {"id": i, "citations_google_scholar": n, "date": aujourdhui, "author": e["author"], "year": e["year"], "title": e["title"], "titre_scholar": r["bib"].get("title", ""), "similarite": s}
        except Exception as ex:  # CAPTCHA / blocage de l'IP : on sauvegarde et on ARRÊTE (insister prolonge le blocage)
            print(f"[{k}/{len(ids)}] {i}: ERREUR {type(ex).__name__}: {str(ex)[:120]}")
            deja.setdefault(i, {"id": i, "citations_google_scholar": "", "date": "", "author": e["author"], "year": e["year"], "title": e["title"], "titre_scholar": "", "similarite": ""})
            bloque = "MaxTries" in type(ex).__name__ or "Cannot Fetch" in str(ex)
            if bloque:
                sauvegarder(deja, corpus, byid)
                print("\nGoogle Scholar bloque cette adresse IP. Progression sauvegardée dans Data/citations_google_scholar.csv.")
                print("Attendre 30 à 60 minutes (ou changer de réseau / utiliser --proxy), puis relancer :")
                print("  python Scripts/recuperer_citations_scholar.py --reprendre --pause 30")
                return
        sauvegarder(deja, corpus, byid)
        time.sleep(a.pause)
    print("terminé ; lancer ensuite : python3 Scripts/maj_citations_scholar.py && python3 Scripts/score_snowballing.py")


if __name__ == "__main__":
    main()
