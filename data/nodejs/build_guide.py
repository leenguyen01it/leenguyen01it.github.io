"""Build the Middle Node.js/React guide. Usage: python3 data/nodejs/build_guide.py [--pdf]

Sources: part*.html in this folder (plain HTML) with fenced blocks:
  ```js / ```ts / ```tsx / ```sql / ```graphql / ```yaml / ```dockerfile / ```bash / ```php  -> highlighted code
  ```qa    Q: question / A: answer                     -> review questions (click to reveal)
  ```quiz  Q: question / - wrong / + right / E: why     -> multiple-choice quiz
Inside qa/quiz text: `code` and **bold** are supported.
"""
import hashlib, html, os, random, re, subprocess, sys, tempfile
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
OUT = 'Lo-trinh-Middle-NodeJS-React.html'
TITLE = 'Lộ trình kiến thức Middle Node.js &amp; React'
esc = html.escape
LANG = {'js': 'javascript', 'ts': 'typescript', 'tsx': 'typescript', 'jsx': 'javascript', 'sql': 'sql', 'graphql': 'graphql',
        'yaml': 'yaml', 'dockerfile': 'docker', 'bash': 'bash', 'php': 'php', 'json': 'json', 'nginx': 'nginx', 'text': 'text'}
FMT = HtmlFormatter(nowrap=True)


def inline(s):
    s = esc(s, quote=False)
    s = re.sub(r'`([^`]+)`', r'<code>\1</code>', s)
    return re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', s)


def code_block(lang, src):
    lexer = get_lexer_by_name(LANG[lang], startinline=True) if lang == 'php' else get_lexer_by_name(LANG[lang])
    return f'<div class="code"><span class="lang">{lang}</span><pre class="hl"><code>{highlight(src, lexer, FMT)}</code></pre></div>'


def qa_block(src):
    items, cur = [], None
    for line in src.splitlines():
        if line.startswith('Q: '):
            cur = [line[3:], []]; items.append(cur)
        elif line.startswith('A: '):
            cur[1].append(line[3:])
        elif line.strip():
            cur[1].append(line)
    out = ['<h3 class="rev">Câu hỏi ôn tập</h3><p class="hint">Tự trả lời thành tiếng trước, rồi bấm vào câu hỏi để xem gợi ý.</p><div class="qas">']
    for i, (q, a) in enumerate(items, 1):
        out.append(f'<details class="qa"><summary><b>{i}.</b> {inline(q)}</summary><div class="ans">'
                   + ''.join(f'<p>{inline(p)}</p>' for p in a) + '</div></details>')
    return ''.join(out) + '</div>', len(items)


def quiz_block(src):
    qs, cur = [], None
    for line in src.splitlines():
        if line.startswith('Q: '):
            cur = {'q': line[3:], 'opts': [], 'e': ''}; qs.append(cur)
        elif line.startswith(('+ ', '- ')):
            cur['opts'].append((line[0] == '+', line[2:]))
        elif line.startswith('E: '):
            cur['e'] = line[3:]
    out = [f'<h3 class="rev">Trắc nghiệm</h3><div class="quiz" data-total="{len(qs)}"><p class="score">Đã làm <b class="done">0</b>/{len(qs)} · Đúng <b class="right">0</b></p>']
    for i, q in enumerate(qs, 1):
        assert sum(ok for ok, _ in q['opts']) == 1, q['q']
        # shuffle options with a stable per-question seed so answer letters are spread out
        random.Random(hashlib.md5(q['q'].encode()).hexdigest()).shuffle(q['opts'])
        key = 'ABCD'[[ok for ok, _ in q['opts']].index(True)]
        opts = ''.join(f'<li><button type="button" data-ok="{int(ok)}"><b>{"ABCD"[j]}.</b> {inline(t)}</button></li>'
                       for j, (ok, t) in enumerate(q['opts']))
        out.append(f'<div class="qz"><p class="qq"><b>Câu {i}.</b> {inline(q["q"])}</p><ol class="opts">{opts}</ol>'
                   f'<p class="ex"><strong>Đáp án {key}.</strong> {inline(q["e"])}</p></div>')
    return ''.join(out) + '</div>', len(qs)


def slug_toc(body):
    return [(m.group(1), re.sub('<[^>]+>', '', m.group(2))) for m in re.finditer(r'<h2 id="([^"]+)">(.*?)</h2>', body)]


parts = sorted(f for f in os.listdir(HERE) if re.fullmatch(r'part\d+\.html', f))
body = '\n'.join(open(os.path.join(HERE, f), encoding='utf-8').read() for f in parts)
n_qa = n_quiz = 0


def repl(m):
    global n_qa, n_quiz
    lang, src = m.group(1), m.group(2)
    if lang == 'qa':
        h, n = qa_block(src); n_qa += n; return h
    if lang == 'quiz':
        h, n = quiz_block(src); n_quiz += n; return h
    return code_block(lang, src)


body = re.sub(r'^```(\w+)\n(.*?)\n```$', repl, body, flags=re.S | re.M)
assert '```' not in body, 'unclosed fence'

base = open(os.path.join(ROOT, 'giao-trinh-python-ai-engineer.html'), encoding='utf-8').read()
style = base[base.index('<style>'):base.index('</style>')]
style += '''
h4{font-size:16.5px;margin:28px 0 8px;color:#1f2328}
h4 code{font-size:.85em}
.tag{display:inline-block;font-size:11.5px;font-weight:600;padding:1px 8px;border-radius:999px;vertical-align:middle;margin-left:4px;white-space:nowrap}
.tag.must{background:#fde8e8;color:#b42318}.tag.should{background:#e7f1fb;color:#1a5fb4}.tag.plus{background:#e5f4e4;color:#1a7f37}
h3.rev{margin-top:36px;padding-top:16px;border-top:1px dashed #c9c3ef}
p.hint{color:var(--muted);font-size:14px;margin-top:0}
details.qa{background:#fff;border:1px solid var(--line);border-radius:10px;margin:8px 0;padding:0 16px}
details.qa summary{cursor:pointer;padding:12px 0;font-weight:600;list-style:none}
details.qa summary::-webkit-details-marker{display:none}
details.qa summary::before{content:"▸ ";color:var(--accent)} details.qa[open] summary::before{content:"▾ "}
details.qa .ans{border-top:1px solid var(--line);padding:10px 0 12px;color:#2d333a}
details.qa .ans p{margin:4px 0}
.quiz{background:#fff;border:1px solid var(--line);border-radius:12px;padding:8px 18px 4px}
.quiz .score{position:sticky;top:0;background:#fff;margin:0;padding:8px 0;color:var(--muted);font-size:14px;border-bottom:1px solid var(--line);z-index:1}
.qz{padding:12px 0;border-bottom:1px solid var(--line)} .qz:last-child{border-bottom:none}
.qq{margin:0 0 8px;font-weight:600}
ol.opts{list-style:none;padding:0;margin:0;display:grid;gap:6px}
ol.opts li{margin:0}
ol.opts button{width:100%;text-align:left;font:inherit;font-size:15px;color:inherit;background:#fbfaf7;border:1px solid var(--line);border-radius:8px;padding:8px 12px;cursor:pointer}
ol.opts button:hover:not(:disabled){border-color:var(--accent)}
ol.opts button:disabled{cursor:default}
ol.opts button.right{background:#e5f4e4;border-color:#2ea043}
ol.opts button.wrong{background:#fbebeb;border-color:#d64545}
.qz .ex{display:none;margin:8px 0 0;padding:8px 12px;background:#f4f2fd;border-radius:8px;font-size:14.5px}
.qz.answered .ex{display:block}
ul.check{list-style:none;padding:0}
ul.check li{margin:0;padding:8px 12px;border:1px solid var(--line);border-top:none;background:#fff}
ul.check li:first-child{border-top:1px solid var(--line);border-radius:10px 10px 0 0} ul.check li:last-child{border-radius:0 0 10px 10px}
ul.check label{display:flex;gap:8px;align-items:flex-start;cursor:pointer} ul.check input{margin-top:5px;flex:none}
ul.check li:has(input:checked){background:#f2faf1}
@media print{
  ul.check li{break-inside:avoid} h4{font-size:11.5pt;break-after:avoid}
  details.qa{break-inside:avoid;border:none;border-bottom:1px solid var(--line);border-radius:0;padding:0}
  details.qa summary::before{content:""} details.qa summary{padding:8px 0 2px}
  details.qa .ans{border:none;padding:0 0 8px}
  .quiz{border:none;padding:0} .quiz .score{display:none}
  .qz{break-inside:avoid;padding:8px 0}
  ol.opts{gap:2px} ol.opts button{border:none;background:none;padding:1px 0;font-size:10pt}
  .qz .ex{display:block;background:none;padding:2px 0 0;font-size:9.5pt;color:#57606a}
  .tag{border:1px solid currentColor}
}
'''
script = '''<script>
document.querySelectorAll('.quiz').forEach(qb => {
  const done = qb.querySelector('.done'), right = qb.querySelector('.right');
  qb.querySelectorAll('.qz').forEach(q => q.querySelectorAll('button').forEach(b => b.addEventListener('click', () => {
    if (q.classList.contains('answered')) return;
    q.classList.add('answered');
    q.querySelectorAll('button').forEach(x => { x.disabled = true; if (x.dataset.ok === '1') x.classList.add('right'); });
    if (b.dataset.ok !== '1') b.classList.add('wrong'); else right.textContent = +right.textContent + 1;
    done.textContent = +done.textContent + 1;
  })));
});
document.querySelectorAll('ul.check input').forEach((c, i) => {
  const k = 'nodejs-check-' + i;
  try { c.checked = localStorage.getItem(k) === '1'; } catch (e) {}
  c.addEventListener('change', () => { try { localStorage.setItem(k, c.checked ? '1' : '0'); } catch (e) {} });
});
</script>'''
toc = ''.join(f'<a href="#{i}">{esc(t, quote=False)}</a>' for i, t in slug_toc(body))
page = ('<!DOCTYPE html>\n<html lang="vi"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">\n'
        f'<title>{TITLE}</title>\n{style}</style></head>\n'
        f'<body><div class="wrap"><nav><details id="toc" open><summary class="t">Mục lục</summary>{toc}</details></nav>\n'
        '<script>if(matchMedia("(max-width:900px)").matches)document.getElementById("toc").removeAttribute("open")</script><main>\n'
        f'<h1 id="top">{TITLE}</h1>\n<p><time datetime="2026-11-18">2026-11-18</time> · Ôn tập để ứng tuyển Middle Fullstack · '
        f'{n_qa} câu hỏi ôn tập · {n_quiz} câu trắc nghiệm</p>\n'
        + body + '\n</main></div>\n' + script + '\n</body>\n</html>\n')
open(os.path.join(ROOT, OUT), 'w', encoding='utf-8').write(page)
print(f'{OUT}: {len(page)//1024} KB, {len(slug_toc(body))} sections, {n_qa} qa, {n_quiz} quiz')

if '--pdf' in sys.argv:
    printable = page.replace('<details class="qa">', '<details class="qa" open>')
    with tempfile.NamedTemporaryFile('w', suffix='.html', delete=False, encoding='utf-8') as f:
        f.write(printable); tmp = f.name
    pdf = os.path.join(ROOT, 'pdf', OUT.replace('.html', '.pdf'))
    subprocess.run(['google-chrome', '--headless', '--disable-gpu', '--no-pdf-header-footer',
                    f'--print-to-pdf={pdf}', 'file://' + tmp], check=True, capture_output=True)
    os.unlink(tmp)
    print('PDF:', pdf)
