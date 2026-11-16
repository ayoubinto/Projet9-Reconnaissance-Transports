"""Évaluation exploratoire de la lecture après détection sur huit panneaux lisibles."""
import json
import cv2
from src.pipeline import Pipeline,ROOT
from src.vision import route_candidates

def iou(a,b):
    inter=max(0,min(a[2],b[2])-max(a[0],b[0]))*max(0,min(a[3],b[3])-max(a[1],b[1]))
    union=(a[2]-a[0])*(a[3]-a[1])+(b[2]-b[0])*(b[3]-b[1])-inter
    return inter/union if union>0 else 0

if __name__=='__main__':
    pipeline=Pipeline();rows=json.loads((ROOT/'examples/ocr_rois/annotations.json').read_text(encoding='utf-8'));out=[]
    for r in rows:
        if r['readable'] is not True:continue
        im=cv2.imread(str(ROOT/r['source']));prediction,_=pipeline.predict(im)
        matches=[d for d in prediction['detections'] if d['task']=='route' and iou(d['box'],r['box'])>=.5]
        best=max(matches,key=lambda d:d['confidence']) if matches else None
        text=best['route_candidates'][0] if best and best['route_candidates'] else ''
        out.append(dict(source=r['source'],roi=r['roi'],truth=r['route_truth'],prediction=text,localized=best is not None,correct=text==r['route_truth']))
    report=dict(n=len(out),correct=sum(r['correct'] for r in out),localized=sum(r['localized'] for r in out),
                exact_success_rate=sum(r['correct'] for r in out)/len(out),detection_conf=.25,IoU=.5,rows=out,
                limitation='Exploratory readable positive subset only; not a full system accuracy or false-positive evaluation')
    (ROOT/'results/pipeline_metrics.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps(report,indent=2))
