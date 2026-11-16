import json, os, time
from pathlib import Path
import cv2
import numpy as np
from src.vision import crop,preprocess,route_candidates
ROOT=Path(__file__).resolve().parents[1]
os.environ.setdefault('YOLO_CONFIG_DIR',str(ROOT/'.cache/ultralytics'))

class Pipeline:
    def __init__(self,ocr=True):
        import torch
        from ultralytics import YOLO
        torch.set_num_threads(4)
        self.models={t:YOLO(str(ROOT/f'models/{t}.pt')) for t in ['transport','route','stop']}
        self.reader=None
        if ocr:
            import easyocr
            self.reader=easyocr.Reader(['en','fr'],gpu=False,model_storage_directory=str(ROOT/'models/ocr'),user_network_directory=str(ROOT/'.cache/easyocr'),download_enabled=False)

    def read(self,roi):
        if self.reader is None: return []
        # Une seule variante prédéfinie évite la sélection a posteriori selon le test.
        gray=preprocess(roi)['contrast']
        gray=cv2.resize(gray,None,fx=2,fy=2,interpolation=cv2.INTER_CUBIC)
        return [{'text':s,'confidence':float(c)} for _,s,c in self.reader.readtext(gray,detail=1,paragraph=False)]

    def predict(self,image,conf=.25):
        if image is None or image.size==0: raise ValueError('Image invalide')
        start=time.perf_counter(); out=[]; annotated=image.copy()
        for task,model in self.models.items():
            result=model.predict(image,conf=conf,imgsz=320,device='cpu',verbose=False)[0]
            for b in result.boxes:
                xyxy=b.xyxy[0].tolist();label=model.names[int(b.cls.item())]
                item=dict(task=task,label=label,confidence=float(b.conf.item()),box=xyxy,text=[],route_candidates=[],stop_name=None)
                if task in {'route','stop'}:
                    item['text']=self.read(crop(image,xyxy))
                    if task=='route': item['route_candidates']=route_candidates(' '.join(x['text'] for x in item['text'] if x['confidence']>=.3))
                    # Texte visible uniquement, pas une identité géographique certifiée.
                    else: item['visible_stop_text']=' '.join(x['text'] for x in item['text'] if x['confidence']>=.3)
                out.append(item)
                x1,y1,x2,y2=map(int,xyxy); color={'transport':(30,210,40),'route':(0,180,255),'stop':(240,170,30)}[task]
                cv2.rectangle(annotated,(x1,y1),(x2,y2),color,2)
                cv2.putText(annotated,f'{label} {item["confidence"]:.2f}',(x1,max(18,y1-5)),cv2.FONT_HERSHEY_SIMPLEX,.5,color,1)
        # Associer un panneau au véhicule contenant son centre; conserve les cas non associés.
        vehicles=[i for i,x in enumerate(out) if x['task']=='transport']
        for x in out:
            if x['task']=='route':
                cx=(x['box'][0]+x['box'][2])/2;cy=(x['box'][1]+x['box'][3])/2
                candidates=[i for i in vehicles if out[i]['box'][0]<=cx<=out[i]['box'][2] and out[i]['box'][1]<=cy<=out[i]['box'][3]]
                x['vehicle_index']=min(candidates,key=lambda i:(out[i]['box'][2]-out[i]['box'][0])*(out[i]['box'][3]-out[i]['box'][1])) if candidates else None
        return dict(detections=out,seconds=time.perf_counter()-start,ocr_enabled=self.reader is not None),annotated

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('image',type=Path);p.add_argument('--out',type=Path,default=ROOT/'results/prediction');p.add_argument('--no-ocr',action='store_true');a=p.parse_args()
    im=cv2.imdecode(np.fromfile(a.image,dtype=np.uint8),cv2.IMREAD_COLOR)
    result,vis=Pipeline(not a.no_ocr).predict(im);a.out.mkdir(parents=True,exist_ok=True)
    (a.out/'prediction.json').write_text(json.dumps(result,indent=2,ensure_ascii=False),encoding='utf-8');cv2.imwrite(str(a.out/'prediction.jpg'),vis)
    print(json.dumps(result,indent=2,ensure_ascii=False))

