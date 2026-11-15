"""Build the three English vocabulary pages from data files.

Usage (from the repo root):
  python3 data/build_vocab.py <cmudict.dict>
cmudict.dict: https://raw.githubusercontent.com/cmusphinx/cmudict/master/cmudict.dict
"""
import csv, glob, json, os, sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from ipa_us import Pron

P = Pron(sys.argv[1], manual={
    'quadrillion': '/kwɑːˈdrɪljən/', 'quintillion': '/kwɪnˈtɪljən/',
    'e-book': '/ˈiːˌbʊk/', 'résumé': '/ˈrɛzəˌmeɪ/', 'café': '/kæˈfeɪ/', 'distractor': '/dɪˈstræktɚ/',
    'ice cream': '/ˈaɪs ˌkriːm/', 'entrée': '/ˈɑːnˌtreɪ/', 'vend': '/vɛnd/', 'fundraise': '/ˈfʌndˌreɪz/',
    'repairperson': '/rɪˈpɛrˌpɝːsən/', 'housekeep': '/ˈhaʊsˌkiːp/', 'by-law': '/ˈbaɪˌlɔː/',
    'refactor': '/riːˈfæktɚ/', 'runtime': '/ˈrʌnˌtaɪm/', 'concurrency': '/kənˈkɝːənsi/', 'recursion': '/rɪˈkɝːʒən/',
    'hardcode': '/ˈhɑːrdˌkoʊd/', 'config': '/ˈkɑːnfɪɡ/', 'linter': '/ˈlɪntɚ/', 'rebase': '/riːˈbeɪs/',
    'maintainer': '/meɪnˈteɪnɚ/', 'onboarding': '/ˈɑːnˌbɔːrdɪŋ/', 'breakpoint': '/ˈbreɪkˌpɔɪnt/', 'hotfix': '/ˈhɑːtˌfɪks/',
    'uptime': '/ˈʌpˌtaɪm/', 'idempotent': '/ˌaɪdəmˈpoʊtənt/', 'frontend': '/ˈfrʌntˌɛnd/', 'webhook': '/ˈwɛbˌhʊk/',
    'microservice': '/ˈmaɪkroʊˌsɝːvɪs/', 'serialization': '/ˌsɪriələˈzeɪʃən/', 'overfitting': '/ˌoʊvɚˈfɪtɪŋ/',
    'multimodal': '/ˌmʌltiˈmoʊdəl/',
    'multi': '/ˈmʌlti/', 'semi': '/ˈsɛmi/', 'trans': '/trænz/', 'mid': '/mɪd/', 'anti': '/ˈæntaɪ/', 'ex': '/ɛks/',
    'micro': '/ˈmaɪkroʊ/', 'neo': '/ˈniːoʊ/', 'non': '/nɑːn/', 'pi': '/paɪ/', 'pre': '/priː/', 'sub': '/sʌb/',
    'super': '/ˈsuːpɚ/', 'descendent': '/dɪˈsɛndənt/', 'postgraduate': '/ˌpoʊstˈɡrædʒuət/', 'factorial': '/fækˈtɔːriəl/',
    'json': '/ˈdʒeɪsən/', 'readme': '/ˈriːdmiː/', 'rag': '/ræɡ/', 'lgtm': '/ˌɛl ˌdʒiː ˌtiː ˈɛm/',
})
TPL = open(os.path.join(HERE, 'vocab_template.html'), encoding='utf-8').read()
SRC_CMU = '<a href="https://github.com/cmusphinx/cmudict">CMU Pronouncing Dictionary</a>'
BYSA = '<a href="https://creativecommons.org/licenses/by-sa/4.0/">CC BY-SA 4.0</a>'
VOICE_NOTE = ('🔊 <b>Nút nghe</b> dùng giọng đọc có sẵn trong máy, không cần mạng nếu máy đã tải giọng tiếng Anh. '
              'Chất lượng giọng tùy thiết bị, nên <b>phiên âm mới là chuẩn để dựa vào</b>.')
COLORS = ['#2563eb', '#0d9488', '#7c3aed', '#d97706', '#db2777', '#475569', '#16a34a', '#0891b2',
          '#9333ea', '#c2410c', '#be123c', '#4d7c0f', '#1d4ed8', '#a16207']


def read_rows(pattern):
    rows, group, groups = [], None, {}
    for f in sorted(glob.glob(pattern)):
        for l in open(f, encoding='utf-8'):
            l = l.rstrip('\n')
            if not l.strip():
                continue
            if l.startswith('## '):
                k, name = l[3:].split('|')
                group = int(k)
                groups[group] = name
                continue
            rows.append((group, l.split('|')))
    return rows, groups


def word_entry(lv, w, pos, vi, ex, exvi):
    ipa, het = P.entry(w)
    e = {'lv': lv, 'w': w, 'pos': pos, 'vi': vi, 'ex': ex, 'exvi': exvi, 'ipa': ipa}
    if het:
        e['het'] = 1
    return e


def write(out, cfg, data, title, h1, sub, note):
    missing = [d['w'] for d in data if not d.get('ph') and not d['ipa']]
    js = json.dumps(data, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
    cj = json.dumps(cfg, ensure_ascii=False).replace('</', '<\\/')
    html = (TPL.replace('__TITLE__', title).replace('__H1__', h1).replace('__SUB__', sub)
            .replace('__NOTE__', note).replace('__CONFIG__', cj).replace('__DATA__', js))
    open(os.path.join(ROOT, out), 'w', encoding='utf-8').write(html)
    print(f'{out}: {len(data)} rows', sorted(Counter(d["lv"] for d in data).items()),
          'heteronyms', sum(1 for d in data if d.get('het')), '| missing IPA:', missing)


# ---------------- NGSL ----------------
D = os.path.join(HERE, 'ngsl')
ngsl = [r['Lemma'] for r in csv.DictReader(open(D + '/NGSL_12_stats.csv'))]
rank = {(w.lower() if w in ('TRUE', 'FALSE') else w): i + 1 for i, w in enumerate(ngsl)}
data = []
for _, (w, pos, vi, ex, exvi) in read_rows(D + '/b*.txt')[0]:
    r = rank.get(w)
    data.append(word_entry(7 if r is None else min((r - 1) // 500 + 1, 6), w, pos, vi, ex, exvi))
ranges = ['1–500', '501–1000', '1001–1500', '1501–2000', '2001–2500', '2501–2809']
levels = [{'k': 0, 'n': 'Tất cả', 'c': '#1f2433'}] + \
         [{'k': i + 1, 'n': f'Nhóm {i + 1}', 'r': r, 'c': COLORS[i]} for i, r in enumerate(ranges)] + \
         [{'k': 7, 'n': 'Bổ sung', 'r': 'thứ, tháng, số', 'c': '#16a34a', 'b': '+'}]
write('Tu-vung-tieng-Anh-NGSL.html', {
    'levels': levels, 'key': 'ngsl-thuoc', 'unit': 'từ', 'h1print': 'Từ vựng tiếng Anh thiết yếu',
    'cover': [f'{len(data):,} từ · phiên âm giọng Mỹ · nghĩa tiếng Việt · câu ví dụ'.replace(',', '.'),
              'Học theo thứ tự nhóm: nhóm 1 là những từ gặp nhiều nhất. Tích ô ☐ bằng bút khi đã thuộc.'],
    'src': 'Danh sách từ: New General Service List 1.2 (Browne, Culligan &amp; Phillips), CC BY-SA 4.0 · Phiên âm: CMU Pronouncing Dictionary<br>Nghĩa và ví dụ: soạn 11/2026, CC BY-SA 4.0 · ⚠ = từ đọc khác nhau tùy nghĩa'},
    data, 'Từ vựng tiếng Anh NGSL', '📘 Từ vựng tiếng Anh thiết yếu',
    '2.809 từ NGSL 1.2 xếp theo tần suất + 52 từ bổ sung · Tích ô “Đã thuộc” để theo dõi tiến độ (lưu trên trình duyệt này)',
    '💡 <b>Cách học:</b> mỗi ngày 15–20 từ, học theo thứ tự nhóm vì nhóm 1 là những từ xuất hiện nhiều nhất. Bật “Che nghĩa” để tự kiểm tra, bấm vào chỗ bị che để xem đáp án.<br>'
    + VOICE_NOTE + ' Từ có dấu ⚠ đọc được nhiều kiểu tùy nghĩa (ví dụ <i>read</i>), nút nghe chỉ đọc một kiểu.<br>'
    f'📚 <b>Nguồn:</b> danh sách từ <a href="https://www.newgeneralservicelist.com/">New General Service List 1.2</a> của Browne, C., Culligan, B. và Phillips, J. (giấy phép {BYSA}); phiên âm chuyển từ {SRC_CMU}. '
    'Nghĩa tiếng Việt và câu ví dụ soạn riêng (11/2026), phát hành theo CC BY-SA 4.0; nghĩa chỉ ghi các nghĩa thường gặp. Khi in (Ctrl+P), trang tự chuyển sang bản in đủ các nhóm, có ô để tích bằng bút.')

# ---------------- TSL ----------------
D = os.path.join(HERE, 'tsl')
tsl = [r[0] for r in list(csv.reader(open(D + '/TSL_12_stats.csv', encoding='latin-1')))[1:] if r and r[0]]
rank = {w: i + 1 for i, w in enumerate(tsl)}
data = [word_entry(min((rank[w] - 1) // 500 + 1, 3), w, pos, vi, ex, exvi)
        for _, (w, pos, vi, ex, exvi) in read_rows(D + '/t*.txt')[0]]
assert len(data) == len(tsl) and all(d['w'] in rank for d in data)
levels = [{'k': 0, 'n': 'Tất cả', 'c': '#1f2433'}] + \
         [{'k': i + 1, 'n': f'Nhóm {i + 1}', 'r': r, 'c': COLORS[i]} for i, r in enumerate(['1–500', '501–1000', '1001–1250'])]
write('Tu-vung-tieng-Anh-cong-so-TOEIC.html', {
    'levels': levels, 'key': 'tsl-thuoc', 'unit': 'từ', 'h1print': 'Từ vựng tiếng Anh công sở (TOEIC)',
    'cover': ['1.250 từ TOEIC Service List 1.2 · học tiếp sau 2.809 từ NGSL', 'Phiên âm giọng Mỹ · nghĩa tiếng Việt · câu ví dụ trong môi trường công sở. Tích ô ☐ bằng bút khi đã thuộc.'],
    'src': 'Danh sách từ: TOEIC Service List 1.2 (Browne &amp; Culligan), CC BY-SA 4.0 · Phiên âm: CMU Pronouncing Dictionary<br>Nghĩa và ví dụ: soạn 11/2026, CC BY-SA 4.0'},
    data, 'Từ vựng tiếng Anh công sở', '💼 Từ vựng tiếng Anh công sở (TOEIC)',
    '1.250 từ TOEIC Service List 1.2, học tiếp sau NGSL · Tích ô “Đã thuộc” để theo dõi tiến độ (lưu trên trình duyệt này)',
    '💡 <b>Cách học:</b> học sau khi đã nắm phần lớn NGSL. Theo nhóm tác giả, 2.809 từ NGSL cộng 1.250 từ này bao phủ khoảng 98,5% từ ngữ trong đề TOEIC. Danh sách không trùng từ nào với NGSL.<br>'
    + VOICE_NOTE + '<br>'
    f'📚 <b>Nguồn:</b> <a href="https://www.newgeneralservicelist.com/toeic-service-list">TOEIC Service List 1.2</a> của Browne, C. và Culligan, B. (giấy phép {BYSA}); phiên âm chuyển từ {SRC_CMU}. Nghĩa tiếng Việt và câu ví dụ soạn riêng (11/2026), phát hành theo CC BY-SA 4.0.')

# ---------------- IT / AI ----------------
D = os.path.join(HERE, 'it')
data, groups = [], {}
rows, g = read_rows(D + '/terms.txt'); groups.update(g)
data += [word_entry(lv, *f) for lv, f in rows]
rows, g = read_rows(D + '/phrases.txt'); groups.update(g)
data += [{'lv': lv, 'w': en, 'vi': vi, 'note': note, 'ph': 1, 'ipa': '', 'pos': ''} for lv, (en, vi, note) in rows]
SHORT = {1: 'Quy trình', 2: 'Viết code', 3: 'Git', 4: 'Kiểm thử', 5: 'Vận hành', 6: 'Dữ liệu & API', 7: 'AI & LLM',
         8: 'Bảo mật', 9: 'Email', 10: 'Họp', 11: 'Review code', 12: 'Tiến độ', 13: 'Thảo luận', 14: 'Phỏng vấn'}
nterm = sum(1 for d in data if not d.get('ph'))
levels = [{'k': 0, 'n': 'Tất cả', 'c': '#1f2433'}] + \
         [{'k': k, 'n': ('💬 ' if k >= 9 else '') + SHORT[k], 'r': name, 'c': COLORS[(k - 1) % len(COLORS)], 'b': ('💬' if k >= 9 else str(k))} for k, name in sorted(groups.items())]
write('Tieng-Anh-cho-ky-su-phan-mem-AI.html', {
    'levels': levels, 'key': 'it-thuoc', 'unit': 'mục', 'h1print': 'Tiếng Anh cho kỹ sư phần mềm &amp; AI',
    'cover': [f'{nterm} thuật ngữ theo 8 chủ đề · {len(data) - nterm} mẫu câu giao tiếp công việc',
              'Thuật ngữ có phiên âm và câu ví dụ trong ngữ cảnh thực tế; mẫu câu kèm ghi chú khi nào dùng. Tích ô ☐ bằng bút khi đã thuộc.'],
    'src': 'Soạn 11/2026, CC BY-SA 4.0 · Phiên âm: CMU Pronouncing Dictionary · Mục AI có thể thay đổi nhanh, nên đối chiếu lại sau năm 2028'},
    data, 'Tiếng Anh cho kỹ sư phần mềm', '💻 Tiếng Anh cho kỹ sư phần mềm &amp; AI',
    f'{nterm} thuật ngữ IT/AI theo chủ đề + {len(data) - nterm} mẫu câu giao tiếp công việc · Tích ô “Đã thuộc” để theo dõi tiến độ',
    '💡 <b>Cách dùng:</b> các tab 1–8 là thuật ngữ, chú ý nghĩa riêng trong ngành (ví dụ <i>issue</i> là “đầu việc, lỗi” chứ không phải “số báo”). Các tab 💬 là mẫu câu dùng khi viết email, họp, review code, báo cáo tiến độ, thảo luận kỹ thuật và phỏng vấn. Nên đọc to các mẫu câu cho quen miệng.<br>'
    + VOICE_NOTE + ' Thuật ngữ AI thay đổi nhanh: nội dung phản ánh tháng 11/2026.<br>'
    f'📚 <b>Nguồn:</b> danh sách và nội dung soạn riêng (11/2026), phát hành theo {BYSA}; phiên âm chuyển từ {SRC_CMU}.')

# ---------------- NAWL (only words not already in NGSL/TSL) ----------------
D = os.path.join(HERE, 'nawl')
order = [l.strip() for l in open(D + '/order_new_words.txt') if l.strip()]
order = ['descendent' if w == 'DESCENDENT' else w for w in order]
pos_of = {w: i for i, w in enumerate(order)}
grp = lambda w: 1 if pos_of[w] < pos_of['acute'] else (2 if pos_of[w] < pos_of['abdominal'] else 3)
data = [word_entry(grp(w), w, pos, vi, ex, exvi) for _, (w, pos, vi, ex, exvi) in read_rows(D + '/n*.txt')[0]]
assert len(data) == len(order)
levels = [{'k': 0, 'n': 'Tất cả', 'c': '#1f2433'},
          {'k': 1, 'n': 'Nhóm 1', 'r': 'thường gặp nhất', 'c': COLORS[0]},
          {'k': 2, 'n': 'Nhóm 2', 'r': 'thường gặp', 'c': COLORS[1]},
          {'k': 3, 'n': 'Nhóm 3', 'r': 'chuyên ngành', 'c': COLORS[2]}]
write('Tu-vung-hoc-thuat-IELTS-NAWL.html', {
    'levels': levels, 'key': 'nawl-thuoc', 'unit': 'từ', 'h1print': 'Từ vựng học thuật cho IELTS (NAWL)',
    'cover': [f'{len(data)} từ học thuật (NAWL 1.2) · đã bỏ các từ trùng với NGSL và TOEIC',
              'Học sau NGSL. Nhóm 1–2 là trọng tâm cho IELTS Reading và Writing; nhóm 3 là từ chuyên ngành, chủ yếu cần để đọc hiểu. Tích ô ☐ bằng bút khi đã thuộc.'],
    'src': 'Danh sách từ: New Academic Word List 1.2 (Browne, Culligan &amp; Phillips), CC BY-SA 4.0 · Phiên âm: CMU Pronouncing Dictionary<br>Nghĩa và ví dụ: soạn 11/2026, CC BY-SA 4.0'},
    data, 'Từ vựng học thuật IELTS', '🎓 Từ vựng học thuật cho IELTS (NAWL)',
    f'{len(data)} từ học thuật thường gặp trong sách báo, bài nghiên cứu · Tích ô “Đã thuộc” để theo dõi tiến độ',
    '💡 <b>Cách học:</b> học sau NGSL. NAWL gốc có 957 từ; khoảng 230 từ đã có trong bộ TOEIC và NGSL nên được bỏ ra ở đây. '
    '<b>Nhóm 1–2</b> nên học kỹ, dùng được cả khi viết. <b>Nhóm 3</b> là từ chuyên ngành (sinh học, ngôn ngữ học, toán…), chỉ cần nhận ra nghĩa khi đọc. '
    'Câu ví dụ được viết theo văn phong học thuật giống bài đọc IELTS.<br>'
    + VOICE_NOTE + '<br>'
    f'📚 <b>Nguồn:</b> <a href="https://www.newgeneralservicelist.com/new-academic-word-list">New Academic Word List 1.2</a> của Browne, C., Culligan, B. và Phillips, J. (giấy phép {BYSA}); phiên âm chuyển từ {SRC_CMU}. Nghĩa tiếng Việt và câu ví dụ soạn riêng (11/2026), phát hành theo CC BY-SA 4.0.')
