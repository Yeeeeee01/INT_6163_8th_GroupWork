"""Package one verified raw-data ABCD run and its report-page numeric index.

Scientific stage artifacts are kept byte-for-byte. The report/ directory is the
publication index; early stage T5 files remain under workspace/ for provenance.
"""
from pathlib import Path, PurePosixPath
from io import StringIO
import copy, csv, hashlib, json, math, re, zipfile

def encode(value):return (json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False)+'\n').encode('utf-8')
def load(path):return json.loads(Path(path).read_text(encoding='utf-8'))
def fp_bytes(data):
    return {'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),'lf_normalized_sha256':hashlib.sha256(data.replace(b'\r\n',b'\n').replace(b'\r',b'\n')).hexdigest()}
def fp(path):return fp_bytes(Path(path).read_bytes())
def safe(name):
    p=PurePosixPath(name)
    if p.is_absolute() or '..' in p.parts or '\\' in name or ':' in name:raise ValueError('Unsafe archive path: '+name)
    return p
def leaves(value,prefix=''):
    if isinstance(value,bool):return
    if isinstance(value,(int,float)):
        if not math.isfinite(value):raise ValueError('Non-finite numeric registry value')
        yield prefix,value
    elif isinstance(value,dict):
        for key,item in value.items():yield from leaves(item,prefix+'.'+key if prefix else key)
    elif isinstance(value,list):
        for i,item in enumerate(value):yield from leaves(item,prefix+'.'+str(i))
def resolve(value,key):
    for part in key.split('.'):value=value[int(part)] if isinstance(value,list) else value[part]
    return value

def figure_rules(contract):
    pages=contract['report']['figure_pages']
    # These are data-source references; they do not claim every plotted point
    # was printed as a separate sentence or numeric annotation in the report.
    return [
        ('F1',['data.n_columns','data.main_feature_count','report_evidence.derived.pre_call_field_count'],pages['F1']),
        ('F2',['data.n_rows','data.n_columns','data.n_train','data.n_validation','data.n_test','report_evidence.frozen_split_plan.'],pages['F2']),
        ('F1b',['data.positive_rate','data.positive_rate_decile_by_row_order.'],pages['F1b']),
        ('F3',['pr_curves.']+['models.'+m+'.pr_auc' for m in ['logistic','poutcome_success','no_skill','logistic_duration_ablation']],pages['F3']),
        ('F4',['sensitivity.records.'],pages['F4']),
        ('F5',[x['key'] for x in contract['diagram_reference']['numeric_annotations']],pages['F5']),
    ]

def numeric_documents(metrics,contract):
    claims=contract['claims'];rules=figure_rules(contract);direct={}
    for claim in claims:
        if not claim.get('report_pages') or claim.get('ppt_pages') is not None:raise ValueError('Report pages absent or unverified PPT pages supplied')
        direct.setdefault(claim['key'],set()).update(claim['report_pages'])
    stream=StringIO(newline='');writer=csv.writer(stream,lineterminator='\n')
    writer.writerow(['metrics.json键名','原值','类型','报告页码','引用类型','图数据来源','PPT页码','数字源文件'])
    count=0
    for key,value in leaves(metrics):
        figures=[(name,page) for name,prefixes,page in rules if any(key.startswith(p) if p.endswith('.') else key==p for p in prefixes)]
        pages=sorted(direct.get(key,set())|{p for _,p in figures})
        kind='正文或表格' if key in direct else ('图数据源，非逐项文字引用' if figures else '未在报告逐项引用')
        if not figures and key not in direct and (key.startswith(('reproducibility.','contact_policy.provenance.','report_evidence.')) or key in ['data.raw_file_bytes']):kind='来源或版式元数据，非实验成效'
        writer.writerow([key,repr(value),type(value).__name__,','.join(map(str,pages)) or '未引用',kind,','.join(name for name,_ in figures),'待E实际PPT核对','metrics.json'])
        count+=1
    lines=['# T5 数字与报告页码核对表','',
           '正式数字源为同目录[metrics.json](metrics.json)。本表逐项登记报告107处科学数字；完整JSON数值叶子见[T5_all_numbers.csv](T5_all_numbers.csv)。',
           '页码来自已实际渲染核对的8页report.docx，并以报告SHA256绑定；分析脚本不假装重新计算Word页码。PPT尚未登记，所有PPT页码保持待核对。',
           '阶段原始表、指标及运行清单在workspace/保留原字节；正式报告引用优先使用本目录，不把早期空白页码阶段表当作正式T5。','',
           '报告SHA256：`'+contract['report']['sha256']+'`。','',
           '| 序号 | 报告显示值 | metrics.json键 | 报告页码 | PPT页码 |','|---:|---|---|---|---|']
    for i,claim in enumerate(claims,1):
        value=resolve(metrics,claim['key']);expected=claim['raw_value']
        matches=math.isclose(value,expected,rel_tol=0,abs_tol=1e-12) if isinstance(expected,float) else value==expected
        if not matches:raise ValueError('T5 numeric claim differs: '+claim['key'])
        lines.append('| '+str(i)+' | '+claim['display']+' | `'+claim['key']+'` | '+','.join(map(str,claim['report_pages']))+' | 待E实际PPT核对 |')
    lines += ['', '## 图中数据的JSON来源','',
              '下表登记图数据源与报告页码；曲线数据、刻度和正文单独数字不是同一概念。完整CSV将“正文或表格”“图数据源”及“元数据”分开标示，不为未引用值编报告页码。','',
              '| 图资源 | 报告页码 | 原始键或键前缀 |','|---|---:|---|']
    for name,prefixes,page in rules:lines.append('| '+name+' | '+str(page)+' | '+'；'.join('`'+p+'`' for p in prefixes)+' |')
    lines += ['', 'F1通话前字段19=21列减duration及y；F2的60/20/20是原固定切分计划，整数切分仍按原A代码执行。这些原图注释的可追溯登记位于report_evidence，不新增模型或实验。',
              'C原名单漏报1340、闸门全段触发订阅42和主情景额外漏报3严格分开；不递补为主情景，递补+8仅为固定对照。',
              '原guardrails对联系策略的描述属于C阶段；contact_policy是D01补充结果，report_evidence只登记文档与原图来源。',
              '', '## 运行清单与数值边界','',
              '来源清单和观察环境为运行元数据，不作为跨环境逐位科学一致的承诺。CSV字节大小会随LF/CRLF改变，规范化内容指纹仍须一致。']
    return {'report/T5_数字核对表.md':('\n'.join(lines)+'\n').encode('utf-8'),
            'report/T5_all_numbers.csv':stream.getvalue().encode('utf-8-sig'),
            'report/T5_report_claims.json':encode({'report_sha256':contract['report']['sha256'],'page_count':8,'claims':claims,'PPT_status':'not registered'})},count

def package_verified_run(root,run,contract,compare,scientific):
    root=Path(root).resolve();run=Path(run).resolve()
    if (root/'runs') not in run.parents:raise ValueError('Package only a verified run under this project runs/')
    info=load(run/'run_manifest.json');check=load(run/'report_evidence_check.json');catalog=load(run/'artifact_index.json')
    if info['status']!='ABCD_REPRODUCED' or info['cached_outputs_copied'] is not False or [s['stage'] for s in info['stages']]!=['A','B','C','D01','D02'] or any(s['returncode'] for s in info['stages']):raise ValueError('Not a successful fresh full run')
    if check['matched_claims']!=107 or check['science_differences'] or check['diagram_differences'] or not all(c['matches'] for c in check['claims']):raise ValueError('Run report evidence did not pass')
    for name,record in info['input_fingerprints'].items():
        safe(name)
        if fp(root/name)!=record:raise ValueError('Packaging input changed since calculation: '+name)
    if fp(root/'report.docx')['sha256']!=contract['report']['sha256']:raise ValueError('Report changed before packaging')
    metrics=load(run/info['metrics_relative_to_run'])
    if compare(contract['science_reference'],scientific(metrics)):raise ValueError('Scientific results differ before packaging')
    locations={'A_outputs':'workspace/outputs','A_figures':'workspace/figures','B':'workspace/local_review/B01_candidate/outputs',
               'C_outputs':'workspace/local_review/C01_candidate/outputs','C_figures':'workspace/local_review/C01_candidate/figures',
               'D01':'workspace/local_review/D01_candidate/outputs','D02':'workspace/local_review/D02_candidate/outputs'}
    members={};relocations={};public_catalog={}
    for label,record in catalog.items():
        group,name=label.split('/',1);safe(record['path']);path=(run/record['path']).resolve()
        if run not in path.parents or fp(path)!={k:record[k] for k in ['bytes','sha256','lf_normalized_sha256']}:raise ValueError('Output changed before packaging: '+label)
        member=locations[group]+'/'+name;safe(member);members[member]=path.read_bytes();relocations[record['path']]=member
        public_catalog[label]={'member':member,**fp_bytes(members[member])}
    for relative,member in [
        ('abc/input_manifest.json','run/abc_input_manifest.json'),('abc/run_manifest.json','run/abc_run_manifest.json'),
        ('run_manifest.json','run/run_manifest.json'),('report_evidence_check.json','run/report_evidence_check.json'),
        ('abc/workspace/data/README_data.md','workspace/data/README_data.md'),
        ('local_review/D02_candidate/inputs/metrics.D01.accepted.json','workspace/local_review/D02_candidate/inputs/metrics.D01.accepted.json')]:
        members[member]=(run/relative).read_bytes();relocations[relative]=member
    original=copy.deepcopy(metrics)
    metrics['report_evidence']={'report_sha256':contract['report']['sha256'],'report_page_count':8,
          'derived':{'pre_call_field_count':metrics['data']['n_columns']-2},
          'frozen_split_plan':{'train':0.60,'validation':0.20,'test':0.20},
          'meaning':'Documentation and existing F1/F2 annotations only; all original C/D01 keys and values preserved',
          'PPT_status':'Actual slides not registered; no slide page numbers supplied'}
    if metrics['report_evidence']['derived']['pre_call_field_count']!=19 or any(metrics[k]!=v for k,v in original.items()):raise ValueError('Original metric keys changed')
    official,count=numeric_documents(metrics,contract);official['report/metrics.json']=encode(metrics)
    members.update(official)
    members['report/D01_policy_registration.json']=encode(contract['policy_registration'])
    members['run/artifact_catalog.json']=encode(public_catalog)
    notes=['# ABC与D同次结果包','',
        '正式引用入口：[report/metrics.json](report/metrics.json)、[T5数字及报告页码](report/T5_数字核对表.md)、[完整数值CSV](report/T5_all_numbers.csv)。',
        '107处正文/表格数字及原图数据源已登记报告页码；PPT页码待E实际稿核对。report.docx在仓库根目录，不重复装入ZIP。',
        'workspace/保存原始阶段产物与B/C/D01/D02清单，未重写它们；早期阶段T5仍可能保留当时未填页码状态，不能替代本包report/的正式T5。',
        'run/保留真实无缓存运行及比对清单。原始CSV、配置和源码在仓库内，不重复打包。snapshot.json记录成员指纹、源码输入及原运行路径到成员的映射。',
        '正式metrics在原D01全部键值之上仅添加report_evidence文档登记节；原D01 JSON在workspace/local_review/D01_candidate/outputs/保持原字节。',
        '本包含历史回放，不代表真实人工放行、上线、外呼或因果成效。',
        '原阶段清单使用各自工作区相对路径；从snapshot.json和run/artifact_catalog.json查成员，不把解压目录当作原工作区，也不改清单指纹迁就路径。',
        'ZIP内旧阶段Markdown的默认命令/相对链接属于原阶段记录；查看本包以本页和正式report/索引为准。',
        'metrics的只读属性不一定被解压工具保留；内容以成员SHA256为准。',
        '', '| 内容 | 位置 |','|---|---|',
        '| 原数据说明与许可 | [数据说明](workspace/data/README_data.md) |',
        '| Test模型比较 | [模型表](workspace/local_review/C01_candidate/outputs/C_测试集模型比较表.md) |',
        '| 补充规则及损失 | [T6](workspace/local_review/D01_candidate/outputs/T6_联系限制补充评价.md) |',
        '| 建议行动图 | [F5 PNG](workspace/local_review/D02_candidate/outputs/F5_行动闭环.png) / [SVG](workspace/local_review/D02_candidate/outputs/F5_行动闭环.svg) |']
    members['README_RESULTS.md']=('\n'.join(notes)+'\n').encode('utf-8')
    source_names=list(contract['source_inputs'])
    snapshot={'schema':'D04-02-1.0','origin':'one fresh A/B/C/D01/D02 run verified against registered authored report evidence',
        'origin_run_id':run.name,'cached_outputs_used':False,'source_inputs':{n:fp(root/n) for n in source_names},
        'report_sha256':contract['report']['sha256'],'report_evidence_contract_sha256':fp(root/'docs/REPORT_EVIDENCE.json')['sha256'],
        'primary_metrics':'report/metrics.json','primary_number_audit':'report/T5_数字核对表.md','numeric_leaf_count':count,'report_claim_count':107,
        'PPT_pages':'not registered','report_page_basis':contract['report']['page_registration_basis'],
        'relocation_map':relocations,'members':{n:fp_bytes(b) for n,b in sorted(members.items())},
        'metadata_scope':'Original timestamps, environment and path metadata preserved; no claim of recovering all historical upstream scores.'}
    members['snapshot.json']=encode(snapshot)
    for name,data in members.items():
        safe(name)
        if name.endswith(('.json','.md','.csv','.svg')):
            text=data.decode('utf-8-sig')
            if re.search(r'(?<![A-Za-z0-9])[A-Za-z]:[\\/]|/Users/|/home/',text):raise ValueError('Machine-specific absolute path in public snapshot: '+name)
    # Validate before persisting any publication output; existing differing files
    # are refused, not silently overwritten.
    for name,data in official.items():
        path=run/name
        if path.exists() and path.read_bytes()!=data:raise ValueError('Existing official result differs: '+name)
    output=run/'results/ABCD_verified.zip';output.parent.mkdir(exist_ok=True)
    building=output.with_name(output.name+'.building')
    with zipfile.ZipFile(building,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for name,data in sorted(members.items()):
            item=zipfile.ZipInfo(name,date_time=(1980,1,1,0,0,0));item.compress_type=zipfile.ZIP_DEFLATED;item.create_system=3
            item.external_attr=(0o100444 if name.endswith('/metrics.json') else 0o100644)<<16
            z.writestr(item,data,compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
    if output.exists():
        if output.read_bytes()!=building.read_bytes():
            building.unlink();raise ValueError('Existing snapshot differs; use a new verified run instead of overwriting')
        building.unlink()
    else:building.replace(output)
    for name,data in official.items():
        path=run/name;path.parent.mkdir(parents=True,exist_ok=True)
        if not path.exists():path.write_bytes(data)
        if name.endswith('/metrics.json'):path.chmod(0o444)
    receipt={'schema':'D04-02-bundle','snapshot':'results/ABCD_verified.zip',**fp(output),
             'members':len(members),'numeric_leaf_count':count,'report_claim_count':107,
             'primary_metrics':'report/metrics.json','report_sha256':contract['report']['sha256'],'PPT_pages':'not registered',
             'source_run_manifest_sha256':fp(run/'run_manifest.json')['sha256'],'source_artifacts_unchanged':True}
    (run/'bundle_manifest.json').write_bytes(encode(receipt))
    return receipt
