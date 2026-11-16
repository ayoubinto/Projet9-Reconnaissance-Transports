"""Audit, conversion des polygones et séparation par source, sans modifier les originaux."""
import argparse, hashlib, json, random, shutil
from collections import Counter, defaultdict
from pathlib import Path
import cv2
import numpy as np
import yaml

ROOT = Path(__file__).resolve().parents[1]
DATASETS = {'transport': 'Public Transport.v1i.yolov8', 'route': 'bus-route-number.v1i.yolov8', 'stop': 'BusStop.v1i.yolov8'}

def box_from_line(line, nc):
    v = list(map(float, line.split()))
    if not v or not np.isfinite(v).all() or v[0] != int(v[0]) or not 0 <= v[0] < nc:
        raise ValueError('Classe ou coordonnées invalides')
    c, coords = int(v[0]), v[1:]
    if len(coords) == 4:
        x, y, w, h = coords
    elif len(coords) >= 6 and len(coords) % 2 == 0:
        xs, ys = coords[::2], coords[1::2]
        if min(coords) < 0 or max(coords) > 1: raise ValueError('Polygone hors image')
        x, y = (min(xs)+max(xs))/2, (min(ys)+max(ys))/2
        w, h = max(xs)-min(xs), max(ys)-min(ys)
    else: raise ValueError('Format annotation invalide')
    if w <= 0 or h <= 0 or min(x-w/2,y-h/2) < -1e-5 or max(x+w/2,y+h/2) > 1.00001:
        raise ValueError('Rectangle hors image ou vide')
    return c, x, y, w, h

def prepare(raw, target, seed=42):
    if target.exists(): raise FileExistsError(f'{target} existe déjà. Utiliser un autre dossier pour préserver les résultats.')
    target.mkdir(parents=True)
    audit = {}
    for task, folder in DATASETS.items():
        source = raw / folder
        cfg = yaml.safe_load((source/'data.yaml').read_text(encoding='utf-8'))
        names = cfg['names']; records=[]; errors=[]; polygons=0
        parent={}
        def find(x):
            parent.setdefault(x,x)
            if parent[x]!=x: parent[x]=find(parent[x])
            return parent[x]
        def union(a,b): parent[find(a)]=find(b)
        hashes={}
        for p in sorted(source.glob('*/images/*')):
            if p.suffix.lower() not in {'.jpg','.jpeg','.png'}: continue
            try:
                image=cv2.imdecode(np.fromfile(p,dtype=np.uint8),cv2.IMREAD_COLOR)
                if image is None: raise ValueError('Image illisible')
                label=p.parent.parent/'labels'/f'{p.stem}.txt'
                lines=[x for x in label.read_text().splitlines() if x.strip()]
                boxes=[box_from_line(x,len(names)) for x in lines]
                polygons+=sum(len(x.split())>5 for x in lines)
                group=p.stem.split('.rf.')[0]
                find(group)
                sha=hashlib.sha256(image.tobytes()+str(image.shape).encode()).hexdigest()
                if sha in hashes: union(group,hashes[sha])
                hashes[sha]=group
                records.append(dict(path=p, boxes=boxes, group=group, sha256=sha, original_split=p.parent.parent.name))
            except (ValueError,OSError) as e: errors.append({'path':str(p.relative_to(raw)), 'error':str(e)})
        if errors:
            (target/'errors.json').write_text(json.dumps(errors,indent=2),encoding='utf-8')
            raise ValueError(f'{task}: {len(errors)} erreurs; voir errors.json')
        groups=defaultdict(list)
        for r in records: groups[find(r['group'])].append(r)
        # Stratification par ensemble des classes du groupe, sans séparer les variantes.
        strata=defaultdict(list)
        for g,rs in groups.items(): strata[tuple(sorted({b[0] for r in rs for b in r['boxes']}))].append(g)
        assignment={}; rng=random.Random(seed)
        for gs in strata.values():
            gs.sort(); rng.shuffle(gs); n=len(gs)
            if n<3: raise ValueError('Moins de trois groupes dans une strate; séparation manuelle nécessaire')
            nv=max(1,round(n*.15)); nt=max(1,round(n*.15))
            for i,g in enumerate(gs): assignment[g]='val' if i<nv else 'test' if i<nv+nt else 'train'
        manifest=[]; counts=defaultdict(Counter); original=Counter()
        for i,r in enumerate(records):
            split=assignment[find(r['group'])]; stem=f'{i:05d}_{r["path"].stem}'
            idir=target/task/split/'images'; ldir=target/task/split/'labels'
            idir.mkdir(parents=True,exist_ok=True); ldir.mkdir(parents=True,exist_ok=True)
            dst=idir/(stem+r['path'].suffix)
            shutil.copy2(r['path'],dst)
            (ldir/(stem+'.txt')).write_text('\n'.join(f'{b[0]} '+ ' '.join(f'{v:.8f}' for v in b[1:]) for b in r['boxes'])+'\n')
            counts[split]['images']+=1
            for b in r['boxes']: counts[split][names[b[0]]]+=1
            original[r['original_split']]+=1
            manifest.append(dict(image=str(dst.relative_to(target/task)).replace('\\','/'), source=str(r['path'].relative_to(raw)), group=find(r['group']), sha256=r['sha256'], split=split))
        for field in ['group','sha256']:
            sets={s:{r[field] for r in manifest if r['split']==s} for s in ['train','val','test']}
            assert not(sets['train']&sets['val'] or sets['train']&sets['test'] or sets['val']&sets['test'])
        (target/task/'manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
        (target/task/'data.yaml').write_text(yaml.safe_dump(dict(path=str((target/task).resolve()), train='train/images',val='val/images',test='test/images', names=names)),encoding='utf-8')
        audit[task]=dict(images=len(records),groups=len(groups),polygons_converted=polygons,original_splits=original,splits=dict(counts),names=names,provenance=cfg.get('roboflow'),seed=seed)
    (target/'audit.json').write_text(json.dumps(audit,indent=2,ensure_ascii=False),encoding='utf-8')
    return audit

if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('--raw',type=Path,default=ROOT/'data_raw'); p.add_argument('--out',type=Path,default=ROOT/'data'); p.add_argument('--seed',type=int,default=42); a=p.parse_args()
    print(json.dumps(prepare(a.raw,a.out,a.seed),indent=2,ensure_ascii=False))
