# Projet 9 — Reconnaissance des transports publics

## Version légère pour le dépôt

Ouvrez ce dossier dans VS Code avec **Fichier > Ouvrir le dossier**. Dans son terminal PowerShell, suivez le démarrage rapide ci-dessous. Après la création de .venv, choisissez .venv/Scripts/python.exe via **Python: Select Interpreter** dans la palette de commandes.

Les trois jeux de données bruts et préparés, les poids finaux, les poids OCR, les tests et les résultats sont inclus. L'environnement Python doit être recréé sur le poste destinataire. Les checkpoints intermédiaires sont conservés dans le dossier original uniquement. Pour reprendre exactement une session d'entraînement interrompue, utilisez les checkpoints de l'original.


Prototype universitaire conforme au périmètre du PDF fourni : préparation des données, traitements OpenCV, détection de véhicules et panneaux, classification Bus/Metro/Tram, OCR et application Python locale. Le rapport distingue les mesures réelles, les expériences exploratoires et les fonctions non validées.

## Démarrage rapide sous Windows

Décompresser tout le dossier dans un chemin court, par exemple `C:\Projets\Projet9`. Ouvrir PowerShell dans ce dossier. Python 3.12 64 bits est recommandé.

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install torch==2.9.0 torchvision==0.24.0 --index-url https://download.pytorch.org/whl/cpu
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py --server.address 127.0.0.1
```

Ouvrir l’adresse locale indiquée dans le terminal. Choisir « Exemple fourni », sélectionner une image puis « Analyser ». Les modèles entraînés et les poids OCR sont inclus. L'application ne télécharge aucun poids à l'exécution. L’installation des dépendances demande Internet. L’analyse fonctionne ensuite hors ligne sur CPU.

L’interface affiche les détections, les textes bruts OCR, des numéros de ligne candidats, les étapes OpenCV et un export JSON. Le seuil de détection par défaut est 0,25. Une sortie vide signifie qu’aucun résultat suffisamment confiant n’a été trouvé. Le score du réseau n'est pas une probabilité de fiabilité calibrée.

## Organisation

- `src/` : préparation, entraînement, évaluation, prétraitements, pipeline, OCR et démonstration.
- `app.py` : interface Streamlit, import JPG/PNG et exemples intégrés.
- `data_raw/` : les trois exports Roboflow originaux, inchangés.
- `data/` : images et rectangles normalisés, lots train/val/test, manifestes et audit.
- `models/` : trois détecteurs YOLOv8n, référence HOG/SVM, poids initiaux et OCR.
- `results/` : journaux, métriques JSON, courbes, matrices de confusion et prédictions.
- `examples/` : images pour la démonstration et ROI OCR transcrites visuellement.
- `tests/` : tests de géométrie, OCR, intégrité des annotations et absence de fuite exacte.
- `legacy/` : scripts initiaux du projet, conservés pour traçabilité, non utilisés dans le pipeline final.
- `docs/` : cahier des charges et guides. Le rapport et le PowerPoint sont livrés séparément.

## Reproduire les expériences

Toujours exécuter les commandes depuis la racine `Projet9`. Remplacer `python` par `.\.venv\Scripts\python.exe` si l’environnement n’est pas activé.

```powershell
python -m unittest discover -s tests -v
python -m src.baseline
python -m src.ocr_benchmark
python -m src.evaluate_pipeline
python -m src.demo
python -m src.pipeline examples/route_readable.jpg --out results/ma_prediction
```

Les derniers scripts nécessitent les détecteurs inclus. `--no-ocr` permet une inférence uniquement visuelle. Les tests d’intégrité utilisent le dataset préparé inclus.

### Préparation

`python -m src.prepare --raw data_raw --out data_nouveau` crée une nouvelle préparation sans écraser un dossier existant. Le script vérifie le décodage, les classes et la géométrie, convertit les polygones en boîtes englobantes, regroupe les variantes `.rf.` et les doublons de pixels, puis répartit les groupes par strate de classes (environ 70/15/15, seed 42). Les proportions d’images peuvent différer des proportions de groupes. Les fichiers `manifest.json` permettent de retracer chaque image.

Les `data.yaml` préparés résolvent les partitions par rapport à leur propre dossier. Pour enregistrer de nouveau un chemin absolu si nécessaire, utiliser `python -m src.relocate`.

### Entraînement

```powershell
python -m src.relocate
python -m src.download_models
python -m src.train --task transport --epochs 12 --imgsz 320 --batch 8 --device cpu
python -m src.train --task route --epochs 12 --imgsz 320 --batch 8 --device cpu
python -m src.train --task stop --epochs 5 --imgsz 320 --batch 8 --device cpu
```

`download_models` est utile si les poids initiaux ou OCR ont été retirés. La commande peut télécharger les poids, contrairement à l'application. Les tâches `transport`, `route` et `stop` peuvent être entraînées séparément. Chaque tâche utilise YOLOv8n préentraîné, seed 42, quatre threads, zéro worker, sans inversion ni mosaïque pour préserver les textes. Les journaux d'entraînement fournissent les paramètres réellement appliqués et le nombre d’époques terminé.

Le meilleur checkpoint est choisi sur validation, puis évalué sur test une fois. Les fichiers `models/<task>.pt` et `results/<task>_metrics.json` sont remplacés par une nouvelle exécution, tandis que les dossiers d'entraînement numérotés sont conservés. Sauvegarder les modèles livrés avant une nouvelle expérience. Pour améliorer le modèle, utiliser validation et réserver un nouveau test final si l’on a exploité les erreurs du test actuel pour choisir des réglages.

L'expérience livrée pour les panneaux reprend des checkpoints sans réentraîner les premières époques. L'entraînement des arrêts utilise cinq époques pour limiter le temps CPU. Les checkpoints et la chronologie sont documentés dans `PROGRESS.md`. Après décompression, le réentraînement reste facultatif et le lancement direct est possible via `Lancer_Application.cmd` après installation.

### OCR et annotations

Le benchmark fourni utilise des ROI de panneaux issues du test et des transcriptions visuelles consignées avant l'exécution OCR. Les régions ambiguës sont explicitement exclues. `python -m src.ocr_benchmark --export` recrée les ROI et **réinitialise leurs transcriptions** : ne pas l’exécuter sur les annotations livrées sans copie préalable. Le taux exact compare la première ligne candidate à la transcription, et le CER est la distance d’édition totale divisée par le nombre de caractères attendus.

Le test OCR sur ROI connues isole la lecture. `evaluate_pipeline` mesure séparément la localisation (IoU ≥ 0,5) puis la lecture sur les seuls exemples positifs lisibles. Aucun de ces tests ne mesure la fiabilité complète en circulation réelle.

## Limites à présenter à l’oral

Les datasets sont petits, hétérogènes et ne constituent pas un échantillon représentatif du réseau marocain. Le regroupement élimine les fuites de noms sources et de pixels identiques, mais ne garantit pas l’absence de scènes visuellement proches sous d’autres noms. Les régions d’arrêt décrivent une catégorie générique, sans nom d’arrêt ni coordonnées GPS. L’application peut afficher un texte visible, mais ne certifie pas une identité d’arrêt. Aucun taux de reconnaissance des noms n’est revendiqué.

L’OCR n’a pas été réentraîné : ses poids anglais/français sont préentraînés. Les textes en autres écritures, les petits panneaux, les segments LED et les images floues posent problème. Le programme ne fournit pas de guidage autonome, d’estimation de distance, de suivi vidéo ou de validation d’accessibilité auprès d’usagers. Le fonctionnement temps réel n’est pas revendiqué.

## Dépannage

- `torchvision::nms does not exist` : installer ensemble les versions CPU de torch et torchvision ci-dessus dans un environnement neuf.
- `No module named polars` : réinstaller les dépendances du fichier requirements avant l’entraînement.
- Modèle OCR absent : lancer `python -m src.download_models` avec Internet.
- Image illisible : utiliser un JPG/PNG valide, réduire la taille si nécessaire.
- Entraînement lent : CPU utilisé volontairement ; réduire le batch ou utiliser un GPU compatible dans un autre environnement. Le GPU local GTX 850M n’a pas servi aux résultats livrés.

## Sources et attribution

Les métadonnées de chaque export indiquent **CC BY 4.0**. Les sources exactes, auteurs de workspace et transformations figurent dans `docs/SOURCES.md` et les README Roboflow originaux. Les bibliothèques et modèles tiers conservent leurs licences propres, dont Ultralytics (AGPL-3.0) et EasyOCR (Apache-2.0). Consulter leurs distributions avant redistribution au-delà du cadre prévu.

Chaque étudiant doit déposer individuellement les trois livrables selon la consigne de remise fournie. Compléter les noms des membres et leurs contributions réelles avant dépôt. Aucune contribution individuelle n’a été inventée dans ce dossier.
