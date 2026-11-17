"""Reproduce A -> B -> C from raw inputs, without copying cached results.

Run with the Python environment installed from the repository requirements.txt.
This is a reproducibility workspace, not a replacement for the root frozen files.
"""
from pathlib import Path
import argparse
from datetime import datetime
import hashlib
import json
import shutil
import subprocess
import sys
import time


def main():
    root=Path(__file__).resolve().parents[1]
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-root',type=Path,default=root/'local_review/ABC_reproduction')
    args=parser.parse_args()
    base=args.output_root.resolve()
    if base==root or root not in base.parents:
        raise ValueError('output-root must be a project child directory')
    run=base/(datetime.now().strftime('%Y%m%d_%H%M%S_')+str(time.time_ns()))
    run.mkdir(parents=True,exist_ok=False)
    workspace=run/'workspace';workspace.mkdir()
    inputs=['01_data_quality.py','01_data_quality.ipynb','02_models.py','03_eval.py',
            '03_eval.ipynb','c01_support.py','requirements.txt','configs/features.yaml',
            'data/raw/bank-additional-full.csv']
    optional='data/raw/bank-additional-names.txt'
    if (root/optional).is_file():inputs.append(optional)
    hashes={}
    for name in inputs:
        target=workspace/name;target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(root/name,target)
        hashes[name]=hashlib.sha256(target.read_bytes()).hexdigest()
    manifest={'criterion':'complete reproduction under GitHub-declared environment',
              'requires_identical_original_environment':False,
              'copied_input_sha256':hashes,'cached_outputs_copied':False,'stages':[]}
    (run/'input_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
    for phase,script in [('A','01_data_quality.py'),('B','02_models.py'),('C','03_eval.py')]:
        start=time.perf_counter()
        completed=subprocess.run([sys.executable,str(workspace/script)],cwd=workspace,capture_output=True,text=True,encoding='utf-8',errors='replace')
        (run/(phase+'.log')).write_text(completed.stdout+'\n'+completed.stderr,encoding='utf-8')
        manifest['stages'].append({'phase':phase,'returncode':completed.returncode,'seconds_observed':time.perf_counter()-start})
        (run/'run_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
        if completed.returncode:
            raise RuntimeError(f'{phase} failed; inspect {run / (phase+".log")}')
        print(f'PASS {phase}: {script}',flush=True)
    metrics=workspace/'local_review/C01_candidate/outputs/metrics.json'
    if not metrics.is_file():raise RuntimeError('Missing paired C metrics')
    manifest['metrics_relative_to_run']=metrics.relative_to(run).as_posix()
    manifest['status']='ABC_REPRODUCED'
    (run/'run_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
    (base/'latest_run.txt').write_text(str(run),encoding='utf-8')
    print(f'[ABC_REPRODUCED] {metrics}',flush=True)


if __name__=='__main__':main()
