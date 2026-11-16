"""Entraînement indépendant des trois détecteurs et évaluation sur le test réservé."""
import argparse, json, os, platform, shutil, time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
os.environ.setdefault('YOLO_CONFIG_DIR',str(ROOT/'.cache/ultralytics'))
import torch
from ultralytics import YOLO
from src.prepare import DATASETS

def run(task,epochs,imgsz,batch,device):
    torch.set_num_threads(4)
    start=time.perf_counter()
    model=YOLO(str(ROOT/'models/yolov8n.pt'))
    model.train(data=str(ROOT/f'data/{task}/data.yaml'),epochs=epochs,imgsz=imgsz,batch=batch,device=device,
                workers=0,seed=42,deterministic=True,project=str(ROOT/'results/training'),name=task,
                exist_ok=False,patience=10,pretrained=True,plots=True,cache=False,amp=False,
                degrees=3,translate=.05,scale=.2,fliplr=0,flipud=0,mosaic=0,close_mosaic=0)
    best=Path(model.trainer.best)
    dst=ROOT/f'models/{task}.pt'; shutil.copy2(best,dst)
    trained=YOLO(str(dst))
    metrics=trained.val(data=str(ROOT/f'data/{task}/data.yaml'),split='test',device=device,imgsz=imgsz,batch=batch,
                        workers=0,project=str(ROOT/'results/evaluation'),name=task,plots=True)
    report=dict(task=task,epochs_requested=epochs,epochs_completed=len((best.parent.parent/'results.csv').read_text().splitlines())-1,
                imgsz=imgsz,batch=batch,device=device,seed=42,seconds=time.perf_counter()-start,
                test_metrics={k:float(v) for k,v in metrics.results_dict.items()},
                per_class_ap50_95={trained.names[int(c)]:float(v) for c,v in zip(metrics.box.ap_class_index,metrics.box.ap)},
                speed_ms=metrics.speed,checkpoint=str(dst.relative_to(ROOT)),python=platform.python_version(),torch=torch.__version__)
    (ROOT/f'results/{task}_metrics.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    return report

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--task',choices=['all',*DATASETS],default='all');p.add_argument('--epochs',type=int,default=12);p.add_argument('--imgsz',type=int,default=320);p.add_argument('--batch',type=int,default=8);p.add_argument('--device',default='cpu');a=p.parse_args()
    for t in DATASETS if a.task=='all' else [a.task]: print(json.dumps(run(t,a.epochs,a.imgsz,a.batch,a.device),indent=2))
