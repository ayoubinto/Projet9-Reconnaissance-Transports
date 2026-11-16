"""Génère une démonstration reproductible sur des images de test, sans sélection au score."""
import json,shutil
from pathlib import Path
import cv2
from src.pipeline import Pipeline,ROOT
from src.vision import preprocess

if __name__=='__main__':
    pipeline=Pipeline();dest=ROOT/'results/demo';dest.mkdir(parents=True,exist_ok=True)
    (ROOT/'examples').mkdir(exist_ok=True)
    summary=[]
    for task in ['transport','route','stop']:
        path=sorted((ROOT/f'data/{task}/test/images').glob('*.jpg'))[0]
        im=cv2.imread(str(path));shutil.copy2(path,ROOT/f'examples/{task}.jpg')
        result,vis=pipeline.predict(im)
        result['source']=str(path.relative_to(ROOT));summary.append(result)
        cv2.imwrite(str(dest/f'{task}_prediction.jpg'),vis)
        pp=preprocess(im)
        for k in ['gray','denoise','contrast','binary','edges']:cv2.imwrite(str(dest/f'{task}_{k}.png'),pp[k])
    rows=json.loads((ROOT/'examples/ocr_rois/annotations.json').read_text(encoding='utf-8'))
    readable=next(r for r in rows if r['readable'] is True)
    path=ROOT/readable['source'];im=cv2.imread(str(path));shutil.copy2(path,ROOT/'examples/route_readable.jpg')
    result,vis=pipeline.predict(im);result['source']=str(path.relative_to(ROOT));summary.append(result)
    cv2.imwrite(str(dest/'route_readable_prediction.jpg'),vis)
    (dest/'predictions.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False),encoding='utf-8')
    print('Démonstration enregistrée dans results/demo')
