"""Assemble the IELTS practice tests page from fragments.

Usage (from repo root): python3 data/ielts/build_tests.py
"""
import math, os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
INK, MUTED, GRID = '#1f2328', '#5b6470', '#d9dde3'
C = ['#2563eb', '#0d9488', '#d97706', '#db2777', '#7c3aed', '#475569']


def svg(w, h, body, label):
    return (f'<figure class="chart"><svg viewBox="0 0 {w} {h}" role="img" aria-label="{label}" '
            f'xmlns="http://www.w3.org/2000/svg" font-family="Segoe UI, Roboto, Arial, sans-serif">{body}</svg></figure>')


def line_chart():
    years = [2010, 2015, 2020, 2025]
    series = {'16–24': [3.0, 4.5, 6.0, 6.5], '25–44': [2.5, 3.5, 4.5, 5.0],
              '45–64': [1.5, 2.0, 3.0, 3.5], '65+': [0.5, 0.8, 1.5, 2.5]}
    x0, y0, x1, y1, ymax = 70, 40, 470, 300, 7
    X = lambda i: x0 + (x1 - x0) * i / (len(years) - 1)
    Y = lambda v: y1 - (y1 - y0) * v / ymax
    b = f'<text x="{(x0+x1)/2}" y="22" text-anchor="middle" font-size="15" font-weight="600" fill="{INK}">Average hours online per day, by age group</text>'
    for v in range(0, ymax + 1):
        b += f'<line x1="{x0}" y1="{Y(v)}" x2="{x1}" y2="{Y(v)}" stroke="{GRID}"/><text x="{x0-8}" y="{Y(v)+4}" text-anchor="end" font-size="12" fill="{MUTED}">{v}</text>'
    for i, yr in enumerate(years):
        b += f'<text x="{X(i)}" y="{y1+20}" text-anchor="middle" font-size="12" fill="{MUTED}">{yr}</text>'
    b += f'<text x="20" y="{(y0+y1)/2}" transform="rotate(-90 20 {(y0+y1)/2})" text-anchor="middle" font-size="12" fill="{MUTED}">hours per day</text>'
    for k, (name, vals) in enumerate(series.items()):
        pts = ' '.join(f'{X(i)},{Y(v)}' for i, v in enumerate(vals))
        b += f'<polyline points="{pts}" fill="none" stroke="{C[k]}" stroke-width="2.5"/>'
        b += ''.join(f'<circle cx="{X(i)}" cy="{Y(v)}" r="3.5" fill="{C[k]}"/>' for i, v in enumerate(vals))
        b += f'<rect x="495" y="{70+k*28}" width="14" height="14" fill="{C[k]}"/><text x="515" y="{82+k*28}" font-size="13" fill="{INK}">{name}</text>'
    b += f'<text x="495" y="58" font-size="12" fill="{MUTED}">Age group</text>'
    return svg(600, 330, b, 'Line graph of average hours online per day by age group, 2010 to 2025')


def bar_chart():
    cities = ['City A', 'City B', 'City C', 'City D']
    data = {'2015': [45, 30, 25, 10], '2025': [62, 48, 41, 35]}
    x0, y0, x1, y1, ymax = 60, 40, 470, 300, 70
    Y = lambda v: y1 - (y1 - y0) * v / ymax
    b = f'<text x="{(x0+x1)/2}" y="22" text-anchor="middle" font-size="15" font-weight="600" fill="{INK}">Percentage of household waste recycled</text>'
    for v in range(0, ymax + 1, 10):
        b += f'<line x1="{x0}" y1="{Y(v)}" x2="{x1}" y2="{Y(v)}" stroke="{GRID}"/><text x="{x0-8}" y="{Y(v)+4}" text-anchor="end" font-size="12" fill="{MUTED}">{v}%</text>'
    gw = (x1 - x0) / len(cities)
    for i, c in enumerate(cities):
        for k, (yr, vals) in enumerate(data.items()):
            bx = x0 + i * gw + gw * 0.18 + k * gw * 0.32
            v = vals[i]
            b += f'<rect x="{bx}" y="{Y(v)}" width="{gw*0.3}" height="{y1-Y(v)}" fill="{C[k]}"/>'
            b += f'<text x="{bx+gw*0.15}" y="{Y(v)-5}" text-anchor="middle" font-size="11" fill="{INK}">{v}</text>'
        b += f'<text x="{x0+i*gw+gw/2}" y="{y1+20}" text-anchor="middle" font-size="12" fill="{MUTED}">{c}</text>'
    for k, yr in enumerate(data):
        b += f'<rect x="495" y="{70+k*28}" width="14" height="14" fill="{C[k]}"/><text x="515" y="{82+k*28}" font-size="13" fill="{INK}">{yr}</text>'
    return svg(600, 330, b, 'Bar chart of recycling rates in four cities in 2015 and 2025')


def pie(cx, cy, r, parts, title):
    b = f'<text x="{cx}" y="{cy-r-34}" text-anchor="middle" font-size="14" font-weight="600" fill="{INK}">{title}</text>'
    a = -math.pi / 2
    for k, (name, v) in enumerate(parts):
        a2 = a + 2 * math.pi * v / 100
        large = 1 if v > 50 else 0
        p1 = (cx + r * math.cos(a), cy + r * math.sin(a)); p2 = (cx + r * math.cos(a2), cy + r * math.sin(a2))
        b += f'<path d="M{cx},{cy} L{p1[0]:.1f},{p1[1]:.1f} A{r},{r} 0 {large} 1 {p2[0]:.1f},{p2[1]:.1f} Z" fill="{C[k]}" stroke="#fff" stroke-width="1.5"/>'
        m = (a + a2) / 2
        lr = r * 0.68 if v >= 8 else r + 16
        col = '#fff' if v >= 8 else INK
        b += f'<text x="{cx + lr*math.cos(m):.1f}" y="{cy + lr*math.sin(m) + 4:.1f}" text-anchor="middle" font-size="12" font-weight="600" fill="{col}">{v}%</text>'
        a = a2
    return b


def pie_charts():
    names = ['Coal', 'Oil', 'Natural gas', 'Hydropower', 'Solar', 'Wind']
    p05 = [55, 10, 15, 15, 2, 3]
    p25 = [35, 3, 17, 15, 18, 12]
    b = pie(150, 200, 110, list(zip(names, p05)), '2005') + pie(430, 200, 110, list(zip(names, p25)), '2025')
    for k, n in enumerate(names):
        x = 40 + (k % 3) * 190; y = 360 + (k // 3) * 24
        b += f'<rect x="{x}" y="{y}" width="14" height="14" fill="{C[k]}"/><text x="{x+20}" y="{y+12}" font-size="13" fill="{INK}">{n}</text>'
    return svg(600, 415, b, 'Two pie charts of electricity sources in 2005 and 2025')


def process():
    steps = ['Used paper is collected from homes and offices', 'Paper is sorted by type',
             'Paper is mixed with water and chemicals to make pulp', 'Pulp is screened to remove plastic and metal',
             'Ink is removed (de-inking)', 'Pulp is pressed and dried by heated rollers',
             'Paper is wound onto large reels', 'Reels are delivered to manufacturers']
    cells = ''.join(f'<div class="step"><b>{i+1}</b><span>{s}</span></div>' for i, s in enumerate(steps))
    return (f'<figure class="chart"><p class="ptitle">The production of recycled paper</p><div class="process">{cells}</div>'
            f'<p class="pnote">Stages 2–7 take place at the recycling plant.</p></figure>')


CSS = '''
.passage{background:#fbfaf7;border:1px solid var(--line);border-radius:10px;padding:14px 18px;margin:12px 0}
.passage h4{text-align:center;font-size:1.15rem;margin:.2em 0 .6em}
.passage p{text-align:justify}
.qbox{border-left:4px solid var(--teal);padding:4px 0 4px 14px;margin:14px 0}
.qbox ol{padding-left:2.4em}.qbox ol li{margin:.45em 0}
.inst{color:var(--muted);font-style:italic}
.tfng,.wordbox,.headings,.summary,.notes,.flow{background:#f1f5f9;border-radius:8px;padding:10px 14px}
.flow{text-align:center;line-height:1.9}
.chart{margin:12px 0;text-align:center}.chart svg{width:100%;max-width:600px;height:auto}
.ptitle{font-weight:600;margin:.2em 0 .6em}.pnote{color:var(--muted);font-size:.9rem}
.process{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:10px;text-align:left}
.step{border:1px solid var(--line);border-radius:10px;padding:8px 10px;background:#fff;font-size:.92rem;position:relative}
.step b{display:inline-grid;place-items:center;width:24px;height:24px;border-radius:50%;background:var(--teal);color:#fff;margin-right:6px;font-size:.85rem}
@media (max-width:640px){.process{grid-template-columns:repeat(2,minmax(0,1fr))}}
table.key td:first-child{width:3em;text-align:center} table.key td:nth-child(2){white-space:nowrap}
.sheet{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:0 24px}
.sheet div{border-bottom:1px solid #999;padding:7px 0 3px;font-size:.95rem}
@media print{
  h2[id^="de-"],h2#dap-an,h2#phieu{break-before:page}
  h3[id$="-writing"]{break-before:page}
  .passage{background:#fff;border:none;padding:0}
  .passage p{font-size:10pt;line-height:1.45}
  .qbox{border-left:none;padding-left:0}
  .step{break-inside:avoid}
  .sheet div{padding:9px 0 2px}
}
'''

style = open(os.path.join(ROOT, 'Tong-hop-ngu-phap-tieng-Anh.html'), encoding='utf-8').read()
style = style[style.index('<style>'):style.index('</style>')] + CSS + '</style>'

intro = '''<header class="page"><div class="inner"><h1>4 đề luyện IELTS Academic: Reading &amp; Writing</h1><p>Soạn theo đúng định dạng đề thi · Có đáp án và giải thích · Cập nhật 11/2026</p></div></header>
<main>
<h2 id="mục-lục">Mục lục</h2>
<p>Bấm vào tên mỗi phần để nhảy tới phần đó.</p>
<ul><li><p><a href="#cach-dung">Cách dùng bộ đề</a></p></li>
<li><p><a href="#de-1">Đề 1</a> · <a href="#de-2">Đề 2</a> · <a href="#de-3">Đề 3</a> · <a href="#de-4">Đề 4</a></p></li>
<li><p><a href="#dap-an">Đáp án và giải thích</a></p></li>
<li><p><a href="#phieu">Phiếu trả lời Reading (photo nhiều bản)</a></p></li></ul>
<h2 id="cach-dung">Cách dùng bộ đề</h2>
<ul><li><p><strong>Reading:</strong> bấm giờ đúng <strong>60 phút</strong> cho cả 3 bài, viết đáp án vào phiếu trả lời ở cuối tài liệu. Không xem đáp án trước khi làm xong.</p></li>
<li><p><strong>Chấm điểm:</strong> mỗi câu đúng 1 điểm. Quy đổi xấp xỉ: khoảng 23/40 ≈ band 6.0, khoảng 27/40 ≈ 6.5, khoảng 30/40 ≈ 7.0.</p></li>
<li><p><strong>Sau khi chấm:</strong> đọc phần giải thích của <em>mọi</em> câu sai, tìm lại câu đó trong bài đọc, và ghi các cặp paraphrase vào sổ.</p></li>
<li><p><strong>Writing:</strong> Task 1 viết trong 20 phút, Task 2 trong 40 phút. Tự chấm bằng bảng trong cuốn <em>Cẩm nang IELTS</em>, rồi đối chiếu với phần gợi ý ở cuối tài liệu.</p></li></ul>
<blockquote class="tip"><p><strong>Lưu ý:</strong> bài đọc được soạn riêng để luyện tập. Bối cảnh chung dựa trên kiến thức phổ biến, nhưng <strong>tên các nhà nghiên cứu (trừ Karl von Frisch và Richard Easterlin) và một số chi tiết là hư cấu</strong>, đừng dùng làm nguồn trích dẫn. Độ khó được ước lượng theo đề thật nhưng không được hiệu chuẩn chính thức, nên hãy dùng bộ sách Cambridge IELTS để đo điểm chính xác.</p></blockquote>
'''

sheet = '<h2 id="phieu">Phiếu trả lời Reading</h2><p>Họ tên: ……………………………… &nbsp; Đề số: ……… &nbsp; Ngày: ……………… &nbsp; Điểm: ……… / 40</p><div class="sheet">' + \
        ''.join(f'<div>{i}. </div>' for i in [n for pair in zip(range(1, 21), range(21, 41)) for n in pair]) + '</div>'

parts = [intro]
charts = {'__CHART1__': line_chart(), '__CHART2__': bar_chart(), '__CHART3__': pie_charts(), '__CHART4__': process()}
for i in range(1, 5):
    t = open(os.path.join(HERE, f'test{i}.html'), encoding='utf-8').read()
    for k, v in charts.items():
        t = t.replace(k, v)
    parts.append(t)
parts.append('<h2 id="dap-an">Đáp án và giải thích</h2>')
for i in range(1, 5):
    parts.append(open(os.path.join(HERE, f'key{i}.html'), encoding='utf-8').read())
parts.append(sheet + '\n</main>\n<a class="to-top" href="#top" title="Lên đầu trang">↑</a>')

html = ('<!DOCTYPE html>\n<html lang="vi">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        '<title>Đề luyện IELTS Academic</title>\n' + style + '\n</head>\n<body id="top">\n' + '\n'.join(parts) + '\n</body>\n</html>\n')
assert '__CHART' not in html
open(os.path.join(ROOT, 'De-luyen-IELTS-Academic.html'), 'w', encoding='utf-8').write(html)
print('written', len(html))
