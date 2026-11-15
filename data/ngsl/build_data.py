"""Build the English vocab page.

Usage: python3 data/ngsl/build_data.py data/ngsl <cmudict.dict> Tu-vung-tieng-Anh-NGSL.html
cmudict.dict: https://raw.githubusercontent.com/cmusphinx/cmudict/master/cmudict.dict
Inputs: NGSL_12_stats.csv, SUP_lemmatized.csv and b*.txt (word|pos|vi|example|example_vi).
"""
import csv, glob, json, re, sys

D, CMU, OUT = sys.argv[1], sys.argv[2], sys.argv[3]

# --- CMU dict ---
cmu = {}
for line in open(CMU, encoding='utf-8'):
    line = line.split('#')[0].strip()
    if not line:
        continue
    head, *ph = line.split()
    m = re.match(r'^(.+?)(?:\((\d+)\))?$', head)
    cmu.setdefault(m.group(1), []).append(ph)

V = {'AA': 'ɑː', 'AE': 'æ', 'AH': 'ʌ', 'AO': 'ɔː', 'AW': 'aʊ', 'AY': 'aɪ', 'EH': 'ɛ', 'ER': 'ɝː',
     'EY': 'eɪ', 'IH': 'ɪ', 'IY': 'iː', 'OW': 'oʊ', 'OY': 'ɔɪ', 'UH': 'ʊ', 'UW': 'uː'}
C = {'B': 'b', 'CH': 'tʃ', 'D': 'd', 'DH': 'ð', 'F': 'f', 'G': 'ɡ', 'HH': 'h', 'JH': 'dʒ', 'K': 'k',
     'L': 'l', 'M': 'm', 'N': 'n', 'NG': 'ŋ', 'P': 'p', 'R': 'r', 'S': 's', 'SH': 'ʃ', 'T': 't',
     'TH': 'θ', 'V': 'v', 'W': 'w', 'Y': 'j', 'Z': 'z', 'ZH': 'ʒ'}
ONSETS = {(c,) for c in C if c != 'NG'} | {tuple(o.split()) for o in '''B L|B R|D R|D W|F L|F R|G L|G R|G W|K L|K R|K W|P L|P R|T R|T W|TH R|SH R|S K|S L|S M|S N|S P|S T|S W|S F
S K R|S K W|S P L|S P R|S T R|S K Y|P Y|B Y|F Y|K Y|M Y|HH Y|V Y|G Y|L Y|N Y|TH W'''.replace('\n', '|').split('|') if o.strip()}


def ipa(ph):
    toks = []
    for p in ph:
        m = re.match(r'([A-Z]+)(\d)?$', p)
        toks.append((m.group(1), m.group(2)))
    # ER0 directly before a vowel = schwa + r (a-rrest, op-er-ate)
    fixed = []
    for i, t in enumerate(toks):
        nxt = toks[i + 1] if i + 1 < len(toks) else None
        if t == ('ER', '0') and nxt and nxt[1] is not None:
            fixed += [('AH', '0'), ('R', None)]
        else:
            fixed.append(t)
    toks = fixed
    # word-final -y with secondary stress (compan-y, categor-y) is unstressed /i/
    if toks and toks[-1] == ('IY', '2'):
        toks[-1] = ('IY', '0')
    # no secondary stress on an unstressed-sounding first syllable (im-, in-, ex- before primary)
    vs = [i for i, t in enumerate(toks) if t[1] is not None]
    if len(vs) > 1 and toks[vs[0]] in (('IH', '2'), ('EH', '2')) and toks[vs[1]][1] == '1':
        toks[vs[0]] = (toks[vs[0]][0], '0')
    out = [''] * len(toks)
    marks = {}
    vowel_idx = [i for i, (b, s) in enumerate(toks) if s is not None]
    for i, (b, s) in enumerate(toks):
        if s is None:
            out[i] = C[b]
        else:
            if b == 'AH' and s == '0':
                out[i] = 'ə'
            elif b == 'ER' and s == '0':
                out[i] = 'ɚ'
            elif b == 'IY' and s == '0':
                out[i] = 'i'
            elif b == 'UW' and i + 1 < len(toks) and toks[i + 1][0] == 'R':
                out[i] = 'ʊ'
            elif b == 'UW' and s == '0':
                out[i] = 'u'
            else:
                out[i] = V[b]
    if len(vowel_idx) > 1:
        prev_v = -1
        for vi in vowel_idx:
            s = toks[vi][1]
            if s in ('1', '2'):
                # consonants between previous vowel and this vowel: take the longest legal onset
                cons = list(range(prev_v + 1, vi))
                start = vi
                for k in range(len(cons)):
                    cand = tuple(toks[j][0] for j in cons[k:])
                    if cand in ONSETS:
                        start = cons[k]
                        break
                marks[start] = 'ˈ' if s == '1' else 'ˌ'
            prev_v = vi
    return ''.join((marks.get(i, '') + out[i]) for i in range(len(toks)))


# word -> list of (cmu variant index 1-based, label); multiple entries => heteronym flag
HET = {
 'read': [(2, 'hiện tại'), (1, 'quá khứ')], 'live': [(2, 'v: sống'), (1, 'adj: trực tiếp')],
 'lead': [(2, 'v: dẫn'), (1, 'n: chì')], 'record': [(2, 'n'), (3, 'v')],
 'present': [(1, 'n, adj'), (2, 'v')], 'object': [(1, 'n'), (2, 'v')], 'project': [(1, 'n'), (2, 'v')],
 'close': [(2, 'v: đóng'), (1, 'adj: gần')], 'use': [(2, 'v'), (1, 'n')],
 'wind': [(2, 'n: gió'), (1, 'v: quấn')], 'tear': [(2, 'n: nước mắt'), (1, 'v: xé')],
 'wound': [(2, 'n: vết thương'), (1, 'quá khứ của wind')], 'minute': [(1, 'n: phút'), (3, 'adj: nhỏ xíu')],
 'content': [(1, 'n: nội dung'), (2, 'adj: hài lòng')], 'desert': [(1, 'n: sa mạc'), (2, 'v: bỏ rơi')],
 'produce': [(1, 'v'), (2, 'n: nông sản')], 'increase': [(1, 'v'), (2, 'n')], 'decrease': [(1, 'v'), (2, 'n')],
 'permit': [(1, 'v'), (2, 'n')], 'contract': [(1, 'n'), (2, 'v')], 'conduct': [(2, 'v'), (1, 'n')],
 'subject': [(2, 'n'), (1, 'v')], 'refuse': [(3, 'v: từ chối'), (2, 'n: rác')],
 'separate': [(3, 'adj'), (1, 'v')], 'estimate': [(1, 'n'), (2, 'v')], 'graduate': [(1, 'n'), (2, 'v')],
 'excuse': [(1, 'n'), (2, 'v')], 'moderate': [(1, 'adj')], 'appropriate': [(1, 'adj')],
 'associate': [(2, 'v'), (1, 'n')], 'attribute': [(2, 'v'), (1, 'n')], 'import': [(1, 'v'), (2, 'n')],
 'transfer': [(1, 'v'), (2, 'n')], 'perfect': [(2, 'adj')], 'conflict': [(1, 'n')],
 'contrast': [(1, 'n'), (2, 'v')], 'extract': [(2, 'v'), (1, 'n')], 'convert': [(2, 'v')],
 'progress': [(1, 'n'), (2, 'v')], 'address': [(1, 'n'), (2, 'v')], 'survey': [(2, 'n'), (1, 'v')],
 'abuse': [(1, 'n'), (2, 'v')], 'advocate': [(2, 'v'), (1, 'n')], 'combine': [(2, 'v')],
 'discount': [(2, 'n'), (1, 'v')], 'suspect': [(1, 'v'), (2, 'n')], 'protest': [(1, 'n'), (2, 'v')],
 'complex': [(1, 'adj')], 'upset': [(1, 'adj, v')], 'construct': [(1, 'v')], 'compound': [(1, 'n')],
 'alternate': [(1, 'adj')], 'segment': [(1, 'n')], 'export': [(1, 'v')],
}

FUNC = {
 'the': '/ðə/ · trước nguyên âm /ðiː/', 'a': '/ə/ · nhấn mạnh /eɪ/', 'and': '/ænd/ · yếu /ənd/',
 'to': '/tuː/ · yếu /tə/', 'for': '/fɔːr/ · yếu /fɚ/', 'of': '/ʌv/ · yếu /əv/', 'from': '/frʌm/ · yếu /frəm/',
 'at': '/æt/ · yếu /ət/', 'can': '/kæn/ · yếu /kən/', 'that': '/ðæt/ · yếu /ðət/', 'than': '/ðæn/ · yếu /ðən/',
 'or': '/ɔːr/ · yếu /ɚ/', 'as': '/æz/ · yếu /əz/', 'but': '/bʌt/ · yếu /bət/', 'have': '/hæv/ · yếu /həv/',
 'do': '/duː/ · yếu /də/', 'must': '/mʌst/ · yếu /məst/', 'some': '/sʌm/ · yếu /səm/',
 'will': '/wɪl/ · yếu /wəl/', 'would': '/wʊd/ · yếu /wəd/', 'shall': '/ʃæl/ · yếu /ʃəl/',
 'you': '/juː/ · yếu /jə/', 'be': '/biː/', 'was': '/wʌz/ · yếu /wəz/', 'were': '/wɝː/ · yếu /wɚ/',
 'an': '/æn/ · yếu /ən/', 'he': '/hiː/', 'she': '/ʃiː/', 'we': '/wiː/', 'me': '/miː/',
}
MANUAL = {'quadrillion': '/kwɑːˈdrɪljən/', 'quintillion': '/kwɪnˈtɪljən/'}
ngsl = [r['Lemma'] for r in csv.DictReader(open(D + '/NGSL_12_stats.csv'))]
ngsl = [w.lower() if w in ('TRUE', 'FALSE') else w for w in ngsl]
rank = {w: i + 1 for i, w in enumerate(ngsl)}

rows = []
for f in sorted(glob.glob(D + '/b*.txt')):
    for l in open(f, encoding='utf-8'):
        l = l.rstrip('\n')
        if l.strip():
            rows.append(l.split('|'))

data, missing = [], []
for w, pos, vi, ex, exvi in rows:
    r = rank.get(w)
    lv = 7 if r is None else min((r - 1) // 500 + 1, 6)
    key = w.lower()
    vars_ = cmu.get(key)
    if not vars_ and key in MANUAL:
        data.append({'lv': lv, 'w': w, 'pos': pos, 'vi': vi, 'ex': ex, 'exvi': exvi, 'ipa': MANUAL[key]})
        continue
    if not vars_:
        missing.append(w)
        continue
    entry = {'lv': lv, 'w': w, 'pos': pos, 'vi': vi, 'ex': ex, 'exvi': exvi}
    if key in HET:
        spec = HET[key]
        if len(spec) == 1:
            entry['ipa'] = '/' + ipa(vars_[spec[0][0] - 1]) + '/'
        else:
            entry['ipa'] = ' · '.join(f"/{ipa(vars_[i - 1])}/ ({lab})" for i, lab in spec)
            entry['het'] = 1
    else:
        entry['ipa'] = FUNC.get(key) or '/' + ipa(vars_[0]) + '/'
    data.append(entry)

js = json.dumps(data, ensure_ascii=False, separators=(',', ':'))
if OUT.endswith('.html'):
    import os
    tpl = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'template.html'), encoding='utf-8').read()
    assert tpl.count('__DATA__') == 1
    open(OUT, 'w', encoding='utf-8').write(tpl.replace('__DATA__', js.replace('</', '<\\/')))
else:
    open(OUT, 'w', encoding='utf-8').write(js)
from collections import Counter
print('entries', len(data), 'missing pron', missing)
print(sorted(Counter(d['lv'] for d in data).items()), 'heteronyms', sum(1 for d in data if d.get('het')))
for w in ['a', 'of', 'to', 'can', 'at', 'from', 'that', 'quadrillion', 'the', 'and', 'information', 'government', 'read', 'record', 'university', 'interesting', 'comfortable', 'strength', 'I', 'May', 'thousand', 'extraordinary', 'photograph', 'available']:
    for d in data:
        if d['w'] == w:
            print(f"  {w:14} {d['ipa']}")
            break
