"""Téléchargement explicite des modèles; aucun téléchargement pendant l'application."""
from pathlib import Path
import os, shutil
ROOT=Path(__file__).resolve().parents[1]
os.environ.setdefault('YOLO_CONFIG_DIR',str(ROOT/'.cache/ultralytics'))

if __name__=='__main__':
    from ultralytics import YOLO
    import easyocr
    (ROOT/'models').mkdir(exist_ok=True)
    YOLO(str(ROOT/'models/yolov8n.pt'))
    easyocr.Reader(['en','fr'],gpu=False,model_storage_directory=str(ROOT/'models/ocr'),user_network_directory=str(ROOT/'.cache/easyocr'),download_enabled=True)
    print('Modèles disponibles dans models/')

