import json, unittest
from pathlib import Path
from src.prepare import ROOT,box_from_line

class DataTests(unittest.TestCase):
    def test_no_leakage(self):
        for task in ['transport','route','stop']:
            rows=json.loads((ROOT/f'data/{task}/manifest.json').read_text())
            for field in ['group','sha256']:
                sets={s:{r[field] for r in rows if r['split']==s} for s in ['train','val','test']}
                self.assertFalse(sets['train']&sets['test']);self.assertFalse(sets['train']&sets['val']);self.assertFalse(sets['test']&sets['val'])
            for r in rows:
                image=ROOT/f'data/{task}'/r['image']; self.assertTrue(image.is_file())
                label=image.parent.parent/'labels'/f'{image.stem}.txt';self.assertTrue(label.is_file())
                for l in label.read_text().splitlines():
                    if l.strip():box_from_line(l,3 if task=='transport' else 1)

if __name__=='__main__':unittest.main()
