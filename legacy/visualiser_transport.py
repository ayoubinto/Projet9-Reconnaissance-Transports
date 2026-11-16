
from pathlib import Path
import cv2
import matplotlib.pyplot as plt

BASE = Path(__file__).resolve().parent.parent
dataset = BASE / "datasets" / "prepared" / "Public Transport"

classes = ["Bus", "Metro", "Tram"]

images_dir = dataset / "train" / "images"
labels_dir = dataset / "train" / "labels"

for image_path in sorted(images_dir.iterdir()):
    if image_path.suffix.lower() not in [".jpg", ".jpeg", ".png"]:
        continue

    label_path = labels_dir / (image_path.stem + ".txt")

    if not label_path.exists() or not label_path.read_text().strip():
        continue

    image = cv2.imread(str(image_path))
    if image is None:
        continue

    hauteur, largeur = image.shape[:2]

    for ligne in label_path.read_text().splitlines():
        classe, x, y, w, h = map(float, ligne.split())

        x1 = int((x - w / 2) * largeur)
        y1 = int((y - h / 2) * hauteur)
        x2 = int((x + w / 2) * largeur)
        y2 = int((y + h / 2) * hauteur)

        cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(
            image, classes[int(classe)], (x1, max(20, y1 - 10)),
            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2
        )

    plt.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    plt.axis("off")
    plt.show()
    break
