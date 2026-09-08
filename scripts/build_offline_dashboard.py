from __future__ import annotations

if __package__:
    from ._ui_presentation import localize_html as _ui_localize_html
else:
    from _ui_presentation import localize_html as _ui_localize_html


import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "web" / "DIKWP_QINGYUAN_OS_Offline_Demo.html"


def load_runs() -> list[dict]:
    runs = []
    for example in sorted((ROOT / "examples").glob("*.json")):
        output = ROOT / "outputs" / "reference" / example.stem
        certificate = json.loads((output / "qingyuan_certificate.json").read_text(encoding="utf-8"))
        assessment = json.loads((output / "assessment.json").read_text(encoding="utf-8"))
        plan = json.loads((output / "intervention_plan.json").read_text(encoding="utf-8"))
        truth = json.loads((output / "truth_return_card.json").read_text(encoding="utf-8"))
        support = json.loads((output / "real_life_support_plan.json").read_text(encoding="utf-8"))
        residual = json.loads((output / "residual_queue.json").read_text(encoding="utf-8"))
        semantic = json.loads((output / "semantic_graph.json").read_text(encoding="utf-8"))
        item = json.loads(example.read_text(encoding="utf-8"))
        runs.append({
            "id": item["item_id"],
            "title": item["title"],
            "channel": item["channel"],
            "content_type": item.get("content_type", ""),
            "text": item["text"],
            "certificate": certificate,
            "profile": assessment["non_aggregated_profile"],
            "models": assessment["world_models"],
            "model_disagreement": assessment["model_disagreement"],
            "plan": plan,
            "truth": truth,
            "support": support,
            "residual": residual,
            "semantic": {"closure_vector": semantic["closure_vector"], "records": len(semantic["records"]), "routes": len(semantic["routes"])},
        })
    return runs


def main() -> None:
    data = load_runs()
    data_json = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    html_text = f'''<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>DIKWP-QINGYUAN-OS · 清源离线驾驶舱</title>
<style>
:root{{--bg:#07182d;--bg2:#12394c;--card:#f7fbfb;--ink:#153541;--muted:#5b7480;--teal:#25aa9a;--cyan:#69e4d5;--red:#bd4554;--amber:#c98a26;--line:#d9ece9}}
*{{box-sizing:border-box}} body{{margin:0;font-family:Inter,Segoe UI,Arial,"Noto Sans SC",sans-serif;background:linear-gradient(135deg,var(--bg),var(--bg2));color:#fff;min-height:100vh}}
header{{padding:48px 5vw 26px;border-bottom:1px solid rgba(255,255,255,.14)}} h1{{font-size:clamp(30px,5vw,58px);margin:0 0 10px}} .subtitle{{font-size:18px;color:#bce9e4;max-width:1100px;line-height:1.6}}
.firewall{{margin-top:18px;display:flex;flex-wrap:wrap;gap:9px}} .pill{{padding:8px 12px;border-radius:999px;background:rgba(105,228,213,.14);border:1px solid rgba(105,228,213,.45);font-size:13px}}
main{{padding:26px 5vw 70px;max-width:1700px;margin:auto}} .toolbar{{display:grid;grid-template-columns:minmax(260px,1fr) auto;gap:14px;align-items:center;margin-bottom:20px}}
select,button{{font:inherit;border:1px solid rgba(255,255,255,.25);border-radius:12px;padding:12px 14px}} select{{background:#fff;color:#123}} button{{background:#1f8d82;color:#fff;cursor:pointer}}
.grid{{display:grid;grid-template-columns:1.1fr .9fr;gap:18px}} .card{{background:var(--card);color:var(--ink);border-radius:18px;padding:22px;box-shadow:0 18px 50px rgba(0,0,0,.22);border:1px solid rgba(255,255,255,.4)}} .card h2{{margin:0 0 15px;font-size:23px}} .card h3{{margin:21px 0 10px}}
.full{{grid-column:1/-1}} .meta{{display:flex;flex-wrap:wrap;gap:8px;margin:10px 0 16px}} .tag{{background:#e5f5f2;border:1px solid #b9e6df;border-radius:999px;padding:6px 10px;font-size:12px}}
.disposition{{font-weight:800;font-size:22px;color:#0b786e}} .quote{{background:#eef7f6;border-left:5px solid var(--teal);padding:15px;border-radius:8px;line-height:1.55}}
.profile{{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px}} .metric{{border:1px solid var(--line);border-radius:12px;padding:10px}} .metric-row{{display:flex;justify-content:space-between;font-size:13px;gap:8px}} .bar{{height:8px;background:#dcebea;border-radius:999px;overflow:hidden;margin-top:8px}} .bar span{{display:block;height:100%;background:linear-gradient(90deg,#2bb5a5,#db8b36)}}
.action{{border:1px solid var(--line);border-radius:14px;padding:14px;margin:10px 0}} .action .level{{font-size:12px;font-weight:800;color:#8b5f11}} .action strong{{display:block;margin:5px 0}} .action p{{margin:6px 0;color:#45616c;line-height:1.5}}
.claim{{border-bottom:1px solid var(--line);padding:10px 0}} .claim:last-child{{border:0}} .status{{font-size:12px;font-weight:700;color:#0b786e}}
.model{{border:1px solid var(--line);padding:12px;border-radius:12px;margin:9px 0}} .model code{{font-size:12px}}
ol.steps{{padding-left:22px}} ol.steps li{{padding:6px 0;line-height:1.5}} .warning{{background:#fff2f0;border:1px solid #f1c0ba;border-radius:12px;padding:13px;color:#7e2634}}
.footer-note{{text-align:center;color:#bce9e4;margin-top:30px;line-height:1.6}} @media(max-width:980px){{.grid{{grid-template-columns:1fr}} .profile{{grid-template-columns:1fr}} .toolbar{{grid-template-columns:1fr}}}}
</style>
</head>
<body>
<header>
<h1>DIKWP-QINGYUAN-OS · 清源</h1>
<div class="subtitle">主动认知环境免疫、操纵断链与证据回流。系统针对证据断裂、来源遮蔽、上瘾放大、脆弱人群利用和利益回流；不把悲伤、批评、坏消息或异议当成需要清除的“负能量”。</div>
<div class="firewall"><span class="pill">负面事实保护</span><span class="pill">正面包装同等审计</span><span class="pill">三类世界模型并存</span><span class="pill">非聚合结算</span><span class="pill">具名·限时·可逆·可申诉</span><span class="pill">自动外部行动权限 = 0</span></div>
</header>
<main>
<div class="toolbar"><select id="scenario"></select><button id="next">下一个案例 / Next</button></div>
<div class="grid">
<section class="card"><h2 id="title"></h2><div class="meta" id="meta"></div><div class="disposition" id="disp"></div><h3>输入摘要</h3><div class="quote" id="text"></div><h3>证据回流卡</h3><div id="claims"></div></section>
<section class="card"><h2>非聚合风险与保护向量</h2><div class="profile" id="profile"></div><h3>模型分歧</h3><div id="disagreement"></div></section>
<section class="card full"><h2>主动处置阶梯：不删除人，不以情绪定真假</h2><div id="actions"></div></section>
<section class="card"><h2>三个非同构世界模型</h2><div id="models"></div></section>
<section class="card"><h2>现实生活支持</h2><div id="support"></div></section>
<section class="card"><h2>DIKWP 与余量</h2><div id="semantic"></div><div id="residuals"></div></section>
<section class="card"><h2>权利、申诉与边界</h2><div class="warning">任何高影响措施都必须由具名授权主体执行；本原型不删除、不降权、不举报、不冻结支付，也不诊断个人。</div><ul><li>批评、揭弊、少数意见和公共利益材料设有误伤防火墙。</li><li>暂时处置必须到期、复核并可申诉。</li><li>未知效果保持为现实债务，必须用结果校准并允许模型退役。</li></ul><div id="cert"></div></section>
</div>
<div class="footer-note">完全离线 · 无外部脚本 · 8 个合成案例 · 结果只在声明范围内有效</div>
</main>
<script>const DATA={data_json};
const $=id=>document.getElementById(id);const esc=s=>String(s??'').replace(/[&<>"']/g,m=>({{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}}[m]));
function label(k){{return k.replaceAll('_',' ')}}
function render(i){{const d=DATA[i];$('title').textContent=d.title;$('meta').innerHTML=`<span class="tag">${{esc(d.id)}}</span><span class="tag">${{esc(d.channel)}}</span><span class="tag">${{esc(d.content_type)}}</span>`;$('disp').textContent=d.plan.disposition;$('text').textContent=d.text;
$('profile').innerHTML=Object.entries(d.profile).map(([k,v])=>`<div class="metric"><div class="metric-row"><span>${{esc(label(k))}}</span><b>${{Number(v).toFixed(3)}}</b></div><div class="bar"><span style="width:${{Math.round(Number(v)*100)}}%"></span></div></div>`).join('');
$('claims').innerHTML=d.truth.claim_statuses.length?d.truth.claim_statuses.map(c=>`<div class="claim"><b>${{esc(c.claim_id)}}</b> <span class="status">${{esc(c.status)}}</span><div>evidence=${{c.evidence_quality===null?'—':Number(c.evidence_quality).toFixed(3)}} · mismatch=${{Number(c.certainty_mismatch).toFixed(3)}}</div></div>`).join(''):'<div class="claim">No factual claim submitted; interface design and incentive paths are assessed separately.</div>';
$('actions').innerHTML=d.plan.actions.map(a=>`<div class="action"><span class="level">${{esc(a.level)}} · target=${{esc(a.target)}}</span><strong>${{esc(a.action_type)}}</strong><p>${{esc(a.detail)}}</p><small>owner=${{esc(a.owner)}} · expiry=${{a.expiry_hours}}h · reversible=${{a.reversible}} · appeal=${{a.appeal_available}} · automatic=${{a.automatic_execution}}</small></div>`).join('');
const m=d.models;$('models').innerHTML=[['WM-EVIDENCE',`quality=${{m.evidence.mean_evidence_quality}} · deficit=${{m.evidence.max_evidence_deficit}} · provenance deficit=${{m.evidence.provenance_deficit}}`],['WM-MANIPULATION',`pressure=${{m.manipulation.manipulation_pressure}} · addiction=${{m.manipulation.addictive_design}} · commercial=${{m.manipulation.commercial_conflict}}`],['WM-HARM-RIGHTS',`harm=${{m.harm_and_rights.potential_harm}} · autonomy=${{m.harm_and_rights.autonomy_risk}} · suppression protection=${{m.harm_and_rights.suppression_protection}}`]].map(x=>`<div class="model"><b>${{x[0]}}</b><br><code>${{esc(x[1])}}</code></div>`).join('');
$('disagreement').innerHTML='<ul>'+d.model_disagreement.observations.map(x=>`<li>${{esc(x)}}</li>`).join('')+'</ul>';
if(d.support.applicable){{$('support').innerHTML=`<b>${{esc(d.support.mode)}}</b><ol class="steps">${{d.support.steps.map(s=>`<li><b>${{esc(s.name)}}</b>：${{esc(s.instruction)}}</li>`).join('')}}</ol><p><b>下一步：</b>${{esc(d.support.next_action)}}</p>`}}else{{$('support').innerHTML='<p>此案例未登记为现实生活支持场景。</p>'}}
$('semantic').innerHTML=`<p>closure vector: <b>${{d.semantic.closure_vector}}</b> · records=${{d.semantic.records}} · actual routes=${{d.semantic.routes}} · allowed route types=25</p>`;
$('residuals').innerHTML='<h3>开放余量 / 现实债务</h3><ul>'+d.residual.open_items.map(r=>`<li><b>${{esc(r.type)}}</b>：${{esc(r.description)}}</li>`).join('')+'</ul>';
$('cert').innerHTML=`<h3>证书</h3><p><code>${{esc(d.certificate.certificate_id)}}</code></p><p>run hash: <code>${{esc(d.certificate.run_hash.slice(0,24))}}…</code></p>`;$('scenario').value=String(i);}}
$('scenario').innerHTML=DATA.map((d,i)=>`<option value="${{i}}">${{esc(d.id+' · '+d.title)}}</option>`).join('');$('scenario').onchange=e=>render(Number(e.target.value));$('next').onclick=()=>{{let i=(Number($('scenario').value)+1)%DATA.length;render(i)}};render(0);
</script></body></html>'''
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(_ui_localize_html(html_text), encoding="utf-8")
    print(OUT)


if __name__ == "__main__":
    main()
