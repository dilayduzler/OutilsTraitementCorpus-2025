# PROJET :  OutilsTraitementCorpus-2025

## Définissez les besoins de votre projet:

Ce projet vise à construire un corpus de questions-réponses (QA) à partir de textes narratifs structurés provenant du wiki du jeu **Stardew Valley**. L’objectif est de produire des données exploitables pour l’analyse ou l’évaluation de systèmes de QA (question answering), dans un cadre narratif et culturel riche.

## Quel sujet allez-vous traiter ?

À l'origine, l'intention était de couvrir l’ensemble du wiki de Stardew Valley (lieux, quêtes, dialogues, personnages, objets, etc.). Toutefois, après évaluation de l’ampleur du site et des contraintes techniques, j'ai restreint le périmètre à 12 personnages datables (bachelors et bachelorettes). 

## Quel type de tâche allez-vous réaliser ?

- Récupération automatique des pages HTML
- Extraction de données structurées : emploi du temps, événements de cœur et préférences de cadeaux
- Génération automatique de questions via le modèle `flan-t5-base`, puis génération de réponses avec `unifiedqa-t5-small`  
- Organisation des données au format SQuAD pour l’entraînement supervisé d’un modèle de QA (`roberta-base-squad2`)  
- Entraînement du modèle avec évaluation intégrée sur un split équilibré par personnage

> Les réponses générées n’ont pas pu être validées manuellement comme prévu initialement, ce qui a impacté leur qualité. Certaines souffrent d’hallucinations ou de réponses vagues.

## Quel type de données allez-vous exploiter ? & Où allez-vous récupérer vos données ?

Les données sources sont issues du site [stardewvalleywiki.com](https://stardewvalleywiki.com), notamment les pages de personnages datables. Le contenu textuel inclut :

- préférences de cadeaux
- événements de cœur (heart events)
- emplois du temps journaliers par saison et conditions

> Seules quelques pages HTML et fichiers JSON d’exemple sont fournies dans `data/` pour éviter une surcharge du dépôt.

Sur le site https://stardewvalleywiki.com, qui regroupe des informations sur le jeu Stardew Valley.

## Sont-elles libres d'accès ?

Le site Stardew Valley Wiki est librement accessible et publie son contenu sous licence Creative Commons Attribution-NonCommercial-ShareAlike 3.0.


## Structure du projet

```bash
Projet/
├── data/                  # Données brutes, structurées, contextes, QA
├── figures/               # Visualisations exploratoires
├── model/                 # Modèle + résultats d’évaluation
└── src/                   # Scripts organisés par étape de traitement
    ├── 01-data_collection/
    ├── 02-process-analysis/
    ├── 03-qa_generation/
    └── 04-train/