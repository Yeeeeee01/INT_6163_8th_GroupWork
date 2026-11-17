"""D02: render F5 and a chapter/evidence index from one frozen D01 metrics file.

python scripts/d02_report_assets.py
This creates report assets, not the final report, and changes no ABC/D01 results.
"""
from __future__ import annotations

import argparse
import copy
from datetime import datetime,timezone
import hashlib
import json
import math
from pathlib import Path
import shutil
import sys
import zipfile

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.ft2font import FT2Font
from matplotlib.patches import FancyArrowPatch,FancyBboxPatch,Polygon
import c01_support as c01

CHAPTERS=[
    # [D02-E01 原行保留] (1,'问题与目标',250,'通话前记录、目标使用者、优先名单与三个成功标准',['F1']),
    (1,'问题与目标',250,'通话前记录、目标使用者、优先名单与三个成功标准',['data_notes','F1']),
    (2,'数据与质量',350,'来源与粒度、质量证据、处理决定、敏感属性与时间限制',['T1','F2','F1b']),
    (3,'方法与基线',450,'合理基线、实际特征、Train内预处理与Validation选参',['T2','coefficients']),
    # [D02-E02 原行保留] (4,'实验评价与结果',650,'同K比较、三业务量、消融、错误与预算敏感性',['F3','F4','T3','T4','T5']),
    (4,'实验评价与结果',650,'同K比较、三业务量、消融、错误与预算敏感性',['C_models','F3','F4','T3','T4','T5']),
    (5,'行动与责任',350,'预算上限、人工复核、示例联系限制及代价',['F5','T6']),
    (6,'限制与结论',350,'历史回放、非因果、漂移与不确定性，结论回应名单效率',['F1b','T6']),
]


def digest(data):return hashlib.sha256(data).hexdigest()


def resolve(value,key):
    for part in key.split('.'):
        value=value[int(part)] if isinstance(value,list) else value[part]
    return value


def validate_metrics(m):
    cp=m['contact_policy'];p=cp['policy'];fold=cp['folds']['test'];b=fold['baseline'];main=m['models']['logistic']
    encoded=json.dumps(p,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False).encode('utf-8')
    if digest(encoded)!=cp['policy_sha256'] or p['previous_minimum']!=3 or p['poutcome_equals']!='failure' or p['primary_scenario']!='hold_no_refill':
        raise ValueError('输入不是已评价的D01固定规则')
    if b['contacts']!=main['k'] or b['hits']!=main['hits_at_k'] or b['confusion']!=main['confusion_at_budget']:
        raise ValueError('D01与C01原名单不一致')
    for scenario in ['hold_no_refill','hold_with_refill']:
        row=fold[scenario]
        if row['net_extra_missed_vs_baseline']!=row['missed_subscriptions']-b['missed_subscriptions'] or row['net_extra_missed_vs_baseline']!=row['gross_removed_original_hits']-row['replacement_hits']:
            raise ValueError('D01净变化口径错误')
    if m['business']['extra_hits_vs_rule']!=main['hits_at_k']-m['models']['poutcome_success']['hits_at_k']:
        raise ValueError('C01业务量不一致')
    if m['business']['missed_subscriptions_at_k']!=main['missed_subscriptions_at_k']:
        raise ValueError('C01漏报被误改为D01漏报')
    if 'post-hoc' not in cp['evaluation_type']:raise ValueError('缺少D01事后评价标识')


def artifact_index(m):
    abc={
        # [D02-E06 新增] 问题界定与Test比较分别绑定实际来源。
        'data_notes':'data/README_data.md',
        'C_models':'local_review/C01_candidate/outputs/C_测试集模型比较表.md',
        'F1':'figures/F1_通话前后字段分界图.png','F1b':'figures/F1b_时间漂移证据.png','F2':'figures/F2_数据血缘图.png',
        'T1':'outputs/T1_数据质量表.md','dictionary':'outputs/data_dictionary.csv',
        'T2':'local_review/B01_candidate/outputs/T2_模型对比表.csv',
        'coefficients':'local_review/B01_candidate/outputs/logistic_coefficients.csv',
        'F3':'local_review/C01_candidate/figures/F3_PR曲线.png','F4':'local_review/C01_candidate/figures/F4_预算收益曲线.png',
        'T3':'local_review/C01_candidate/outputs/T3_误差切片表.md','T4':'local_review/C01_candidate/outputs/T4_duration消融表.md',
        'T5':'local_review/C01_candidate/outputs/T5_数字核对表.md'}
    source=m['contact_policy']['provenance']['baseline'];result={}
    if source['mode']=='accepted_p01_snapshot':
        path=ROOT/source['snapshot_path'];payload=path.read_bytes()
        if digest(payload)!=source['snapshot_fingerprint']['sha256']:raise ValueError('基线结果ZIP已变化')
        with zipfile.ZipFile(path) as archive:
            for name,relative in abc.items():
                member='workspace/'+relative;data=archive.read(member)
                result[name]={'kind':'zip_member','archive':path.relative_to(ROOT).as_posix(),'member':member,'sha256':digest(data)}
    elif source['mode']=='fresh_abc_run':
        ws=ROOT/source['run_directory']/'workspace'
        for name,relative in abc.items():
            path=ws/relative;result[name]={'kind':'file','path':path.relative_to(ROOT).as_posix(),'sha256':digest(path.read_bytes())}
    else:raise ValueError('未知D01基线来源')
    result['F5']={'kind':'generated','path':'F5_行动闭环.svg','companion':'F5_行动闭环.png'}
    result['T6']={'kind':'input_section','metrics_section':'contact_policy','reference':'D01已验收T6；本阶段从冻结JSON读取同一数字'}
    return result


def evidence_index(m):
    rows=[]
    def add(ident,chapters,title,keys,artifacts,interpretation,kind='observed'):
        rows.append({'id':ident,'chapters':chapters,'title':title,'kind':kind,
                     'bindings':[{'key':key,'value':copy.deepcopy(resolve(m,key))} for key in keys],
                     'artifacts':artifacts,'interpretation':interpretation})
    # [D02-E03 原行保留] add('E01',[1],'分析对象与输出',['protocol.label','protocol.positive_label','contact_policy.policy.unit'],['F1'],
    add('E01',[1],'分析对象与输出',['protocol.label','protocol.positive_label','contact_policy.policy.unit'],['data_notes','F1'],
        '一条留出期待联系记录；通话前排序。没有客户ID，不把行数等同独立客户数。')
    add('E02',[2],'样本与标签',['data.n_rows','data.n_columns','data.n_positive','data.positive_rate'],['T1','dictionary'],
        '报告实际样本规模、粒度和类别不平衡。')
    add('E03',[2],'质量处理',['data.n_duplicated_rows','data.n_pdays_999','data.n_nan_cells'],['T1','F2'],
        '重复保留留证；999为特殊含义；unknown保留为独立缺失类别，不写成已新增哨兵特征。')
    add('E04',[2],'unknown按列计数',['data.unknown_count_by_column.'+k for k in m['data']['unknown_count_by_column']],['T1'],
        '逐列质量证据，不把unknown丢进插补。')
    add('E05',[2,4,6],'行序切分与分布变化',['data.n_train','data.n_validation','data.n_test']+['data.positive_rate_by_fold.'+k for k in ['train','validation','test']],['F1b','T1'],
        '连续60/20/20，不打乱；正类率变化不证明宏观事件因果，也不等于精确日期切分。')
    add('E06',[3],'主特征与选参',['data.main_feature_count','model_selection.seed','model_selection.selection_fold','model_selection.selected_parameters.logistic.C'],['T2'],
        '主模型不用duration和宏观项；预处理仅Train拟合，Validation选参；不是按Test选赢家。')
    idx=next(i for i,r in enumerate(m['validation']['models']) if r['model']=='logistic')
    add('E07',[3],'Validation证据',[f'validation.models.{idx}.validation_pr_auc',f'validation.models.{idx}.hits_at_30pct'],['T2','coefficients'],
        '验证比较与Test分开；系数只解释相关，不解释因果。')
    add('E08',[4],'工作点及主模型',['protocol.test_rows','protocol.test_positive_rows','protocol.work_fraction','protocol.k_at_30pct','models.logistic.pr_auc','models.logistic.precision_at_k','models.logistic.recall_at_k'],['F3','F4'],
        'K为实验预算上限，非真实银行产能；AP为average_precision_score，图用阶梯口径。')
    add('E09',[1,4],'三个成功标准',['business.extra_hits_vs_rule','business.invalid_calls_avoided_vs_rule','business.missed_subscriptions_at_k'],['T5','F4'],
        '两个276是固定K下同一变化的两种表达，不相加；原模型漏报1340不改写成D01策略损失。')
    # [D02-E04 原行保留] add('E10',[4],'固定模型比较',['models.'+name+'.pr_auc' for name in ['poutcome_success','logistic','decision_tree','random_forest']],['F3','T2'],
    add('E10',[4],'固定模型比较',['models.'+name+'.pr_auc' for name in ['poutcome_success','logistic','decision_tree','random_forest']],['C_models'],
        '同切分同指标比较，不把小差异称为统计显著，也不使用Test重新调参。')
    add('E11',[4],'duration消融',['ablation.test_pr_auc_main','ablation.test_pr_auc_with_duration','ablation.test_pr_auc_absolute_difference','ablation.test_hits_absolute_difference'],['T4'],
        '通话后字段不可作真实通话前输入；较高分数是泄漏对照。')
    idx=next(i for i,r in enumerate(m['error_slices']['records']) if r['dimension']=='poutcome' and r['level']=='failure')
    add('E12',[4],'失败切片',[f'error_slices.records.{idx}.{key}' for key in ['sample_n','positives','recall','fn']],['T3'],
        '检查名单在哪类记录失灵；低召回不能作为永久排除整类的理由。')
    # [D02-E05 原行保留] add('E13',[4],'三例失败案例',[f'failure_cases.{i}.row_id' for i in range(len(m['failure_cases']))],['T3'],
    add('E13',[4],'原主模型三例失败案例',[f'failure_cases.{i}.row_id' for i in range(len(m['failure_cases']))],['T3'],
        '回到T3核对案例类型和真实标签；row_id是记录定位，不是客户ID。')
    indices=[next(i for i,r in enumerate(m['sensitivity']['records']) if r['model']==name and r['contact_fraction']==.1) for name in ['logistic','poutcome_success']]
    add('E14',[4,6],'10%预算反例',[f'sensitivity.records.{i}.hits' for i in indices],['F4'],
        '规则536、主模型417；不能写所有预算主模型均优。')
    add('E15',[5],'示例联系闸门',['contact_policy.policy.previous_minimum','contact_policy.policy.poutcome_equals','contact_policy.policy.primary_scenario'],['F5','T6'],
        '阈值3为预设示例；previous不是失败次数；人工放行未模拟。',kind='predefined_assumption')
    add('E16',[5],'主情景代价',['contact_policy.folds.test.hold_no_refill.'+k for k in ['contacts','hits','net_invalid_calls_avoided','net_extra_missed_vs_baseline','missed_subscriptions']],['F5','T6'],
        '保守假定人工不放行且不递补：2455联系、1197命中、少14无效、额外漏3、总漏1343。')
    add('E17',[5],'触发群体与名单损失',['contact_policy.folds.test.'+k for k in ['triggered_records','triggered_positive_total','triggered_original_selected','triggered_original_selected_positive']],['T6'],
        '群体120条含42订阅；原名单17条含3订阅。额外损失不能填42。')
    add('E18',[5],'固定递补对照',['contact_policy.folds.test.hold_with_refill.'+k for k in ['contacts','hits','replacement_hits','net_hits_change_vs_baseline']],['T6'],
        '固定对照，不按已看过的Test改选主方案；净+8不取消原3条记录被移出的机会损失。')
    add('E19',[5,6],'策略验证边界',['contact_policy.folds.validation.triggered_records','contact_policy.folds.validation.triggered_original_selected','contact_policy.evaluation_type'],['T6'],
        'Validation只有2条触发且不影响名单；Test已看过，不能称新的独立验证或稳定性证明。')
    add('E20',[6],'限制与结论',['guardrails.no_causal_claim','guardrails.no_uplift_claim','guardrails.does_not_deploy_or_call_customers'],['F1b','F5','T6'],
        '历史回放；缺未拨打对照和置信区间；不外推其他银行/时期，不写提高总体订阅率。')
    return rows


def diagram_spec(m):
    bindings=[('protocol.k_at_30pct','budget'),('contact_policy.policy.previous_minimum','gate'),
              ('contact_policy.folds.test.baseline.contacts','caption'),
              ('contact_policy.folds.test.hold_no_refill.contacts','caption'),
              ('contact_policy.folds.test.hold_no_refill.net_extra_missed_vs_baseline','caption')]
    nodes=[
        {'id':'input','xy':[3.6,8.7],'size':[4.8,1.05],'kind':'box','color':'blue','label':'通话前信息与固定模型分数\n核对来源、字段和版本'},
        {'id':'budget','xy':[3.6,7.2],'size':[4.8,1.05],'kind':'box','color':'blue','label':f"生成优先名单与预算上限\nK = {m['protocol']['k_at_30pct']}，可不打满预算"},
        # [D02-L01 原行保留] {'id':'gate','xy':[3.6,5.55],'size':[4.5,1.65],'kind':'diamond','color':'amber','label':f"触发示例闸门？\nprevious ≥ {m['contact_policy']['policy']['previous_minimum']} 且\npoutcome = failure"},
        {'id':'gate','xy':[3.6,5.48],'size':[5.0,1.85],'kind':'diamond','color':'amber','label':f"触发示例闸门？\nprevious ≥ {m['contact_policy']['policy']['previous_minimum']} 且\npoutcome = failure"},
        # [D02-L02 原行保留] {'id':'hold','xy':[9.3,5.55],'size':[3.5,1.15],'kind':'box','color':'amber','label':'暂缓自动联系\n进入人工复核队列'},
        {'id':'hold','xy':[9.3,5.48],'size':[3.5,1.15],'kind':'box','color':'amber','label':'暂缓自动联系\n进入人工复核队列'},
        {'id':'review','xy':[3.6,3.5],'size':[5.0,1.15],'kind':'box','color':'green','label':'人工复核联系依据与限制\n敏感属性不单独决定联系'},
        {'id':'call','xy':[3.6,1.8],'size':[4.8,1.05],'kind':'box','color':'green','label':'确认允许后按顺序外呼\n保留预算余额，不强制打满'},
        {'id':'record','xy':[9.3,1.8],'size':[3.5,1.05],'kind':'box','color':'gray','label':'结果留痕与后续审计\n联系、暂缓和复核理由'},
    ]
    edges=[
        {'from':'input','to':'budget','points':[[3.6,8.175],[3.6,7.725]],'label':'','label_xy':[0,0]},
        # [D02-L03 原行保留] {'from':'budget','to':'gate','points':[[3.6,6.675],[3.6,6.375]],'label':'','label_xy':[0,0]},
        {'from':'budget','to':'gate','points':[[3.6,6.675],[3.6,6.405]],'label':'','label_xy':[0,0]},
        # [D02-L04 原行保留] {'from':'gate','to':'hold','points':[[5.85,5.55],[7.55,5.55]],'label':'是','label_xy':[6.65,5.82]},
        {'from':'gate','to':'hold','points':[[6.1,5.48],[7.55,5.48]],'label':'是','label_xy':[6.65,5.82]},
        # [D02-L05 原行保留] {'from':'gate','to':'review','points':[[3.6,4.725],[3.6,4.075]],'label':'否','label_xy':[3.95,4.45]},
        {'from':'gate','to':'review','points':[[3.6,4.555],[3.6,4.075]],'label':'否','label_xy':[3.95,4.32]},
        # [D02-L06 原行保留] {'from':'hold','to':'review','points':[[9.3,4.975],[9.3,4.35],[5.0,4.35],[5.0,4.075]],'label':'转人工队列','label_xy':[8.0,4.60]},
        {'from':'hold','to':'review','points':[[9.3,4.905],[9.3,4.35],[5.0,4.35],[5.0,4.075]],'label':'转人工队列','label_xy':[8.0,4.60]},
        {'from':'review','to':'call','points':[[3.6,2.925],[3.6,2.325]],'label':'确认允许后','label_xy':[4.45,2.64]},
        {'from':'review','to':'record','points':[[6.1,3.5],[9.3,3.5],[9.3,2.325]],'label':'暂缓 / 未获准','label_xy':[8.0,3.78]},
        {'from':'call','to':'record','points':[[6.0,1.8],[7.55,1.8]],'label':'联系结果','label_xy':[6.78,2.05]},
        {'from':'record','to':'input','points':[[11.05,1.8],[11.9,1.8],[11.9,8.7],[6.0,8.7]],'label':'后续新数据审计；更新须另行验证','label_xy':[8.9,9.00]},
    ]
    a=m['contact_policy']['folds']['test'];caption=f"历史回放：不递补、人工不放行时，联系 {a['baseline']['contacts']} → {a['hold_no_refill']['contacts']}，额外漏报 {a['hold_no_refill']['net_extra_missed_vs_baseline']} 条订阅记录。"
    return {'title':'F5 名单使用与责任闭环','subtitle':'建议使用流程｜未部署，人工放行未模拟',
            'nodes':nodes,'edges':edges,'numeric_annotations':[{'key':k,'value':resolve(m,k),'location':where} for k,where in bindings],
            'caption':caption,'footnote':'阈值为作业示例；previous 是既往联系次数，poutcome 仅表示上次活动结果。',
            'canvas_inches':[12.6,10.6],'dpi':240,'svg_text':'outlined for portable Chinese rendering'}


def choose_font(spec,requested):
    names=[requested] if requested else ['Microsoft YaHei','SimHei','Noto Sans CJK SC','WenQuanYi Micro Hei']
    strings=[spec['title'],spec['subtitle'],spec['caption'],spec['footnote']]+[n['label'] for n in spec['nodes']]+[e['label'] for e in spec['edges']]
    required={ord(c) for text in strings for c in text if ord(c)>127}
    for name in names:
        try:
            path=font_manager.findfont(font_manager.FontProperties(family=name),fallback_to_default=False)
            if required<=set(FT2Font(path).get_charmap()):return name,Path(path).name
        except ValueError:continue
    raise RuntimeError('缺少覆盖本图中文字的字体；请指定可用的--font-family')


def render_f5(spec,out,font):
    plt.rcParams.update({'font.family':font,'axes.unicode_minus':False,'svg.fonttype':'path','svg.hashsalt':'INT6163-Group8-D02'})
    fig,ax=plt.subplots(figsize=spec['canvas_inches']);fig.subplots_adjust(left=0,right=1,top=1,bottom=0)
    ax.set(xlim=(0,12.6),ylim=(0,10.6));ax.axis('off')
    palette={'blue':('#EEF5FB','#315D7B'),'green':('#EBF5F0','#34765F'),'amber':('#FFF4DC','#B2862B'),'gray':('#EFF2F5','#667583')}
    texts=[]
    ax.text(6.3,10.18,spec['title'],ha='center',va='center',fontsize=23,color='#213F55',weight='bold')
    ax.text(6.3,9.70,spec['subtitle'],ha='center',va='center',fontsize=14,color='#52616C')
    for node in spec['nodes']:
        x,y=node['xy'];w,h=node['size'];fill,border=palette[node['color']]
        if node['kind']=='diamond':
            patch=Polygon([[x,y+h/2],[x+w/2,y],[x,y-h/2],[x-w/2,y]],closed=True,facecolor=fill,edgecolor=border,lw=1.6)
        else:patch=FancyBboxPatch((x-w/2,y-h/2),w,h,boxstyle='round,pad=0,rounding_size=0.10',facecolor=fill,edgecolor=border,lw=1.5)
        ax.add_patch(patch)
        t=ax.text(x,y,node['label'],ha='center',va='center',fontsize=16.5 if node['kind']=='diamond' else 17,linespacing=1.4,color='#203743')
        texts.append((node,t))
    for edge in spec['edges']:
        points=edge['points']
        for start,end in zip(points[:-2],points[1:-1]):
            ax.plot([start[0],end[0]],[start[1],end[1]],color='#657681',lw=1.35,zorder=1)
        ax.add_patch(FancyArrowPatch(points[-2],points[-1],arrowstyle='-|>',mutation_scale=15,lw=1.35,color='#657681',shrinkA=0,shrinkB=1,zorder=2))
        if edge['label']:
            # [D02-L07 原行保留] ax.text(*edge['label_xy'],edge['label'],ha='center',va='center',fontsize=11.3 if edge['from']=='record' else 12,color='#465966')
            ax.text(*edge['label_xy'],edge['label'],ha='center',va='center',fontsize=13.2 if edge['from']=='record' else 14,color='#465966')
    # [D02-L08 原行保留] ax.text(6.3,.65,spec['caption'],ha='center',va='center',fontsize=12.1,color='#334D5D')
    ax.text(6.3,.65,spec['caption'],ha='center',va='center',fontsize=14.2,color='#334D5D')
    # [D02-L09 原行保留] ax.text(6.3,.25,spec['footnote'],ha='center',va='center',fontsize=11.7,color='#52616C')
    ax.text(6.3,.25,spec['footnote'],ha='center',va='center',fontsize=13.5,color='#52616C')
    fig.canvas.draw();renderer=fig.canvas.get_renderer();layout=[]
    for node,text in texts:
        bbox=text.get_window_extent(renderer).transformed(ax.transData.inverted())
        x,y=node['xy'];w,h=node['size']
        inside=bbox.x0>=x-w/2+.03 and bbox.x1<=x+w/2-.03 and bbox.y0>=y-h/2+.03 and bbox.y1<=y+h/2-.03
        layout.append({'node':node['id'],'text_bbox':[float(v) for v in bbox.extents],'inside_node_rectangle':bool(inside)})
    description=json.dumps({'numeric_annotations':spec['numeric_annotations'],'status':'proposed workflow; supplementary historical replay'},ensure_ascii=False,sort_keys=True)
    fig.savefig(out/'F5_行动闭环.svg',metadata={'Date':None,'Creator':'INT6163 Group 8 D02','Description':description})
    fig.savefig(out/'F5_行动闭环.png',dpi=spec['dpi'],metadata={'Software':'INT6163 Group 8 D02 / Matplotlib '+matplotlib.__version__})
    plt.close(fig)
    return layout


def write_md(path,text):
    begin='<!-- D02_ORIGINAL_MARKDOWN_BEGIN\n';end='\nD02_ORIGINAL_MARKDOWN_END -->\n'
    if path.exists():
        old=path.read_text(encoding='utf-8')
        if old.startswith(begin) and end in old:prefix=old.split(end,1)[0]+end
        elif '-->' not in old:prefix=begin+old+end
        else:raise ValueError('旧Markdown不能嵌套注释')
    else:prefix=begin+'D02新增素材表，无被替换旧稿。'+end
    path.write_text(prefix+'\n'+text,encoding='utf-8')


def write_evidence(index,out):
    lines=['# 六章报告与证据对应表','', '本表是写作准备，不是正式报告。数字统一引用本阶段冻结的[已验收D01数字源](../inputs/metrics.D01.accepted.json)，F5为建议流程，尚未部署。','',
           '| 章 | 建议字数 | 主要内容 | 证据编号 | 图表 |','|---|---:|---|---|---|']
    for chapter in index['chapters']:
        ids=[r['id'] for r in index['evidence'] if chapter['number'] in r['chapters']]
        lines.append(f"| {chapter['number']} {chapter['title']} | {chapter['target_characters']} | {chapter['focus']} | {', '.join(ids)} | {', '.join(chapter['artifacts'])} |")
    lines += ['', '字数合计约2400；封面与参考文献不计，图表文字不自行全部排除。实际动笔顺序：第4章结果→第5章行动→第6章限制与结论→第3章方法→第2章数据→第1章问题，最后回查结论。','',
              '## 逐项数字与写法','', '| 编号与内容 | metrics.json键及原值 | 解释边界 |','|---|---|---|']
    for row in index['evidence']:
        bindings='<br>'.join('`'+b['key']+'` = '+json.dumps(b['value'],ensure_ascii=False) for b in row['bindings'])
        lines.append(f"| {row['id']} {row['title']} | {bindings} | {row['interpretation']} |")
    lines += ['', '## 图表实际来源','', 'F5：[SVG](F5_行动闭环.svg) / [PNG](F5_行动闭环.png)。','',
              # [D04_02-02 原包名链接保留]
              # 'ABC图表见[P01同次结果包](../../../results/ABC_C01_verified.zip)，按下表ZIP内部路径查看；不引用根目录旧outputs/figures。若输入来自新ABC运行，则使用表中本次工作区文件。','', '| 图表 | 实际文件或ZIP成员 |','|---|---|']
              'ABC与D结果见[同次统一结果包](../../../results/ABCD_verified.zip)；正式引用以包内report目录为准，原阶段路径由snapshot.json映射。若输入来自新ABC运行，素材来自本次工作区文件。','', '| 图表 | 实际文件或ZIP成员 |','|---|---|']
    for name,artifact in index['artifacts'].items():
        location=artifact.get('member',artifact.get('path',artifact.get('metrics_section','')))
        lines.append(f'| {name} | `{location}` |')
    lines += ['', '## 写作与待核对事项','']+['- '+x for x in index['pending_items']]
    lines += ['', '## 重跑本阶段','', '```powershell','python scripts/d02_report_assets.py','```','',
              '默认使用本阶段已冻结的D01输入；首次无冻结件时从D01候选读取。评估新版本时显式指定--metrics并选择新的D02输出目录，已有不同输入的冻结件不会被覆盖。',
              '本阶段不重训、不改原指标、不生成整篇report.docx，也不更新P01发布包。']
    write_md(out/'章节_图表_数字对应表.md','\n'.join(lines)+'\n')


def main():
    # [D02-IO01 新增] 明确命令行输出编码，不改变图表或数字口径。
    if hasattr(sys.stdout,'reconfigure'):sys.stdout.reconfigure(encoding='utf-8')
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--metrics',type=Path)
    parser.add_argument('--output-root',type=Path,default=ROOT/'local_review/D02_candidate')
    parser.add_argument('--font-family')
    args=parser.parse_args();target=args.output_root.resolve()
    allowed=[ROOT/'local_review/D02_candidate',ROOT/'local_review/repairs/D02']
    if not any(target==p or p in target.parents for p in allowed):raise ValueError('D02只能输出到D02目录，不能覆盖ABC/D01/P01')
    frozen=target/'inputs/metrics.D01.accepted.json'
    source=(args.metrics or (frozen if frozen.exists() else ROOT/'local_review/D01_candidate/outputs/metrics.json')).resolve()
    if ROOT not in source.parents:raise ValueError('数字源必须在本项目内')
    payload=source.read_bytes();m=json.loads(payload);validate_metrics(m)
    environment=c01.environment(ROOT);artifacts=artifact_index(m);evidence=evidence_index(m);spec=diagram_spec(m)
    font,font_basename=choose_font(spec,args.font_family)
    if frozen.exists() and frozen.read_bytes()!=payload:raise ValueError('D02已有不同冻结输入，请选择新输出目录')
    frozen.parent.mkdir(parents=True,exist_ok=True)
    if not frozen.exists():frozen.write_bytes(payload);frozen.chmod(0o444)
    out=target/'outputs'
    if out.exists():
        files=[p for p in out.iterdir() if p.is_file()]
        if files:
            backup=target/'D02_generated_before'/datetime.now().strftime('%Y%m%d_%H%M%S_%f')/'outputs';backup.mkdir(parents=True)
            for path in files:shutil.copy2(path,backup/path.name)
            (backup/'backup_manifest.json').write_text(json.dumps({p.name:digest(p.read_bytes()) for p in files},ensure_ascii=False,indent=2),encoding='utf-8')
    out.mkdir(parents=True,exist_ok=True)
    chapters=[{'number':n,'title':title,'target_characters':count,'focus':focus,'artifacts':refs} for n,title,count,focus,refs in CHAPTERS]
    index={'schema':'D02-1.0','input_sha256':digest(payload),'input_copy':'../inputs/metrics.D01.accepted.json',
           'status':'report assets only; formal report not written','chapters':chapters,'writing_order':[4,5,6,3,2,1],
           'evidence':evidence,'artifacts':artifacts,'diagram':spec,
           'pending_items':['正式正文约2400字，引用图表和数字按本表选择，避免把全部材料塞入正文。',
                            'UCI数据许可/DOI与Moro论文书目信息在正式写作前按原始来源核对。',
                            '贡献表需要真实组员姓名和实际产出；不猜姓名或记录未发生的贡献。',
                            'GenAI如实披露代码修复、验证、规划、图表生成及后续实际用途。',
                            '人工放行、真实产能和后续监测仅为建议流程；D01阈值3不是银行政策。',
                            'D01为事后补充回放；Validation触发2条，不构成稳定性或未来成效证据。',
                            '报告/PPT页码和字数待正式文档定稿后回填，不提前宣称核对完成。']}
    layout=render_f5(spec,out,font)
    index['rendering']={'font_family':font,'font_file_basename':font_basename,'layout':layout}
    (out/'D02_报告素材索引.json').write_text(json.dumps(index,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')
    write_evidence(index,out)
    if source.read_bytes()!=payload or frozen.read_bytes()!=payload:raise RuntimeError('绘图期间数字源变化')
    outputs={p.name:{'bytes':p.stat().st_size,'sha256':digest(p.read_bytes())} for p in sorted(out.iterdir()) if p.is_file() and p.name!='D02_run_manifest.json'}
    manifest={'stage':'D02','status':'candidate_pending_user_rerun','created_at_utc':datetime.now(timezone.utc).isoformat(timespec='seconds'),
              'metrics_sha256':digest(payload),'source_sha256':digest(Path(__file__).read_bytes()),'environment':environment,
              'font_family':font,'output_fingerprints':outputs,'models_retrained':False,'original_metrics_modified':False,'formal_report_created':False}
    (out/'D02_run_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
    print(f'[F5] SVG与PNG已生成；{len(spec["nodes"])}节点；建议流程，非部署')
    print(f'[证据] {len(chapters)}章；{len(evidence)}组证据；建议字数合计{sum(c["target_characters"] for c in chapters)}')
    print(f'[D02_PASS] {out}')


if __name__=='__main__':main()
