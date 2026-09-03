# stratification_qc — état du savoir par snowballing

**Question de recherche.** Entre 1961 et 2021, comment l'écart de revenu d'emploi et de statut
socioprofessionnel entre francophones et anglophones de langue maternelle au Québec a-t-il évolué, et à
partir de quel recensement cet écart s'est-il inversé, si tant est qu'il l'ait fait ?

Ce dépôt contient le repérage systématique des références (méthode CLESSN de *backward / forward
snowballing*), la grille de pertinence, les graphiques et un gabarit R Markdown prêt à l'emploi.

## Contenu

| Dossier / fichier | Contenu |
|---|---|
| `Protocole/protocole_snowballing.md` | Question, critères d'inclusion, formule du score, outils utilisés et limites |
| `Protocole/journal_des_rondes.md` | Bilan des rondes (0 à 3) et saturation |
| `Data/corpus.json` | Les 103 publications repérées (métadonnées, DOI, citations, notes, critères C1-C4, ronde) |
| `Data/bibliographies.json` | Bibliographies dépouillées (id citant → ids cités) ; provenance dans `bibliographies_sources.json` |
| `Data/grille_snowballing.csv` / `.xlsx` | Grille complète classée par score (onglets `grille`, `top30`, `parametres`) |
| `Data/grille_snowballing_top30.csv` | Les 30 lectures les plus pertinentes (publications incluses seulement) |
| `Data/reseau_citations_top30_*.csv` | Nœuds et arêtes du réseau de citations entre les 30 lectures |
| `Graphiques/lectures_snowballing_top30.png` | Graphique des 30 lectures ordonnées par indice de pertinence |
| `Graphiques/reseau_citations_top30.png` | Réseau de citations (disposition par forces, taille = citations reçues dans le top 30) |
| `CodeR/graphique_snowballing.R` | Script R (dplyr, ggplot2, igraph) : score, graphique des lectures, réseau |
| `Gabarit/gabarit_snowballing.Rmd` | **Gabarit prêt à l'emploi** (méthode + graphiques + bibliographie), PDF via xelatex |
| `Gabarit/gabarit_snowballing.docx` | Rendu Word du même gabarit (généré par `Scripts/render_gabarit_docx.py`) |
| `Zotero/corpus_snowballing.{ris,bib,json}` | Import Zotero du corpus complet (DOI/URL inclus) ; `top30_snowballing.*` pour les 30 lectures |
| `Scripts/` | Scripts Python : `grille.py` (gestion du corpus), `score_snowballing.py`, `reseau_citations.py`, `export_zotero.py`, `render_gabarit_docx.py` |

## Reproduire

```bash
python3 Scripts/score_snowballing.py      # grille CSV/XLSX + graphique des 30 lectures (matplotlib)
python3 Scripts/reseau_citations.py       # réseau de citations
python3 Scripts/export_zotero.py          # fichiers d'import Zotero
python3 Scripts/render_gabarit_docx.py    # rendu Word du gabarit
```

```r
# dans RStudio, à la racine du dépôt
source("CodeR/graphique_snowballing.R")                 # version R des graphiques
rmarkdown::render("Gabarit/gabarit_snowballing.Rmd")    # gabarit PDF (Times New Roman 12, double interligne, etc.)
```

Le gabarit PDF nécessite R (rmarkdown, dplyr, ggplot2, readr, knitr, igraph, jsonlite) et une distribution
LaTeX (`tinytex::install_tinytex()`). Sous Linux, remplacer `mainfont: "Times New Roman"` par `"TeX Gyre Termes"`
si la police n'est pas installée. Le Rmd n'a pas pu être tricoté dans l'environnement de production (ni R ni
LaTeX disponibles) ; le rendu Word a été généré à partir du même texte pour vérification.

## Indice de pertinence

`score = (minmax(log(1 + citations)) + minmax(année) + minmax(récurrence)) / 3` (poids égaux)

- citations : Consensus / Semantic Scholar (proxy de Google Scholar ; à mettre à jour) ; valeurs manquantes
  imputées par la médiane et signalées ;
- année : 1 = plus récente, 0 = plus ancienne ;
- récurrence : nombre de bibliographies du corpus citant la publication (101 bibliographies dépouillées).

## Zotero et PDF

Aucune connexion à Zotero n'était disponible depuis l'environnement d'exécution. Importer
`Zotero/top30_snowballing.ris` (ou `corpus_snowballing.ris`) dans Zotero : les DOI y figurent pour 64 des 103
références, ce qui permet à Zotero de récupérer les métadonnées et les PDF depuis le poste de l'usager.

## Comptes de citations Google Scholar

Aucun connecteur Google Scholar n'existe dans le registre MCP de claude.ai (recherche du 2026-09-03 : le seul
connecteur académique non installé est « Scholar Gateway », un moteur de recherche sémantique qui ne fournit
pas les comptes Google Scholar ; Consensus, déjà connecté, fournit les comptes Semantic Scholar). Google Scholar
n'offre pas d'API officielle. Voie recommandée :

1. importer `Zotero/corpus_snowballing.ris` dans Zotero et installer l'extension *Citation Counts Manager*
   (`zotero-citationcounts`), qui remplit le champ « Citation count » depuis Google Scholar (ou Crossref /
   Semantic Scholar), ou utiliser *Publish or Perish* ;
2. reporter les comptes dans `Data/citations_google_scholar.csv` (colonne `citations_google_scholar`) ;
3. lancer `python3 Scripts/maj_citations_scholar.py`, puis `Scripts/score_snowballing.py`,
   `Scripts/reseau_citations.py` et `Scripts/export_zotero.py` (ou tricoter le Rmd).

### Connecteur Scholar Gateway (ajouté le 2026-09-03)

Le connecteur *Scholar Gateway* (Wiley) a été connecté à la session. Il ne fournit **pas** les comptes de
citations Google Scholar : c'est un moteur de recherche sémantique en texte intégral sur le corpus Wiley, qui
renvoie des passages avec leurs citations dans le texte. Il a servi à confirmer une partie de la bibliographie
d'Albouy (2008) (`Data/bibliographies_sources.json`). Pour les comptes Google Scholar, la voie Zotero décrite
ci-dessus reste la seule praticable.

## Produire le PDF du gabarit

- **Avec LaTeX** (poste de l'usager) : `rmarkdown::render("Gabarit/gabarit_snowballing.Rmd")` (sortie par défaut,
  xelatex, Times New Roman ; préambule dans `Gabarit/preambule.tex`).
- **Sans LaTeX** : `bash Scripts/imprimer_gabarit_pdf.sh` tricote le Rmd en HTML puis l'imprime en PDF avec
  Chrome/Chromium headless (mise en forme dans `Gabarit/gabarit_snowballing.css`). C'est la voie utilisée pour
  produire `Gabarit/gabarit_snowballing.pdf` dans l'environnement de production (R 4.5 et pandoc installés via
  conda-forge, LaTeX indisponible) ; la police y est Liberation Serif, métriquement identique à Times New Roman.
