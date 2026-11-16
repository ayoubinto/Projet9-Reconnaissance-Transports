"""Reprise conservatrice : copie de travail des checkpoints, aucun modèle validé écrasé."""
import argparse,json,os,shutil,time,platform
from datetime import datetime
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
os.environ.setdefault('YOLO_CONFIG_DIR',str(ROOT/'.cache/ultralytics'))
import torch
from ultralytics import YOLO

def progress(message):
    with (ROOT/'PROGRESS.md').open('a',encoding='utf-8') as f:f.write(f'\n- {datetime.now().isoformat(timespec="seconds")} : {message}\n')
    print(message,flush=True)

def finish(task,model,start,resume_epoch=0,previous_seconds=0):
    best=Path(model.trainer.best);dst=ROOT/f'models/{task}.pt'
    if dst.exists():raise FileExistsError(dst)
    shutil.copy2(best,dst)
    trained=YOLO(str(dst))
    metrics=trained.val(data=str(ROOT/f'data/{task}/data.yaml'),split='test',device='cpu',imgsz=320,batch=8,workers=0,project=str(ROOT/'results/evaluation'),name=task,plots=True)
    report=dict(task=task,epochs_requested=model.trainer.epochs,epochs_completed=len((best.parent.parent/'results.csv').read_text().splitlines())-1,
        imgsz=320,batch=8,device='cpu',seed=42,seconds=time.perf_counter()-start,seconds_scope='current resumed execution plus test' if resume_epoch else 'training plus test',
        resumed_after_epoch=resume_epoch,previous_recorded_training_seconds=previous_seconds,
        test_metrics={k:float(v) for k,v in metrics.results_dict.items()},
        per_class_ap50_95={trained.names[int(c)]:float(v) for c,v in zip(metrics.box.ap_class_index,metrics.box.ap)},speed_ms=metrics.speed,
        checkpoint=str(dst.relative_to(ROOT)),python=platform.python_version(),torch=torch.__version__)
    out=ROOT/f'results/{task}_metrics.json'
    with out.open('x',encoding='utf-8') as f:json.dump(report,f,indent=2)
    progress(f'{task} terminé et évalué sur test : '+json.dumps(report['test_metrics']))

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--stop-epochs',type=int,default=12)
    args=parser.parse_args()
    torch.set_num_threads(4)
    if not (ROOT/'models/route.pt').exists():
        candidates=[]
        for checkpoint in (ROOT/'results/training').glob('route*/weights/last.pt'):
            try:
                saved=torch.load(checkpoint,map_location='cpu',weights_only=False)
                if saved.get('optimizer') is not None and saved.get('epoch',-1)>=0:
                    candidates.append((saved['epoch'],checkpoint.stat().st_mtime,checkpoint))
            except Exception as exc:progress(f'Checkpoint ignoré car illisible : {checkpoint} ({exc})')
        if not candidates:raise FileNotFoundError('Aucun checkpoint route reprenable')
        _,_,checkpoint=max(candidates)
        source=checkpoint.parent.parent
        ck=torch.load(checkpoint,map_location='cpu',weights_only=False)
        epoch=ck['epoch']+1
        if epoch<=0 or ck.get('optimizer') is None:raise ValueError('Checkpoint non reprenable')
        target=ROOT/'results/training'/('route_resume_'+datetime.now().strftime('%Y%m%d_%H%M%S'))
        shutil.copytree(source,target)
        lines=(target/'results.csv').read_text().splitlines()
        (target/'results.csv').write_text('\n'.join([lines[0]]+[line for line in lines[1:] if int(line.split(',')[0])<=epoch])+'\n')
        ck['train_args'].update(project=str(target.parent),name=target.name,save_dir=str(target),save_period=1)
        torch.save(ck,target/'weights/last.pt')
        previous_seconds=float((source/'results.csv').read_text().splitlines()[-1].split(',')[1])
        progress(f'Reprise route après époque {epoch}/12, copie isolée {target.name}. Optimiseur et poids restaurés. Checkpoint à chaque époque.')
        model=YOLO(str(target/'weights/last.pt'))
        model.add_callback('on_model_save',lambda t:progress(f'route : époque {t.epoch+1}/{t.epochs} enregistrée dans {t.last}'))
        start=time.perf_counter();model.train(resume=True,device='cpu',workers=0)
        finish('route',model,start,epoch,previous_seconds)
    else:progress('Modèle route déjà présent : entraînement ignoré.')
    if not (ROOT/'models/stop.pt').exists():
        progress('Début du détecteur stop uniquement ; transport et HOG/SVM réutilisés sans entraînement.')
        start=time.perf_counter();model=YOLO(str(ROOT/'models/yolov8n.pt'))
        model.add_callback('on_model_save',lambda t:progress(f'stop : époque {t.epoch+1}/{t.epochs} enregistrée dans {t.last}'))
        model.train(data=str(ROOT/'data/stop/data.yaml'),epochs=args.stop_epochs,imgsz=320,batch=8,device='cpu',workers=0,seed=42,deterministic=True,
          project=str(ROOT/'results/training'),name='stop',exist_ok=False,patience=10,pretrained=True,plots=True,cache=False,amp=False,
          degrees=3,translate=.05,scale=.2,fliplr=0,flipud=0,mosaic=0,close_mosaic=0,save_period=1)
        finish('stop',model,start)
    else:progress('Modèle stop déjà présent : entraînement ignoré.')

if __name__=='__main__':main()
