# Sources et provenance

Consultation et exécution : 16 novembre 2026. Le PDF `cahier_des_charges.pdf` est la source des exigences, pas un cahier reconstitué à partir de conseils génériques.

## Données fournies

Les références suivantes proviennent des `data.yaml` et README des exports locaux. Leur licence déclarée est CC BY 4.0. Les versions d’origine sont incluses dans `data_raw`.

- Public Transport, workspace **lab2-2hu69**, projet **public-transport-bxwdm**, version 1 : https://universe.roboflow.com/lab2-2hu69/public-transport-bxwdm/dataset/1
- Bus Route Number, workspace **s-workspace-b9ro3**, projet **bus-route-number-zitdp**, version 1 : https://universe.roboflow.com/s-workspace-b9ro3/bus-route-number-zitdp/dataset/1
- BusStop, workspace **detectioncompetition**, projet **busstop**, version 1 : https://universe.roboflow.com/detectioncompetition/busstop/dataset/1

Modifications effectuées : conversion de polygones en rectangles englobants, nouveaux lots par groupes, préfixes de traçabilité, recadrages OCR, transcriptions visuelles et visualisations annotées. Les originaux sont conservés.

## Documentation technique

- Ultralytics, entraînement : https://docs.ultralytics.com/modes/train/
- Ultralytics, validation : https://docs.ultralytics.com/modes/val/
- Ultralytics, paramètres : https://docs.ultralytics.com/usage/cfg/
- EasyOCR, API : https://www.jaided.ai/easyocr/documentation/
- OpenCV, documentation : https://docs.opencv.org/4.x/
- Scikit-learn, LinearSVC : https://scikit-learn.org/stable/modules/generated/sklearn.svm.LinearSVC.html

Les pages Ultralytics évoluent ; les expériences utilisent spécifiquement la version 8.3.230 et YOLOv8n, pas nécessairement le modèle le plus récent présenté sur la documentation.
