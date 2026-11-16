# Architecture technique

## Flux

`data_raw` est immuable. `prepare.py` construit `data`, `audit.json` et les manifestes. `train.py` permet une nouvelle expérience et `resume_remaining.py` reprend les travaux manquants sans remplacer les modèles validés. Les poids finaux sont chargés par `Pipeline`, utilisé en CLI et par Streamlit.

Les trois tâches utilisent les classes distinctes suivantes : transport = Bus/Metro/Tram ; route = LED-Panel ; stop = bus-stop. L'identifiant numérique d'une classe reste local à son détecteur. L'application ne fusionne pas les labels numériques de plusieurs modèles.

## Contrat de sortie du pipeline

`Pipeline.predict(image, conf=0.25)` accepte une image BGR NumPy et retourne `(resultat, image_annotee)`.

`resultat` contient `detections`, `seconds` et `ocr_enabled`. Chaque détection contient :

- `task` et `label` : tâche et classe.
- `confidence` : score du détecteur, non calibré.
- `box` : `[x1, y1, x2, y2]` en pixels dans l'image d'entrée.
- `text` : textes OCR bruts avec leur propre confiance.
- `route_candidates` : tokens numériques/alphanumériques plausibles après filtrage OCR à 0,3.
- `stop_name` : toujours nul, faute d'identité vérifiable.
- Pour les arrêts, `visible_stop_text` conserve un texte éventuellement lisible.
- Pour les panneaux, `vehicle_index` associe le centre du panneau à la plus petite boîte de véhicule qui le contient, ou reste nul. C'est une heuristique spatiale, sans taux de précision mesuré.

Les coordonnées sont recadrées aux limites de l'image. Aucune transformation géographique ni estimation de distance n'est calculée. L'OCR anglais/français fonctionne hors ligne lorsque ses poids sont présents.

## Application

L'interface charge les modèles en cache. Une empreinte de l'image, l'option OCR et le seuil identifient chaque analyse. Les résultats sont conservés dans la session pour survivre aux interactions, mais ne sont pas affichés comme résultats d'une autre image ou d'un nouveau seuil.

## Évaluation

La classification HOG/SVM reçoit des boîtes annotées. Les détecteurs sont évalués séparément sur les lots test. L'OCR sur ROI et l'évaluation après détection utilisent les annotations exploratoires de `examples/ocr_rois/annotations.json`. Ces protocoles ne sont pas interchangeables et ne fournissent pas un score global universel.

## Reprise et conservation

Les résultats préexistants sont identifiés dans `results/preservation_sha256.json`. Les corrections de l'application et du README conservent leur version antérieure dans `archive_before_resume`. Les checkpoints initiaux de route sont conservés et la reprise s'effectue dans un dossier distinct. `PROGRESS.md` trace l'exécution et les limites.
