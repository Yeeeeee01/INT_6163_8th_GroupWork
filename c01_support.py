"""C01 shared registry/rendering. Scientific evaluation functions remain in 03_eval.py."""
from pathlib import Path
import argparse
import csv
import hashlib
import importlib.metadata
import json
import math
import os
import shutil
import sys
from datetime import datetime

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.metrics import precision_recall_curve

DECLARED = {"pandas":"2.2.3", "scikit-learn":"1.6.1", "PyYAML":"6.0.2", "matplotlib":"3.9.4"}
LEGACY_SCORES_NORMALIZED = "b354c6cb35d3c6ef2f39d2b6b66a3c136319e072bc62770f5aecc615735cc2bc"


def fingerprint(path, root):
    content=path.read_bytes()
    return {"path":path.relative_to(root).as_posix(),"bytes":len(content),
            "sha256":hashlib.sha256(content).hexdigest(),
            "lf_normalized_sha256":hashlib.sha256(content.replace(b"\r\n",b"\n").replace(b"\r",b"\n")).hexdigest()}


def json_default(value):
    if isinstance(value,np.generic):return value.item()
    raise TypeError(type(value).__name__)


def environment(root):
    required={}
    for line in (root/"requirements.txt").read_text(encoding="utf-8").splitlines():
        if line.strip() and not line.lstrip().startswith("#"):
            name,version=line.strip().split("==",1);required[name]=version
    if required!=DECLARED or sys.version_info<(3,9):
        raise RuntimeError("环境声明不符合本次GitHub基线：Python3.9+及原requirements")
    for name,version in required.items():
        if importlib.metadata.version(name)!=version:raise RuntimeError("依赖版本不符："+name)
    return {"authority":"GitHub README Python3.9+ and requirements.txt","declared":required,
            "observed_python":sys.version,"observed_packages":{n:importlib.metadata.version(n) for n in [*DECLARED,"numpy","scipy"]},
            "requires_identical_original_environment":False}


def configure(root):
    parser=argparse.ArgumentParser(description="C01：评价同一次B输出并生成统一数字与图表")
    parser.add_argument("--input-root",type=Path,default=root/"local_review/B01_candidate")
    parser.add_argument("--output-root",type=Path,default=root/"local_review/C01_candidate")
    parser.add_argument("--legacy-reference",action="store_true",help="只对原GitHub冻结分数作回归对照，不代表从原始数据重新训练")
    args=parser.parse_args()
    incoming=args.input_root.resolve();out=args.output_root.resolve()
    if incoming!=root and root not in incoming.parents:raise ValueError("输入必须在本项目内")
    if out==root or root not in out.parents:raise ValueError("C01候选输出必须在项目子目录，保留根目录原冻结结果")
    if incoming==out:raise ValueError("C输出目录不能覆盖B输入目录")
    env=environment(root)
    files={"scores":incoming/"outputs/scores.csv","validation":incoming/"outputs/T2_模型对比表.csv",
           "split":root/"outputs/split_v1.csv","a_summary":root/"outputs/A_summary.json",
           "raw":root/"data/raw/bank-additional-full.csv","config":root/"configs/features.yaml",
           "c_source":root/"03_eval.py","c_support":root/"c01_support.py","requirements":root/"requirements.txt",
           "pool":incoming/"outputs/model_selection_pool.csv","coefficients":incoming/"outputs/logistic_coefficients.csv"}
    for path in files.values():
        if not path.is_file():raise FileNotFoundError(str(path)+"；请先完成A和同一版本B")
    fps={name:fingerprint(path,root) for name,path in files.items()}
    b_manifest=None;byte_only=[]
    if args.legacy_reference:
        if fps["scores"]["lf_normalized_sha256"]!=LEGACY_SCORES_NORMALIZED:
            raise ValueError("legacy-reference必须使用原GitHub冻结分数")
        mode="github_frozen_score_reference"
    else:
        path=incoming/"outputs/B_run_manifest.json"
        if not path.is_file():raise FileNotFoundError("缺少B_run_manifest，无法确认同次结果配对")
        b_manifest=json.loads(path.read_text(encoding="utf-8"));fps["b_manifest"]=fingerprint(path,root)
        if b_manifest["protocol"]["selection_fold"]!="validation" or b_manifest["protocol"]["test_labels_used_by_B"]:
            raise ValueError("B选参协议不符合Validation-only要求")
        if b_manifest["protocol"]["seed"]!=42:raise ValueError("B种子与既定协议不一致")
        for relative,old in b_manifest["input_fingerprints"].items():
            now=fingerprint(root/relative,root)
            if now["lf_normalized_sha256"]!=old["lf_normalized_sha256"]:raise ValueError("B输入/源码已变化："+relative)
            if now["sha256"]!=old["sha256"]:byte_only.append(relative)
        for name,old in b_manifest["output_fingerprints"].items():
            now=fingerprint(incoming/"outputs"/name,root)
            if now["lf_normalized_sha256"]!=old["lf_normalized_sha256"]:raise ValueError("B输出与清单不匹配："+name)
            if now["sha256"]!=old["sha256"]:byte_only.append(name)
        mode="same_run_B01_output"
    out.mkdir(parents=True,exist_ok=True)
    for name in ["outputs","figures"]:
        folder=out/name
        if folder.exists():
            old_files=[p for p in folder.iterdir() if p.is_file()]
            if old_files:
                archive=out/"C01_generated_before"/datetime.now().strftime("%Y%m%d_%H%M%S_%f")/name
                archive.mkdir(parents=True)
                for path in old_files:shutil.copy2(path,archive/path.name)
                (archive/"manifest.json").write_text(json.dumps({p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in old_files},ensure_ascii=False,indent=2),encoding="utf-8")
        folder.mkdir(exist_ok=True)
    # The first candidate retains the submitted Markdown as an HTML comment.
    for name in ["T3_误差切片表.md","T4_duration消融表.md","T5_数字核对表.md","C_测试集模型比较表.md"]:
        if not (out/"outputs"/name).exists() and (root/"outputs"/name).is_file():
            shutil.copy2(root/"outputs"/name,out/"outputs"/name)
    return {"root":root,"incoming":incoming,"output_root":out,"out":out/"outputs","fig":out/"figures",
            "files":files,"fingerprints":fps,"environment":env,"b_manifest":b_manifest,"mode":mode,
            "byte_only_differences":byte_only,"legacy_reference":args.legacy_reference}


def build_registry(models,business,slices,sensitivity,a_summary,validation,cases,context,test_labels,scores):
    y=test_labels.set_index("row_id")["y"].eq("yes").astype(int)
    if a_summary["data"]["n_test"]!=len(y) or a_summary["data"]["n_positive_by_fold"]["test"]!=int(y.sum()):
        raise ValueError("A汇总与实际Test标签不一致")
    raw_hash=context["fingerprints"]["raw"]["lf_normalized_sha256"]
    if a_summary["data"].get("raw_normalized_sha256",a_summary["data"]["raw_sha256"])!=raw_hash:
        raise ValueError("A汇总不对应当前原始数据内容")
    main=models["logistic"];abl=models["logistic_duration_ablation"]
    vm=validation.loc[validation.model.eq("logistic")].iloc[0]
    va=validation.loc[validation.model.eq("logistic_duration_ablation")].iloc[0]
    curves={}
    for model in ["logistic","poutcome_success","no_skill","logistic_duration_ablation"]:
        risk=scores.loc[scores.model.eq(model)].set_index("row_id").risk.reindex(y.index)
        precision,recall,_=precision_recall_curve(y,risk)
        curves[model]={"precision":precision.tolist(),"recall":recall.tolist(),"average_precision":models[model]["pr_auc"]}
    b=context["b_manifest"]
    source_dir=context["incoming"]/"outputs"
    pool=pd.read_csv(source_dir/"model_selection_pool.csv") if (source_dir/"model_selection_pool.csv").exists() else pd.DataFrame()
    coefficients=pd.read_csv(source_dir/"logistic_coefficients.csv") if (source_dir/"logistic_coefficients.csv").exists() else pd.DataFrame()
    validation_records=validation.to_dict(orient="records")
    for row in validation_records:row["parameters"]=json.loads(row.get("selected_parameters","{}"))
    pool_records=pool.to_dict(orient="records")
    for row in pool_records:
        if "parameters" in row:row["parameters"]=json.loads(row["parameters"])
    result={
        "schema_version":"C01-1.0","generated_by":"C","generated_at":datetime.now().isoformat(timespec="seconds"),
        "data":a_summary["data"],
        "source_files":{k:v["path"] for k,v in context["fingerprints"].items()},
        "protocol":{"split_id":a_summary["split_id"],"split_method":a_summary["data"]["split_method"],"label":"y","positive_label":"yes",
                    "test_row_id_min":int(y.index.min()),"test_row_id_max":int(y.index.max()),"test_rows":len(y),
                    "test_positive_rows":int(y.sum()),"test_positive_rate":float(a_summary["data"]["positive_rate_by_fold"]["test"]),
                    "test_positive_rate_exact":float(y.mean()),"work_fraction":0.30,"k_at_30pct":main["k"],
                    "ranking_rule":"risk descending; row_id ascending as deterministic tie-breaker","k_rule":"ceil(work_fraction * test_rows)",
                    "test_used_for_final_evaluation_only":True,"test_label_read_location":"03_eval.py/load_test_labels()"},
        "selected_model":"logistic","models":models,"business":business,
        "validation":{"source_precision":"B T2 CSV retained at original six-decimal export precision","models":validation_records},
        "model_selection":{"seed":42,"selection_fold":"validation","candidate_records":pool_records,
                           "selected_parameters":b["selected_parameters"] if b else {r["model"]:r["parameters"] for r in validation_records}},
        "coefficients":{"interpretation":"associations, not causal effects","records":coefficients.to_dict(orient="records")},
        "ablation":{"compared_models":["logistic","logistic_duration_ablation"],
                    "test_pr_auc_main":main["pr_auc"],"test_pr_auc_with_duration":abl["pr_auc"],
                    "test_pr_auc_absolute_difference":abl["pr_auc"]-main["pr_auc"],
                    "test_pr_auc_relative_inflation":(abl["pr_auc"]-main["pr_auc"])/main["pr_auc"],
                    "test_hits_main":main["hits_at_k"],"test_hits_with_duration":abl["hits_at_k"],
                    "test_hits_absolute_difference":abl["hits_at_k"]-main["hits_at_k"],
                    "validation_pr_auc_main":float(vm.validation_pr_auc),"validation_pr_auc_with_duration":float(va.validation_pr_auc),
                    "validation_hits_main":int(vm.hits_at_30pct),"validation_hits_with_duration":int(va.hits_at_30pct),
                    "uci_decision":"duration should be discarded if the intention is to have a realistic predictive model"},
        "error_slices":{"dimensions":slices.dimension.unique().tolist(),"minimum_reported_slice_n":100,"rows":len(slices),
                        "small_sample_rows":int(slices.small_sample_flag.sum()),"records":slices.to_dict(orient="records"),"table":"outputs/T3_误差切片表.md"},
        "failure_cases":cases.to_dict(orient="records"),
        "sensitivity":{"fractions":[x/100 for x in range(10,101,10)],"models":["logistic","poutcome_success","no_skill"],
                       "rows":len(sensitivity),"records":sensitivity.to_dict(orient="records"),"interpretation":"30% primary; other budgets are sensitivity only"},
        "pr_curves":curves,
        "artifacts":{"pr_curve":"figures/F3_PR曲线.png","budget_curve":"figures/F4_预算收益曲线.png",
                     "slice_table":"outputs/T3_误差切片表.md","duration_ablation_table":"outputs/T4_duration消融表.md",
                     "number_audit_table":"outputs/T5_数字核对表.md","all_numeric_index":"outputs/T5_all_numbers.csv",
                     "model_comparison_table":"outputs/C_测试集模型比较表.md"},
        "reproducibility":{"input_mode":context["mode"],"input_fingerprints":context["fingerprints"],"environment":context["environment"],
                           "b_run_environment":b["environment"] if b else None,"byte_only_differences":context["byte_only_differences"],
                           "acceptance":"complete analysis under GitHub-declared requirements; paired results and repeatable computations",
                           "requires_identical_original_environment":False,"test_label_loads_per_evaluation":1},
        "guardrails":{"single_source_of_truth":"outputs/metrics.json","metrics_json_locked_read_only":True,"no_causal_claim":True,
                      "no_uplift_claim":True,"does_not_claim_increase_subscription_rate":True,"does_not_deploy_or_call_customers":True,
                      "sensitive_attributes_not_used_as_single_contact_rule":True,"test_metrics_not_used_for_model_selection":True,
                      "duration_ablation_not_used_as_main_model":True,
                      "limitations":["Historical replay only; no untreated control group.","Associations are not causal effects.",
                                     "One chronological Test period; no cross-bank or cross-period generalization.",
                                     "No confidence intervals or prospective deployment evidence.",
                                     "Positive prevalence differs across chronological folds; compare on the same Test rows."],
                      "contact_cap_policy":"not_defined_or_evaluated_in_C01; reserved for later D action design"}}
    # Reject accidental missing/nonfinite values before publishing a numeric registry.
    return json.loads(json.dumps(result,ensure_ascii=False,allow_nan=False,default=json_default))


def write_markdown(path,text):
    begin="<!-- C01_ORIGINAL_MARKDOWN_BEGIN\n";end="\nC01_ORIGINAL_MARKDOWN_END -->\n"
    if path.exists():
        old=path.read_text(encoding="utf-8")
        if old.startswith(begin) and end in old:prefix=old.split(end,1)[0]+end
        elif "-->" not in old:prefix=begin+old+end
        else:raise ValueError("旧Markdown已备份，请核对嵌套注释："+str(path))
    else:prefix=begin+"本次新生成，无被替换旧稿。"+end
    path.write_text(prefix+"\n"+text,encoding="utf-8")


def model_table(metrics,out):
    p=metrics["protocol"]
    lines=["# C 测试集模型比较表", "",f"同次输入：Test {p['test_rows']}条，K={p['k_at_30pct']}；同分按row_id升序。", "",
           "| 模型 | Test AP | Precision@K | Recall@K | 命中@K | 无效联系 | 漏报订阅 |","|---|---:|---:|---:|---:|---:|---:|"]
    for name,row in metrics["models"].items():
        lines.append(f"| {name} | {row['pr_auc']:.6f} | {row['precision_at_k']:.6f} | {row['recall_at_k']:.6f} | {row['hits_at_k']} | {row['invalid_calls_at_k']} | {row['missed_subscriptions_at_k']} |")
    lines += ["", "AP为average_precision_score。恒0基线的Top-K由原行号决定，不是随机联系的期望表现。duration版本只作泄漏消融。", ""]
    write_markdown(out/"C_测试集模型比较表.md","\n".join(lines))


def slice_table(metrics,out):
    p=metrics["protocol"];s=metrics["error_slices"]
    lines=[f"# T3 误差切片（Test，K={p['k_at_30pct']}）","",f"样本量小于{s['minimum_reported_slice_n']}标记小样本。召回率=TP/(TP+FN)，误报率=FP/(FP+TN)。","",
           "| 维度 | 分桶 | 样本量 | 真实订阅 | 名单人数 | TP | FP | FN | TN | 召回率 | 误报率 | 精度 | 标记 |","|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|"]
    for r in s["records"]:
        flag="小样本" if r["small_sample_flag"] else ""
        lines.append(f"| {r['dimension_label']} | {r['level']} | {r['sample_n']} | {r['positives']} | {r['selected_n']} | {r['tp']} | {r['fp']} | {r['fn']} | {r['tn']} | {r['recall']:.4f} | {r['false_positive_rate']:.4f} | {r['precision']:.4f} | {flag} |")
    lines += ["","## 本次切片读数",""]
    for r in s["records"]:
        if (r["dimension"]=="poutcome" and r["level"]=="failure") or (r["dimension"]=="campaign" and r["level"] in ["4-6次","7次及以上"]) or (r["dimension"]=="job" and r["level"]=="unknown"):
            lines.append(f"- {r['dimension']}={r['level']}：样本{r['sample_n']}，真实订阅{r['positives']}，漏报{r['fn']}，召回率{r['recall']:.2%}。")
    lines += ["", "切片解释误差，不作为单一排除规则；联系上限及其额外代价尚待后续行动方案评价。", "", "## 失败案例", "",
              "| 类型 | row_id | 风险分 | 是否进名单 | poutcome | contact | job | campaign | previous | pdays | y |","|---|---:|---:|---|---|---|---|---:|---:|---:|---|"]
    for r in metrics["failure_cases"]:
        lines.append(f"| {r['case_type']} | {r['row_id']} | {r['risk']:.6f} | {'是' if r['selected_at_k'] else '否'} | {r['poutcome']} | {r['contact']} | {r['job']} | {r['campaign']} | {r['previous']} | {r['pdays']} | {r['y']} |")
    write_markdown(out/"T3_误差切片表.md","\n".join(lines)+"\n")


def ablation_table(metrics,out):
    a=metrics["ablation"]
    lines=["# T4 duration消融","","主模型与消融只差duration；不可用于通话前决策的字段不作为主模型输入。","",
           "| 数据段 | 主模型AP | 主模型命中 | 含duration AP | 含duration命中 | AP绝对差 | 命中差 | AP相对差 |","|---|---:|---:|---:|---:|---:|---:|---:|"]
    for fold,prefix in [("Validation","validation"),("Test","test")]:
        ap=a[prefix+"_pr_auc_main"];other=a[prefix+"_pr_auc_with_duration"]
        hits=a[prefix+"_hits_main"];extra=a[prefix+"_hits_with_duration"]
        lines.append(f"| {fold} | {ap:.6f} | {hits} | {other:.6f} | {extra} | {other-ap:+.6f} | {extra-hits:+d} | {(other-ap)/ap:+.2%} |")
    lines += ["",'UCI说明："should be discarded if the intention is to have a realistic predictive model"。',""]
    write_markdown(out/"T4_duration消融表.md","\n".join(lines))


def numeric_leaves(value,prefix=""):
    if isinstance(value,bool):return
    if isinstance(value,(int,float)):
        yield prefix,value
    elif isinstance(value,dict):
        for key,item in value.items():yield from numeric_leaves(item,prefix+"."+key if prefix else key)
    elif isinstance(value,list):
        for i,item in enumerate(value):yield from numeric_leaves(item,prefix+"."+str(i))


def number_audit(metrics,out):
    values=dict(numeric_leaves(metrics))
    with (out/"T5_all_numbers.csv").open("w",encoding="utf-8-sig",newline="") as f:
        writer=csv.writer(f);writer.writerow(["metrics.json键名","数值","类型","报告/PPT页码"])
        for key,value in values.items():writer.writerow([key,repr(value),type(value).__name__,""])
    keys=["data.n_rows","data.n_columns","data.n_positive","data.n_duplicated_rows","data.n_pdays_999","data.n_train","data.n_validation","data.n_test",
          "protocol.test_positive_rows","protocol.test_positive_rate_exact","protocol.k_at_30pct","model_selection.seed"]
    keys += [f"models.{m}.{k}" for m in metrics["models"] for k in ["pr_auc","hits_at_k","precision_at_k","recall_at_k"]]
    keys += ["business.extra_hits_vs_rule","business.invalid_calls_avoided_vs_rule","business.missed_subscriptions_at_k",
             "ablation.test_pr_auc_absolute_difference","ablation.test_hits_absolute_difference"]
    keys += [k for k in values if k.startswith("error_slices.records.") and k.endswith((".sample_n",".positives",".recall",".fn"))]
    keys += [k for k in values if k.startswith("sensitivity.records.") and k.endswith((".contact_fraction",".contacted",".hits"))]
    lines=["# T5 常用数字核对表","","所有分析数字保存在同次metrics.json。此表列常用数字，完整数值叶节点索引见T5_all_numbers.csv（含曲线、参数、案例及系数）。列表索引用点号数字，例如error_slices.records.0.recall。页码由D/E回填。","",
           "| 数字 | metrics.json键名 | 报告/PPT页码 |","|---:|---|---|"]
    for key in dict.fromkeys(keys):
        if key in values:
            value=values[key];shown=str(value) if isinstance(value,int) else f"{value:.6f}"
            lines.append(f"| {shown} | `{key}` | 待D/E回填 |")
    write_markdown(out/"T5_数字核对表.md","\n".join(lines)+"\n")


def pr_plot(metrics,figdir):
    fig,ax=plt.subplots(figsize=(7.2,4.6))
    labels={"logistic":"Logistic（主模型）","poutcome_success":"poutcome_success规则","no_skill":"恒0基线","logistic_duration_ablation":"Logistic + duration（仅消融）"}
    colors={"logistic":"#185FA5","poutcome_success":"#0F6E56","no_skill":"#777777","logistic_duration_ablation":"#A32D2D"}
    for name,c in metrics["pr_curves"].items():
        ax.step(c["recall"],c["precision"],where="post",label=f"{labels[name]}  AP={c['average_precision']:.3f}",color=colors[name],linewidth=2 if name=="logistic" else 1.4)
    rate=metrics["protocol"]["test_positive_rate_exact"]
    ax.axhline(rate,ls="--",lw=1,color="#A32D2D",label=f"Test正类率 {rate:.1%}")
    ax.set(xlim=(0,1),ylim=(0,1.02),xlabel="Recall",ylabel="Precision",title="F3  Test PR曲线（与AP一致的阶梯式）")
    ax.grid(alpha=.22);ax.legend(frameon=False,fontsize=8.2,loc="upper right");fig.tight_layout()
    fig.savefig(figdir/"F3_PR曲线.png",dpi=180,bbox_inches="tight");plt.close(fig)


def budget_plot(metrics,figdir):
    data=pd.DataFrame(metrics["sensitivity"]["records"]);fraction=metrics["protocol"]["work_fraction"]
    labels={"logistic":"Logistic（主模型）","poutcome_success":"poutcome_success规则","no_skill":"恒0基线（同分按行序）"}
    colors={"logistic":"#185FA5","poutcome_success":"#0F6E56","no_skill":"#777777"}
    fig,ax=plt.subplots(figsize=(7.2,4.6))
    for name in metrics["sensitivity"]["models"]:
        part=data.loc[data.model.eq(name)]
        ax.plot(part.contact_fraction*100,part.hits,marker="o",markersize=4,lw=2 if name=="logistic" else 1.5,color=colors[name],label=labels[name])
    main=data.loc[data.model.eq("logistic") & np.isclose(data.contact_fraction,fraction)].iloc[0]
    ax.axvline(fraction*100,color="#A32D2D",ls="--",lw=1);ax.scatter([fraction*100],[main.hits],s=55,color="#A32D2D",zorder=5)
    ax.annotate(f"主工作点 {fraction:.0%}: {int(main.hits)}次命中",xy=(fraction*100,main.hits),xytext=(fraction*100+6,main.hits-120),arrowprops={"arrowstyle":"->","color":"#A32D2D"},color="#A32D2D",fontsize=9)
    ax.set(xlabel="联系预算占Test名单比例 (%)",ylabel="名单命中的真实订阅数",title="F4  预算-收益曲线：同样名单规模下的命中")
    ax.set_xticks([x*100 for x in metrics["sensitivity"]["fractions"]]);ax.grid(alpha=.22);ax.legend(frameon=False,fontsize=8.4,loc="lower right");fig.tight_layout()
    fig.savefig(figdir/"F4_预算收益曲线.png",dpi=180,bbox_inches="tight");plt.close(fig)


def write_metrics(path,metrics):
    if path.exists():os.chmod(path,0o666)
    path.write_text(json.dumps(metrics,ensure_ascii=False,indent=2,allow_nan=False),encoding="utf-8")
    os.chmod(path,0o444)


def finish(context,metrics):
    current={name:fingerprint(path,context["root"]) for name,path in context["files"].items()}
    if any(current[name]!=context["fingerprints"][name] for name in current):raise RuntimeError("评价期间输入发生变化")
    if context["b_manifest"] is not None:
        now=fingerprint(context["incoming"]/"outputs/B_run_manifest.json",context["root"])
        if now!=context["fingerprints"]["b_manifest"]:raise RuntimeError("评价期间B清单发生变化")
    files=[p for folder in [context["out"],context["fig"]] for p in folder.iterdir() if p.is_file() and p.name!="C_run_manifest.json"]
    record={"stage":"C01","generated_at":datetime.now().isoformat(timespec="seconds"),"input_mode":context["mode"],
            "input_fingerprints":context["fingerprints"],"output_fingerprints":{p.relative_to(context["output_root"]).as_posix():fingerprint(p,context["root"]) for p in files},
            "requires_identical_original_environment":False,"status":"C01_paired_reproduction_candidate","root_legacy_files_replaced":False}
    (context["out"]/"C_run_manifest.json").write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding="utf-8")
