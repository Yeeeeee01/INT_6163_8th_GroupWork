"""D01: fixed contact-gate policy, supplementary historical replay.

Run from the project root with the original GitHub-declared requirements:
  python scripts/d01_contact_policy.py
or after a fresh complete ABC reproduction:
  python scripts/d01_contact_policy.py --abc-run <ABC run directory>

The policy is fixed in POLICY before evaluation. No threshold grid is searched.
This does not implement a real customer-level dialling system or causal analysis.
"""
from __future__ import annotations

import argparse
import copy
import csv
from datetime import datetime, timezone
import hashlib
from io import BytesIO
import json
import math
from pathlib import Path, PurePosixPath
import shutil
import sys
import zipfile

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
import numpy as np
import pandas as pd
from sklearn.metrics import average_precision_score
import c01_support as c01

POLICY={
    'policy_id':'D01_previous3_last_failure_v1',
    'previous_minimum':3,
    'poutcome_equals':'failure',
    'trigger_expression':'previous >= 3 and poutcome == failure',
    'primary_scenario':'hold_no_refill',
    'secondary_scenario':'hold_with_refill',
    'budget_fraction':0.30,
    'ranking_rule':'risk descending, row_id ascending',
    'review_action':'hold from automatic call list and send to human review',
    'replay_review_assumption':'no human override or release in either scenario',
    'threshold_basis':'illustrative assignment assumption: at least three prior contacts; not a bank-confirmed cap or outcome-optimized threshold',
    'selection_method':'one rule fixed before this supplementary calculation; no threshold search or choice of better Test scenario',
    'test_status':'post-hoc descriptive replay; Test results were already examined in C01',
    'unit':'record-level gate using prior-contact count and last campaign result; no customer identifier',
    'semantic_limit':'previous counts prior contacts, not confirmed failed contacts; poutcome describes the last campaign only',
    'sensitive_fields_in_gate':[],
}

CORE_CODE=['01_data_quality.py','01_data_quality.ipynb','02_models.py','03_eval.py',
           '03_eval.ipynb','c01_support.py','scripts/reproduce_abc.py']


def canonical(value):
    return json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False).encode('utf-8')


POLICY_SHA256=hashlib.sha256(canonical(POLICY)).hexdigest()


def fingerprint_bytes(data):
    return {'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),
            'lf_normalized_sha256':hashlib.sha256(data.replace(b'\r\n',b'\n').replace(b'\r',b'\n')).hexdigest()}


def safe_relative(name):
    path=PurePosixPath(name)
    if path.is_absolute() or '..' in path.parts or '\\' in name or ':' in name:
        raise ValueError('输入清单包含不安全路径：'+name)
    return path


def require_match(data,record,exact=False):
    now=fingerprint_bytes(data)
    field='sha256' if exact else 'lf_normalized_sha256'
    if now[field]!=record[field]:raise ValueError('输入或结果指纹与同次清单不一致')


def load_bundle(snapshot=None,abc_run=None):
    """Read a paired baseline, validating manifests before exposing data to evaluation."""
    needed=['outputs/A_summary.json','outputs/split_v1.csv',
            'local_review/B01_candidate/outputs/scores.csv',
            'local_review/B01_candidate/outputs/T2_模型对比表.csv',
            'local_review/B01_candidate/outputs/B_run_manifest.json',
            'local_review/C01_candidate/outputs/metrics.json',
            'local_review/C01_candidate/outputs/C_run_manifest.json']
    # [D05-08 默认使用新运行的ABC；不再要求仓库结果ZIP]
    if snapshot is None and abc_run is None:
        marker=ROOT/'runs/latest_run.txt'
        if not marker.is_file():raise ValueError('请先运行python scripts/reproduce_all.py，或用--abc-run指定已完成的同次ABC目录')
        relative=Path(marker.read_text(encoding='utf-8').strip())
        abc_run=(ROOT/relative/'abc').resolve()
        if ROOT not in abc_run.parents:raise ValueError('ABC目录必须在本项目内')
    watched={}
    def disk(path):
        payload=path.read_bytes();watched[path]=fingerprint_bytes(payload);return payload
    if abc_run is not None:
        run=Path(abc_run).resolve()
        if ROOT not in run.parents:raise ValueError('abc-run必须位于本项目内')
        ws=run/'workspace';info=json.loads(disk(run/'run_manifest.json'))
        if info.get('status')!='ABC_REPRODUCED' or info.get('cached_outputs_copied') is not False:
            raise ValueError('abc-run不是成功的无缓存完整ABC运行')
        if [s['returncode'] for s in info['stages']]!=[0,0,0]:raise ValueError('ABC阶段未全部成功')
        copied=info['copied_input_sha256']
        if any(n.startswith(('outputs/','figures/')) for n in copied):raise ValueError('ABC起始目录使用了结果缓存')
        for name,digest in copied.items():
            safe_relative(name)
            if fingerprint_bytes(disk(ws/name))['sha256']!=digest:raise ValueError('ABC复制输入已变化：'+name)
        for name in CORE_CODE:
            if (ws/name).is_file():require_match(disk(ROOT/name),fingerprint_bytes(disk(ws/name)))
        def read(name):safe_relative(name);return disk(ws/name)
        raw_path=ws/'data/raw/bank-additional-full.csv'
        source={'mode':'fresh_abc_run','run_directory':run.relative_to(ROOT).as_posix(),
                'run_manifest':fingerprint_bytes(disk(run/'run_manifest.json')),'cached_results_used':False}
    else:
        # [D04_02-01 原默认快照路径保留]
        # snapshot=Path(snapshot or ROOT/'results/ABC_C01_verified.zip').resolve()
        # [D05-09 原行保留]
        # snapshot=Path(snapshot or ROOT/'results/ABCD_verified.zip').resolve()
        snapshot=Path(snapshot).resolve()
        if ROOT not in snapshot.parents:raise ValueError('快照必须位于本项目内')
        payload=disk(snapshot)
        with zipfile.ZipFile(BytesIO(payload)) as archive:
            names=archive.namelist()
            if len(names)!=len(set(names)):raise ValueError('ZIP重复成员')
            for name in names:safe_relative(name)
            if archive.testzip() is not None:raise ValueError('ZIP校验失败')
            index=json.loads(archive.read('snapshot.json'))
            if set(names)!=set(index['members'])|{'snapshot.json'}:raise ValueError('快照成员与索引不符')
            data={}
            for name,record in index['members'].items():
                content=archive.read(name)
                if len(content)!=record['bytes'] or hashlib.sha256(content).hexdigest()!=record['sha256']:
                    raise ValueError('快照成员内容与索引不一致：'+name)
                if name.startswith('workspace/'):data[name[len('workspace/'):]]=content
            for name,record in index['source_inputs'].items():
                safe_relative(name);require_match(disk(ROOT/name),record)
        def read(name):
            safe_relative(name)
            return data[name] if name in data else disk(ROOT/name)
        raw_path=ROOT/'data/raw/bank-additional-full.csv'
        source={'mode':'accepted_p01_snapshot','snapshot_path':snapshot.relative_to(ROOT).as_posix(),
                'snapshot_fingerprint':fingerprint_bytes(payload),'cached_results_used':'accepted fixed model scores; labels and gate replayed from raw CSV'}
    b=json.loads(read(needed[4]));c=json.loads(read(needed[6]))
    if b['protocol']['selection_fold']!='validation' or b['protocol']['test_labels_used_by_B'] or b['protocol']['seed']!=42:
        raise ValueError('B训练选参协议不符合原方案')
    for manifest in [b,c]:
        for name,record in manifest['input_fingerprints'].items():
            safe_relative(record['path']);require_match(read(record['path']),record)
        for name,record in manifest['output_fingerprints'].items():
            safe_relative(record['path']);require_match(read(record['path']),record,exact=True)
    metrics=json.loads(read(needed[5]));a_summary=json.loads(read(needed[0]))
    if metrics['data']!=a_summary['data']:raise ValueError('A汇总与C指标不是同批')
    source['baseline_metrics_fingerprint']=fingerprint_bytes(read(needed[5]))
    source['raw_fingerprint']=fingerprint_bytes(disk(raw_path))
    source['b_manifest_fingerprint']=fingerprint_bytes(read(needed[4]))
    source['c_manifest_fingerprint']=fingerprint_bytes(read(needed[6]))
    source['scores_fingerprint']=fingerprint_bytes(read(needed[2]))
    return {'raw_path':raw_path,'metrics':metrics,'split_bytes':read(needed[1]),
            'scores_bytes':read(needed[2]),'validation_bytes':read(needed[3]),'source':source,'watched':watched}


def prepare_frames(bundle):
    """Load only rule fields and labels; ranking scores are the fixed B output."""
    raw=pd.read_csv(bundle['raw_path'],sep=';',usecols=['previous','poutcome','y'])
    raw.insert(0,'row_id',range(len(raw)))
    if len(raw)!=41188 or raw.isna().any().any():raise ValueError('原数据行数或必需字段无效')
    if not set(raw.y).issubset({'yes','no'}):raise ValueError('标签无效')
    if not np.isfinite(raw.previous).all() or (raw.previous<0).any() or (raw.previous%1!=0).any():
        raise ValueError('previous必须是非负整数')
    split=pd.read_csv(BytesIO(bundle['split_bytes']))
    expected=['train']*24712+['validation']*8238+['test']*8238
    if split.columns.tolist()!=['row_id','fold'] or split.row_id.tolist()!=list(range(41188)) or split.fold.tolist()!=expected:
        raise ValueError('不是原冻结60/20/20切分')
    scores=pd.read_csv(BytesIO(bundle['scores_bytes']))
    if scores.columns.tolist()!=['row_id','fold','model','risk'] or len(scores)!=115332:
        raise ValueError('B分数结构无效')
    if scores.duplicated(['row_id','fold','model']).any() or not np.isfinite(scores.risk).all() or not scores.risk.between(0,1).all():
        raise ValueError('B分数键或概率无效')
    if set(scores.model)!=set(bundle['metrics']['models']) or set(scores.fold)!={'validation','test'}:
        raise ValueError('B模型或分段不完整')
    frames={}
    for fold,first,last in [('validation',24712,32950),('test',32950,41188)]:
        for model in bundle['metrics']['models']:
            ids=scores.loc[scores.fold.eq(fold)&scores.model.eq(model),'row_id'].tolist()
            if ids!=list(range(first,last)):raise ValueError('分数行号不完整或错位')
        main=scores.loc[scores.fold.eq(fold)&scores.model.eq('logistic'),['row_id','risk']]
        frame=raw.iloc[first:last].merge(main,on='row_id',validate='one_to_one')
        if len(frame)!=8238:raise ValueError('行对齐失败')
        frame['is_positive']=frame.y.eq('yes')
        frame['fold']=fold
        frames[fold]=frame
    return frames


def outcome(frame,selected):
    """Return actual contacts/confusion counts with explicit zero denominators."""
    selected_set=set(selected)
    chosen=frame.row_id.isin(selected_set);positive=frame.is_positive
    tp=int((chosen&positive).sum());fp=int((chosen&~positive).sum())
    fn=int((~chosen&positive).sum());tn=int((~chosen&~positive).sum())
    contacts=tp+fp;positives=tp+fn
    return {'contacts':contacts,'hits':tp,'invalid_calls':fp,'missed_subscriptions':fn,
            'precision':tp/contacts if contacts else None,'recall':tp/positives if positives else None,
            'confusion':{'tp':tp,'fp':fp,'fn':fn,'tn':tn}}


def evaluate_fold(frame):
    """Apply the one fixed gate to a fixed ranking, with and without replacement."""
    ranked=frame.sort_values(['risk','row_id'],ascending=[False,True],kind='mergesort').copy()
    k=math.ceil(len(ranked)*POLICY['budget_fraction'])
    trigger=ranked.previous.ge(POLICY['previous_minimum']) & ranked.poutcome.eq(POLICY['poutcome_equals'])
    baseline_ids=ranked.head(k).row_id.tolist()
    held_ids=ranked.loc[trigger,'row_id'].tolist();held=set(held_ids);base_set=set(baseline_ids)
    removed=base_set & held
    no_refill=[row for row in baseline_ids if row not in held]
    with_refill=ranked.loc[~trigger].head(k).row_id.tolist()
    additions=set(with_refill)-base_set
    truth=ranked.set_index('row_id').is_positive
    gross_lost=int(truth.loc[sorted(removed)].sum()) if removed else 0
    added_hits=int(truth.loc[sorted(additions)].sum()) if additions else 0
    baseline=outcome(ranked,baseline_ids)
    baseline.update({'calls_reduced_vs_baseline':0,'gross_removed_original_hits':0,
                     'replacement_hits':0,'net_extra_missed_vs_baseline':0})
    def scenario(ids,refill):
        current=outcome(ranked,ids)
        return {**current,'calls_reduced_vs_baseline':baseline['contacts']-current['contacts'],
                'gross_removed_original_hits':gross_lost,'removed_original_contacts':len(removed),
                'removed_original_invalid_calls':len(removed)-gross_lost,
                'replacement_contacts':len(additions) if refill else 0,
                'replacement_hits':added_hits if refill else 0,
                'net_hits_change_vs_baseline':current['hits']-baseline['hits'],
                'net_extra_missed_vs_baseline':current['missed_subscriptions']-baseline['missed_subscriptions'],
                'net_invalid_calls_avoided':baseline['invalid_calls']-current['invalid_calls'],
                'unused_budget':k-current['contacts']}
    ledger=ranked.sort_values('row_id').copy()
    ledger['rule_trigger']=ledger.row_id.isin(held)
    ledger['baseline_selected']=ledger.row_id.isin(base_set)
    ledger['hold_no_refill_selected']=ledger.row_id.isin(set(no_refill))
    ledger['hold_with_refill_selected']=ledger.row_id.isin(set(with_refill))
    ledger['removed_from_baseline']=ledger.row_id.isin(removed)
    ledger['added_by_refill']=ledger.row_id.isin(additions)
    result={
        'rows':len(ranked),'positive_rows':int(ranked.is_positive.sum()),'budget_k':k,
        'triggered_records':len(held),'triggered_positive_total':int(truth.loc[held_ids].sum()) if held_ids else 0,
        'triggered_original_selected':len(removed),'triggered_original_selected_positive':gross_lost,
        'triggered_already_unselected_positive':int(truth.loc[held_ids].sum())-gross_lost if held_ids else 0,
        'baseline':baseline,'hold_no_refill':scenario(no_refill,False),'hold_with_refill':scenario(with_refill,True),
        'removed_original_row_ids':sorted(removed),'replacement_row_ids':sorted(additions)}
    return result,ledger


def validate_baseline(bundle,frames,results):
    """Independently bind the fixed logistic list to C01 Test and B Validation."""
    base=bundle['metrics']['models']['logistic'];test=results['test']['baseline']
    ap=float(average_precision_score(frames['test'].is_positive.astype(int),frames['test'].risk))
    if abs(ap-base['pr_auc'])>1e-14 or test['hits']!=base['hits_at_k'] or test['confusion']!=base['confusion_at_budget']:
        raise ValueError('D01原名单与C01主模型评价不一致')
    table=pd.read_csv(BytesIO(bundle['validation_bytes']))
    vm=table.loc[table.model.eq('logistic')].iloc[0]
    apv=float(average_precision_score(frames['validation'].is_positive.astype(int),frames['validation'].risk))
    if abs(apv-float(vm.validation_pr_auc))>5.1e-7 or results['validation']['baseline']['hits']!=int(vm.hits_at_30pct):
        raise ValueError('D01原Validation名单与B结果不一致')


def archive_existing(out):
    folder=out/'outputs'
    if folder.exists():
        files=[p for p in folder.iterdir() if p.is_file()]
        if files:
            backup=out/'D01_generated_before'/datetime.now().strftime('%Y%m%d_%H%M%S_%f')/'outputs'
            backup.mkdir(parents=True)
            for path in files:shutil.copy2(path,backup/path.name)
            (backup/'backup_manifest.json').write_text(json.dumps({p.name:fingerprint_bytes(p.read_bytes()) for p in files},ensure_ascii=False,indent=2),encoding='utf-8')
    folder.mkdir(parents=True,exist_ok=True)
    return folder


def write_markdown(path,text):
    begin='<!-- D01_ORIGINAL_MARKDOWN_BEGIN\n';end='\nD01_ORIGINAL_MARKDOWN_END -->\n'
    if path.exists():
        old=path.read_text(encoding='utf-8')
        if old.startswith(begin) and end in old:prefix=old.split(end,1)[0]+end
        elif '-->' not in old:prefix=begin+old+end
        else:raise ValueError('不能嵌套Markdown旧稿注释')
    else:prefix=begin+'D01新增文件，无被替换旧稿。'+end
    path.write_text(prefix+'\n'+text,encoding='utf-8')


def render_outputs(master,ledger,out):
    """Render the replay summary and both numeric indexes from the persisted JSON."""
    policy=master['contact_policy'];rows=policy['folds']
    lines=['# T6 联系限制补充评价','',
           '固定规则：previous≥3且poutcome=failure的记录暂缓自动外呼，交人工复核。3次是作业预设示例，不是银行确认或寻优得到的阈值。',
           '回放假定人工不放行。主情景不递补；递补情景仅作固定对照，不按Test结果改选方案。Test此前已查看，本表属于事后描述性回放。','',
           '| 分段 | 情景 | 实际联系 | 命中 | 无效联系 | 总漏报 | 移除原名单订阅 | 递补命中 | 净额外漏报 |',
           '|---|---|---:|---:|---:|---:|---:|---:|---:|']
    for fold in ['validation','test']:
        for scenario,label in [('baseline','原主模型名单'),('hold_no_refill','暂缓且不递补（主情景）'),('hold_with_refill','暂缓并递补（对照）')]:
            r=rows[fold][scenario]
            lines.append(f"| {fold} | {label} | {r['contacts']} | {r['hits']} | {r['invalid_calls']} | {r['missed_subscriptions']} | {r.get('gross_removed_original_hits',0)} | {r.get('replacement_hits',0)} | {r.get('net_extra_missed_vs_baseline',0):+d} |")
    test=rows['test'];primary=test['hold_no_refill'];secondary=test['hold_with_refill']
    lines += ['',f"Test全段触发{test['triggered_records']}条，其中真实订阅{test['triggered_positive_total']}；原Top-K中触发{test['triggered_original_selected']}条，其中真实订阅{test['triggered_original_selected_positive']}。",
              f"主情景实际联系{primary['contacts']}条、命中{primary['hits']}，较原名单减少{primary['calls_reduced_vs_baseline']}次联系，少{primary['net_invalid_calls_avoided']}次无效联系，同时额外漏掉{primary['net_extra_missed_vs_baseline']}个历史真实订阅，总漏报变为{primary['missed_subscriptions']}。",
              f"递补对照增加{secondary['replacement_contacts']}条合规候选、命中{secondary['replacement_hits']}；相对原名单净命中变化{secondary['net_hits_change_vs_baseline']:+d}。递补不消除被移除个体的机会损失。",
              '', '## 数字引用口径','',
              '- 触发群体全部订阅、原名单被移除的订阅、递补后的净变化是三个不同量。',
              '- 原名单漏报1340属于C01；D01额外漏报引用contact_policy.folds.test.hold_no_refill.net_extra_missed_vs_baseline，不能混写。',
              '- 所有C01原键和值原样保留；原guardrails中的联系策略文字描述C01当时状态，D01新增结果仅在contact_policy节。',
              '- previous不是连续失败次数，poutcome仅是上次活动结果；无客户ID，不能称已实现客户级终身限拨或真实上线。',
              '- 敏感属性不参与本闸门；原Logistic使用哪些属性仍按原配置披露，不因此宣称模型公平或已移除敏感属性。',
              '- 历史标签是在既有外呼条件下观察的；回放计数不证明暂停外呼造成未订阅，也不估计人工放行、客户意愿或因果收益。',
              '', '## 重跑入口','',
              '```powershell','python scripts/d01_contact_policy.py',
              '# 完整从原始CSV重新生成ABC后评价D01：','python scripts/reproduce_abc.py',
              # [D01-Q01 原行保留] '$d01AbcRun = Get-Content .\local_review\ABC_reproduction\latest_run.txt',
              r'$d01AbcRun = Get-Content .\local_review\ABC_reproduction\latest_run.txt',
              'python scripts/d01_contact_policy.py --abc-run $d01AbcRun','```','',
              '默认输出local_review/D01_candidate；结果JSON只读、旧输出重跑前备份。本表不是正式报告或F5。']
    write_markdown(out/'T6_联系限制补充评价.md','\n'.join(lines)+'\n')
    ledger.to_csv(out/'D01_逐记录审计.csv',index=False,float_format='%.10g')
    with (out/'T5_all_numbers.csv').open('w',encoding='utf-8-sig',newline='') as f:
        writer=csv.writer(f);writer.writerow(['metrics.json键名','数值','类型','报告/PPT页码'])
        for key,value in c01.numeric_leaves(master):writer.writerow([key,repr(value),type(value).__name__,''])
    table=['# T5 D01写作数字核对表','', 'C01常用表保留在验收快照；本表覆盖业务三量与D01核心数字。完整数值索引见T5_all_numbers.csv，页码由D/E定稿时回填。','',
           '| 数字 | metrics.json键名 | 报告/PPT页码 |','|---:|---|---|']
    values=dict(c01.numeric_leaves(master))
    keys=['business.extra_hits_vs_rule','business.invalid_calls_avoided_vs_rule','business.missed_subscriptions_at_k']
    keys += [k for k in values if k.startswith('contact_policy.folds.') and '.confusion.' not in k and '_row_ids.' not in k]
    for key in keys:table.append(f"| {values[key]} | `{key}` | 待D/E回填 |")
    write_markdown(out/'T5_数字核对表.md','\n'.join(table)+'\n')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    group=parser.add_mutually_exclusive_group()
    group.add_argument('--abc-snapshot',type=Path)
    group.add_argument('--abc-run',type=Path)
    parser.add_argument('--output-root',type=Path,default=ROOT/'local_review/D01_candidate')
    args=parser.parse_args()
    out=args.output_root.resolve()
    allowed=[ROOT/'local_review/D01_candidate',ROOT/'local_review/repairs/D01']
    if not any(out==parent or parent in out.parents for parent in allowed):
        raise ValueError('D01输出限于D01候选或验收目录，不能覆盖ABC/P01')
    environment=c01.environment(ROOT)
    script_fingerprint=fingerprint_bytes(Path(__file__).read_bytes())
    # POLICY is a literal constant, identified before any labels are loaded.
    policy_hash=hashlib.sha256(canonical(POLICY)).hexdigest()
    if policy_hash!=POLICY_SHA256:raise ValueError('规则常量在运行时被修改')
    bundle=load_bundle(args.abc_snapshot,args.abc_run)
    frames=prepare_frames(bundle)
    results={};ledgers=[]
    for fold in ['validation','test']:
        result,ledger=evaluate_fold(frames[fold]);results[fold]=result;ledgers.append(ledger)
    validate_baseline(bundle,frames,results)
    master=copy.deepcopy(bundle['metrics'])
    if 'contact_policy' in master:raise ValueError('输入不是尚未加入D01的C01基线')
    master['contact_policy']={
        'schema':'D01-1.0','generated_by':'scripts/d01_contact_policy.py',
        'computed_at_utc':datetime.now(timezone.utc).isoformat(timespec='seconds'),
        'policy':copy.deepcopy(POLICY),'policy_sha256':policy_hash,
        'evaluation_type':'post-hoc descriptive supplementary replay; not new unseen Test validation',
        'folds':results,
        'definitions':{'triggered_positive_total':'all positive labels in the gated group, including people outside the original list',
                       'gross_removed_original_hits':'positive labels removed from the original logistic Top-K',
                       'replacement_hits':'positive labels among newly inserted eligible records',
                       'net_extra_missed_vs_baseline':'policy FN minus baseline FN = gross removed original hits minus replacement hits',
                       'negative_net_extra_missed':'net hits improved under the fixed observed-label replay, not a causal benefit'},
        'provenance':{'baseline':bundle['source'],'d01_source_fingerprint':script_fingerprint,'environment':environment},
        'limitations':['No customer identifier or per-contact failed-call history.',
                       'Threshold 3 is an illustrative assignment assumption, not empirically optimal or approved by a bank.',
                       'Test already examined; this is supplementary post-hoc replay.',
                       'No human override, causal effect, deployment or future conversion claim.',
                       'Original model may use sensitive attributes; the gate itself uses only previous and poutcome.']}
    if any(master[k]!=value for k,value in bundle['metrics'].items()):raise RuntimeError('原C01指标被意外改动')
    folder=archive_existing(out)
    (folder/'D01_policy_spec.json').write_text(json.dumps({'policy':POLICY,'policy_sha256':policy_hash},ensure_ascii=False,indent=2),encoding='utf-8')
    c01.write_metrics(folder/'metrics.json',master)
    persisted=json.loads((folder/'metrics.json').read_text(encoding='utf-8'))
    render_outputs(persisted,pd.concat(ledgers,ignore_index=True),folder)
    source_after=fingerprint_bytes(Path(__file__).read_bytes())
    if source_after!=script_fingerprint:raise RuntimeError('计算期间D01源码变化')
    if fingerprint_bytes(bundle['raw_path'].read_bytes())!=bundle['source']['raw_fingerprint']:
        raise RuntimeError('计算期间原始数据变化')
    if any(fingerprint_bytes(path.read_bytes())!=record for path,record in bundle['watched'].items()):
        raise RuntimeError('计算期间基线输入发生变化')
    outputs={p.name:fingerprint_bytes(p.read_bytes()) for p in sorted(folder.iterdir()) if p.is_file() and p.name!='D01_run_manifest.json'}
    manifest={'stage':'D01','status':'candidate_pending_user_validation','policy_sha256':policy_hash,
              'input_mode':bundle['source']['mode'],'source':bundle['source'],'source_code_fingerprint':script_fingerprint,
              'output_fingerprints':outputs,'preserved_all_c01_keys':True,'threshold_search_performed':False,
              'root_baseline_or_publication_bundle_modified':False,'real_customer_calls_performed':False}
    (folder/'D01_run_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
    t=results['test'];p=t['hold_no_refill'];q=t['hold_with_refill']
    print(f"[规则] {POLICY['trigger_expression']}；主情景不递补；事后历史回放")
    print(f"[Test] 触发={t['triggered_records']}；原名单受限={t['triggered_original_selected']}；其中订阅={t['triggered_original_selected_positive']}")
    print(f"[主情景] 联系={p['contacts']}；命中={p['hits']}；额外漏报={p['net_extra_missed_vs_baseline']}；总漏报={p['missed_subscriptions']}")
    print(f"[递补对照] 联系={q['contacts']}；命中={q['hits']}；净命中变化={q['net_hits_change_vs_baseline']:+d}")
    print(f'[D01_PASS] {folder / "metrics.json"}')


if __name__=='__main__':main()
