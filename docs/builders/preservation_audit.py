import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]/'outputs/Projet9'
paths=[ROOT/'models/transport.pt',ROOT/'models/hog_svm.joblib',ROOT/'models/yolov8n.pt']
paths += list((ROOT/'data_raw').rglob('*'))
paths += [ROOT/f'results/{n}' for n in ['baseline_metrics.json','ocr_metrics.json','transport_metrics.json','tests.log','training.log']]
paths += list((ROOT/'results/training/route/weights').glob('*.pt'))
paths += list((ROOT/'results/training/transport2/weights').glob('*.pt'))
result={str(p.relative_to(ROOT)).replace('\\','/'):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths if p.is_file()}
dest=ROOT/'results/preservation_sha256.json'
if not dest.exists():dest.write_text(json.dumps(result,indent=2),encoding='utf-8');print(f'{len(result)} empreintes enregistrées')
else:
    old=json.loads(dest.read_text());changes=[p for p,h in old.items() if result.get(p)!=h]
    print({'files_verified':len(old),'changes':changes});assert not changes
