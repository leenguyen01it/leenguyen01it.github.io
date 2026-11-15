"""Build the HSK 4–5 guide + graded readings page. Usage: python3 data/hanzi/build_hsk_guide.py"""
import html, os, re
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
esc = html.escape
body = open(os.path.join(HERE, 'guide_body.html'), encoding='utf-8').read()
m = re.search(r'<p class="zh">(.*?)</p>', body, re.S)
essay_len = len([c for c in re.sub('<[^>]+>', '', m.group(1)) if '一' <= c <= '鿿'])
body = body.replace('__ESSAY_LEN__', str(essay_len))

texts = []; cur = None
for line in open(os.path.join(HERE, 'readings.txt'), encoding='utf-8'):
    line = line.rstrip('\n')
    if not line: continue
    if line.startswith('### '):
        lv, zh, vi = line[4:].split('|'); cur = {'lv': int(lv), 'title': zh, 'vi': vi, 'lines': [], 'qs': []}; texts.append(cur)
    elif line.startswith('Q|'):
        _, q, qvi, a = line.split('|'); cur['qs'].append((q, qvi, a))
    else:
        cur['lines'].append(line.split('|'))

COL = {1: '#2a9d8f', 2: '#e76f51', 3: '#5a8f29', 4: '#7b61ff', 5: '#c2185b'}
read_html = ['<h2 id="bai-doc"><span class="c-red">Bài đọc luyện theo cấp</span></h2>',
             '<p>15 bài, mỗi cấp 3 bài. Mọi chữ trong bài đều thuộc danh sách chữ của cấp đó trở xuống (theo đề cương HSK 3.0). '
             'Bài cấp 1–3 có pinyin dưới từng câu; cấp 4–5 không có pinyin, giống bài thi thật. <strong>Bản dịch và đáp án ở cuối tài liệu.</strong> '
             'Cách học: đọc to 2–3 lần, trả lời câu hỏi, rồi mới xem bản dịch.</p>']
key_html = ['<h2 id="dap-an-doc"><span class="c-red">Bản dịch và đáp án bài đọc</span></h2>']
n = 0
for t in texts:
    n += 1
    nchar = sum(1 for l in t['lines'] for c in l[0] if '一' <= c <= '鿿')
    h = f'<h3 id="bai-{n}"><span class="lvtag" style="background:{COL[t["lv"]]}">HSK {t["lv"]}</span> Bài {n}. <span class="zh">{esc(t["title"])}</span></h3><div class="reading">'
    for zh, py, vi in t['lines']:
        h += f'<p class="zh">{esc(zh)}</p>' + (f'<p class="py">{esc(py)}</p>' if py != '-' else '')
    h += f'</div><p class="note">{nchar} chữ</p>'
    if t['lv'] <= 3:
        h += '<p><strong>Đúng (对) hay sai (错)?</strong></p><ol class="qs">' + ''.join(f'<li><span class="zh">{esc(q)}</span></li>' for q, _, _ in t['qs']) + '</ol>'
    else:
        h += '<p><strong>Chọn đáp án đúng / trả lời câu hỏi:</strong></p><ol class="qs">' + ''.join(f'<li><span class="zh">{esc(q)}</span></li>' for q, _, _ in t['qs']) + '</ol>'
    read_html.append(h)
    k = f'<h3>Bài {n}. <span class="zh">{esc(t["title"])}</span> – {esc(t["vi"])}</h3><p>' + ' '.join(esc(vi) for _, _, vi in t['lines']) + '</p>'
    k += '<p><strong>Đáp án:</strong> ' + ' · '.join(f'{i+1}. <strong>{esc(a)}</strong> <span class="note">({esc(qvi)})</span>' for i, (_, qvi, a) in enumerate(t['qs'])) + '</p>'
    key_html.append(k)

style = open(os.path.join(ROOT, 'Tong-hop-ngu-phap-tieng-Trung.html'), encoding='utf-8').read()
style = style[style.index('<style>'):style.index('</style>')] + '''
.zh{font-family:"Noto Sans SC","Microsoft YaHei","PingFang SC",sans-serif}
.reading{background:#fbfaf7;border:1px solid var(--line);border-radius:10px;padding:10px 16px;margin:8px 0}
.reading p.zh{font-size:1.15rem;margin:.5em 0 0;line-height:1.7}.reading p.py{color:#6d28d9;font-style:italic;margin:0 0 .3em;font-size:.95rem}
.lvtag{color:#fff;border-radius:6px;padding:1px 8px;font-size:.8rem;vertical-align:middle;margin-right:4px}
.qs li{margin:.35em 0}.qs .zh{font-size:1.05rem}
.formula{background:#f1f5f9;border-radius:8px;padding:10px 14px;text-align:center}
.note{color:var(--muted);font-size:.88rem}
blockquote.tip p.zh{font-size:1.1rem;line-height:1.8}
@media print{h2#bai-doc,h2#dap-an-doc{break-before:page} .reading{background:#fff;border:none;padding:0} h3[id^="bai-"]{break-after:avoid} .reading{break-inside:avoid}}
</style>'''
intro = '''<header class="page"><div class="inner"><h1>Cẩm nang thi HSK 4–5 và bài đọc luyện theo cấp</h1><p>Theo đề cương HSK 3.0 (11/2025) · Cập nhật 11/2026</p></div></header>
<main>
<h2 id="mục-lục">Mục lục</h2>
<ul><li><p><a href="#tong-quan">Tổng quan và lưu ý về định dạng đề</a></p></li><li><p><a href="#lo-trinh">Lộ trình 24 tháng</a></p></li>
<li><p><a href="#doc">Kỹ năng Đọc</a> · <a href="#viet">Kỹ năng Viết</a> · <a href="#loi">Lỗi người Việt hay mắc</a> · <a href="#tu-hoc">Mẹo tự học</a></p></li>
<li><p><a href="#bai-doc">15 bài đọc luyện theo cấp</a> · <a href="#dap-an-doc">Bản dịch và đáp án</a></p></li></ul>
'''
page = ('<!DOCTYPE html>\n<html lang="vi">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        '<title>Cẩm nang thi HSK 4–5</title>\n' + style + '\n</head>\n<body id="top">\n' + intro + body + '\n'.join(read_html) + '\n'.join(key_html)
        + '\n</main>\n<a class="to-top" href="#top" title="Lên đầu trang">↑</a>\n</body>\n</html>\n')
open(os.path.join(ROOT, 'Cam-nang-HSK-4-5-va-bai-doc.html'), 'w', encoding='utf-8').write(page)
print('texts', n, 'essay chars', essay_len)
