"""Vérification effective des fichiers, modèles et application, après entraînement."""
import sys,subprocess,json,os,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]/'outputs/Projet9'
os.chdir(ROOT);sys.path.insert(0,str(ROOT))
def run(module,log):
    with (ROOT/'results'/log).open('x',encoding='utf-8') as f:
        subprocess.run([sys.executable,'-m',module],stdout=f,stderr=subprocess.STDOUT,check=True)
run('src.demo','demo_execution.log')
run('src.evaluate_pipeline','pipeline_evaluation.log')
with (ROOT/'results/tests_final.log').open('x',encoding='utf-8') as f:
    result=subprocess.run([sys.executable,'-m','unittest','discover','-s','tests','-v'],stdout=f,stderr=subprocess.STDOUT)
log=(ROOT/'results/tests_final.log').read_text(encoding='utf-8')
report=dict(exit_code=result.returncode,log='results/tests_final.log',functional_tests=['OCR and persistent results','No OCR and threshold change'],passed=result.returncode==0,skipped='skipped=' in log)
(ROOT/'results/app_test.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
if result.returncode or report['skipped']:raise RuntimeError('Les tests ont échoué ou été ignorés; examiner le journal.')
with (ROOT/'PROGRESS.md').open('a',encoding='utf-8') as f:f.write('\n- Démonstration et évaluation de bout en bout exécutées. Suite complète et tests fonctionnels Streamlit réussis, sans test ignoré. Voir results/tests_final.log.\n')
print('Validation terminée',flush=True)
