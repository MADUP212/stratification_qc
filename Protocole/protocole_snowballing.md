# Protocole de revue par « boule de neige » (snowballing)

## 1. Question de recherche

> Entre 1961 et 2021, comment l'écart de revenu d'emploi et de statut socioprofessionnel
> entre francophones et anglophones de langue maternelle au Québec a-t-il évolué, et à
> partir de quel recensement cet écart s'est-il inversé, si tant est qu'il l'ait fait ?

Concepts-clés et synonymes utilisés pour la recherche de l'ensemble de départ :

| Concept | Termes (FR) | Termes (EN) |
|---|---|---|
| Groupes linguistiques | francophones, anglophones, langue maternelle, allophones, bilingues | francophones, anglophones, mother tongue, language groups, allophones |
| Revenu d'emploi | revenu de travail, salaire, rémunération, écart salarial, disparités de revenu | earnings, wages, labour income, wage gap, earnings differentials |
| Statut socioprofessionnel | profession, cadres, mobilité professionnelle, stratification, propriété des entreprises, contrôle de l'économie | occupational status, status attainment, social mobility, vertical mosaic, ownership, control of the economy |
| Contexte | Québec, Montréal, recensement, Loi 101, Révolution tranquille | Quebec, Montreal, census, Bill 101, Quiet Revolution |

## 2. Méthode (d'après la présentation CLESSN « Le Snowballing » et Jalali & Wohlin, 2012)

1. **Ensemble de départ** : 6 à 12 publications récentes et centrales, choisies pour couvrir les
   communautés qui s'intéressent à la question (économie du langage, sociologie de la
   stratification, démolinguistique, histoire économique, littérature grise gouvernementale).
2. **Backward snowballing** : dépouillement des bibliographies de chaque publication retenue ;
   toute référence répondant aux critères d'inclusion est ajoutée à la grille et sa
   *récurrence* (nombre de bibliographies du corpus où elle apparaît) est incrémentée.
3. **Forward snowballing** : repérage des publications qui citent chaque publication retenue.
4. Répétition (rondes) jusqu'à saturation : aucune nouvelle référence pertinente.
5. Compilation dans la grille, calcul du score pondéré, graphique des lectures ordonnées.

### Outils réellement utilisés dans cette session (et limites)

- **Consensus** (moteur académique adossé à Semantic Scholar) : métadonnées, résumés, DOI,
  nombre de citations.
- **Recherche web** : repérage des références listées sur IDEAS/RePEc, des rapports
  gouvernementaux (OQLF, Statistique Canada, ISQ, C.D. Howe, CIRANO) et des comptes rendus.
- **Limites** : les API OpenAlex, Semantic Scholar, Crossref, Google Scholar, Unpaywall et
  Érudit, ainsi que le téléchargement direct de pages ou de PDF, sont bloqués par la politique
  réseau de l'environnement d'exécution. Les bibliographies ont donc été reconstituées à
  partir (a) des références affichées par IDEAS/RePEc et les moteurs, (b) des résumés et
  (c) de la connaissance de la littérature ; les comptes de récurrence sont des **bornes
  inférieures**. Le nombre de citations provient de Consensus/Semantic Scholar et non de
  Google Scholar (colonne `citations_source`) ; il est systématiquement plus bas que
  Google Scholar et doit être mis à jour manuellement avant publication.
- **Zotero / PDF** : aucune connexion à Zotero n'est disponible dans cette session. Les
  fichiers `Zotero/*.ris`, `Zotero/*.bib` et `Zotero/*.json` contiennent le DOI (ou l'URL) de
  chaque référence pour que l'import dans Zotero et la récupération des PDF se fassent
  depuis le poste de l'usager.

## 3. Critères d'inclusion (pertinence thématique)

Une publication est incluse dans le corpus si elle obtient **au moins 3 points sur 6** :

| Critère | Points | Définition |
|---|---|---|
| C1 | 2 | Compare explicitement francophones et anglophones (langue maternelle ou groupe linguistique) **au Québec** (ou au Canada avec résultats distincts pour le Québec). |
| C2 | 2 | Mesure le revenu d'emploi (salaire, revenu de travail) **ou** le statut socioprofessionnel (profession, cadres, mobilité, propriété/contrôle des entreprises). |
| C3 | 1 | Couvre au moins un recensement (ou une enquête équivalente) entre 1961 et 2021, idéalement une évolution temporelle. |
| C4 | 1 | Propose une explication (capital humain, discrimination, offre/demande de compétences linguistiques, politiques linguistiques, cohortes, émigration, propriété du capital). |

Sont exclues : les publications portant uniquement sur les minorités francophones hors Québec,
sur les immigrants sans comparaison franco-anglaise, ou sur des périodes antérieures à 1901
sans lien avec l'évolution 1961-2021 (les travaux 1901-1951 sont conservés comme contexte
historique s'ils servent à situer le point de départ de 1961).

## 4. Score pondéré

Pour chaque publication *i* :

- `cit_norm`  = min-max de `log(1 + citations)` (log pour atténuer l'asymétrie extrême entre
  ouvrages classiques et articles récents) ;
- `year_norm` = min-max de l'année (1 = plus récente, 0 = plus ancienne) ;
- `pert_norm` = min-max de la récurrence (nombre de bibliographies du corpus citant *i*, plus 1
  si la publication est elle-même dans le corpus de départ).

`score = w_cit * cit_norm + w_year * year_norm + w_pert * pert_norm`

Pondération : poids égaux `w_cit = w_year = w_pert = 1/3` (demande de l'usager, conforme au script CLESSN). Les poids sont des
paramètres des scripts `CodeR/graphique_snowballing.R` et `Scripts/score_snowballing.py`.

## 5. Structure du dépôt

```
Protocole/   protocole (ce fichier), journal des rondes
Data/        grille de snowballing (CSV + XLSX), bibliographies dépouillées (JSON)
Scripts/     scripts Python (construction de la grille, score, graphique)
CodeR/       script R (méthode CLESSN) pour le score et le graphique
Graphiques/  graphique des lectures ordonnées
Zotero/      fichiers d'import Zotero (RIS, BibTeX, CSL-JSON) avec DOI
Docs/        état du savoir (Markdown, DOCX)
```

## 6. Précisions ajoutées en cours de route

- **Classement** : seules les publications au statut `inclus` (critère C1 satisfait et total ≥ 3) entrent
  dans le classement des 30 lectures ; les outils de mesure du statut (Blishen 1967, 1987), les travaux
  canadiens sur la mosaïque verticale et les études d'immigrants restent dans la grille avec le statut
  `contexte`.
- **Citations manquantes** (39 publications non indexées : rapports, ouvrages) : imputées par la médiane du
  corpus (15) et signalées dans la colonne `citations_imputees` ; à remplacer par les comptes Google Scholar.
- **Bibliographies** : `Data/bibliographies.json` (id citant → ids cités, corpus seulement) ;
  `Data/bibliographies_sources.json` indique pour chaque bibliographie si elle provient des références
  affichées par IDEAS/RePEc (partielles) ou de la connaissance du texte. Les comptes de récurrence sont des
  bornes inférieures à valider sur les PDF.
- **Ronde de raffinement** (demande de l'usager) : publications citant Blishen (1958) et Porter (1965) et
  traitant des francophones et des anglophones (Blishen 1970 ; Cuneo et Curtis 1975 ; Darroch 1979 ;
  Ogmundson et McLaughlin 1992 ; Nakhaie 1997 ; Wanner 1999, 2005 ; Lautard et Guppy 1990 ; Herberg 1990).
- **Réseau de citations** : `Scripts/reseau_citations.py` (Python) et section 6 de
  `CodeR/graphique_snowballing.R` (igraph) ; nœuds = 30 lectures, disposition par forces (Fruchterman-Reingold),
  flèche = « cite », taille = citations reçues des autres lectures du top 30.
- **Gabarit** : `Gabarit/gabarit_snowballing.Rmd` (PDF via xelatex) et son rendu Word
  `Gabarit/gabarit_snowballing.docx` (produit par `Scripts/render_gabarit_docx.py`) : Times New Roman 12 pt,
  interligne double, texte justifié, pagination, identifiants en gras et en majuscules en haut à droite,
  nombre de mots sur la page titre, aucun nom.
