"""
Data-driven income-tax calculator generator.

Reads calculators/data/income_tax.json (the single, audited source of tax truth)
and renders one accurate calculator page per country plus a hub index and sitemap
into calculators/site/. Add a verified country to the JSON and re-run — no
hand-built HTML, so accuracy lives in one reviewable place.

    python calculators/build.py
"""
import json
import os
from datetime import date

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data", "income_tax.json")
OUT = os.path.join(HERE, "site")
BASE_URL = "https://example.com"  # replace with the real domain at deploy time

# green -> clay heat ramp; higher bands read "hotter"
RAMP = ["#2E8B6B", "#5F9A54", "#8B9C45", "#C0983A", "#C67C38", "#BD6230", "#B0492A"]


def band_colors(n):
    if n <= 1:
        return [RAMP[0]]
    return [RAMP[round(i * (len(RAMP) - 1) / (n - 1))] for i in range(n)]


def compute_annual(taxable, bands, credit):
    gross, lower, slices = 0.0, 0.0, []
    for up_to, rate in bands:
        top = float("inf") if up_to is None else up_to
        if taxable > lower:
            amt = min(taxable, top) - lower
            tax = amt * rate / 100.0
            gross += tax
            slices.append((rate, amt, tax))
            lower = top
        else:
            break
    return gross, max(0.0, gross - credit), slices


def money(sym, n):
    return f"{sym} {round(n):,}"


def render_country(slug, c):
    bands = c["bands"]
    credit = sum(x["annual"] for x in c.get("credits", []))
    colors = band_colors(len(bands))
    sym = c["symbol"]

    # worked example
    ex = c.get("example_annual", 600000)
    ex_gross, ex_net, ex_slices = compute_annual(ex, bands, credit)

    # bands table rows
    def band_range(i):
        lo = 0 if i == 0 else bands[i - 1][0]
        hi = bands[i][0]
        lo_s = f"{lo:,}"
        return f"{lo_s} – {hi:,}" if hi is not None else f"Above {lo:,}"
    band_rows = "\n".join(
        f'<tr><td>{band_range(i)}</td><td>{r}%</td></tr>' for i, (_, r) in enumerate(bands)
    )

    # worked example rows
    ex_rows = ""
    for rate, amt, tax in ex_slices:
        ex_rows += f'<tr><td>{rate}%</td><td>{round(amt):,}</td><td>{tax:,.0f}</td></tr>'
    ex_rows += f'<tr><td>Gross tax</td><td></td><td>{ex_gross:,.0f}</td></tr>'
    if credit:
        ex_rows += f'<tr><td>Less {c["credits"][0]["label"].lower()}</td><td></td><td>−{credit:,.0f}</td></tr>'
    ex_rows += f'<tr><td><strong>Income tax</strong></td><td></td><td><strong>{ex_net:,.0f}</strong></td></tr>'

    # deduction fields
    dfields = ""
    for d in c.get("deductions", []):
        dfields += (
            f'<div class="field"><label for="d-{d["id"]}">{d["label"]} '
            f'<span class="hint">{d["hint"]}</span></label>'
            f'<div class="control"><span class="prefix">{sym}</span>'
            f'<input id="d-{d["id"]}" class="num" inputmode="numeric" value="0" autocomplete="off"></div></div>'
        )
    adv = ""
    if dfields:
        adv = f'<details class="adv"><summary>Add pension &amp; deductions</summary>{dfields}</details>'

    notes = "".join(f"<li>{n}</li>" for n in c.get("notes", []))
    credit_label = c["credits"][0]["label"] if credit else None

    cfg = {
        "symbol": sym, "currency": c["currency"],
        "bands": [[b[0], b[1]] for b in bands],
        "credit": credit, "creditLabel": credit_label,
        "colors": colors,
        "deductions": [{"id": d["id"], "kind": d["kind"]} for d in c.get("deductions", [])],
    }

    default_period = "month"
    ex_net_month = ex_net / 12
    repl = {
        "{{SLUG}}": slug, "{{COUNTRY}}": c["name"], "{{CURRENCY}}": c["currency"],
        "{{SYMBOL}}": sym, "{{TAX_YEAR}}": c["tax_year"],
        "{{SOURCE}}": c["source"], "{{SOURCE_URL}}": c["source_url"], "{{VERIFIED}}": c["verified"],
        "{{CANONICAL}}": f"{BASE_URL}/{slug}/income-tax-calculator/",
        "{{BANDS_ROWS}}": band_rows, "{{EX_ROWS}}": ex_rows,
        "{{EX_ANNUAL}}": f"{ex:,}", "{{DEDUCTION_BLOCK}}": adv, "{{NOTES}}": notes,
        "{{DEFAULT_NET}}": money(sym, ex_net_month), "{{DEFAULT_NET_YEAR}}": money(sym, ex_net),
        "{{DEFAULT_GROSS}}": f"{round(ex/12):,}",
        "{{CFG_JSON}}": json.dumps(cfg),
    }
    html = TEMPLATE
    for k, v in repl.items():
        html = html.replace(k, str(v))
    return html


def render_index(countries):
    cards = ""
    for slug, c in countries.items():
        bands_n = len(c["bands"])
        cards += (
            f'<a class="hub-card" href="/{slug}/income-tax-calculator/">'
            f'<span class="flag">{c["name"]}</span>'
            f'<span class="hub-t">{c["name"]} Income Tax Calculator</span>'
            f'<span class="hub-s">{bands_n} bands · {c["currency"]} · tax year {c["tax_year"]}</span>'
            f'<span class="hub-v">Verified {c["verified"]}</span></a>'
        )
    return INDEX_TEMPLATE.replace("{{CARDS}}", cards).replace("{{YEAR}}", str(date.today().year))


CSS = r"""
:root{
  --paper:#F6F4EF;--surface:#FFF;--ink:#1B1A16;--muted:#6A6F67;--line:#E5E1D8;
  --accent:#1E6B54;--accent-ink:#12513F;--field:#FCFBF8;
  --shadow:0 1px 2px rgba(27,26,22,.05),0 8px 24px -12px rgba(27,26,22,.18);
}
@media (prefers-color-scheme:dark){:root{
  --paper:#14140F;--surface:#1E1F19;--ink:#ECEAE1;--muted:#9AA091;--line:#2F3129;
  --accent:#47A585;--accent-ink:#7FC7AE;--field:#191A14;
  --shadow:0 1px 2px rgba(0,0,0,.3),0 10px 30px -14px rgba(0,0,0,.6);
}}
:root[data-theme="light"]{--paper:#F6F4EF;--surface:#FFF;--ink:#1B1A16;--muted:#6A6F67;--line:#E5E1D8;--accent:#1E6B54;--accent-ink:#12513F;--field:#FCFBF8;--shadow:0 1px 2px rgba(27,26,22,.05),0 8px 24px -12px rgba(27,26,22,.18)}
:root[data-theme="dark"]{--paper:#14140F;--surface:#1E1F19;--ink:#ECEAE1;--muted:#9AA091;--line:#2F3129;--accent:#47A585;--accent-ink:#7FC7AE;--field:#191A14;--shadow:0 1px 2px rgba(0,0,0,.3),0 10px 30px -14px rgba(0,0,0,.6)}
*{box-sizing:border-box}
body{margin:0;background:var(--paper);color:var(--ink);font-family:system-ui,-apple-system,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;line-height:1.6;-webkit-font-smoothing:antialiased}
.wrap{max-width:760px;margin:0 auto;padding:28px 20px 80px}
.serif{font-family:"Iowan Old Style","Palatino Linotype",Palatino,Georgia,"Times New Roman",serif}
.num{font-variant-numeric:tabular-nums;font-feature-settings:"tnum" 1}
.eyebrow{font-size:12px;letter-spacing:.12em;text-transform:uppercase;color:var(--accent-ink);font-weight:600;margin:0 0 10px;display:flex;gap:8px;align-items:center;flex-wrap:wrap}
.eyebrow .dot{width:4px;height:4px;border-radius:50%;background:currentColor;opacity:.5}
h1{font-size:clamp(27px,5vw,38px);line-height:1.12;margin:0 0 12px;font-weight:600;letter-spacing:-.01em;text-wrap:balance}
.lede{font-size:17px;color:var(--muted);margin:0 0 26px;max-width:60ch}
.theme-btn{position:absolute;top:20px;right:20px;background:var(--surface);color:var(--muted);border:1px solid var(--line);border-radius:999px;padding:7px 14px;font:inherit;font-size:13px;cursor:pointer}
.theme-btn:hover{color:var(--ink)}
.card{background:var(--surface);border:1px solid var(--line);border-radius:16px;box-shadow:var(--shadow);overflow:hidden}
.calc{display:grid;grid-template-columns:1fr;gap:0}
@media(min-width:640px){.calc{grid-template-columns:minmax(0,1fr) minmax(0,1.05fr)}}
.inputs{padding:24px 22px;border-bottom:1px solid var(--line)}
@media(min-width:640px){.inputs{border-bottom:none;border-right:1px solid var(--line)}}
.result{padding:24px 22px;background:linear-gradient(180deg,color-mix(in srgb,var(--accent) 6%,var(--surface)),var(--surface))}
.field{margin:0 0 16px}.field:last-child{margin-bottom:0}
label{display:block;font-size:13px;font-weight:600;margin:0 0 6px;color:var(--ink)}
.hint{font-weight:400;color:var(--muted);font-size:12px}
.control{display:flex;align-items:stretch;border:1px solid var(--line);border-radius:10px;background:var(--field);overflow:hidden;transition:border-color .15s,box-shadow .15s}
.control:focus-within{border-color:var(--accent);box-shadow:0 0 0 3px color-mix(in srgb,var(--accent) 22%,transparent)}
.control .prefix{display:flex;align-items:center;padding:0 12px;color:var(--muted);font-size:14px;border-right:1px solid var(--line);background:color-mix(in srgb,var(--ink) 3%,transparent)}
.control input{border:0;background:transparent;color:var(--ink);font:inherit;font-size:16px;padding:11px 12px;width:100%;outline:none;font-weight:600}
.seg{display:inline-flex;background:var(--field);border:1px solid var(--line);border-radius:10px;padding:3px;gap:2px}
.seg button{border:0;background:transparent;color:var(--muted);font:inherit;font-size:13px;font-weight:600;padding:7px 14px;border-radius:7px;cursor:pointer}
.seg button[aria-pressed="true"]{background:var(--accent);color:#fff}
@media (prefers-color-scheme:dark){.seg button[aria-pressed="true"]{color:#0d130f}}
:root[data-theme="dark"] .seg button[aria-pressed="true"]{color:#0d130f}
:root[data-theme="light"] .seg button[aria-pressed="true"]{color:#fff}
details.adv{margin-top:16px;border-top:1px dashed var(--line);padding-top:14px}
details.adv>summary{cursor:pointer;font-size:13px;font-weight:600;color:var(--accent-ink);list-style:none}
details.adv>summary::-webkit-details-marker{display:none}
details.adv>summary::before{content:"+ "}
details.adv[open]>summary::before{content:"– "}
details.adv .field{margin-top:14px}
.rlabel{font-size:12px;letter-spacing:.1em;text-transform:uppercase;color:var(--muted);font-weight:600;margin:0}
.big{font-size:clamp(34px,8vw,46px);font-weight:700;letter-spacing:-.02em;line-height:1;margin:6px 0 2px}
.sub{color:var(--muted);font-size:14px;margin:0}
.pill{display:inline-flex;align-items:center;gap:6px;margin-top:14px;background:color-mix(in srgb,var(--accent) 12%,transparent);color:var(--accent-ink);border-radius:999px;padding:5px 12px;font-size:13px;font-weight:600}
.bar{display:flex;height:14px;border-radius:7px;overflow:hidden;margin:20px 0 6px;background:color-mix(in srgb,var(--ink) 6%,transparent)}
.bar span{display:block;height:100%}
.legend{display:flex;flex-wrap:wrap;gap:4px 14px;font-size:12px;color:var(--muted)}
.legend .k{display:inline-flex;align-items:center;gap:6px}
.sw{width:9px;height:9px;border-radius:2px;display:inline-block}
.break{margin:18px 0 0;width:100%;border-collapse:collapse;font-size:13.5px}
.break th,.break td{text-align:right;padding:7px 4px;border-bottom:1px solid var(--line)}
.break th:first-child,.break td:first-child{text-align:left}
.break thead th{font-size:11px;letter-spacing:.06em;text-transform:uppercase;color:var(--muted);font-weight:600}
.break tfoot td{font-weight:700;border-bottom:none;padding-top:10px}
.break .relief td{color:var(--accent-ink)}
.break .band td:first-child{display:flex;align-items:center;gap:8px}
section.doc{margin-top:44px}
section.doc h2{font-size:22px;margin:34px 0 12px;font-weight:600;letter-spacing:-.01em}
section.doc h2:first-of-type{margin-top:0}
section.doc p{margin:0 0 14px;max-width:65ch}
section.doc ul{color:var(--muted);padding-left:20px;max-width:65ch}section.doc li{margin:0 0 8px}
.tbl{width:100%;overflow-x:auto}
table.bands{width:100%;border-collapse:collapse;font-size:14px;min-width:360px}
table.bands th,table.bands td{padding:9px 10px;border-bottom:1px solid var(--line);text-align:right}
table.bands th:first-child,table.bands td:first-child{text-align:left}
table.bands thead th{font-size:11px;letter-spacing:.06em;text-transform:uppercase;color:var(--muted);font-weight:600}
.updated{display:inline-flex;gap:8px;align-items:center;font-size:12.5px;color:var(--muted);border:1px solid var(--line);border-radius:999px;padding:5px 12px}
.updated b{color:var(--accent-ink);font-weight:600}
.src{font-size:13px;color:var(--muted)}.src a{color:var(--accent-ink)}
footer{margin-top:40px;padding-top:18px;border-top:1px solid var(--line);font-size:12.5px;color:var(--muted)}
a{color:var(--accent-ink)}
:focus-visible{outline:2px solid var(--accent);outline-offset:2px;border-radius:4px}
"""

TEMPLATE = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{{COUNTRY}} Income Tax Calculator ({{TAX_YEAR}}) — Bands &amp; Reliefs</title>
<meta name="description" content="Calculate {{COUNTRY}} income tax for {{TAX_YEAR}} using the current verified bands, with a live band-by-band breakdown of exactly where your tax comes from. Source: {{SOURCE}}.">
<link rel="canonical" href="{{CANONICAL}}">
<style>__CSS__</style>
</head>
<body>
<button class="theme-btn" id="themeBtn" type="button" aria-label="Toggle light or dark theme">Theme</button>
<main class="wrap">
  <p class="eyebrow">{{COUNTRY}} <span class="dot"></span> Income tax <span class="dot"></span> Tax year {{TAX_YEAR}}</p>
  <h1 class="serif">{{COUNTRY}} Income Tax Calculator</h1>
  <p class="lede">Enter your gross pay to see your {{COUNTRY}} income tax for {{TAX_YEAR}} on the current bands — and exactly which band each unit of income is taxed in.</p>
  <div class="card"><div class="calc">
    <div class="inputs">
      <div class="field">
        <label for="gross">Gross pay <span class="hint">before tax</span></label>
        <div class="control"><span class="prefix">{{SYMBOL}}</span><input id="gross" class="num" inputmode="numeric" value="{{DEFAULT_GROSS}}" autocomplete="off"></div>
      </div>
      <div class="field">
        <label>Pay period</label>
        <div class="seg" role="group" aria-label="Pay period">
          <button type="button" data-period="month" aria-pressed="true">Monthly</button>
          <button type="button" data-period="year" aria-pressed="false">Annual</button>
        </div>
      </div>
      {{DEDUCTION_BLOCK}}
    </div>
    <div class="result" aria-live="polite">
      <p class="rlabel">Income tax</p>
      <p class="big num" id="netMain">{{DEFAULT_NET}}</p>
      <p class="sub"><span class="num" id="netAlt">{{DEFAULT_NET_YEAR}}</span> <span id="altLabel">per year</span></p>
      <span class="pill">Effective rate <span class="num" id="effRate">–</span></span>
      <div class="bar" id="bar" role="img" aria-label="Share of income taxed in each band"></div>
      <div class="legend" id="legend"></div>
      <table class="break">
        <thead><tr><th>Band</th><th>Income in band <span class="hint">(annual)</span></th><th>Tax</th></tr></thead>
        <tbody id="rows"></tbody>
        <tfoot id="foot"></tfoot>
      </table>
    </div>
  </div></div>
  <p style="margin:16px 2px 0"><span class="updated">Rates <b>verified {{VERIFIED}}</b> · {{SOURCE}}</span></p>

  <section class="doc">
    <h2 class="serif">{{COUNTRY}} income tax bands for {{TAX_YEAR}}</h2>
    <p>{{COUNTRY}} taxes income progressively: each band's rate applies only to the income that falls within it, not to your whole salary. Figures below are annual taxable-income thresholds in {{CURRENCY}}.</p>
    <div class="tbl"><table class="bands"><thead><tr><th>Annual income ({{CURRENCY}})</th><th>Rate</th></tr></thead><tbody class="num">{{BANDS_ROWS}}</tbody></table></div>
    <h2 class="serif">Worked example — {{SYMBOL}} {{EX_ANNUAL}} a year</h2>
    <div class="tbl"><table class="bands num"><thead><tr><th>Band</th><th>Income taxed</th><th>Tax</th></tr></thead><tbody>{{EX_ROWS}}</tbody></table></div>
    <h2 class="serif">Notes</h2>
    <ul>{{NOTES}}</ul>
    <h2 class="serif">Source</h2>
    <p class="src">Bands and reliefs verified against <a href="{{SOURCE_URL}}" rel="nofollow noopener">{{SOURCE}}</a> on {{VERIFIED}}. Confirm your own position with the tax authority or a licensed adviser before acting.</p>
  </section>
  <footer>{{COUNTRY}} income tax for the {{TAX_YEAR}} tax year, for general information only — not tax advice.</footer>
</main>
<script>
const CFG=__CFG__;
const el=id=>document.getElementById(id);
let period='month';
const parseNum=v=>{const n=parseFloat(String(v).replace(/[^0-9.]/g,''));return isNaN(n)?0:n;};
const fmt=n=>Math.round(n).toLocaleString('en-US');
const money=n=>CFG.symbol+' '+fmt(n);
function compute(taxable){
  let gross=0,lower=0;const slices=[];
  for(let i=0;i<CFG.bands.length;i++){
    const up=CFG.bands[i][0], rate=CFG.bands[i][1]/100, top=(up===null?Infinity:up);
    if(taxable>lower){const amt=Math.min(taxable,top)-lower;gross+=amt*rate;slices.push({i,rate:CFG.bands[i][1],amt,tax:amt*rate});lower=top;}else break;
  }
  return {gross,net:Math.max(0,gross-CFG.credit),slices};
}
function render(){
  const grossIn=parseNum(el('gross').value);
  const grossAnnual=period==='month'?grossIn*12:grossIn;
  let deduct=0;
  for(const d of CFG.deductions){
    const v=parseNum((el('d-'+d.id)||{}).value||0);
    if(d.kind==='rent20cap500k') deduct+=Math.min(v*0.2,500000);
    else deduct+=(period==='month'?v*12:v);
  }
  const taxable=Math.max(0,grossAnnual-deduct);
  const r=compute(taxable);
  const netAnnual=r.net, netMonth=r.net/12;
  if(period==='month'){el('netMain').textContent=money(netMonth);el('netAlt').textContent=money(netAnnual);el('altLabel').textContent='per year';}
  else{el('netMain').textContent=money(netAnnual);el('netAlt').textContent=money(netMonth);el('altLabel').textContent='per month';}
  el('effRate').textContent=(grossAnnual>0?(netAnnual/grossAnnual*100):0).toFixed(1)+'%';
  // bar
  const bar=el('bar'),legend=el('legend');bar.innerHTML='';legend.innerHTML='';
  const base=Math.max(grossAnnual,taxable,1);
  r.slices.forEach(s=>{
    if(s.amt<=0)return;
    const seg=document.createElement('span');seg.style.width=(s.amt/base*100)+'%';seg.style.background=CFG.colors[s.i];seg.title=s.rate+'% band: '+money(s.amt);bar.appendChild(seg);
    const k=document.createElement('span');k.className='k';k.innerHTML='<span class="sw" style="background:'+CFG.colors[s.i]+'"></span>'+s.rate+'%';legend.appendChild(k);
  });
  const untaxed=Math.max(0,grossAnnual-taxable);
  if(untaxed>1){const seg=document.createElement('span');seg.style.width=(untaxed/base*100)+'%';seg.style.background='color-mix(in srgb,var(--ink) 12%,transparent)';seg.title='Deductions / allowances';bar.appendChild(seg);}
  // breakdown (annual)
  const rows=el('rows');rows.innerHTML='';
  r.slices.forEach(s=>{const tr=document.createElement('tr');tr.className='band';tr.innerHTML='<td><span class="sw" style="background:'+CFG.colors[s.i]+'"></span>'+s.rate+'%</td><td class="num">'+fmt(s.amt)+'</td><td class="num">'+fmt(s.tax)+'</td>';rows.appendChild(tr);});
  const foot=el('foot');foot.innerHTML='';
  if(CFG.credit>0){foot.innerHTML+='<tr class="relief"><td>Less '+CFG.creditLabel.toLowerCase()+'</td><td></td><td class="num">−'+fmt(CFG.credit)+'</td></tr>';}
  foot.innerHTML+='<tr><td>Income tax payable</td><td></td><td class="num">'+fmt(netAnnual)+'</td></tr>';
}
['gross',...CFG.deductions.map(d=>'d-'+d.id)].forEach(id=>{const inp=el(id);if(!inp)return;inp.addEventListener('input',()=>{const raw=inp.value.replace(/[^0-9.]/g,'');const p=raw.split('.');let out=p[0]?parseInt(p[0],10).toLocaleString('en-US'):'';if(p.length>1)out+='.'+p[1];inp.value=out;render();});});
document.querySelectorAll('.seg button').forEach(b=>b.addEventListener('click',()=>{period=b.dataset.period;document.querySelectorAll('.seg button').forEach(x=>x.setAttribute('aria-pressed',x===b?'true':'false'));render();}));
const root=document.documentElement;
el('themeBtn').addEventListener('click',()=>{const cur=root.getAttribute('data-theme')||(matchMedia('(prefers-color-scheme:dark)').matches?'dark':'light');root.setAttribute('data-theme',cur==='dark'?'light':'dark');});
render();
</script>
</body>
</html>
"""

INDEX_TEMPLATE = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Income Tax Calculators by Country — Verified Bands</title>
<meta name="description" content="Accurate, verified income-tax calculators by country, each with a live band-by-band breakdown and cited sources.">
<style>__CSS__
.hub{display:grid;gap:14px;grid-template-columns:1fr}
@media(min-width:620px){.hub{grid-template-columns:1fr 1fr}}
.hub-card{display:flex;flex-direction:column;gap:4px;text-decoration:none;color:var(--ink);background:var(--surface);border:1px solid var(--line);border-radius:14px;padding:18px 20px;box-shadow:var(--shadow);transition:transform .12s,border-color .12s}
.hub-card:hover{transform:translateY(-2px);border-color:var(--accent)}
.flag{font-size:12px;letter-spacing:.1em;text-transform:uppercase;color:var(--accent-ink);font-weight:600}
.hub-t{font-size:18px;font-weight:600}
.hub-s{font-size:13px;color:var(--muted)}
.hub-v{font-size:12px;color:var(--muted);margin-top:2px}
</style>
</head>
<body>
<button class="theme-btn" id="themeBtn" type="button" aria-label="Toggle theme">Theme</button>
<main class="wrap">
  <p class="eyebrow">Verified <span class="dot"></span> Income tax <span class="dot"></span> By country</p>
  <h1 class="serif">Income Tax Calculators</h1>
  <p class="lede">Accurate income-tax calculators built from officially-sourced bands — each one shows a live band-by-band breakdown and cites where its rates come from. No guessed numbers, no stale brackets.</p>
  <div class="hub">{{CARDS}}</div>
  <footer>General information only, not tax advice. Each calculator cites and links its source. © {{YEAR}}</footer>
</main>
<script>
const root=document.documentElement;
document.getElementById('themeBtn').addEventListener('click',()=>{const c=root.getAttribute('data-theme')||(matchMedia('(prefers-color-scheme:dark)').matches?'dark':'light');root.setAttribute('data-theme',c==='dark'?'light':'dark');});
</script>
</body>
</html>
"""


def main():
    data = json.load(open(DATA, encoding="utf-8"))
    countries = data["countries"]
    os.makedirs(OUT, exist_ok=True)
    urls = [f"{BASE_URL}/"]
    for slug, c in countries.items():
        html = render_country(slug, c).replace("__CSS__", CSS).replace("__CFG__", repl_cfg(slug, c))
        d = os.path.join(OUT, slug, "income-tax-calculator")
        os.makedirs(d, exist_ok=True)
        open(os.path.join(d, "index.html"), "w", encoding="utf-8").write(html)
        urls.append(f"{BASE_URL}/{slug}/income-tax-calculator/")
        print(f"  built {slug}/income-tax-calculator/")
    open(os.path.join(OUT, "index.html"), "w", encoding="utf-8").write(
        render_index(countries).replace("__CSS__", CSS))
    today = date.today().isoformat()
    sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    sm += "".join(f"  <url><loc>{u}</loc><lastmod>{today}</lastmod></url>\n" for u in urls)
    sm += "</urlset>\n"
    open(os.path.join(OUT, "sitemap.xml"), "w", encoding="utf-8").write(sm)
    print(f"\nBuilt {len(countries)} calculators + index + sitemap into {OUT}")


def repl_cfg(slug, c):
    # returns the JSON string for CFG for this country (kept out of render_country to
    # avoid double-escaping through the placeholder pass)
    bands = c["bands"]
    credit = sum(x["annual"] for x in c.get("credits", []))
    cfg = {
        "symbol": c["symbol"], "currency": c["currency"],
        "bands": [[b[0], b[1]] for b in bands],
        "credit": credit,
        "creditLabel": c["credits"][0]["label"] if credit else "",
        "colors": band_colors(len(bands)),
        "deductions": [{"id": d["id"], "kind": d["kind"]} for d in c.get("deductions", [])],
    }
    return json.dumps(cfg)


if __name__ == "__main__":
    main()
