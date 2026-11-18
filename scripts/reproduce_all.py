"""Rebuild ABC and D assets from raw CSV, then check the authored report evidence.

Requires only the original requirements.txt analysis packages. Word and Codex
are not needed: report.docx is an authored deliverable, verified without saving it.
Every run creates new workspaces; shipped result ZIPs are never calculation inputs.
"""
from pathlib import Path
from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_UP
import argparse
import hashlib
import importlib.metadata
import json
import math
import os
import platform
import shutil
import subprocess
import sys
import time
import unicodedata
import xml.etree.ElementTree as ET
import zipfile

ROOT = Path(__file__).resolve().parents[1]
DECLARED = {'pandas':'2.2.3','scikit-learn':'1.6.1','PyYAML':'6.0.2','matplotlib':'3.9.4'}
ANALYSIS_INPUTS = [
    '01_data_quality.py','01_data_quality.ipynb','02_models.py','03_eval.py',
    '03_eval.ipynb','c01_support.py','requirements.txt','configs/features.yaml',
    'data/raw/bank-additional-full.csv','data/raw/bank-additional-names.txt',
    'scripts/reproduce_abc.py','scripts/d01_contact_policy.py','scripts/d02_report_assets.py',
]
SCIENCE_KEYS = ['data','protocol','selected_model','models','business','validation',
                'model_selection','coefficients','ablation','error_slices','failure_cases',
                'sensitivity','pr_curves']


def fingerprint(path):
    data=Path(path).read_bytes()
    return {'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),
            'lf_normalized_sha256':hashlib.sha256(data.replace(b'\r\n',b'\n').replace(b'\r',b'\n')).hexdigest()}


def read(path):return json.loads(Path(path).read_text(encoding='utf-8'))


def write(path,value):
    Path(path).write_text(json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')


def normalized(text):
    return ''.join(unicodedata.normalize('NFKC',text).replace('\u2060','').split())


def resolve(value,key):
    for part in key.split('.'):value=value[int(part)] if isinstance(value,list) else value[part]
    return value


def display(value,fmt):
    if fmt=='n':return f'{int(value):,}'
    if fmt=='int':return str(int(value))
    if fmt=='ap':return f'{value:.6f}'
    if fmt=='p2':return str((Decimal(str(value))*100).quantize(Decimal('0.01'),rounding=ROUND_HALF_UP))+'%'
    if fmt=='p0':return f'{value:.0%}'
    if fmt=='coef':return str(Decimal(str(value)).quantize(Decimal('0.001'),rounding=ROUND_HALF_UP))
    if fmt=='signed':return f'{int(value):+d}'
    raise ValueError('Unknown report number format: '+fmt)


def scientific(metrics):
    result={k:metrics[k] for k in SCIENCE_KEYS}
    # Original byte identity can change on LF/CRLF checkout; content identity stays checked.
    # [D04_02-03 原比较保留：LF/CRLF也改变原字节大小，不属于科学差异]
    # result['data']={k:v for k,v in metrics['data'].items() if k!='raw_sha256'}
    result['data']={k:v for k,v in metrics['data'].items() if k not in ['raw_sha256','raw_file_bytes']}
    result['contact_policy']={k:metrics['contact_policy'][k] for k in ['policy','policy_sha256','folds','definitions','limitations','evaluation_type']}
    return result


def compare(expected,actual,path='',errors=None):
    """Compare all scientific fields; only float roundoff up to 1e-12 is allowed."""
    if errors is None:errors=[]
    if isinstance(expected,dict):
        if not isinstance(actual,dict) or set(expected)!=set(actual):errors.append(path+': object keys differ');return errors
        for key in expected:compare(expected[key],actual[key],path+'.'+key,errors)
    elif isinstance(expected,list):
        if not isinstance(actual,list) or len(expected)!=len(actual):errors.append(path+': list length differs');return errors
        for i,(a,b) in enumerate(zip(expected,actual)):compare(a,b,path+'.'+str(i),errors)
    elif isinstance(expected,float):
        if isinstance(actual,bool) or not isinstance(actual,(int,float)) or not math.isfinite(actual) or not math.isclose(expected,actual,rel_tol=0,abs_tol=1e-12):errors.append(path+': numeric result differs')
    elif type(expected) is not type(actual) or expected!=actual:errors.append(path+': value differs')
    return errors


def preflight():
    contract=read(ROOT/'docs/REPORT_EVIDENCE.json')
    observed={name:importlib.metadata.version(name) for name in DECLARED}
    if sys.version_info<(3,9) or observed!=DECLARED:raise RuntimeError('Use Python>=3.9 and the unchanged requirements.txt: '+str(observed))
    # [D04_01-02 原行保留] for name in ANALYSIS_INPUTS:
    # [D04_02-04 原输入范围保留]
    # for name in ANALYSIS_INPUTS+['scripts/reproduce_all.py']:
    for name in ANALYSIS_INPUTS+['scripts/reproduce_all.py','scripts/result_bundle.py']:
        current=fingerprint(ROOT/name)
        if current['lf_normalized_sha256']!=contract['source_inputs'][name]['lf_normalized_sha256']:
            raise ValueError('Source input differs from the registered version: '+name)
    report=ROOT/'report.docx'
    if fingerprint(report)['sha256']!=contract['report']['sha256']:raise ValueError('report.docx changed; recheck the authored report before updating its evidence contract')
    with zipfile.ZipFile(report) as z:
        text=''.join(ET.fromstring(z.read('word/document.xml')).itertext())
        images=sorted(hashlib.sha256(z.read(n)).hexdigest() for n in z.namelist() if n.startswith('word/media/'))
    if images!=sorted(contract['report']['embedded_figure_sha256']):raise ValueError('Report embedded figures differ')
    if any(normalized(c['display']) not in normalized(text) for c in contract['claims']):raise ValueError('A registered report number is missing')
    # [D04_02-05 新增：已渲染页码登记的完整性，不把分析脚本当Word分页器]
    page_map={'claims':[{k:c[k] for k in ['element_id','key','report_pages']} for c in contract['claims']], 'figures':contract['report']['figure_pages']}
    digest=hashlib.sha256(json.dumps(page_map,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode('utf-8')).hexdigest()
    if digest!=contract['report']['page_registration_sha256'] or any(not c['report_pages'] or c.get('ppt_pages') is not None for c in contract['claims']):raise ValueError('Report page registration differs or PPT pages were fabricated')
    return contract,observed


# [D04_01-01 原嵌套运行实现逐行注释保留；Windows路径过长修复]
# def main():
#     if hasattr(sys.stdout,'reconfigure'):sys.stdout.reconfigure(encoding='utf-8')
#     parser=argparse.ArgumentParser(description=__doc__)
#     parser.add_argument('--output-root',type=Path,default=ROOT/'runs')
#     parser.add_argument('--font-family',help='Optional installed CJK font for F5, e.g. Microsoft YaHei or Noto Sans CJK SC')
#     parser.add_argument('--check-only',action='store_true',help='Validate inputs and analysis packages without training')
#     args=parser.parse_args();base=args.output_root.resolve();allowed=(ROOT/'runs').resolve()
#     if base!=allowed and allowed not in base.parents:raise ValueError('output-root must be runs/ or a child of runs/; root/historical files cannot be overwritten')
#     contract,observed=preflight()
#     if args.check_only:print('[D04_PREFLIGHT_PASS] declared environment, raw inputs, code and authored report verified');return
#     run=base/(datetime.now().strftime('%Y%m%d_%H%M%S_')+str(time.time_ns()));run.mkdir(parents=True,exist_ok=False)
#     workspace=run/'workspace';workspace.mkdir()
#     watched={name:fingerprint(ROOT/name) for name in ANALYSIS_INPUTS+['report.docx','docs/REPORT_EVIDENCE.json']}
#     for name in ANALYSIS_INPUTS:
#         dest=workspace/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/name,dest)
#     metadata={'schema':'D04-01','status':'RUNNING','created_at_utc':datetime.now(timezone.utc).isoformat(),
#               'input_fingerprints':watched,'copied_analysis_inputs':ANALYSIS_INPUTS,'cached_outputs_copied':False,
#               'scientific_criterion':'GitHub-declared full reconstruction; recorded reference science and report evidence',
#               'historical_scores_must_be_recovered':False,'report_generated':False,'source_report_sha256':watched['report.docx']['sha256'],
#               'environment':{'declared':DECLARED,'observed':observed,'python':sys.version,'platform':platform.platform(),
#                              'observed_distributions':dict(sorted((d.metadata['Name'],d.version) for d in importlib.metadata.distributions() if d.metadata['Name']))},
#               'stages':[]}
#     write(run/'run_manifest.json',metadata)
#     def stage(name,args):
#         started=time.perf_counter();env=os.environ.copy();env['PYTHONUTF8']='1';env['PYTHONIOENCODING']='utf-8';env['MPLBACKEND']='Agg'
#         p=subprocess.run([sys.executable]+[str(a) for a in args],cwd=workspace,env=env,capture_output=True,text=True,encoding='utf-8',errors='replace')
#         (run/(name+'.log')).write_text(p.stdout+'\n'+p.stderr,encoding='utf-8')
#         metadata['stages'].append({'stage':name,'returncode':p.returncode,'seconds_observed':time.perf_counter()-started})
#         if p.returncode:metadata['status']='FAILED';write(run/'run_manifest.json',metadata);raise RuntimeError(name+' failed; inspect '+str(run/(name+'.log')))
#         write(run/'run_manifest.json',metadata);print('PASS '+name,flush=True)
#     stage('ABC',[workspace/'scripts/reproduce_abc.py','--output-root',workspace/'generated/abc'])
#     abc_run=Path((workspace/'generated/abc/latest_run.txt').read_text(encoding='utf-8'))
#     stage('D01',[workspace/'scripts/d01_contact_policy.py','--abc-run',abc_run])
#     d_metrics=workspace/'local_review/D01_candidate/outputs/metrics.json'
#     d2=[workspace/'scripts/d02_report_assets.py','--metrics',d_metrics]
#     if args.font_family:d2+=['--font-family',args.font_family]
#     stage('D02',d2)
#     metrics=read(d_metrics);observed_science=scientific(metrics);differences=compare(contract['science_reference'],observed_science)
#     bindings=[]
#     for claim in contract['claims']:
#         value=resolve(metrics,claim['key']);errors=compare(claim['raw_value'],value,claim['key'])
#         shown=display(value,claim['format'])
#         bindings.append({**claim,'reproduced_value':value,'reproduced_display':shown,'matches':not errors and shown==claim['display']})
#     diagram=read(workspace/'local_review/D02_candidate/outputs/D02_报告素材索引.json')['diagram']
#     diagram_differences=compare(contract['diagram_reference'],diagram)
#     write(run/'report_evidence_check.json',{'report_sha256':watched['report.docx']['sha256'],'report_authored_not_regenerated':True,
#           'science_differences':differences,'diagram_differences':diagram_differences,'claims':bindings,
#           'matched_claims':sum(c['matches'] for c in bindings),'claim_count':len(bindings),
#           'numeric_tolerance':{'integer_and_text':'exact','float_absolute':1e-12},
#           'excluded_from_science_comparison':['timestamps','runtime paths','source code fingerprints','observed package records','raw-byte CSV SHA only; LF content SHA retained'],
#           'reference_environment_scope':'No guarantee of bit-identical historical upstream scores or identical font pixels on every compatible OS.'})
#     if differences or diagram_differences or not all(c['matches'] for c in bindings):
#         metadata['status']='REPORT_EVIDENCE_MISMATCH';write(run/'run_manifest.json',metadata)
#         raise RuntimeError('Rebuilt results do not match the registered authored report; inspect report_evidence_check.json; no report was overwritten')
#     if any(fingerprint(ROOT/name)!=record for name,record in watched.items()):raise RuntimeError('An input changed during reconstruction')
#     output={}
#     abc_ws=abc_run/'workspace'
#     for label,folder in [('A_outputs',abc_ws/'outputs'),('A_figures',abc_ws/'figures'),
#                          ('B',abc_ws/'local_review/B01_candidate/outputs'),('C_outputs',abc_ws/'local_review/C01_candidate/outputs'),
#                          ('C_figures',abc_ws/'local_review/C01_candidate/figures'),('D01',workspace/'local_review/D01_candidate/outputs'),
#                          ('D02',workspace/'local_review/D02_candidate/outputs')]:
#         for path in sorted(folder.iterdir()):
#             if path.is_file():output[label+'/'+path.name]={'path':path.relative_to(run).as_posix(),**fingerprint(path)}
#     write(run/'artifact_index.json',output)
#     # Preferred links follow the current run, not any shipped result ZIP or audit cache.
#     a=lambda label:output[label]['path']
#     index=['# 本次完整重建结果','',
#            '本目录从原始CSV新建工作区运行ABC、D01和D02，未复制既有结果。根目录report.docx是手工定稿，未重新生成或覆盖。',
#            '',f"报告数字核对：{len(bindings)} / {len(bindings)}项通过。",'',
#            '| 内容 | 本次实际文件 |','|---|---|',
#            '| 统一数字源（含补充回放） | [metrics.json]('+a('D01/metrics.json')+') |',
#            '| Test模型比较 | [C_测试集模型比较表.md]('+a('C_outputs/C_测试集模型比较表.md')+') |',
#            '| 固定规则及代价 | [T6_联系限制补充评价.md]('+a('D01/T6_联系限制补充评价.md')+') |',
#            '| 建议行动流程 | [F5 PNG]('+a('D02/F5_行动闭环.png')+') / [SVG]('+a('D02/F5_行动闭环.svg')+') |',
#            '| 完整产物位置及指纹 | [artifact_index.json](artifact_index.json) |',
#            '| 报告107处数字和科学结果比对 | [report_evidence_check.json](report_evidence_check.json) |','',
#            '阶段原始输出中保留了D01/D02当时的写作提示与默认路径；本次查看以本页实际文件和artifact_index为准。D02素材脚本不创建正式Word，不代表当前没有报告。',
#            '内部兼容目录local_review是这次运行新生成的中间工作目录，不需要提交或预先复制本机原local_review。',
#            '不同字体可能改变PNG/SVG字节；科学值、规则和图内数字仍须核对。完整提交快照与T5/PPT页码在后续材料整合中完成。']
#     (run/'RUN_RESULTS.md').write_text('\n'.join(index)+'\n',encoding='utf-8')
#     metadata.update({'status':'ABCD_REPRODUCED','matched_report_claims':len(bindings),'scientific_reference_matched':True,
#                      'metrics_relative_to_run':d_metrics.relative_to(run).as_posix(),'artifact_index':'artifact_index.json','index':'RUN_RESULTS.md',
#                      'report_and_original_inputs_unchanged':True})
#     write(run/'run_manifest.json',metadata)
#     (base/'latest_run.txt').write_text(run.relative_to(ROOT).as_posix(),encoding='utf-8')
#     print('[ABCD_REPRODUCED] '+str(run/'RUN_RESULTS.md'),flush=True)
#     print('[REPORT_EVIDENCE] '+str(len(bindings))+'/'+str(len(bindings))+' matched; authored report unchanged',flush=True)

def load_packager():
    import importlib.util
    spec=importlib.util.spec_from_file_location('result_bundle',Path(__file__).with_name('result_bundle.py'))
    module=importlib.util.module_from_spec(spec);previous=sys.dont_write_bytecode;sys.dont_write_bytecode=True
    try:spec.loader.exec_module(module)
    finally:sys.dont_write_bytecode=previous
    return module

def main():
    if hasattr(sys.stdout,'reconfigure'):sys.stdout.reconfigure(encoding='utf-8')
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-root',type=Path,default=ROOT/'runs')
    parser.add_argument('--font-family',help='Optional installed CJK font for F5')
    parser.add_argument('--check-only',action='store_true',help='Validate inputs without training')
    # [D04_02-06 新增：只对已经成功的同次运行重复打包，不重新训练]
    # [D05-01 原行保留]
    # parser.add_argument('--package-run',type=Path)
    parser.add_argument('--publish-run',type=Path,help='Recreate the direct result directory of an already successful run')
    args=parser.parse_args();base=args.output_root.resolve();allowed=(ROOT/'runs').resolve()
    if base!=allowed and allowed not in base.parents:raise ValueError('output-root must be runs/ or a child of runs/; root/historical files cannot be overwritten')
    deepest=base/('f'*16)/'abc/workspace/local_review/C01_candidate/outputs/C_测试集模型比较表.md'
    if os.name=='nt' and len(str(deepest))>245:raise ValueError('Project path is too long for Windows output files; use a shorter checkout/output-root within runs/')
    contract,observed=preflight()
    if args.check_only:print('[D04_PREFLIGHT_PASS] declared environment, raw inputs, code and authored report verified');return
    # [D05-02 原重复压缩入口逐行保留]
    # if args.package_run is not None:
    # package=load_packager().package_verified_run(ROOT,(ROOT/args.package_run).resolve(),contract,compare,scientific)
    # print('[RESULTS_PACKAGED] '+str(package['members'])+' members; '+package['sha256']);return
    if args.publish_run is not None:
        result=load_packager().publish_verified_run(ROOT,(ROOT/args.publish_run).resolve(),contract,compare,scientific)
        print('[RESULTS_DIRECTORY] '+str(result['directory'])+'; '+str(result['files'])+' direct files');return
    # One compatibility workspace, a short unique run name, and no nested reproduce_abc run.
    run=base/format(time.time_ns(),'x');run.mkdir(parents=True,exist_ok=False)
    workspace=run
    # [D04_02-07 原来源范围保留]
    # watched={name:fingerprint(ROOT/name) for name in ANALYSIS_INPUTS+['scripts/reproduce_all.py','report.docx','docs/REPORT_EVIDENCE.json']}
    watched={name:fingerprint(ROOT/name) for name in ANALYSIS_INPUTS+['scripts/reproduce_all.py','scripts/result_bundle.py','report.docx','docs/REPORT_EVIDENCE.json']}
    for name in ANALYSIS_INPUTS:
        dest=workspace/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/name,dest)
    metadata={'schema':'D04-01','status':'RUNNING','created_at_utc':datetime.now(timezone.utc).isoformat(),
              'input_fingerprints':watched,'copied_analysis_inputs':ANALYSIS_INPUTS,'cached_outputs_copied':False,
              'scientific_criterion':'GitHub-declared full reconstruction; recorded reference science and report evidence',
              'historical_scores_must_be_recovered':False,'report_generated':False,'source_report_sha256':watched['report.docx']['sha256'],
              'environment':{'declared':DECLARED,'observed':observed,'python':sys.version,'platform':platform.platform(),
                             'observed_distributions':dict(sorted((d.metadata['Name'],d.version) for d in importlib.metadata.distributions() if d.metadata['Name']))},
              'stages':[],'abc_run_relative_to_run':'abc'}
    write(run/'run_manifest.json',metadata)
    def stage(name,args,cwd=workspace):
        started=time.perf_counter();env=os.environ.copy();env['PYTHONUTF8']='1';env['PYTHONIOENCODING']='utf-8';env['MPLBACKEND']='Agg'
        p=subprocess.run([sys.executable]+[str(a) for a in args],cwd=cwd,env=env,capture_output=True,text=True,encoding='utf-8',errors='replace')
        (run/(name+'.log')).write_text(p.stdout+'\n'+p.stderr,encoding='utf-8')
        metadata['stages'].append({'stage':name,'returncode':p.returncode,'seconds_observed':time.perf_counter()-started})
        if p.returncode:metadata['status']='FAILED';write(run/'run_manifest.json',metadata);raise RuntimeError(name+' failed; inspect '+str(run/(name+'.log')))
        write(run/'run_manifest.json',metadata);print('PASS '+name,flush=True)
    abc_run=run/'abc';abc_ws=abc_run/'workspace';abc_ws.mkdir(parents=True)
    abc_names=[n for n in ANALYSIS_INPUTS if n not in ['scripts/d01_contact_policy.py','scripts/d02_report_assets.py','scripts/reproduce_abc.py']]
    copied={}
    for name in abc_names:
        target=abc_ws/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(workspace/name,target);copied[name]=fingerprint(target)['sha256']
    abc_info={'criterion':'complete reproduction under GitHub-declared environment','requires_identical_original_environment':False,
              'copied_input_sha256':copied,'cached_outputs_copied':False,'stages':[]}
    write(abc_run/'input_manifest.json',abc_info)
    for phase,script in [('A','01_data_quality.py'),('B','02_models.py'),('C','03_eval.py')]:
        stage(phase,[abc_ws/script],cwd=abc_ws)
        actual=metadata['stages'][-1]
        abc_info['stages'].append({'phase':phase,'returncode':actual['returncode'],'seconds_observed':actual['seconds_observed']})
        write(abc_run/'run_manifest.json',abc_info)
    c_metrics=abc_ws/'local_review/C01_candidate/outputs/metrics.json'
    if not c_metrics.is_file():raise RuntimeError('Missing paired C results')
    abc_info.update({'status':'ABC_REPRODUCED','metrics_relative_to_run':c_metrics.relative_to(abc_run).as_posix()})
    write(abc_run/'run_manifest.json',abc_info)
    stage('D01',[workspace/'scripts/d01_contact_policy.py','--abc-run',abc_run])
    d_metrics=workspace/'local_review/D01_candidate/outputs/metrics.json'
    d2=[workspace/'scripts/d02_report_assets.py','--metrics',d_metrics]
    if args.font_family:d2+=['--font-family',args.font_family]
    stage('D02',d2)
    metrics=read(d_metrics);differences=compare(contract['science_reference'],scientific(metrics))
    bindings=[]
    for claim in contract['claims']:
        value=resolve(metrics,claim['key']);errors=compare(claim['raw_value'],value,claim['key']);shown=display(value,claim['format'])
        bindings.append({**claim,'reproduced_value':value,'reproduced_display':shown,'matches':not errors and shown==claim['display']})
    diagram=read(workspace/'local_review/D02_candidate/outputs/D02_报告素材索引.json')['diagram']
    diagram_differences=compare(contract['diagram_reference'],diagram)
    write(run/'report_evidence_check.json',{'report_sha256':watched['report.docx']['sha256'],'report_authored_not_regenerated':True,
          'science_differences':differences,'diagram_differences':diagram_differences,'claims':bindings,
          'matched_claims':sum(c['matches'] for c in bindings),'claim_count':len(bindings),
          'numeric_tolerance':{'integer_and_text':'exact','float_absolute':1e-12},
          'excluded_from_science_comparison':['timestamps','runtime paths','source code fingerprints','observed package records','raw-byte CSV SHA only; LF content SHA retained'],
          'reference_environment_scope':'No guarantee of bit-identical historical upstream scores or identical font pixels on every compatible OS.'})
    if differences or diagram_differences or not all(c['matches'] for c in bindings):
        metadata['status']='REPORT_EVIDENCE_MISMATCH';write(run/'run_manifest.json',metadata)
        raise RuntimeError('Rebuilt results do not match the registered authored report; inspect report_evidence_check.json; no report was overwritten')
    if any(fingerprint(ROOT/name)!=record for name,record in watched.items()):raise RuntimeError('An input changed during reconstruction')
    output={}
    for label,folder in [('A_outputs',abc_ws/'outputs'),('A_figures',abc_ws/'figures'),
                         ('B',abc_ws/'local_review/B01_candidate/outputs'),('C_outputs',abc_ws/'local_review/C01_candidate/outputs'),
                         ('C_figures',abc_ws/'local_review/C01_candidate/figures'),('D01',workspace/'local_review/D01_candidate/outputs'),
                         ('D02',workspace/'local_review/D02_candidate/outputs')]:
        for path in sorted(folder.iterdir()):
            if path.is_file():output[label+'/'+path.name]={'path':path.relative_to(run).as_posix(),**fingerprint(path)}
    write(run/'artifact_index.json',output)
    a=lambda label:output[label]['path']
    index=['# 本次完整重建结果','',
           '本目录从原始CSV新建工作区运行ABC、D01和D02，未复制既有结果。根目录report.docx是手工定稿，未重新生成或覆盖。',
           '',f"报告数字核对：{len(bindings)} / {len(bindings)}项通过。",'',
           '| 内容 | 本次实际文件 |','|---|---|',
           # [D04_02-08 原阶段数字源链接保留]
           # '| 统一数字源（含补充回放） | [metrics.json]('+a('D01/metrics.json')+') |',
           # [D05-03 原行保留]
           # '| 正式统一数字源与文档登记 | [metrics.json](report/metrics.json) |',
           '| 正式统一数字源与文档登记 | [metrics.json](publication/outputs/metrics.json) |',
           # [D05-04 原行保留]
           # '| 正式T5与完整数字CSV | [T5](report/T5_数字核对表.md) / [CSV](report/T5_all_numbers.csv) |',
           '| 正式T5与完整数字CSV | [T5](publication/outputs/T5_数字核对表.md) / [CSV](publication/outputs/T5_all_numbers.csv) |',
           # [D05-05 原行保留]
           # '| ABC与D统一结果ZIP | [ABCD_verified.zip](results/ABCD_verified.zip) |',
           '| 三项D交付物 | [report.docx](publication/report.docx) / [F5](publication/outputs/F5_行动闭环.png) / [章节对应表](publication/outputs/章节_图表_数字对应表.md) |',
           '| Test模型比较 | [C_测试集模型比较表.md]('+a('C_outputs/C_测试集模型比较表.md')+') |',
           '| 固定规则及代价 | [T6_联系限制补充评价.md]('+a('D01/T6_联系限制补充评价.md')+') |',
           '| 建议行动流程 | [F5 PNG]('+a('D02/F5_行动闭环.png')+') / [SVG]('+a('D02/F5_行动闭环.svg')+') |',
           '| 完整产物位置及指纹 | [artifact_index.json](artifact_index.json) |',
           '| 报告107处数字和科学结果比对 | [report_evidence_check.json](report_evidence_check.json) |','',
           '阶段原始输出保留D01/D02当时的写作提示与默认路径；本次查看以本页实际文件和artifact_index为准。D02素材脚本不创建正式Word，不代表当前没有报告。',
           '内部兼容目录local_review是本次新生成的工作目录，不需要复制本机原local_review。',
           # [D04_02-09 原阶段状态保留]
           # '字体可能改变图像字节；科学值、规则和图内数字仍须核对。完整提交快照与T5/PPT页码在后续整合中完成。']
           # [D05-07 原行保留]
           # '字体可能改变图像字节；正式T5报告页码按已验收Word指纹登记，PPT页码待实际稿。原GitHub基线覆盖组合验收尚待后续。']
           '字体可能改变图像字节；正式T5报告页码按已验收Word指纹登记。所有公开产物直接浏览，publication/可对应仓库目录。']
    (run/'RUN_RESULTS.md').write_text('\n'.join(index)+'\n',encoding='utf-8')
    metadata.update({'status':'ABCD_REPRODUCED','matched_report_claims':len(bindings),'scientific_reference_matched':True,
                     'metrics_relative_to_run':d_metrics.relative_to(run).as_posix(),'artifact_index':'artifact_index.json','index':'RUN_RESULTS.md',
                     'report_and_original_inputs_unchanged':True})
    write(run/'run_manifest.json',metadata)
    (base/'latest_run.txt').write_text(run.relative_to(ROOT).as_posix(),encoding='utf-8')
    # [D04_02-10 新增：科学重建成功后才打包，report.docx始终不重生成]
    # [D05-06 原压缩结果输出保留]
    # package=load_packager().package_verified_run(ROOT,run,contract,compare,scientific)
    # print('[RESULTS_PACKAGED] '+str(run/package['snapshot']),flush=True)
    result=load_packager().publish_verified_run(ROOT,run,contract,compare,scientific)
    print('[RESULTS_DIRECTORY] '+str(run/result['directory']),flush=True)
    print('[ABCD_REPRODUCED] '+str(run/'RUN_RESULTS.md'),flush=True)
    print('[REPORT_EVIDENCE] '+str(len(bindings))+'/'+str(len(bindings))+' matched; authored report unchanged',flush=True)

if __name__=='__main__':main()
