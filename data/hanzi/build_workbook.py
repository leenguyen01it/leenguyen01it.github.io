"""Build the Chinese character writing workbook (HSK 3.0 handwriting list, levels 1–5).

Usage (from repo root): python3 data/hanzi/build_workbook.py
Inputs: data/hanzi/strokes.json (Make Me a Hanzi strokes + decomposition, Unihan kMandarin),
        data/hanzi/hanviet.txt, radicals.txt, components.txt and the HSK vocabulary embedded in
        Tu-vung-HSK-1-5-co-vi-du.html.
"""
import html, json, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
D = json.load(open(os.path.join(HERE, 'strokes.json'), encoding='utf-8'))


def pairs(path):
    out = {}
    for line in open(os.path.join(HERE, path), encoding='utf-8'):
        for p in line.strip().split('|'):
            if p:
                c, r = p.split(' ', 1)
                out[c] = r
    return out


HV = pairs('hanviet.txt')
RAD = pairs('radicals.txt')
COMP = pairs('components.txt')
hsk = open(os.path.join(ROOT, 'Tu-vung-HSK-1-5-co-vi-du.html'), encoding='utf-8').read()
VOCAB = json.loads(re.search(r'const DATA=(\[.*?\]);', hsk, re.S).group(1))
esc = html.escape
T = 'transform="scale(1,-1) translate(0,-900)"'
IDC = set('⿰⿱⿲⿳⿴⿵⿶⿷⿸⿹⿺⿻？')


def examples(c, n=2):
    ws = [w for w in VOCAB if c in w['h']]
    ws.sort(key=lambda w: (w['h'] != c, w['lv'], len(w['h'])))
    return ws[:n]


def name(comp):
    """Readable label for a component: radical name, else Han-Viet reading."""
    if comp in RAD:
        return f'{comp} {RAD[comp].split(" (")[0]}'
    if comp in HV:
        return f'{comp} {HV[comp].capitalize()}'
    if comp in COMP:
        return f'{comp} {COMP[comp].split(" (")[0]}'
    return comp


def structure(c):
    d = D['dic'][c]
    r = d['r']
    rad = f'Bộ <b>{esc(r)}</b> {esc(RAD.get(r, ""))}' if r else ''
    e = d['e']
    if e.get('type') == 'pictophonetic' and e.get('semantic') and e.get('phonetic'):
        comp = f'Hình thanh: <b>{esc(name(e["semantic"]))}</b> chỉ nghĩa + <b>{esc(name(e["phonetic"]))}</b> gợi âm'
    else:
        parts = [x for x in (d['d'] or '') if x not in IDC]
        comp = ('Gồm: ' + ' + '.join(f'<b>{esc(name(p))}</b>' for p in parts)) if len(parts) > 1 else ''
    return ' · '.join(x for x in (rad, comp) if x)


def stroke_defs(c):
    cp = f'{ord(c):x}'
    g = D['glyph'][c]
    paths = ''.join(f'<path id="s{cp}_{i}" d="{s}"/>' for i, s in enumerate(g['s']))
    glyph = f'<g id="g{cp}" {T}>' + ''.join(f'<use href="#s{cp}_{i}"/>' for i in range(len(g['s']))) + '</g>'
    return paths + glyph


def strip(c):
    """One small box per stroke: earlier strokes dark, current stroke red."""
    cp = f'{ord(c):x}'
    n = len(D['glyph'][c]['s'])
    boxes = ''
    for k in range(n):
        uses = ''.join(f'<use href="#s{cp}_{i}" class="{"cur" if i == k else "prev"}"/>' for i in range(k + 1))
        boxes += f'<svg class="sb" viewBox="0 0 1024 1024"><g {T}>{uses}</g></svg>'
    return f'<div class="strip">{boxes}</div>'


def order_fig(c):
    cp = f'{ord(c):x}'
    nums = ''
    for i, (x, y) in enumerate(D['glyph'][c]['m']):
        yy = 900 - y
        nums += f'<circle cx="{x}" cy="{yy}" r="68" class="nb"/><text x="{x}" y="{yy + 34}" class="nt">{i + 1}</text>'
    return f'<svg class="order" viewBox="0 0 1024 1024"><use href="#g{cp}" class="ink"/>{nums}</svg>'


LEVELS = {2: ('HSK 1–2', '#2a9d8f'), 3: ('HSK 3', '#5a8f29'), 4: ('HSK 4', '#7b61ff'), 5: ('HSK 5', '#c2185b')}
defs, blocks = [], []
for idx, (lv, c) in enumerate(D['order'], 1):
    cp = f'{ord(c):x}'
    defs.append(stroke_defs(c))
    ex = ' · '.join(f'<b>{esc(w["h"])}</b> <i>{esc(w["py"])}</i> {esc(w["vi"])}' for w in examples(c))
    cells = ''.join(f'<div class="cell">' + (f'<svg viewBox="0 0 1024 1024"><use href="#g{cp}" class="trace"/></svg>' if k < 4 else '') + '</div>'
                    for k in range(20))
    nm, color = LEVELS[lv]
    blocks.append(
        f'<div class="blk"><div class="info">{order_fig(c)}<div class="meta">'
        f'<div class="py">{esc(D["pinyin"].get(c, ""))}</div><div class="hv">{esc(HV[c])}</div>'
        f'<div class="ns">{len(D["glyph"][c]["s"])} nét · <span style="color:{color}">{nm}</span> · #{idx}</div></div>'
        f'<div class="st">{structure(c)}</div><div class="ex">{ex}</div></div>'
        f'<div class="right">{strip(c)}<div class="grid">{cells}</div></div></div>')

counts = {lv: sum(1 for l, _ in D['order'] if l == lv) for lv in LEVELS}
sections, pos = [], 0
for lv, (nm, color) in LEVELS.items():
    n = counts[lv]
    sections.append(f'<h2 id="lv{lv}" style="border-color:{color}">{nm} · {n} chữ</h2>' + ''.join(blocks[pos:pos + n]))
    pos += n

# ---------- intro: basic strokes and stroke-order rules ----------
STROKES = [('一', 'Ngang (横 héng)', 'kéo từ trái sang phải', '三'), ('丨', 'Sổ (竖 shù)', 'kéo từ trên xuống', '十'),
           ('丿', 'Phẩy (撇 piě)', 'từ trên phải xuống dưới trái', '八'), ('㇏', 'Mác (捺 nà)', 'từ trên trái xuống dưới phải, cuối nét đè mạnh rồi nhấc', '人'),
           ('丶', 'Chấm (点 diǎn)', 'nét ngắn, thường từ trên xuống phải', '小'), ('㇀', 'Hất (提 tí)', 'từ dưới trái hất lên trên phải', '习'),
           ('亅', 'Móc (钩 gōu)', 'cuối nét sổ/ngang móc lên', '小'), ('𠃍', 'Gập (折 zhé)', 'đang đi ngang thì gập xuống (hoặc ngược lại)', '口')]
RULES = [('Ngang trước, sổ sau', '十干'), ('Phẩy trước, mác sau', '八人'), ('Trên trước, dưới sau', '三字'),
         ('Trái trước, phải sau', '你好'), ('Ngoài trước, trong sau', '月同'), ('Vào nhà rồi đóng cửa (khung bao kín: viết khung, viết bên trong, cuối cùng đóng nét đáy)', '国日'),
         ('Giữa trước, hai bên sau (khi hai bên đối xứng)', '小'), ('Bộ 辶, 廴 bao bên dưới-trái: viết phần bên trong trước, bộ bao sau', '这建')]
st_rows = ''.join(f'<tr><td class="big">{a}</td><td><b>{b}</b></td><td>{d}</td><td class="big">{e}</td></tr>' for a, b, d, e in STROKES)
rule_rows = ''.join(f'<div class="rule"><p><b>{i + 1}. {r}</b></p>' + ''.join(f'<div class="rex"><span class="rc">{c}</span>{strip(c)}</div>' for c in cs) + '</div>'
                    for i, (r, cs) in enumerate(RULES))
intro = f'''<div class="intro">
<p class="toc"><a href="#huong-dan">Hướng dẫn</a><a href="#net">Nét cơ bản</a><a href="#quy-tac">Quy tắc thứ tự nét</a><a href="#lv2">HSK 1–2</a><a href="#lv3">HSK 3</a><a href="#lv4">HSK 4</a><a href="#lv5">HSK 5</a></p>
<h2 id="huong-dan" style="border-color:#c2185b">Hướng dẫn</h2>
<p>Vở gồm <strong>550 chữ Hán phải viết tay được</strong> theo đề cương HSK 3.0 (11/2025) từ cấp 1 đến cấp 5: 100 chữ cho HSK 1–2, mỗi cấp 3, 4, 5 thêm 150 chữ. Bài thi HSK trên giấy yêu cầu viết tay, nên những chữ này phải viết được mà không cần nhìn.</p>
<ul>
<li><strong>Ô bên trái</strong> là chữ mẫu, số màu hồng đánh dấu <strong>điểm bắt đầu của từng nét</strong>.</li>
<li><strong>Dãy ô nhỏ</strong> phía trên dòng kẻ là <strong>thứ tự viết từng nét</strong>: nét đang viết tô <span style="color:#e03131;font-weight:700">màu đỏ</span>, các nét đã viết màu đen. Hãy nhìn dãy này trước khi viết.</li>
<li><strong>Bộ thủ và cấu tạo:</strong> phần lớn chữ Hán ghép từ các bộ phận nhỏ. Chữ <em>hình thanh</em> có một phần chỉ nghĩa (thường là bộ thủ) và một phần gợi âm, ví dụ 妈 = 女 (nữ, chỉ nghĩa) + 马 (mã, gợi âm "mā"). Nhớ bộ phận giúp nhớ chữ nhanh hơn nhiều.</li>
<li><strong>Dòng ô kẻ</strong>: 4 ô đầu có chữ mờ để tô theo, các ô sau tự viết, vừa viết vừa đọc to pinyin.</li>
<li>Gợi ý: mỗi ngày 5–8 chữ mới, ôn lại chữ của 3 ngày trước bằng cách tự viết ra giấy nháp.</li>
</ul>
<h2 id="net" style="border-color:#c2185b">Các nét cơ bản</h2>
<p>Mọi chữ Hán được ghép từ một số ít nét cơ bản. Các nét phức tạp hơn (ngang gập móc, sổ cong móc…) là sự kết hợp của những nét này.</p>
<table class="strokes"><thead><tr><th>Nét</th><th>Tên</th><th>Cách viết</th><th>Có trong chữ</th></tr></thead><tbody>{st_rows}</tbody></table>
<h2 id="quy-tac" style="border-color:#c2185b">Quy tắc thứ tự nét</h2>
<p>Thứ tự nét đúng giúp viết nhanh, chữ cân đối và dễ đọc hơn. Mỗi quy tắc có ví dụ kèm dãy viết từng nét. Khi một chữ có vẻ "ngoại lệ", hãy luôn tin theo dãy viết từng nét của chữ đó trong vở.</p>
{rule_rows}
<p class="note">Nguồn: danh sách chữ viết tay theo đề cương HSK 3.0 (dữ liệu từ dự án ofou/hsk); hình chữ, thứ tự nét và cấu tạo chữ từ <a href="https://github.com/skishore/makemeahanzi">Make Me a Hanzi</a> (dựa trên phông Arphic, giấy phép Arphic Public License; dữ liệu cấu tạo theo giấy phép LGPL); pinyin từ Unicode Unihan. Âm Hán Việt và tên bộ thủ soạn tay (11/2026), có thể có chỗ chưa chuẩn. Chữ mẫu theo kiểu chữ Khải (楷体), gần với chữ viết tay.</p>
</div>'''

CSS = '''
:root{--ink:#1f2328;--muted:#5b6470;--line:#e3e6ea;--grid:#e8b4b4;--bg:#f6f7f9}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.5 "Segoe UI",Roboto,"Noto Sans","Noto Sans SC","Microsoft YaHei",sans-serif}
header{background:linear-gradient(135deg,#c2185b,#7b61ff);color:#fff;padding:36px 18px 30px;text-align:center}
header h1{margin:0 0 6px;font-size:26px} header p{margin:0;opacity:.92}
main{max-width:900px;margin:0 auto;background:#fff;padding:20px 22px 40px}
.toc a{display:inline-block;margin:0 10px 6px 0;padding:4px 12px;border:1px solid var(--line);border-radius:999px;color:var(--ink);text-decoration:none}
h2{font-size:20px;border-left:5px solid;padding:4px 0 4px 10px;margin:26px 0 12px}
table.strokes{border-collapse:collapse;width:100%}table.strokes td,table.strokes th{border-bottom:1px solid var(--line);padding:6px 8px;text-align:left}
td.big{font-size:26px;font-family:"Noto Sans SC","Microsoft YaHei",sans-serif;width:56px;text-align:center}
.rule{margin:10px 0}.rule p{margin:0 0 4px}.rex{display:flex;align-items:center;gap:8px;margin:4px 0}
.rc{font-size:24px;font-family:"Noto Sans SC","Microsoft YaHei",sans-serif;width:32px;text-align:center}
.blk{display:grid;grid-template-columns:minmax(0,30%) minmax(0,70%);gap:10px;align-items:start;border-bottom:1px solid var(--line);padding:8px 0;break-inside:avoid}
.info{display:grid;grid-template-columns:72px minmax(0,1fr);gap:4px 8px;align-items:center}
.order{width:72px;height:72px;border:1px solid var(--line);border-radius:6px;background:#fff}
.ink{fill:#333}.nb{fill:#d6336c}.nt{fill:#fff;font:bold 96px sans-serif;text-anchor:middle}
.py{font-size:16px;font-style:italic;color:#7b61ff}.hv{font-weight:700;text-transform:capitalize}
.ns{font-size:12px;color:var(--muted)}
.st,.ex{grid-column:1/3;font-size:12.5px;color:#444;line-height:1.35}.st b,.ex b{font-family:"Noto Sans SC","Microsoft YaHei",sans-serif;color:var(--ink);font-weight:600}
.strip{display:flex;flex-wrap:wrap;gap:3px;margin-bottom:5px}
.sb{width:26px;height:26px;border:1px solid #e5d3c3;border-radius:3px;background:#fff}
.prev{fill:#333}.cur{fill:#e03131}
.grid{display:grid;grid-template-columns:repeat(10,minmax(0,1fr));border-top:1.5px solid #c96;border-left:1.5px solid #c96}
.cell{aspect-ratio:1;border-right:1.5px solid #c96;border-bottom:1.5px solid #c96;position:relative;background:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100' preserveAspectRatio='none'%3E%3Cg stroke='%23e8b4b4' stroke-width='1' stroke-dasharray='4 3' vector-effect='non-scaling-stroke'%3E%3Cline x1='50' y1='0' x2='50' y2='100'/%3E%3Cline x1='0' y1='50' x2='100' y2='50'/%3E%3Cline x1='0' y1='0' x2='100' y2='100'/%3E%3Cline x1='100' y1='0' x2='0' y2='100'/%3E%3C/g%3E%3C/svg%3E") center/100% 100% no-repeat}
.cell{padding:6%}.cell svg{display:block;width:100%;height:auto}
.trace{fill:#c8c8c8}
.note{font-size:13px;color:var(--muted)}
@media (max-width:640px){main{padding:14px 12px}.blk{grid-template-columns:1fr}.sb{width:22px;height:22px}}
@page{size:A4;margin:12mm 12mm 14mm 16mm;@bottom-center{content:counter(page);font-size:9pt;color:#5b6470}}
@media print{body{background:#fff;font-size:10pt} header{background:none;color:var(--ink);padding:0 0 6mm} header h1{font-size:20pt;color:#c2185b}
  main{padding:0;max-width:none} .toc{display:none} #net{break-before:page}
  h2{margin-top:0;font-size:15pt} h2[id^="lv"]{break-before:page} .blk{padding:2mm 0} .order{width:19mm;height:19mm}.info{grid-template-columns:19mm minmax(0,1fr)}
  .st,.ex{font-size:8.3pt} .sb{width:6.2mm;height:6.2mm} .rule{break-inside:avoid}
  *{-webkit-print-color-adjust:exact;print-color-adjust:exact}}
'''

page = (f'<!DOCTYPE html>\n<html lang="vi">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        f'<title>Vở tập viết chữ Hán HSK</title>\n<style>{CSS}</style>\n</head>\n<body>\n'
        f'<svg width="0" height="0" style="position:absolute"><defs>{"".join(defs)}</defs></svg>\n'
        f'<header><h1>✍️ Vở tập viết chữ Hán HSK 1–5</h1><p>550 chữ phải viết tay theo đề cương HSK 3.0 · thứ tự từng nét · bộ thủ · âm Hán Việt · từ ví dụ</p></header>\n'
        f'<main>{intro}{"".join(sections)}</main>\n</body>\n</html>\n')
open(os.path.join(ROOT, 'Vo-tap-viet-chu-Han-HSK.html'), 'w', encoding='utf-8').write(page)
missing_rad = sorted({D['dic'][c]['r'] for c in D['glyph'] if D['dic'][c]['r'] not in RAD})
print('chars', len(D['order']), 'bytes', len(page), counts, 'radicals without name:', missing_rad)
