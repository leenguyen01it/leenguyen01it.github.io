"""Build the Chinese character writing workbook (HSK 3.0 handwriting list, levels 1–5).

Usage (from repo root): python3 data/hanzi/build_workbook.py
Inputs: data/hanzi/strokes.json (Make Me a Hanzi subset + Unihan kMandarin),
        data/hanzi/hanviet.txt, and the HSK vocabulary embedded in Tu-vung-HSK-1-5-co-vi-du.html.
"""
import html, json, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
D = json.load(open(os.path.join(HERE, 'strokes.json'), encoding='utf-8'))
HV = {}
for line in open(os.path.join(HERE, 'hanviet.txt'), encoding='utf-8'):
    for p in line.strip().split('|'):
        if p:
            c, r = p.split(' ', 1)
            HV[c] = r
hsk = open(os.path.join(ROOT, 'Tu-vung-HSK-1-5-co-vi-du.html'), encoding='utf-8').read()
VOCAB = json.loads(re.search(r'const DATA=(\[.*?\]);', hsk, re.S).group(1))


def examples(c, n=2):
    ws = [w for w in VOCAB if c in w['h']]
    ws.sort(key=lambda w: (w['h'] != c, w['lv'], len(w['h'])))
    return ws[:n]


esc = html.escape
LEVELS = {2: ('HSK 1–2', '#2a9d8f'), 3: ('HSK 3', '#5a8f29'), 4: ('HSK 4', '#7b61ff'), 5: ('HSK 5', '#c2185b')}
T = 'transform="scale(1,-1) translate(0,-900)"'

defs, blocks = [], []
idx = 0
for lv, c in D['order']:
    g = D['glyph'][c]
    gid = f'g{ord(c):x}'
    defs.append(f'<g id="{gid}" {T}>' + ''.join(f'<path d="{s}"/>' for s in g['s']) + '</g>')
    # stroke-order figure: strokes in ink, numbers at each stroke's start point
    nums = ''
    for i, (x, y) in enumerate(g['m']):
        yy = 900 - y
        nums += f'<circle cx="{x}" cy="{yy}" r="68" class="nb"/><text x="{x}" y="{yy + 34}" class="nt">{i + 1}</text>'
    order_svg = f'<svg class="order" viewBox="0 0 1024 1024"><use href="#{gid}" class="ink"/>{nums}</svg>'
    ex = ' · '.join(f'<b>{esc(w["h"])}</b> <i>{esc(w["py"])}</i> {esc(w["vi"])}' for w in examples(c))
    nstroke = len(g['s'])
    cells = ''
    for k in range(20):
        inner = f'<svg viewBox="0 0 1024 1024"><use href="#{gid}" class="trace"/></svg>' if k < 4 else ''
        cells += f'<div class="cell">{inner}</div>'
    idx += 1
    name, color = LEVELS[lv]
    blocks.append(
        f'<div class="blk" data-lv="{lv}"><div class="info">{order_svg}<div class="meta">'
        f'<div class="py">{esc(D["pinyin"].get(c, ""))}</div><div class="hv">{esc(HV[c])}</div>'
        f'<div class="ns">{nstroke} nét · <span style="color:{color}">{name}</span> · #{idx}</div></div>'
        f'<div class="ex">{ex}</div></div><div class="grid">{cells}</div></div>')

counts = {lv: sum(1 for l, _ in D['order'] if l == lv) for lv in LEVELS}
sections = []
pos = 0
for lv, (name, color) in LEVELS.items():
    n = counts[lv]
    sections.append(f'<h2 id="lv{lv}" style="border-color:{color}">{name} · {n} chữ</h2>' + ''.join(blocks[pos:pos + n]))
    pos += n

CSS = '''
:root{--ink:#1f2328;--muted:#5b6470;--line:#e3e6ea;--grid:#e8b4b4;--bg:#f6f7f9}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.5 "Segoe UI",Roboto,"Noto Sans","Noto Sans SC","Microsoft YaHei",sans-serif}
header{background:linear-gradient(135deg,#c2185b,#7b61ff);color:#fff;padding:36px 18px 30px;text-align:center}
header h1{margin:0 0 6px;font-size:26px} header p{margin:0;opacity:.92}
main{max-width:900px;margin:0 auto;background:#fff;padding:20px 22px 40px}
.intro p,.intro li{color:#333}
.toc a{display:inline-block;margin:0 10px 6px 0;padding:4px 12px;border:1px solid var(--line);border-radius:999px;color:var(--ink);text-decoration:none}
h2{font-size:20px;border-left:5px solid;padding:4px 0 4px 10px;margin:26px 0 12px}
.blk{display:grid;grid-template-columns:minmax(0,30%) minmax(0,70%);gap:10px;align-items:start;border-bottom:1px solid var(--line);padding:8px 0;break-inside:avoid}
.info{display:grid;grid-template-columns:72px minmax(0,1fr);gap:4px 8px;align-items:center}
.order{width:72px;height:72px;border:1px solid var(--line);border-radius:6px;background:#fff}
.ink{fill:#333}.nb{fill:#d6336c}.nt{fill:#fff;font:bold 96px sans-serif;text-anchor:middle}
.py{font-size:16px;font-style:italic;color:#7b61ff}.hv{font-weight:700;text-transform:capitalize}
.ns{font-size:12px;color:var(--muted)}
.ex{grid-column:1/3;font-size:12.5px;color:#444;line-height:1.35}.ex b{font-family:"Noto Sans SC","Microsoft YaHei",sans-serif;color:var(--ink)}
.grid{display:grid;grid-template-columns:repeat(10,minmax(0,1fr));border-top:1.5px solid #c96;border-left:1.5px solid #c96}
.cell{aspect-ratio:1;border-right:1.5px solid #c96;border-bottom:1.5px solid #c96;position:relative;background:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100' preserveAspectRatio='none'%3E%3Cg stroke='%23e8b4b4' stroke-width='1' stroke-dasharray='4 3' vector-effect='non-scaling-stroke'%3E%3Cline x1='50' y1='0' x2='50' y2='100'/%3E%3Cline x1='0' y1='50' x2='100' y2='50'/%3E%3Cline x1='0' y1='0' x2='100' y2='100'/%3E%3Cline x1='100' y1='0' x2='0' y2='100'/%3E%3C/g%3E%3C/svg%3E") center/100% 100% no-repeat}
.cell{padding:6%}.cell svg{display:block;width:100%;height:auto}
.trace{fill:#c8c8c8}
.note{font-size:13px;color:var(--muted)}
@media (max-width:640px){main{padding:14px 12px}.blk{grid-template-columns:1fr}.grid{grid-template-columns:repeat(10,minmax(0,1fr))}}
@page{size:A4;margin:12mm 12mm 14mm 16mm;@bottom-center{content:counter(page);font-size:9pt;color:#5b6470}}
@media print{body{background:#fff;font-size:10pt} header{background:none;color:var(--ink);padding:0 0 6mm} header h1{font-size:20pt;color:#c2185b}
  main{padding:0;max-width:none} .toc{display:none} .intro{break-after:page}
  h2{break-before:page;margin-top:0;font-size:15pt} .blk{padding:2.2mm 0} .order{width:19mm;height:19mm}.info{grid-template-columns:19mm minmax(0,1fr)}
  .ex{font-size:8.5pt} *{-webkit-print-color-adjust:exact;print-color-adjust:exact}}
'''

intro = '''<div class="intro">
<p class="toc"><a href="#huong-dan">Hướng dẫn</a><a href="#lv2">HSK 1–2</a><a href="#lv3">HSK 3</a><a href="#lv4">HSK 4</a><a href="#lv5">HSK 5</a></p>
<h2 id="huong-dan" style="border-color:#c2185b">Hướng dẫn</h2>
<p>Vở gồm <strong>550 chữ Hán phải viết tay được</strong> theo đề cương HSK 3.0 (11/2025) từ cấp 1 đến cấp 5: 100 chữ cho HSK 1–2, mỗi cấp 3, 4, 5 thêm 150 chữ. Bài thi HSK trên giấy yêu cầu viết tay, nên những chữ này phải viết được mà không cần nhìn.</p>
<ul>
<li><strong>Ô bên trái</strong> là chữ mẫu, số màu hồng đánh dấu <strong>vị trí bắt đầu của từng nét</strong> theo thứ tự.</li>
<li><strong>Dòng ô kẻ</strong>: 4 ô đầu có chữ mờ để tô theo, các ô sau tự viết, vừa viết vừa đọc to pinyin.</li>
<li>Mỗi chữ có <strong>âm Hán Việt</strong> (giúp nhớ nghĩa, vì nhiều từ Hán Việt giống tiếng Việt), <strong>số nét</strong> và <strong>từ ví dụ</strong> lấy từ bộ từ vựng HSK 1–5.</li>
<li>Gợi ý: mỗi ngày 5–8 chữ mới, ôn lại chữ của 3 ngày trước bằng cách tự viết ra giấy nháp.</li>
<li>Quy tắc chung về thứ tự nét: ngang trước sọc sau, phẩy trước mác sau, trên trước dưới sau, trái trước phải sau, ngoài trước trong sau, vào nhà rồi đóng cửa, giữa trước hai bên sau.</li>
</ul>
<p class="note">Nguồn: danh sách chữ viết tay theo đề cương HSK 3.0 (dữ liệu từ dự án ofou/hsk); hình chữ và thứ tự nét từ <a href="https://github.com/skishore/makemeahanzi">Make Me a Hanzi</a> (dựa trên phông Arphic, giấy phép Arphic Public License); pinyin từ Unicode Unihan. Âm Hán Việt soạn tay (11/2026), có thể có chữ chưa chuẩn. Chữ mẫu theo kiểu chữ Khải (楷体), gần với chữ viết tay.</p>
</div>'''

page = (f'<!DOCTYPE html>\n<html lang="vi">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        f'<title>Vở tập viết chữ Hán HSK</title>\n<style>{CSS}</style>\n</head>\n<body>\n'
        f'<svg width="0" height="0" style="position:absolute"><defs>{"".join(defs)}</defs></svg>\n'
        f'<header><h1>✍️ Vở tập viết chữ Hán HSK 1–5</h1><p>550 chữ phải viết tay theo đề cương HSK 3.0 · thứ tự nét · âm Hán Việt · từ ví dụ</p></header>\n'
        f'<main>{intro}{"".join(sections)}</main>\n</body>\n</html>\n')
open(os.path.join(ROOT, 'Vo-tap-viet-chu-Han-HSK.html'), 'w', encoding='utf-8').write(page)
print('chars', idx, 'bytes', len(page), counts)
