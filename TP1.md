# TP

## Partie 1 | Étude de cas CoNLL 2003

### Quelle type de tâche propose CoNLL 2003 ?
CoNLL 2003 propose une tâche de reconnaissance d'entités nommées (Named Entity Recognition - NER).  
Cette tâche est indépendante de la langue et concerne l'identification de quatre types d'entités nommées :  
- Personnes (PER) 
- Localisations (LOC) 
- Organisations (ORG)  
- Autres entités diverses (MISC) qui ne rentrent pas dans les trois premières catégories.  

### Quel type de données y a-t-il dans CoNLL 2003 ?
Le corpus CoNLL 2003 est composé de huit fichiers couvrant l’anglais et l’allemand. Il inclut également des données non annotées qui sont intégrées dans le processus d’apprentissage.

Les données anglaises proviennent des articles de presse de Reuters publiés entre août 1996 et août 1997.  
Les données allemandes viennent du ECI Multilingual Text Corpus, un corpus contenant des textes dans plusieurs langues.  
Pour cette tâche, un extrait a été pris du journal allemand Frankfurter Rundschau.  

Le corpus contient :  
- Des ensembles d'entraînement, de développement et de test  
- Des données non annotées pour encourager les approches d’apprentissage semi-supervisé  
- Des annotations de parties du discours (POS tags), de segmentation (chunking) et de reconnaissance d'entités nommées, sous le format IOB  
- Un texte structuré par phrases, où chaque mot est étiqueté selon son type d’entité  

### À quel besoin répond CoNLL 2003 ?
CoNLL 2003 répond au besoin d’une reconnaissance automatique des entités nommées (NER).  
L’objectif est de permettre aux modèles d’identifier des entités spécifiques dans du texte brut.  
Cette tâche est essentielle pour de nombreuses applications comme :  
- La recherche d’informations  
- La traduction automatique  
- Les systèmes de question-réponse  

Le défi posé par CoNLL 2003 explore aussi des méthodes de NER indépendantes de la langue, c'est-à-dire des techniques applicables à plusieurs langues différentes.  

### Quels types de modèles ont été entraînés sur CoNLL 2003 ?
Différents modèles d’apprentissage automatique ont été testés, notamment :  
- Modèles à Entropie Maximale (Maximum Entropy Models - MEMMs) parmi les plus efficaces  
- Modèles de Markov Cachés (Hidden Markov Models - HMMs)  
- Modèles de Markov Conditionnels (Conditional Markov Models - CMMs)
- Champ Aléatoire Conditionnel (Conditional Random Fields - CRFs), l’un des plus performants  
- Réseaux de Neurones (y compris LSTMs, bien que moins courants à l’époque)  
- Modèles basés sur AdaBoost  
- Machines à Vecteurs de Support (Support Vector Machines - SVMs)  
- Systèmes hybrides combinant plusieurs approches (ex. : modèles empilés, ensembles de vote)  

Les CRFs ont obtenu les meilleurs résultats, surtout lorsqu’ils étaient complétés par des ressources externes comme des listes d’entités nommées (gazetteers) et des données non annotées pour l’apprentissage semi-supervisé.  

### Est-ce un corpus monolingue ou multilingue ?
CoNLL 2003 est un corpus multilingue, contenant des jeux de données en anglais et en allemand.  

---

## Partie 2 | Projet

### Définissez les besoins de votre projet

#### Dans quel besoin vous inscrivez-vous ?
Je pensais faire un projet autour de l’extraction d’informations structurées.  
L’idée, c’est de créer un corpus de QA (question-réponse) 

#### Quel sujet allez-vous traiter ?


#### Quel type de tâche allez-vous réaliser ?
Pour l’instant, je pense faire un corpus de QA structuré.  
L’idée, c’est d’avoir des questions prédéfinies et des réponses correspondantes.  
J’aimerais que ça soit clair et bien organisé pour que ce soit facile à utiliser.

#### Quel type de données allez-vous exploiter ?


#### Où allez-vous récupérer vos données ?


#### Sont-elles libres d’accès ?
Normalement, oui.  
 
