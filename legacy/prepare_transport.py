
from pathlib import Path
import shutil

# Dossier principal du projet
BASE = Path(__file__).resolve().parent.parent

source = BASE / "datasets" / "original" / "Public Transport.v1i.yolov8"
destination = BASE / "datasets" / "prepared" / "Public Transport"

# Copier le dataset sans modifier l'original
shutil.copytree(source, destination, dirs_exist_ok=True)

rectangles = 0
polygones = 0

for split in ["train", "valid", "test"]:
    dossier = destination / split / "labels"

    for fichier in dossier.glob("*.txt"):
        nouvelles_lignes = []

        for ligne in fichier.read_text().splitlines():
            valeurs = ligne.split()
            if not valeurs:
                continue

            classe = valeurs[0]

            if len(valeurs) == 5:
                # Annotation déjà rectangulaire
                nouvelles_lignes.append(ligne)
                rectangles += 1

            elif len(valeurs) >= 7 and (len(valeurs) - 1) % 2 == 0:
                # Annotation polygonale
                coords = list(map(float, valeurs[1:]))
                xs = coords[0::2]
                ys = coords[1::2]

                xmin, xmax = min(xs), max(xs)
                ymin, ymax = min(ys), max(ys)

                x = (xmin + xmax) / 2
                y = (ymin + ymax) / 2
                w = xmax - xmin
                h = ymax - ymin

                nouvelles_lignes.append(
                    f"{classe} {x:.6f} {y:.6f} {w:.6f} {h:.6f}"
                )
                polygones += 1
            else:
                raise ValueError(f"Annotation invalide : {fichier}")

        fichier.write_text("\n".join(nouvelles_lignes) + "\n")

# Corriger les chemins dans data.yaml
yaml_file = destination / "data.yaml"
contenu = yaml_file.read_text()

for split in ["train", "valid", "test"]:
    cle = "val" if split == "valid" else split
    contenu = contenu.replace(
        f"{cle}: ../{split}/images",
        f"{cle}: {split}/images"
    )

yaml_file.write_text(contenu)

print("Préparation terminée !")
print("Rectangles conservés :", rectangles)
print("Polygones convertis :", polygones)
print("Résultat :", destination)
