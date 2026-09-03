#### SNOWBALLING — écart de revenu et de statut francophones/anglophones au Québec, 1961-2021 ####
# Adapté du script CLESSN (graphique_snowballing.R). Lit la grille produite par Scripts/score_snowballing.py,
# recalcule l'indice de pertinence en R et trace les 30 lectures les plus pertinentes.

library(dplyr)
library(ggplot2)
library(readr)

#**********************************************#
#### ____ 0. Ouvrir la base de données ____ ####
#**********************************************#
# Utiliser le RProject (racine du dépôt) ou setwd("chemin/vers/stratification_qc")
Data <- read_csv("Data/grille_snowballing.csv", show_col_types = FALSE)

#***********************************************#
#### ____ 1. Paramètres de la pondération ____ ####
#***********************************************#
w_cit  <- 1/3    # nombre de citations (Google Scholar ; ici Consensus/Semantic Scholar en attendant)
w_year <- 1/3    # année de publication (1 = plus récente, 0 = plus ancienne)
w_pert <- 1/3    # pertinence = récurrence de la publication dans les bibliographies du corpus (poids égaux)
n_top  <- 30

#********************************************************#
#### ____ 2. Créer notre indicateur de pertinence ____ ####
#********************************************************#
normalize0to1 <- function(x) (x - min(x, na.rm = TRUE)) / (max(x, na.rm = TRUE) - min(x, na.rm = TRUE))

# Citations : Google Scholar si relevé ; sinon compte Consensus ramené à l'échelle Google Scholar (ratio médian) ; sinon médiane
if (!"citations_google_scholar" %in% names(Data)) Data$citations_google_scholar <- NA_real_
ok    <- !is.na(Data$citations_google_scholar) & !is.na(Data$number_citations) & Data$number_citations > 0
ratio <- if (sum(ok) >= 5) median(Data$citations_google_scholar[ok] / Data$number_citations[ok]) else 1
Data <- Data %>%
  mutate(
    citations_score = ifelse(!is.na(citations_google_scholar), citations_google_scholar,
                             ifelse(!is.na(number_citations), round(number_citations * ratio), NA_real_)),
    citations_imputees  = as.integer(is.na(citations_score)),
    citations_utilisees = ifelse(is.na(citations_score), median(citations_score, na.rm = TRUE), citations_score),
    cit_norm  = normalize0to1(log1p(citations_utilisees)),   # log pour atténuer l'asymétrie extrême
    year_norm = normalize0to1(year),
    pert_norm = normalize0to1(recurrence),
    formula   = round(w_cit * cit_norm + w_year * year_norm + w_pert * pert_norm, 2)
  )

#******************************************#
#### ____ 3. Ajouter les citations ____ ####
#******************************************#
# citationAuteurAnnee et etiquette (titre + auteur-année) sont déjà dans la grille ; on les recrée au besoin
if (!"etiquette" %in% names(Data)) {
  Data <- Data %>% mutate(etiquette = paste(substr(title, 1, 70), citationAuteurAnnee))
}

# On ne garde que les publications qui satisfont les critères d'inclusion (statut == "inclus")
DataGraph <- Data %>%
  filter(statut == "inclus") %>%
  arrange(desc(formula)) %>%
  slice_head(n = n_top)

#***************************************#
#### ____ 4. Créer le graphique ____ ####
#***************************************#
g <- ggplot(DataGraph, aes(x = reorder(etiquette, formula), y = formula)) +
  geom_segment(aes(xend = etiquette, y = 0, yend = formula), colour = "grey60", linewidth = 0.4) +
  geom_point(size = 2.5) +
  coord_flip() +
  theme_bw() +
  scale_y_continuous(name = "Indice de pertinence (moyenne à poids égaux : citations, année, récurrence)", limits = c(0, 1)) +
  theme(axis.text.y = element_text(size = 20), panel.grid = element_blank(),
        panel.grid.major.x = element_blank(), axis.title.x = element_text(size = 23, face = "bold", vjust = -1),
        panel.grid.minor.x = element_blank(), axis.title.y = element_blank(),
        axis.text.x = element_text(size = 22, face = "bold"))
g

# Sauvegarder le graphique
ggsave("Graphiques/lectures_snowballing_top30_R.png", g, height = 24, width = 30)

#*************************************************************************#
#### ____ 5. Exporter la liste des 30 lectures (pour Zotero / lecture) ____ ####
#*************************************************************************#
write_csv(DataGraph %>% select(rang, id, author, year, title, journal, doi, url, number_citations, citations_google_scholar, citations_utilisees, recurrence, formula),
          "Data/grille_snowballing_top30_R.csv")

#*********************************************************************#
#### ____ 6. Réseau de citations entre les 30 lectures (igraph) ____ ####
#*********************************************************************#
library(igraph)
library(jsonlite)
bib   <- fromJSON("Data/bibliographies.json")               # id citant -> ids cités (bibliographies dépouillées)
ordre <- DataGraph$id[order(DataGraph$year, DataGraph$id)]   # nœuds dans l'ordre chronologique
aretes <- do.call(rbind, lapply(ordre, function(citant) {
  cites <- intersect(unlist(bib[[citant]]), ordre)
  if (length(cites)) data.frame(citant = citant, cite = cites) else NULL
}))
g <- graph_from_data_frame(aretes, directed = TRUE, vertices = data.frame(name = ordre))
etiq <- setNames(gsub("[()]", "", DataGraph$citationAuteurAnnee), DataGraph$id)
deg_in <- degree(g, mode = "in")
V(g)$label <- paste0(etiq[V(g)$name], " (", deg_in, ")")
V(g)$size  <- 2.5 + 0.55 * deg_in                               # plus grand point = plus cité dans le top 30
set.seed(7)
lay <- layout_with_fr(g, niter = 5000)                       # disposition par forces (Fruchterman-Reingold)

png("Graphiques/reseau_citations_top30_R.png", width = 2800, height = 2400, res = 220)
par(mar = c(0, 0, 0, 0), family = "serif")
plot(g, layout = lay,
     edge.arrow.size = 0.25, edge.color = adjustcolor("grey50", 0.3), edge.curved = 0.15, edge.width = 0.4,
     vertex.color = "grey15", vertex.frame.color = NA,
     vertex.label.color = "black", vertex.label.cex = 0.62, vertex.label.family = "serif",
     vertex.label.dist = 0.5 + V(g)$size / 6, vertex.label.degree = -pi / 2)
dev.off()

write_csv(aretes, "Data/reseau_citations_top30_aretes_R.csv")
