
from pathlib import Path
import shutil

BASE = Path(__file__).resolve().parent.parent

source = BASE / "datasets" / "original" / "BusStop.v1i.yolov8"
destination = BASE / "datasets" / "prepared" / "BusStop"

# Copier sans modifier les données originales
if destination.exists():
    raise FileExistsError("Le dossier préparé existe déjà.")

shutil.copytree(source, destination)

total = 0

for split in ["train", "valid", "test"]:
    labels_dir = destination / split / "labels"

    for fichier in labels_dir.glob("*.txt"):
        nouvelles_lignes = []

        for ligne in fichier.read_text().splitlines():
            valeurs = ligne.split()

            if not valeurs:
                continue

            classe = valeurs[0]
            coords = list(map(float, valeurs[1:]))

            if len(coords) < 6 or len(coords) % 2 != 0:
                raise ValueError(f"Annotation invalide : {fichier}")

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
            total += 1

        fichier.write_text(
            "\n".join(nouvelles_lignes) + "\n"
        )

# Corriger les chemins du fichier YAML
yaml_file = destination / "data.yaml"
contenu = yaml_file.read_text()

for split in ["train", "valid", "test"]:
    cle = "val" if split == "valid" else split
    contenu = contenu.replace(
        f"{cle}: ../{split}/images",
        f"{cle}: {split}/images"
    )

yaml_file.write_text(contenu)

print("Préparation BusStop terminée !")
print("Polygones convertis :", total)
print("Dossier :", destination)
