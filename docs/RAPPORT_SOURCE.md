<b>Projet 9</b><br/>Extraction des informations visuelles associées<br/>Traitement d’image et inclusion sociétale


## Résumé

Ce projet développe une application Python locale qui détecte les bus, métros et tramways, repère les panneaux de ligne et les arrêts, puis tente de lire les informations visibles. Le travail reprend les données et scripts existants et suit les exigences du PDF du professeur, reproduit dans le dossier technique.

Les trois jeux fournis totalisent 725 images. Les détecteurs sont effectivement entraînés sur CPU et évalués sur des lots réservés. Une référence HOG + SVM atteint 71,0 % d’exactitude sur 31 véhicules recadrés. L’OCR préentraîné lit correctement 5 des 8 panneaux lisibles retenus. Ces expériences établissent un prototype fonctionnel, sans valider un dispositif de guidage réel.

Le rapport sépare la classification sur régions connues, la détection d’objets et la lecture après détection. Les métriques, annotations, poids et journaux sont fournis pour rendre les résultats vérifiables. Les noms d’arrêt ne sont pas évaluables à partir des annotations disponibles.

Livrable | Contenu

Rapport | Méthodes, protocole, résultats mesurés et limites

Présentation | Diapositives éditables, exemples et notes de démonstration

Dossier technique | Code, datasets, modèles, résultats, tests et README

Version expérimentale du 16 novembre 2026. Les membres du groupe doivent renseigner leurs identités et leurs contributions réelles avant remise.


## 1  Cahier des charges et périmètre

L’objectif sociétal est d’aider des personnes âgées, malvoyantes ou ayant des difficultés d’orientation à accéder aux informations de transport. Une erreur de ligne peut toutefois induire un mauvais déplacement : la sortie reste une indication expérimentale et peut s’abstenir lorsqu’aucune lecture fiable n’est disponible.

Exigence du professeur | Réalisation et preuve

Constituer une base d’images | Trois exports fournis, sources conservées, audit et manifestes

Prétraiter les images | Niveaux de gris, filtre bilatéral, CLAHE, histogramme, Otsu

Segmenter les régions | Contours classiques et recadrages des boîtes détectées

Détecter les véhicules | Détecteur YOLOv8n spécialisé Public Transport

Reconnaître les textes | Détecteur LED-Panel puis OCR EasyOCR anglais/français

Classifier les transports | Classes Bus/Metro/Tram et référence HOG + SVM

Évaluer le système | Test réservé, mAP, matrice de confusion, exactitude OCR, CER

Trois détecteurs indépendants évitent de traiter comme fond des objets non annotés dans un autre dataset. Par exemple, les images de Bus Route Number contiennent souvent un véhicule, mais n’annotent que le panneau. Une fusion naïve des classes créerait des faux négatifs d’apprentissage.

L’architecture suit deux branches : l’image entière alimente les détecteurs ; les régions de texte détectées alimentent le prétraitement et l’OCR. Les contours et la classification HOG servent de méthodes classiques explicites, sans prétendre remplacer une localisation supervisée robuste.


## 2  Données et séparation expérimentale

Dataset | Images | Groupes | Train | Val. | Test

Public Transport | 135 | 55 | 93 | 21 | 21

Bus Route Number | 459 | 108 | 321 | 72 | 66

BusStop | 131 | 131 | 91 | 20 | 20

Public Transport contient trois classes. Bus Route Number annote LED-Panel, sans transcription. BusStop annote bus-stop, sans identité géographique. Les exports locaux indiquent CC BY 4.0. Les données d’origine restent inchangées et les transformations sont attribuées dans SOURCES.md.

Les lots initiaux ne sont pas utilisés tels quels : Bus Route Number ne comportait que train, et des variantes augmentées partagent une même source. Le nom précédant « .rf. » définit un groupe. Des images exactement identiques après décodage fusionnent aussi leurs groupes, grâce à une empreinte SHA-256 des pixels et dimensions.

Une séparation reproductible par groupes et par ensemble de classes vise 70 % entraînement, 15 % validation et 15 % test (seed 42). Les groupes pouvant contenir plusieurs images, les proportions finales diffèrent. Chaque classe est représentée dans les lots. Les tests automatisés vérifient l’absence de groupes et d’empreintes communs entre lots.

Les 725 images sont décodées et leurs annotations vérifiées. Les classes doivent être entières et valides, les coordonnées finies et normalisées, les boîtes positives et contenues dans l’image. Au total, 104 polygones de transport et 135 d’arrêt sont convertis. Les 459 images de panneaux comportent déjà des rectangles.

Cette séparation empêche les fuites identifiées par nom ou pixels, mais pas toutes les scènes proches sous des noms différents. Les 294 groupes sont des groupes techniques, pas 294 situations nécessairement indépendantes. Les performances sur de nouvelles villes ou conditions ne sont pas établies.


## 3  Traitement d’image avec OpenCV

La chaîne classique commence par la conversion BGR vers niveaux de gris. Le filtre bilatéral (diamètre 7, paramètres 50/50) réduit le bruit tout en préservant les discontinuités. CLAHE (clipLimit 2, grille 8 × 8) rehausse localement le contraste. L’histogramme à 256 niveaux permet d’observer la distribution lumineuse.

Le seuil d’Otsu produit une image binaire sans fixer manuellement un seuil global. Canny (60 et 150) extrait les contours. Les contours externes de la binarisation, dont l’aire atteint au moins 30 pixels, fournissent des régions candidates. Ces régions sont exploratoires : elles ne suffisent pas à déterminer qu’une forme est un bus ou un panneau.

Exemple de sortie du pipeline sur un panneau lisible choisi selon la transcription, pas selon le score du modèle. Les rectangles visibles sont des prédictions.

Contours Canny sur le premier exemple de transport du test, sélectionné par ordre de nom. Les traitements classiques sont consultables dans l’application et enregistrés pour les trois exemples.

Pour un polygone, on calcule xmin, xmax, ymin et ymax puis le centre et la largeur/hauteur normalisés. Cette boîte englobe l’objet mais perd sa forme précise. Les ROI OCR proviennent des rectangles, avec une marge de 4 % et un agrandissement bicubique ×2. CLAHE est appliqué avant lecture ; aucun gain de prétraitement n’est revendiqué sans étude d’ablation.


## 4  Modèles et paramètres d’apprentissage

YOLOv8n fournit une architecture légère initialisée avec des poids préentraînés. Trois adaptations supervisées apprennent respectivement les véhicules, les afficheurs et les arrêts. Le détecteur produit une boîte, une classe et un score pour chaque objet. La suppression des boîtes redondantes repose sur l’inférence Ultralytics.

Paramètre | Valeur utilisée

Architecture et initialisation | YOLOv8n préentraîné, même point de départ pour chaque tâche

Budget | 12 époques transport, 12 panneaux et 5 arrêts

Entrée et batch | 320 × 320 pixels, batch 8

Calcul | CPU, 4 threads PyTorch, 0 worker, AMP désactivé

Reproductibilité | Seed 42, mode déterministe demandé

Augmentations | Rotation ±3°, translation 0,05, scale 0,2 ; pas de flip ni mosaïque

Sélection | Meilleur checkpoint sur validation ; test réservé après entraînement

L’optimiseur automatique Ultralytics détermine les paramètres effectifs ; les fichiers args.yaml et les journaux les conservent. Les classes et les régions de texte changent la difficulté des trois tâches. L’image entière reste en couleur pour YOLO ; les traitements classiques ne sont pas imposés à un modèle préentraîné sur des images naturelles.

Environnement mesuré : Python 3.12.7, PyTorch 2.9.0+cpu, torchvision 0.24.0, Ultralytics 8.3.230, OpenCV 4.11.0.86. La GTX 850M de 2 Go recensée par nvidia-smi n’a pas été utilisée. Le journal conserve un premier essai interrompu par une dépendance manquante ; seules les exécutions terminées alimentent les résultats présentés.

Le faible budget et la résolution 320 privilégient l’exécution locale. Ils peuvent limiter la reconnaissance des petits objets. Une recherche d’hyperparamètres complète, une comparaison d’architectures et une répétition multi-seeds n’ont pas été réalisées.


## 5  Référence classique HOG et SVM

Cette expérience reconnaît le type de véhicule à partir d’un recadrage fourni par l’annotation. Chaque ROI est redimensionnée à 64 × 64, convertie en gris, puis décrite par HOG : blocs 16 × 16, pas 8 × 8, cellules 8 × 8, neuf orientations. Un StandardScaler appris sur train normalise les descripteurs avant LinearSVC.

Le paramètre C est choisi parmi 0,01, 0,1 et 1 selon le macro-F1 de validation. Les trois valeurs obtiennent ici le même score ; la première, C = 0,01, est retenue par une règle déterministe. Le scaler et le SVM ne voient pas le test pendant cette sélection.

Mesure | Résultat réel

Nombre de ROI train / validation / test | 111 / 25 / 31

Exactitude sur test | 71,0 %

Macro-F1 sur test | 0.7003

Durée totale du script | 4.45 secondes

Vérité / prédiction | Bus | Metro | Tram

Bus | 9 | 0 | 0

Metro | 3 | 5 | 1

Tram | 1 | 4 | 8

Les neuf bus sont correctement classés. Les principales confusions opposent métro et tramway, dont les formes et contextes peuvent se ressembler dans les petits recadrages. Le faible effectif interdit de généraliser cette réussite sur les bus à toutes les situations.

Cette exactitude n’est pas directement comparable à la mAP de YOLO. HOG reçoit la bonne région d’objet et ne pénalise pas une mauvaise localisation. Le réseau doit simultanément trouver et classer les véhicules. Le modèle HOG/SVM sérialisé reste inclus comme référence reproductible.


## 6  Évaluation des détecteurs

Tâche | Images test | Précision | Rappel | mAP50 | mAP50-95

transport | 21 | 69,3 % | 66,0 % | 62,9 % | 47,6 %

route | 66 | 99,5 % | 87,0 % | 98,5 % | 69,1 %

stop | 20 | 100,0 % | 96,5 % | 99,5 % | 89,1 %

La précision rapporte les vrais positifs aux prédictions positives ; le rappel les rapporte aux objets annotés. L’IoU mesure l’intersection divisée par l’union des rectangles. La mAP50 résume la courbe précision-rappel à IoU 0,5 ; la mAP50-95 moyenne les seuils 0,50 à 0,95 par pas de 0,05. Elle pénalise davantage les boîtes imprécises.

Les précision/rappel affichés sont ceux du résumé du validateur Ultralytics, et ne décrivent pas nécessairement le seuil 0,25 de l’application. La mAP est intégrée sur les scores de confiance. Les courbes, matrices de confusion et prédictions du validateur sont livrées dans results/evaluation.

Tâche | Époques terminées | Durée entraînement + test

transport | 12 | 8.9 min

route | 12 | 1.6 min

stop | 5 | 2.1 min

Pour route, la durée ci-dessus couvre la dernière reprise après 11 époques et le test final. Les sessions précédentes sont consignées dans PROGRESS.md. Les autres durées couvrent leur entraînement et leur test.

Classe de transport | AP50-95 sur test

Bus | 68,4 %

Metro | 46,6 %

Tram | 27,9 %

Les scores se rapportent uniquement aux partitions livrées. Les petits effectifs, les variations d’annotations et les images proches limitent leur portée. Les trois détecteurs n’ont pas été évalués ensemble sur un corpus où tous les types d’objets seraient exhaustivement annotés ; leurs faux positifs croisés restent à examiner.


## 7  Lecture OCR et analyse des erreurs

EasyOCR 1.7.2 utilise ses poids anglais/français préentraînés, sans réentraînement dans ce projet. Le texte brut et sa confiance sont conservés. Une expression régulière extrait les tokens contenant un à quatre chiffres, éventuellement préfixés ou suffixés d’une lettre. Les caractères ne sont pas corrigés arbitrairement : O n’est pas remplacé automatiquement par 0.

Le benchmark parcourt les groupes de test par ordre de fichier et retient une image par groupe, avec ses panneaux. Dix-sept ROI sont examinées et transcrites visuellement avant lecture. Huit affichent un numéro complet jugé lisible ; neuf sont exclues pour ambiguïté, absence de numéro complet ou recadrage partiel. Cette sélection est exploratoire, réalisée par un seul annotateur, sans double validation.

ROI | Transcription | Prédiction | Lecture exacte

03.jpg | 505 | 505 | Oui

04.jpg | 505 | 505 | Oui

05.jpg | 508 | 508 | Oui

06.jpg | 95 | 95 | Oui

08.jpg | 516 | (vide) | Non

10.jpg | 95 | 95 | Oui

11.jpg | 95 | (vide) | Non

14.jpg | 516 | (vide) | Non

Exactitude : 5/8 = 62,5 %. CER : 8 erreurs d’édition sur 21 caractères = 38,1 %. La durée mesurée du traitement des huit ROI est 4.49 s, hors chargement des modèles. Les poids et les transcriptions permettent de reproduire ces valeurs.

Les affichages « 516 » sont notamment lus comme des lettres ou ignorés ; une image floue de « 95 » produit une sortie vide. La détection interne du texte, le contraste des segments LED et la petite taille des régions contribuent aux échecs possibles. Cette observation n’isole pas causalement chaque facteur.

Le taux conditionnel sur régions lisibles ne représente pas la lecture de tous les panneaux, encore moins la fiabilité de bout en bout. Les textes en arabe ou en autres écritures ne sont pas pris en charge par cette configuration.


## 8  Détection puis lecture automatique

L’évaluation suivante réutilise les huit panneaux positifs lisibles pour vérifier la chaîne complète. Le détecteur route travaille sur l’image entière au seuil 0,25. Une région est considérée localisée si une prédiction atteint IoU ≥ 0,5 avec sa boîte annotée. Parmi les correspondances, le score de détection le plus élevé est retenu. La première ligne candidate doit être exactement égale à la transcription.

Mesure sur les huit panneaux | Résultat réel

Régions localisées | 8 / 8

Lignes exactement lues après localisation | 5 / 8

Taux de succès conditionnel | 62,5 %

Exemple de lecture après détection. La photo choisie correspond à la première transcription lisible du benchmark. Le JSON associé contient toutes les sorties, y compris les textes bruts et les scores.

Sur cet exemple, le détecteur BusStop signale aussi un arrêt sur le véhicule. Ce faux positif illustre la limite des détecteurs spécialisés lorsqu’ils sont appliqués ensemble à des scènes différentes de leur jeu d’entraînement.

Cette mesure conserve les échecs de localisation dans le dénominateur, mais le corpus ne contient ici que des panneaux lisibles positifs. Il ne permet pas d’estimer le taux de fausses lignes dans des scènes sans panneau. Un corpus exhaustivement annoté et davantage de textes sont nécessaires pour une évaluation opérationnelle.

Pour les arrêts, le programme détecte bus-stop et tente de lire du texte dans la région. Le champ stop_name reste nul : aucun nom ni référentiel géographique n’est disponible pour certifier l’identité. Il faut ajouter des transcriptions, des identifiants d’arrêt et éventuellement un référentiel GTFS pour dépasser cette limite.


## 9  Application et démonstration

L’application Streamlit se lance localement et accepte une image JPG/PNG ou un exemple fourni. Le bouton Analyser exécute les trois détecteurs et, si l’option est cochée, l’OCR sur les panneaux et arrêts. L’interface montre les boîtes, les classes, les scores, le texte et les lignes candidates. L’export JSON conserve les coordonnées et le temps mesuré.

La démonstration suit quatre étapes : lancer l’application, analyser route_readable.jpg, observer une lecture difficile sur route.jpg, puis comparer transport.jpg et stop.jpg. Les exemples initiaux de chaque dataset sont pris par ordre de nom de test ; un exemple lisible supplémentaire est sélectionné selon la transcription. Il ne s’agit pas d’un montage de réussites uniquement.

Image de démonstration | Durée pipeline mesurée

00011_2_jpg.rf.38e7e52544e40908000 | 0.51 s

00024_img__18_bus1_jpg.rf.95ea8a6f | 0.25 s

00005_-_202305222200232_jpg.rf.291 | 10.50 s

00123_v1train__WhatsApp-Image-2026 | 10.98 s

Ces durées excluent le chargement initial et concernent seulement quatre images, sur CPU et en présence d’autres activités de génération. Elles ne constituent pas une mesure de débit temps réel. Les exemples et résultats sont intégrés au dossier, afin de disposer d’une démonstration même sans Internet.

L’interface prévoit les images invalides, les modèles absents, l’absence de détection et l’affichage des erreurs. Les contrastes et libellés simples améliorent la lisibilité, mais aucun test d’accessibilité utilisateur ni synthèse vocale n’a été réalisé.


## 10  Vérification et reproductibilité

Les tests unitaires contrôlent la conversion des polygones, les annotations invalides, les recadrages aux bords, le refus d’une ROI vide, le traitement d’une image uniforme, l’extraction alphanumérique et la distance d’édition. Un test d’intégrité parcourt les données préparées. Deux tests fonctionnels Streamlit vérifient l’analyse avec OCR, la conservation des résultats, l’analyse sans OCR et le changement de seuil. Le bilan final figure dans results/tests_final.log ; les journaux antérieurs sont conservés.

Fichier ou commande | Rôle

python -m src.prepare | Audit, conversion et séparation sans écrasement

python -m src.relocate | Réparer les chemins YAML après déplacement

python -m src.train | Entraîner les détecteurs et évaluer le test

python -m src.baseline | Entraîner et évaluer la référence HOG/SVM

python -m src.ocr_benchmark | Évaluer la lecture des ROI transcrites

python -m src.evaluate_pipeline | Vérifier la localisation puis la lecture

python -m src.demo | Régénérer les exemples et visualisations

python -m streamlit run app.py | Lancer l’application locale

L’environnement recommandé utilise Python 3.12 et un environnement virtuel neuf. Les versions centrales sont fixées dans requirements.txt ; environment.json consigne les versions observées et requirements-lock.txt complète l’inventaire. Les modèles entraînés et poids OCR sont inclus pour que l’inférence ne dépende pas d’un nouveau téléchargement.

Les seeds et manifestes stabilisent le protocole, mais ne garantissent pas l’identité bit à bit sur tout matériel ou toute bibliothèque. Les résultats doivent être régénérés après un nouvel entraînement. Le test actuel ne doit pas devenir un jeu de réglage à force d’itérations.

Les journaux montrent les erreurs d’installation rencontrées puis résolues. Le projet source du Bureau n’a pas été modifié. Le dossier final contient une copie des données d’origine, les scripts initiaux et les nouveaux modules, ce qui permet de distinguer la reprise du travail des expérimentations ajoutées.


## 11  Limites et perspectives

<b>Qualité et diversité des données.</b> Les images proviennent de petits exports et de contextes hétérogènes. Les variantes partagent leur lot, mais d’autres ressemblances peuvent subsister. Les tests ne couvrent ni un réseau local déterminé, ni toutes les conditions de nuit, pluie, foule, occlusion ou mouvement.

<b>Annotations.</b> Les boîtes englobantes perdent la géométrie des polygones. Les panneaux de ligne n’ont pas de transcription systématique. Les arrêts n’ont pas d’identité ni de nom. Certaines ROI sont trop partielles pour une lecture complète. Il faut compléter et faire relire les annotations avant de viser un résultat fiable.

<b>Modèles.</b> Le budget d’apprentissage et la résolution sont limités par le CPU. Les choix d’architecture et de prétraitement n’ont pas fait l’objet d’une ablation exhaustive. Les scores ne sont pas calibrés et l’application peut produire des faux positifs, notamment lorsqu’un détecteur est appliqué à un domaine différent de son jeu d’apprentissage.

<b>Évaluation.</b> Les métriques de détection, classification sur ROI et lecture conditionnelle répondent à des questions différentes. Le sous-ensemble OCR est petit, sélectionné sur la lisibilité, et annoté une seule fois. Aucun intervalle de confiance, test multi-seeds ou taux de reconnaissance des noms d’arrêt n’est revendiqué.

<b>Évolutions prioritaires.</b> Collecter un corpus de scènes locales où tous les objets et textes sont annotés ; séparer par trajet ou séquence ; ajouter des transcriptions validées en français et arabe ; tester une résolution supérieure sur GPU ; comparer les prétraitements sur validation ; intégrer un référentiel d’arrêts et une restitution audio évaluée avec des usagers.

<b>Conclusion.</b> Le projet fournit une chaîne exécutable, des modèles réellement entraînés, des tests et trois livrables cohérents. Les mesures établissent la faisabilité sur les jeux fournis. Elles ne démontrent pas une fiabilité suffisante pour un guidage autonome. La suite du travail porte d’abord sur les annotations textuelles et la diversité des situations, puis sur l’optimisation des modèles.


## 12  Références et traçabilité

Exigences : TIM_2026_Projet_9.pdf, « Reconnaissance des moyens de transport et des informations associées », copie fournie dans docs/cahier_des_charges.pdf. La consigne de remise demande à chaque membre de déposer individuellement rapport, présentation et dossier technique.

<b>Public Transport</b><br/>Workspace lab2-2hu69, projet public-transport-bxwdm, version 1. Licence déclarée : CC BY 4.0.<br/>https://universe.roboflow.com/lab2-2hu69/public-transport-bxwdm/dataset/1

<b>Bus Route Number</b><br/>Workspace s-workspace-b9ro3, projet bus-route-number-zitdp, version 1. Licence déclarée : CC BY 4.0.<br/>https://universe.roboflow.com/s-workspace-b9ro3/bus-route-number-zitdp/dataset/1

<b>BusStop</b><br/>Workspace detectioncompetition, projet busstop, version 1. Licence déclarée : CC BY 4.0.<br/>https://universe.roboflow.com/detectioncompetition/busstop/dataset/1

Documentation Ultralytics : https://docs.ultralytics.com/modes/train/ ; https://docs.ultralytics.com/modes/val/ ; https://docs.ultralytics.com/usage/cfg/

Documentation EasyOCR : https://www.jaided.ai/easyocr/documentation/ ; OpenCV : https://docs.opencv.org/4.x/ ; LinearSVC : https://scikit-learn.org/stable/modules/generated/sklearn.svm.LinearSVC.html

Les pages techniques sont évolutives ; les versions réellement utilisées sont consignées dans environment.json. Les fichiers data.yaml des exports constituent la source de provenance des datasets. Toutes les photographies du rapport et de la présentation viennent des données fournies, avec les transformations décrites dans le dossier technique.

Preuve | Emplacement dans le dossier technique

Inventaire et séparation | data/audit.json et data/*/manifest.json

Détection | results/*_metrics.json, results/training, results/evaluation

Classification classique | results/baseline_metrics.json

OCR et annotations | results/ocr_metrics.json et examples/ocr_rois

Chaîne complète | results/pipeline_metrics.json

Tests et application | results/tests.log, results/app_test.json

Démo | results/demo et docs/DEMONSTRATION.md

Les scores figurant dans ce rapport sont calculés à partir des fichiers de résultats, sans valeur illustrative présentée comme mesure. Les sources et scripts d’édition des livrables restent dans le dossier technique pour correction des noms et préparation de la soutenance.