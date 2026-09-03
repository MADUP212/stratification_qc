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
| `Data/corpus.json` | Les 100 publications repérées (métadonnées, DOI, citations, notes, critères C1-C4, ronde) |
| `Data/bibliographies.json` | Bibliographies dépouillées (id citant → ids cités) ; provenance dans `bibliographies_sources.json` |
| `Data/grille_snowballing.csv` / `.xlsx` | Grille complète classée par score (onglets `grille`, `top30`, `parametres`) |
| `Data/grille_snowballing_top30.csv` | Les 30 lectures les plus pertinentes (publications incluses seulement) |
| `Data/reseau_citations_top30_*.csv` | Nœuds et arêtes du réseau de citations entre les 30 lectures |
| `Graphiques/lectures_snowballing_top30.png` | Graphique des 30 lectures ordonnées par indice de pertinence |
| `Graphiques/reseau_citations_top30.png` | Réseau de citations (cercle chronologique, taille = citations reçues dans le top 30) |
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

`score = 0,35 × minmax(log(1 + citations)) + 0,25 × minmax(année) + 0,40 × minmax(récurrence)`

- citations : Consensus / Semantic Scholar (proxy de Google Scholar ; à mettre à jour) ; valeurs manquantes
  imputées par la médiane et signalées ;
- année : 1 = plus récente, 0 = plus ancienne ;
- récurrence : nombre de bibliographies du corpus citant la publication (98 bibliographies dépouillées).

## Zotero et PDF

Aucune connexion à Zotero n'était disponible depuis l'environnement d'exécution. Importer
`Zotero/top30_snowballing.ris` (ou `corpus_snowballing.ris`) dans Zotero : les DOI y figurent pour 61 des 100
références, ce qui permet à Zotero de récupérer les métadonnées et les PDF depuis le poste de l'usager.
