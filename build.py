#!/usr/bin/env python3
"""Badge generator.

  python build.py                          rebuild all SVGs, README.md and index.html
  python build.py add "Name" COLOR ABBR [Category] [folder]
                                           add a badge, for example:
                                           python build.py add "Bun" E8B84A Bn "Web"
                                           (give a folder only for a new category)
Nothing to install: just Python 3.
"""
import json, sys, html, re
from pathlib import Path

# English names for the categories stored in badges.json (Russian originals)
CAT_EN = {"Языки": "Languages", "Игры": "Games", "Движки": "Engines", "Веб": "Web", "Мобильное и мессенджеры": "Mobile & messengers", "Инструменты и хостинг": "Tools & hosting", "Редакторы и IDE": "Editors & IDEs", "ИИ": "AI", "Базы данных": "Databases", "Облака и DevOps": "Cloud & DevOps", "ОС и железо": "OS & hardware", "Дизайн и медиа": "Design & media", "Платформы и соцсети": "Platforms & social", "Другое": "Other"}


def cat_name(name):
    return CAT_EN.get(name, name)

ROOT = Path(__file__).parent
CFG = ROOT / "badges.json"
OUT = ROOT / "badges"
# Preset colors: every badge is built in each of them (badges/colors/COLOR/...).
# You can set your own list in badges.json with the "colors" key.
DEFAULT_COLORS = ["3A9B68", "2563EB", "7C3AED", "DB2777", "DC2626", "EA580C",
                  "CA8A04", "16A34A", "0891B2", "374151", "111827", "F3F4F6"]
CHAR_W = 7.7  # character width at font-size 10, letter-spacing


def lum(hexcolor):
    h = hexcolor.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
    f = lambda c: c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b)


def load_icon(bid):
    """Icon from icons/<id>.svg: returns (content, viewBox) or None."""
    f = ROOT / "icons" / f"{bid}.svg"
    if not f.exists():
        return None
    raw = f.read_text(encoding="utf-8")
    m = re.search(r"<svg[^>]*>(.*)</svg>", raw, re.S)
    if not m:
        return None
    vb = re.search(r'viewBox="([^"]+)"', raw)
    box = [float(x) for x in vb.group(1).replace(",", " ").split()] if vb else [0, 0, 24, 24]
    body = re.sub(r"<title>.*?</title>", "", m.group(1), flags=re.S)
    return body, box


def make_svg(item, height=28, use_icon=True):
    label = item["label"].upper()
    color = item["color"].lstrip("#").upper()
    fg = "#1F1F1F" if lum(color) > 0.45 else "#FFFFFF"
    tl = round(len(label) * CHAR_W, 1)
    w = round(32 + tl + 12)
    name = html.escape(item["label"])
    inner = None
    if use_icon:
        inner = (item["svg"], [0, 0, 24, 24]) if item.get("svg") else load_icon(item["id"])
    if inner:            # real logo: drawn in the badge text color
        body, vb = inner
        sc = 14 / max(vb[2], vb[3])
        tx = 9 + (14 - vb[2] * sc) / 2 - vb[0] * sc
        ty = 7 + (14 - vb[3] * sc) / 2 - vb[1] * sc
        icon = (f'<g transform="translate({tx:.2f} {ty:.2f}) scale({sc:.4f})" fill="{fg}" color="{fg}">'
                f'{body}</g>')
    else:                # monogram badge
        icon = (f'<rect x="8" y="6" width="16" height="16" rx="3" fill="{fg}" fill-opacity="0.2"/>'
                f'<text x="16" y="17.3" fill="{fg}" font-family="Verdana,\'DejaVu Sans\',Geneva,sans-serif" '
                f'font-size="8" font-weight="bold" text-anchor="middle">{html.escape(item["icon"])}</text>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{height}" '
            f'viewBox="0 0 {w} {height}" role="img" aria-label="{name}">\n'
            f'  <title>{name}</title>\n'
            f'  <rect width="{w}" height="{height}" rx="2" fill="#{color}"/>\n'
            f'  {icon}\n'
            f'  <text x="32" y="18" fill="{fg}" font-family="Verdana,\'DejaVu Sans\',Geneva,sans-serif" '
            f'font-size="10" font-weight="bold" textLength="{tl}" lengthAdjust="spacing">{html.escape(label)}</text>\n'
            f'</svg>\n')


def urls(cfg, item, variant):
    return (f'https://raw.githubusercontent.com/{cfg["owner"]}/{cfg["repo"]}/{cfg["branch"]}'
            f'/badges/{variant}/{item["dir"]}/{item["id"]}.svg')


def snippets(cfg, item, variant):
    u = urls(cfg, item, variant)
    return {"md": f'![{item["label"]}]({u})',
            "html": f'<img src="{u}" alt="{item["label"]}" height="{cfg["height"]}" />',
            "url": u}


def build_readme(cfg):
    items = [i for c in cfg["categories"] for i in c["items"]]
    total, with_icon = len(items), sum(1 for i in items if i["has_icon"])
    pages = f'https://{cfg["owner"].lower()}.github.io/{cfg["repo"]}/'
    raw = f'https://raw.githubusercontent.com/{cfg["owner"]}/{cfg["repo"]}/{cfg["branch"]}/badges'
    h = cfg["height"]
    L = []
    L.append('# README Badges\n')
    L.append(f'**{total} ready-made badges** in one style, each available in two variants:\n')
    L.append(f'- **With icon**: the real technology logo (currently {with_icon} badges have one).')
    L.append(f'- **With letters**: a monogram of one or two letters (available for all {total}).\n')
    L.append('These are plain SVG files: they live in the repository, don\'t depend on shields.io, and never break because of "unknown icons".\n')
    L.append('## How to use\n')
    L.append(f'1. **The easiest way:** open the [gallery page]({pages}), pick a variant (with icons or with letters), '
             f'click a badge, and the code is copied to your clipboard. Paste it into your README.')
    L.append('2. **Via this README:** browse the badges in the tables below and copy a category\'s code '
             '(each category has collapsible code blocks: one badge per line, with a copy button in the corner of the block). '
             'Just delete any extra lines after pasting.')
    L.append(f'3. **Directly:** a badge link looks like `{raw}/VARIANT/CATEGORY/NAME.svg`, '
             f'where VARIANT is `with-icon` or `letters`.\n')
    L.append('To center the badges in your profile, wrap them in:\n')
    L.append('```html\n<div align="center">\n\n  <!-- paste your badges here -->\n\n</div>\n```\n')
    L.append('To make a badge a link, wrap it like this: `[![Python](badge-link)](https://python.org)`.\n')
    L.append('## Gallery\n')
    for cat in cfg["categories"]:
        L.append(f'### {cat["name"]}\n')
        L.append('| Name | With icon | With letters |')
        L.append('|---|---|---|')
        for it in cat["items"]:
            alt = html.escape(it["label"])
            let_img = f'<img src="badges/letters/{it["dir"]}/{it["id"]}.svg" alt="{alt}" height="{h}" />'
            ico_img = (f'<img src="badges/with-icon/{it["dir"]}/{it["id"]}.svg" alt="{alt}" height="{h}" />'
                       if it["has_icon"] else '—')
            L.append(f'| {alt} | {ico_img} | {let_img} |')
        L.append('')
        icon_items = [i for i in cat["items"] if i["has_icon"]]
        if icon_items:
            L.append('<details><summary><b>Code: with icons</b> (one badge per line)</summary>\n')
            L.append('```markdown')
            L += [snippets(cfg, i, "with-icon")["md"] for i in icon_items]
            L.append('```\n')
            L.append('</details>\n')
        L.append('<details><summary><b>Code: with letters</b> (one badge per line)</summary>\n')
        L.append('```markdown')
        L += [snippets(cfg, i, "letters")["md"] for i in cat["items"]]
        L.append('```\n')
        L.append('</details>\n')
    L.append('## Folder structure\n')
    L.append('```text')
    L.append('badges/')
    L.append('  with-icon/         # version with the real logo')
    for cat in cfg["categories"]:
        n = sum(1 for i in cat["items"] if i["has_icon"])
        if n:
            L.append(f'    {cat["slug"]}/'.ljust(26) + f'# {cat["name"]} ({n})')
    L.append('  letters/           # version with letters (available for all)')
    for cat in cfg["categories"]:
        L.append(f'    {cat["slug"]}/'.ljust(26) + f'# {cat["name"]} ({len(cat["items"])})')
    L.append('icons/               # source logos (SVG)')
    L.append('```\n')
    L.append('## Icons\n')
    L.append('If the `icons/` folder contains a file with the same name as a badge (for example, `icons/python.svg` for the `python` badge), '
             'an icon version is generated for it. The letters version is always generated.\n')
    L.append('To add or replace an icon: put a single-color SVG (preferably square, viewBox 24×24) '
             'at `icons/NAME.svg` and run `python build.py`. You don\'t need to set a color, the generator colors the icon itself. '
             'You can get logos from [simpleicons.org](https://simpleicons.org). Sources and licenses: `icons/NOTICE.md`.\n')
    L.append('## Add your own badge\n')
    L.append('All you need is Python 3:\n')
    L.append('```bash\npython build.py add "Bun" E8B84A Bn "Web"\n```\n')
    L.append('Parameters: name, color (HEX without `#`), 1-2 letters for the monogram, category and (for a new category) '
             'a folder name in Latin letters. The script creates the SVG and updates the README and the gallery page.\n')
    L.append('## Configuration\n')
    L.append('At the top of `badges.json` you\'ll find `owner`, `repo` and `branch`. If you named the repository '
             'differently or have a different username, change them and run `python build.py`: '
             'all links in the README and on the page will be updated.\n')
    L.append(f'The gallery page runs on GitHub Pages: *Settings → Pages → Deploy from a branch → `{cfg["branch"]}` / `(root)`*.\n')
    L.append('Every badge is built in all preset colors: `badges/colors/COLOR/VARIANT/category/name.svg`. On the gallery page click "Custom" and a color circle, and the code will use the link to the matching file. Any other color can be picked with the color picker: the page draws the badge, you download it with the "↓ SVG" button and put it in `badges/custom/` (`build.py` doesn\'t touch that folder).\n')
    return "\n".join(L)


HTML = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Badges: click and copy</title>
<style>
:root{--bg:#0d1117;--card:#161b22;--line:#30363d;--fg:#e6edf3;--mute:#8b949e;--acc:#3a9b68}
@media (prefers-color-scheme:light){:root{--bg:#f6f8fa;--card:#fff;--line:#d0d7de;--fg:#1f2328;--mute:#59636e;--acc:#2d7d54}}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--fg);font:15px/1.5 system-ui,Segoe UI,Roboto,sans-serif;padding:24px 16px 80px}
main{max-width:1000px;margin:0 auto}
h1{margin:0 0 4px;font-size:26px}
p.sub{margin:0 0 20px;color:var(--mute)}
.bar{display:flex;flex-wrap:wrap;gap:10px;align-items:center;margin-bottom:14px}
input[type=search]{flex:1 1 220px;padding:9px 12px;border-radius:8px;border:1px solid var(--line);background:var(--card);color:var(--fg);font:inherit}
.seg{display:flex;border:1px solid var(--line);border-radius:8px;overflow:hidden}
.seg button{background:var(--card);color:var(--fg);border:0;padding:9px 12px;font:inherit;cursor:pointer}
.seg button[aria-pressed=true]{background:var(--acc);color:#fff}
.chips{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:22px}
.chips button{border:1px solid var(--line);background:var(--card);color:var(--fg);border-radius:999px;padding:5px 12px;font:inherit;cursor:pointer}
.chips button[aria-pressed=true]{border-color:var(--acc);color:var(--acc)}
h2{font-size:17px;margin:26px 0 10px;color:var(--mute);font-weight:600}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:10px}
.card{display:flex;flex-direction:column;align-items:flex-start;gap:10px;padding:14px;border:1px solid var(--line);background:var(--card);border-radius:10px;cursor:pointer;text-align:left;color:var(--fg);font:inherit}
.card:hover,.card:focus-visible{border-color:var(--acc);outline:none}
.card img{max-width:100%;height:28px}
.card span{font-size:12px;color:var(--mute)}
.all{margin-left:auto}
.all button{background:var(--card);color:var(--fg);border:1px solid var(--line);border-radius:8px;padding:9px 12px;font:inherit;cursor:pointer}
#toast{position:fixed;left:50%;bottom:24px;transform:translateX(-50%) translateY(20px);background:var(--acc);color:#fff;padding:10px 18px;border-radius:8px;opacity:0;pointer-events:none;transition:.2s}
#toast.show{opacity:1;transform:translateX(-50%)}
.empty{color:var(--mute);padding:30px 0}
.colorbar{padding:10px 12px;border:1px solid var(--line);border-radius:10px;background:var(--card)}
.colorbar .lbl{color:var(--mute);font-size:13px}
#cpick{width:38px;height:34px;padding:0;border:1px solid var(--line);border-radius:6px;background:none;cursor:pointer}
#chex{width:92px;padding:8px 10px;border-radius:8px;border:1px solid var(--line);background:var(--bg);color:var(--fg);font:13px ui-monospace,Consolas,monospace;text-transform:uppercase}
.sw{display:flex;flex-wrap:wrap;gap:6px}
.sw button{width:22px;height:22px;border-radius:50%;border:2px solid var(--line);padding:0;cursor:pointer}
.sw button[aria-pressed=true]{border-color:var(--fg)}
.note{margin:-4px 0 14px;font-size:13px;color:var(--mute)}
.note code{background:var(--card);border:1px solid var(--line);border-radius:4px;padding:0 4px}
.wrap{position:relative;display:flex}
.wrap .card{width:100%}
.dl{position:absolute;right:8px;top:8px;background:var(--bg);color:var(--fg);border:1px solid var(--line);border-radius:6px;padding:2px 8px;font:12px system-ui;cursor:pointer}
.dl:hover{border-color:var(--acc)}
#dlAll{background:var(--card);color:var(--fg);border:1px solid var(--line);border-radius:8px;padding:8px 12px;font:inherit;cursor:pointer}
</style>
</head>
<body>
<main>
  <h1>Badges: click and copy</h1>
  <p class="sub">Choose a format, click a badge, and the code lands in your clipboard.</p>
  <div class="bar">
    <input type="search" id="q" placeholder="Search: python, unity, docker…" aria-label="Search">
    <div class="seg" id="vari">
      <button data-v="with-icon" aria-pressed="true">With icons</button>
      <button data-v="letters" aria-pressed="false">With letters</button>
    </div>
    <div class="seg" id="fmt">
      <button data-f="md" aria-pressed="true">Markdown</button>
      <button data-f="html" aria-pressed="false">HTML</button>
      <button data-f="url" aria-pressed="false">Link</button>
    </div>
    <div class="all"><button id="copyAll">Copy shown</button></div>
  </div>
  <div class="bar colorbar" id="colorbar">
    <span class="lbl">Badge color</span>
    <div class="seg" id="cmode">
      <button data-c="orig" aria-pressed="true">Original</button>
      <button data-c="custom" aria-pressed="false">Custom</button>
    </div>
    <input type="color" id="cpick" value="#3a9b68" aria-label="Pick a color">
    <input type="text" id="chex" maxlength="7" value="#3A9B68" spellcheck="false" aria-label="Color in HEX format">
    <div class="sw" id="sw"></div>
    <button id="dlAll" type="button" hidden>Download shown (SVG)</button>
  </div>
  <p class="note" id="cnote" hidden>This color is not among the presets (the circles above), so it is drawn right here. Click a badge to copy the code with its link, and download the file with the "↓ SVG" button: put it in the repository's <code>badges/custom/</code> folder, otherwise the link won't work.</p>
  <div class="chips" id="chips"></div>
  <div id="list"></div>
</main>
<div id="toast" role="status"></div>
<script>
const DATA = __DATA__;
let fmt = 'md', vari = 'with-icon', cat = '', q = '';
const $ = s => document.querySelector(s);
let cmode = 'orig', ccolor = '#3A9B68';
try{const st=JSON.parse(localStorage.getItem('badge-color')||'null');if(st&&/^#[0-9a-f]{6}$/i.test(st.c)){ccolor=st.c.toUpperCase();cmode=st.m==='custom'?'custom':'orig'}}catch(e){}
function saveColor(){try{localStorage.setItem('badge-color',JSON.stringify({m:cmode,c:ccolor}))}catch(e){}}
const FONT="Verdana,'DejaVu Sans',Geneva,sans-serif";
const esc=t=>String(t).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;').replace(/'/g,'&#x27;');
function lum(hex){const c=[0,2,4].map(i=>parseInt(hex.slice(i,i+2),16)/255).map(v=>v<=0.03928?v/12.92:Math.pow((v+0.055)/1.055,2.4));return 0.2126*c[0]+0.7152*c[1]+0.0722*c[2]}
function pyround(x){const r=Math.round(x);return(Math.abs(x%1)===0.5&&r%2!==0)?r-1:r}
function mkSvg(it,color,withIcon){
  const hex=color.replace('#','').toUpperCase(), label=it.label.toUpperCase();
  const fg=lum(hex)>0.45?'#1F1F1F':'#FFFFFF';
  const tl=Math.round(label.length*7.7*10)/10, w=pyround(32+tl+12), h=DATA.height;
  let icon;
  if(withIcon&&it.ibody){
    const vb=it.ivb, sc=14/Math.max(vb[2],vb[3]);
    const tx=9+(14-vb[2]*sc)/2-vb[0]*sc, ty=7+(14-vb[3]*sc)/2-vb[1]*sc;
    icon=`<g transform="translate(${tx.toFixed(2)} ${ty.toFixed(2)}) scale(${sc.toFixed(4)})" fill="${fg}" color="${fg}">${it.ibody}</g>`;
  }else{
    icon=`<rect x="8" y="6" width="16" height="16" rx="3" fill="${fg}" fill-opacity="0.2"/><text x="16" y="17.3" fill="${fg}" font-family="${FONT}" font-size="8" font-weight="bold" text-anchor="middle">${esc(it.icon)}</text>`;
  }
  const name=esc(it.label);
  return `<svg xmlns="http://www.w3.org/2000/svg" width="${w}" height="${h}" viewBox="0 0 ${w} ${h}" role="img" aria-label="${name}">\n  <title>${name}</title>\n  <rect width="${w}" height="${h}" rx="2" fill="#${hex}"/>\n  ${icon}\n  <text x="32" y="18" fill="${fg}" font-family="${FONT}" font-size="10" font-weight="bold" textLength="${tl.toFixed(1)}" lengthAdjust="spacing">${esc(label)}</text>\n</svg>\n`;
}
const dataUri=svg=>'data:image/svg+xml;charset=utf-8,'+encodeURIComponent(svg);
function useIcon(it){return vari==='with-icon'&&it.has_icon}
function vkind(it){return useIcon(it)?'with-icon':'letters'}
function fileName(it){return `${it.id}-${ccolor.slice(1)}${useIcon(it)?'':'-letters'}.svg`}
function download(it){
  const blob=new Blob([mkSvg(it,ccolor,useIcon(it))],{type:'image/svg+xml'});
  const a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download=fileName(it);
  document.body.appendChild(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(a.href),1000);
}
function inPalette(){return DATA.colors.includes(ccolor.slice(1))}
function snip(it){
  const base=`https://raw.githubusercontent.com/${DATA.owner}/${DATA.repo}/${DATA.branch}/badges/`;
  let u=`${base}${vkind(it)}/${it.dir}/${it.id}.svg`;
  if(cmode==='custom') u=inPalette()?`${base}colors/${ccolor.slice(1)}/${vkind(it)}/${it.dir}/${it.id}.svg`:`${base}custom/${fileName(it)}`;
  if(fmt==='md') return `![${it.label}](${u})`;
  if(fmt==='html') return `<img src="${u}" alt="${it.label}" height="${DATA.height}" />`;
  return u;
}
function toast(t){const e=$('#toast');e.textContent=t;e.classList.add('show');clearTimeout(toast.t);toast.t=setTimeout(()=>e.classList.remove('show'),1400)}
async function copy(text,msg){
  try{await navigator.clipboard.writeText(text)}
  catch(e){const a=document.createElement('textarea');a.value=text;document.body.appendChild(a);a.select();document.execCommand('copy');a.remove()}
  toast(msg)
}
function visible(){
  const s=q.trim().toLowerCase();
  return DATA.categories.map(c=>({name:c.name,items:c.items.filter(i=>(!cat||c.name===cat)&&(!s||i.label.toLowerCase().includes(s)||i.id.includes(s)))})).filter(c=>c.items.length);
}
function render(){
  const vis=visible(), box=$('#list'), custom=cmode==='custom'; box.innerHTML='';
  if(!vis.length){box.innerHTML='<p class="empty">Nothing found.</p>';return}
  for(const c of vis){
    const h=document.createElement('h2');h.textContent=c.name;box.appendChild(h);
    const g=document.createElement('div');g.className='grid';
    for(const it of c.items){
      const w=document.createElement('div');w.className='wrap';
      const b=document.createElement('button');b.className='card';b.type='button';
      const src=custom?dataUri(mkSvg(it,ccolor,useIcon(it))):`badges/${vkind(it)}/${it.dir}/${it.id}.svg`;
      const hint=(vari==='with-icon'&&!it.has_icon)?'Letters only':'Click to copy';
      b.innerHTML=`<img src="${src}" alt="${esc(it.label)}"><span>${hint}</span>`;
      const own=custom&&!inPalette();
      b.onclick=()=>copy(snip(it),own?'Copied. Download the file with the ↓ SVG button':`Copied: ${it.label}`);
      w.appendChild(b);
      if(own){const d=document.createElement('button');d.className='dl';d.type='button';d.textContent='↓ SVG';d.title='Download '+fileName(it);d.onclick=()=>download(it);w.appendChild(d)}
      g.appendChild(w);
    }
    box.appendChild(g);
  }
}
function chips(){
  const w=$('#chips');
  const mk=(n,v)=>{const b=document.createElement('button');b.textContent=n;b.setAttribute('aria-pressed',cat===v);b.onclick=()=>{cat=v;chips();render()};w.appendChild(b)};
  w.innerHTML='';mk('All','');DATA.categories.forEach(c=>mk(c.name,c.name));
}
$('#q').oninput=e=>{q=e.target.value;render()};
$('#vari').onclick=e=>{const v=e.target.dataset.v;if(!v)return;vari=v;[...$('#vari').children].forEach(b=>b.setAttribute('aria-pressed',b.dataset.v===v));render()};
$('#fmt').onclick=e=>{const f=e.target.dataset.f;if(!f)return;fmt=f;[...$('#fmt').children].forEach(b=>b.setAttribute('aria-pressed',b.dataset.f===f))};
$('#copyAll').onclick=()=>{const all=visible().flatMap(c=>c.items);copy(all.map(snip).join('\n'),`Badges copied: ${all.length}`)};
let rq=0;
function later(){cancelAnimationFrame(rq);rq=requestAnimationFrame(render)}
function syncColorUI(){
  [...$('#cmode').children].forEach(b=>b.setAttribute('aria-pressed',b.dataset.c===cmode));
  $('#cpick').value=ccolor.toLowerCase();$('#chex').value=ccolor;
  const cu=cmode==='custom',own=cu&&!inPalette();$('#cnote').hidden=!own;$('#dlAll').hidden=!own;
  [...$('#sw').children].forEach(b=>b.setAttribute('aria-pressed',cu&&b.dataset.c===ccolor));
}
function setColor(c,mode){if(c)ccolor=c.toUpperCase();if(mode)cmode=mode;saveColor();syncColorUI();later()}
DATA.colors.map(c=>'#'+c).forEach(c=>{
  const b=document.createElement('button');b.type='button';b.style.background=c;b.dataset.c=c;b.title=c;b.setAttribute('aria-label',c);
  b.onclick=()=>setColor(c,'custom');$('#sw').appendChild(b);
});
$('#cmode').onclick=e=>{const c=e.target.dataset.c;if(c)setColor(null,c)};
$('#cpick').oninput=e=>setColor(e.target.value,'custom');
$('#chex').oninput=e=>{let v=e.target.value.trim();if(v[0]!=='#')v='#'+v;if(/^#[0-9a-f]{6}$/i.test(v))setColor(v,'custom')};
$('#dlAll').onclick=()=>{const all=visible().flatMap(c=>c.items);all.forEach((it,i)=>setTimeout(()=>download(it),i*200));toast(`Files downloading: ${all.length}`)};
syncColorUI();
chips();render();
</script>
</body>
</html>
"""


def prepare(cfg):
    for cat in cfg["categories"]:
        cat["name"] = cat_name(cat["name"])
        for it in cat["items"]:
            it["dir"] = cat["slug"]
            it["has_icon"] = bool(it.get("svg")) or (ROOT / "icons" / f'{it["id"]}.svg').exists()
            inner = (it["svg"], [0, 0, 24, 24]) if it.get("svg") else load_icon(it["id"])
            if inner:   # the page needs it to draw the badge in the chosen color
                it["ibody"], it["ivb"] = inner
    return cfg


def build_all():
    cfg = prepare(json.loads(CFG.read_text(encoding="utf-8")))
    OUT.mkdir(exist_ok=True)
    keep = set()

    main = set()

    def write(variant, cat, it, use_icon, color=None):
        d = (OUT / "colors" / color if color else OUT) / variant / cat["slug"]
        d.mkdir(parents=True, exist_ok=True)
        f = d / f'{it["id"]}.svg'
        item = dict(it, color=color) if color else it
        f.write_text(make_svg(item, cfg["height"], use_icon), encoding="utf-8")
        keep.add(f)
        if not color:
            main.add(f)

    colors = [c.lstrip("#").upper() for c in cfg.get("colors", DEFAULT_COLORS)]

    for cat in cfg["categories"]:
        for it in cat["items"]:
            write("letters", cat, it, False)
            if it["has_icon"]:
                write("with-icon", cat, it, True)
            for col in colors:
                write("letters", cat, it, False, col)
                if it["has_icon"]:
                    write("with-icon", cat, it, True, col)
    for f in OUT.rglob("*.svg"):   # remove stale files (including from old layouts)
        if f not in keep and f.relative_to(OUT).parts[0] != "custom":   # custom: your own files with a custom color
            f.unlink()
    for d in sorted((x for x in OUT.rglob("*") if x.is_dir()), key=lambda x: len(x.parts), reverse=True):
        if not any(d.iterdir()):
            d.rmdir()
    (ROOT / "README.md").write_text(build_readme(cfg), encoding="utf-8")
    data = {k: cfg[k] for k in ("owner", "repo", "branch", "height", "categories")}
    data["colors"] = colors
    (ROOT / "index.html").write_text(HTML.replace("__DATA__", json.dumps(data, ensure_ascii=False).replace("</", "<\\/")), encoding="utf-8")
    (ROOT / ".nojekyll").write_text("", encoding="utf-8")
    n_icon = sum(1 for k in main if k.parts[-3] == "with-icon")
    print(f"Done: {len(main)} SVGs ({n_icon} with icon, {len(main) - n_icon} with letters) "
          f"+ {len(keep) - len(main)} in {len(colors)} preset colors, README.md and index.html updated.")


def add(argv):
    if len(argv) < 3:
        sys.exit('Usage: python build.py add "Name" COLOR ABBR [Category] [folder]')
    label, color, icon = argv[0], argv[1].lstrip("#"), argv[2]
    catname = cat_name(argv[3]) if len(argv) > 3 else "Other"
    catslug = argv[4] if len(argv) > 4 else "other"
    cfg = json.loads(CFG.read_text(encoding="utf-8"))
    bid = "".join(ch if ch.isalnum() else "-" for ch in label.lower().replace("#", "sharp").replace("+", "p")).strip("-")
    cat = next((c for c in cfg["categories"] if cat_name(c["name"]) == catname), None)
    if not cat:
        cat = {"name": catname, "slug": catslug, "items": []}
        cfg["categories"].append(cat)
    cat["items"] = [i for i in cat["items"] if i["id"] != bid] + [{"id": bid, "label": label, "color": color.upper(), "icon": icon}]
    CFG.write_text(json.dumps(cfg, ensure_ascii=False, indent=2), encoding="utf-8")
    build_all()


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "add":
        add(sys.argv[2:])
    else:
        build_all()
