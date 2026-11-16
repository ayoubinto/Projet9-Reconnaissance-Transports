"""OCR sur ROI vérité terrain: mesure isolée, distincte du pipeline complet."""
import argparse, csv, json, time
from pathlib import Path
import cv2
from src.vision import crop,preprocess,route_candidates,edit_distance
ROOT=Path(__file__).resolve().parents[1]

def export_rois(limit=18):
    dest=ROOT/'examples/ocr_rois';dest.mkdir(parents=True,exist_ok=True)
    images=sorted((ROOT/'data/route/test/images').glob('*.jpg'))
    rows=[];seen=set()
    manifest=json.loads((ROOT/'data/route/manifest.json').read_text())
    groups={Path(r['image']).name:r['group'] for r in manifest}
    for p in images:
        if groups[p.name] in seen: continue
        seen.add(groups[p.name])
        im=cv2.imread(str(p)); h,w=im.shape[:2]
        labels=(p.parent.parent/'labels'/f'{p.stem}.txt').read_text().splitlines()
        for i,l in enumerate(labels):
            if not l.strip(): continue
            _,x,y,bw,bh=map(float,l.split()); box=[(x-bw/2)*w,(y-bh/2)*h,(x+bw/2)*w,(y+bh/2)*h]
            roi=crop(im,box);name=f'{len(rows):02d}.jpg';cv2.imwrite(str(dest/name),roi)
            rows.append(dict(roi=name,source=str(p.relative_to(ROOT)).replace('\\','/'),box=box,route_truth='',readable='',note=''))
            if len(rows)>=limit: break
        if len(rows)>=limit: break
    (dest/'annotations.json').write_text(json.dumps(rows,indent=2),encoding='utf-8')

def evaluate():
    import easyocr
    import torch
    torch.set_num_threads(4)
    reader=easyocr.Reader(['en','fr'],gpu=False,model_storage_directory=str(ROOT/'models/ocr'),user_network_directory=str(ROOT/'.cache/easyocr'),download_enabled=False)
    dest=ROOT/'examples/ocr_rois'
    rows=json.loads((dest/'annotations.json').read_text(encoding='utf-8'));predictions=[];distance=chars=correct=n=0
    start=time.perf_counter()
    for r in rows:
        if r['readable'] is not True: continue
        gray=preprocess(cv2.imread(str(dest/r['roi'])))['contrast']
        gray=cv2.resize(gray,None,fx=2,fy=2,interpolation=cv2.INTER_CUBIC)
        texts=reader.readtext(gray,detail=1,paragraph=False)
        candidates=route_candidates(' '.join(s for _,s,c in texts if c>=.3))
        prediction=candidates[0] if candidates else ''
        gt=r['route_truth'];n+=1;correct+=prediction==gt;distance+=edit_distance(gt,prediction);chars+=len(gt)
        predictions.append(dict(roi=r['roi'],truth=gt,prediction=prediction,candidates=candidates,texts=[{'text':s,'confidence':float(c)} for _,s,c in texts]))
    report=dict(protocol='First readable test ROIs in filename order; manual visual transcription before OCR; ground-truth boxes',
                n=n,excluded=len(rows)-n,exact_accuracy=correct/n if n else None,CER=distance/chars if chars else None,
                seconds=time.perf_counter()-start,predictions=predictions,
                limitation='Small exploratory sample; conditional on ground-truth crop, not end-to-end accuracy; single annotator')
    (ROOT/'results/ocr_metrics.json').write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf-8')
    print(json.dumps(report,indent=2,ensure_ascii=False))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--export',action='store_true');a=p.parse_args()
    export_rois() if a.export else evaluate()

