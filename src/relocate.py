"""Répare les chemins des YAML après déplacement du dossier livré."""
from pathlib import Path
import yaml
ROOT=Path(__file__).resolve().parents[1]
if __name__=='__main__':
    for p in (ROOT/'data').glob('*/data.yaml'):
        cfg=yaml.safe_load(p.read_text(encoding='utf-8'));cfg['path']=str(p.parent.resolve())
        p.write_text(yaml.safe_dump(cfg,allow_unicode=True),encoding='utf-8');print(p)
