# Avancement du Projet 9

## État vérifié à la reprise du 16 novembre 2026

- Aucun processus Python d'entraînement actif trouvé.
- Données préparées et manifestes existants conservés : 725 images.
- HOG/SVM, modèle transport (12 époques), évaluation OCR et sept premiers tests conservés.
- Détecteur route interrompu au milieu de l'époque 3. Les fichiers best.pt et last.pt sont présents ; la reprise vérifie leur contenu avant usage.
- Aucun modèle stop final trouvé.
- Application, pipeline, tests d'intégrité et scripts des livrables présents mais validation complète à terminer.
- Aucun PDF, PPTX ou ZIP final présent à la reprise.

## Règles de conservation

Les checkpoints route originaux et résultats validés sont conservés. La reprise utilise une copie du dossier d'entraînement. Les nouveaux journaux ont des noms distincts. Les corrections de fichiers existants sont précédées d'une sauvegarde. Les métriques anciennes ne sont pas remplacées pour les expériences déjà validées.

## Journal d'exécution

- 2026-11-16T16:26:41 : Reprise route après époque 2/12, copie isolée route_resume_20261116_162641. Optimiseur et poids restaurés. Checkpoint à chaque époque.

- 2026-11-16T16:28:15 : route : époque 3/12 enregistrée dans C:\Users\ayoub\Documents\Codex\2026-11-16\reprends-mon-projet-universitaire-projet-9\outputs\Projet9\results\training\route_resume_20261116_162641\weights\last.pt

- 2026-11-16T16:30:41 : route : époque 4/12 enregistrée dans C:\Users\ayoub\Documents\Codex\2026-11-16\reprends-mon-projet-universitaire-projet-9\outputs\Projet9\results\training\route_resume_20261116_162641\weights\last.pt

- 2026-11-16T16:32:08 : route : époque 5/12 enregistrée dans C:\Users\ayoub\Documents\Codex\2026-11-16\reprends-mon-projet-universitaire-projet-9\outputs\Projet9\results\training\route_resume_20261116_162641\weights\last.pt

- 2026-11-16T16:33:33 : route : époque 6/12 enregistrée dans C:\Users\ayoub\Documents\Codex\2026-11-16\reprends-mon-projet-universitaire-projet-9\outputs\Projet9\results\training\route_resume_20261116_162641\weights\last.pt

- Vérifications intermédiaires : 8 tests réussis (results/tests_resume.log). Interface Streamlit démarrée et ouverte dans Edge sans interface visible. Conservation des résultats en session ajoutée, ancienne application sauvegardée. 1471 empreintes SHA-256 des fichiers antérieurs enregistrées.


- 2026-11-16T16:34:56 : route : époque 7/12 enregistrée dans C:\Users\ayoub\Documents\Codex\2026-11-16\reprends-mon-projet-universitaire-projet-9\outputs\Projet9\results\training\route_resume_20261116_162641\weights\last.pt

- 2026-11-16T16:36:22 : route : époque 8/12 enregistrée dans C:\Users\ayoub\Documents\Codex\2026-11-16\reprends-mon-projet-universitaire-projet-9\outputs\Projet9\results\training\route_resume_20261116_162641\weights\last.pt

- 2026-11-16T16:37:50 : route : époque 9/12 enregistrée dans C:\Users\ayoub\Documents\Codex\2026-11-16\reprends-mon-projet-universitaire-projet-9\outputs\Projet9\results\training\route_resume_20261116_162641\weights\last.pt

- 2026-11-16T16:39:00 : route : époque 10/12 enregistrée dans C:\Users\ayoub\Documents\Codex\2026-11-16\reprends-mon-projet-universitaire-projet-9\outputs\Projet9\results\training\route_resume_20261116_162641\weights\last.pt

- 2026-11-16T16:40:16 : route : époque 11/12 enregistrée dans C:\Users\ayoub\Documents\Codex\2026-11-16\reprends-mon-projet-universitaire-projet-9\outputs\Projet9\results\training\route_resume_20261116_162641\weights\last.pt

- 2026-11-16T19:01:24 : Reprise route après époque 11/12, copie isolée route_resume_20261116_190123. Optimiseur et poids restaurés. Checkpoint à chaque époque.

- 2026-11-16T19:02:42 : route : époque 12/12 enregistrée dans C:\Users\ayoub\Documents\Codex\2026-11-16\reprends-mon-projet-universitaire-projet-9\outputs\Projet9\results\training\route_resume_20261116_190123\weights\last.pt

- 2026-11-16T19:02:59 : route terminé et évalué sur test : {"metrics/precision(B)": 0.9946133483674832, "metrics/recall(B)": 0.8695652173913043, "metrics/mAP50(B)": 0.9852380894650631, "metrics/mAP50-95(B)": 0.6914155141206573, "fitness": 0.6914155141206573}

- 2026-11-16T19:02:59 : Début du détecteur stop uniquement ; transport et HOG/SVM réutilisés sans entraînement.

- 2026-11-16T19:03:22 : stop : époque 1/5 enregistrée dans C:\Users\ayoub\Documents\Codex\2026-11-16\reprends-mon-projet-universitaire-projet-9\outputs\Projet9\results\training\stop\weights\last.pt

- 2026-11-16T19:03:44 : stop : époque 2/5 enregistrée dans C:\Users\ayoub\Documents\Codex\2026-11-16\reprends-mon-projet-universitaire-projet-9\outputs\Projet9\results\training\stop\weights\last.pt

- 2026-11-16T19:04:12 : stop : époque 3/5 enregistrée dans C:\Users\ayoub\Documents\Codex\2026-11-16\reprends-mon-projet-universitaire-projet-9\outputs\Projet9\results\training\stop\weights\last.pt

- Reprise rapide : dernière époque route terminée depuis le checkpoint 11/12. Budget arrêts réduit à cinq époques. Audit de conservation : 1 471 fichiers préexistants vérifiés, aucune différence d’empreinte.


- 2026-11-16T19:04:35 : stop : époque 4/5 enregistrée dans C:\Users\ayoub\Documents\Codex\2026-11-16\reprends-mon-projet-universitaire-projet-9\outputs\Projet9\results\training\stop\weights\last.pt

- 2026-11-16T19:04:56 : stop : époque 5/5 enregistrée dans C:\Users\ayoub\Documents\Codex\2026-11-16\reprends-mon-projet-universitaire-projet-9\outputs\Projet9\results\training\stop\weights\last.pt

- 2026-11-16T19:05:06 : stop terminé et évalué sur test : {"metrics/precision(B)": 1.0, "metrics/recall(B)": 0.9651617907393486, "metrics/mAP50(B)": 0.995, "metrics/mAP50-95(B)": 0.8907258942845724, "fitness": 0.8907258942845724}

- Démonstration et évaluation de bout en bout exécutées. Suite complète et tests fonctionnels Streamlit réussis, sans test ignoré. Voir results/tests_final.log.

- Validation finale : 10 tests automatisés réussis. Sur 8 panneaux lisibles, 8 localisés avec IoU >= 0,5 et 5 lectures exactes. Vérification dans Edge : analyse, JSON téléchargé, résultat conservé et rejet d’un fichier invalide. Références : results/pipeline_metrics.json, results/tests_final.log, results/browser_test.json.


- Livrables générés et contrôlés : PDF 13 pages, PPTX 15 diapositives, dossier technique avec données, checkpoints, modèles et résultats. Les scripts d’édition des livrables sont des sources conservées pour le poste de génération. Le lancement de l’application est indépendant de ces scripts.

