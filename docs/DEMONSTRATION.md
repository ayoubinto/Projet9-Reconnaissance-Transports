# Démonstration orale

## Préparer avant la soutenance

Installer les dépendances selon le README. Depuis le dossier Projet9, lancer `python -m streamlit run app.py --server.address 127.0.0.1`. Les modèles sont inclus ; aucun entraînement n'est nécessaire pour la démonstration. Ouvrir l'adresse locale indiquée et garder le PowerPoint disponible.

## Scénario de deux à trois minutes

1. Présenter l'objectif : distinguer les véhicules, localiser les afficheurs et lire des informations utiles à l'orientation.
2. Choisir **Exemple fourni**, puis **route_readable.jpg**. Laisser OCR activé et le seuil à 0,25. Cliquer **Analyser**.
3. Montrer la boîte de détection, le texte brut et le numéro candidat. Si la sortie est erronée ou vide, expliquer l'échec ; ne pas annoncer la vérité terrain comme une prédiction.
4. Ouvrir **Traitements OpenCV** : image grise, débruitage, contraste, binarisation, contours et histogramme.
5. Télécharger le JSON. Les résultats restent affichés après cette interaction.
6. Analyser **route.jpg** pour montrer une région difficile ou partielle, puis **transport.jpg** et **stop.jpg**. Un arrêt détecté ne correspond pas à un nom certifié.
7. Désactiver OCR pour distinguer la détection de la lecture. Expliquer que les scores de classification, mAP et exactitude OCR n'ont pas le même dénominateur.

## Solution de repli

Ouvrir `results/demo/*_prediction.jpg` et `results/demo/predictions.json`. Ce sont des sorties calculées, pas des images annotées manuellement présentées comme des prédictions. Les diapositives contiennent aussi les exemples et les résultats mesurés. Le fichier vidéo `Demonstration_Projet9.webm`, s'il figure dans les livrables, montre un parcours enregistré dans l'application.

## Questions à préparer

- Pourquoi trois détecteurs ? Les datasets n'annotent pas exhaustivement les mêmes catégories.
- Pourquoi regrouper les variantes ? Pour éviter qu'une variante de la même photo apparaisse à la fois dans train et test.
- Pourquoi seulement huit textes dans le benchmark ? Les données n'ont pas de transcriptions et plusieurs ROI sont partielles ; le benchmark exploratoire conserve les exclusions.
- Peut-on guider une personne malvoyante ? La faisabilité technique est illustrée, mais aucun usage réel ou autonome n'est validé.
- Qui a réalisé chaque partie ? Décrire les contributions réelles des membres. Ne pas inventer de répartition.
