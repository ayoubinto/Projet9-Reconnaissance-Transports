
from pathlib import Path
from collections import defaultdict
import random
import shutil

BASE = Path(__file__).resolve().parent.parent

source = BASE / "datasets" / "original" / "bus-route-number.v1i.yolov8"
destination = BASE / "datasets" / "prepared" / "Bus Route Number"

if destination.exists():
    raise FileExistsError(
        "Le dossier préparé existe déjà. Vérifiez-le avant de relancer."
    )

# 1. Récupérer les images
images = sorted(
    p for p in (source / "train" / "images").iterdir()
    if p.suffix.lower() in [".jpg", ".jpeg", ".png"]
)

# 2. Regrouper les variantes d'une même image
groupes = defaultdict(list)

for image in images:
    nom_original = image.stem.split(".rf.")[0]
    groupes[nom_original].append(image)

# 3. Mélanger les groupes de manière reproductible
noms = sorted(groupes)
random.Random(42).shuffle(noms)

n_train = round(len(noms) * 0.80)
n_val = round(len(noms) * 0.10)

repartition = {
    "train": noms[:n_train],
    "valid": noms[n_train:n_train + n_val],
    "test": noms[n_train + n_val:]
}

# 4. Vérifier les annotations
for image in images:
    label = source / "train" / "labels" / f"{image.stem}.txt"
    if not label.exists():
        raise FileNotFoundError(label)

# 5. Copier les images et les annotations
for split, groupes_split in repartition.items():
    images_dest = destination / split / "images"
    labels_dest = destination / split / "labels"

    images_dest.mkdir(parents=True, exist_ok=True)
    labels_dest.mkdir(parents=True, exist_ok=True)

    compteur = 0

    for nom in groupes_split:
        for image in groupes[nom]:
            label = source / "train" / "labels" / f"{image.stem}.txt"

            shutil.copy2(image, images_dest / image.name)
            shutil.copy2(label, labels_dest / label.name)
            compteur += 1

    print(f"{split}: {compteur} images")

# 6. Adapter le fichier data.yaml
yaml_source = source / "data.yaml"
contenu = yaml_source.read_text(encoding="utf-8")

for split, cle in [("train", "train"), ("valid", "val"), ("test", "test")]:
    contenu = contenu.replace(
        f"{cle}: ../{split}/images",
        f"{cle}: {split}/images"
    )

(destination / "data.yaml").write_text(
    contenu, encoding="utf-8"
)

print("Préparation du dataset terminée !")
