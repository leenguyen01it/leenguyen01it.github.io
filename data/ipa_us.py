"""US IPA from the CMU Pronouncing Dictionary, with fixes for learners."""
import re

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

LETTERS = {'A': 'eɪ', 'B': 'biː', 'C': 'siː', 'D': 'diː', 'E': 'iː', 'F': 'ɛf', 'G': 'dʒiː', 'H': 'eɪtʃ',
           'I': 'aɪ', 'J': 'dʒeɪ', 'K': 'keɪ', 'L': 'ɛl', 'M': 'ɛm', 'N': 'ɛn', 'O': 'oʊ', 'P': 'piː',
           'Q': 'kjuː', 'R': 'ɑːr', 'S': 'ɛs', 'T': 'tiː', 'U': 'juː', 'V': 'viː', 'W': 'ˈdʌbəljuː',
           'X': 'ɛks', 'Y': 'waɪ', 'Z': 'ziː'}


class Pron:
    def __init__(self, cmu_path, manual=None):
        self.cmu = {}
        for line in open(cmu_path, encoding='utf-8'):
            line = line.split('#')[0].strip()
            if not line:
                continue
            head, *ph = line.split()
            m = re.match(r'^(.+?)(?:\((\d+)\))?$', head)
            self.cmu.setdefault(m.group(1), []).append(ph)
        self.manual = manual or {}

    def word(self, w):
        """IPA (without slashes) of one plain word, or None."""
        k = w.lower()
        if k in self.manual:
            return self.manual[k].strip('/')
        v = self.cmu.get(k)
        return ipa(v[0]) if v else None

    def entry(self, w):
        """Return (ipa_display, is_heteronym) for a headword; ipa_display '' if unknown."""
        k = w.lower()
        if k in self.manual:
            return self.manual[k], False
        if re.fullmatch(r'[A-Z]{2,}(/[A-Z]{2,})?', w):          # acronym: API, CI/CD
            ls = [LETTERS[c] for c in w if c != '/']
            return '/ˌ' + ' ˌ'.join(ls[:-1]) + ' ˈ' + ls[-1] + '/', False
        vars_ = self.cmu.get(k)
        if vars_ and k in HET:
            spec = HET[k]
            if len(spec) == 1:
                return '/' + ipa(vars_[spec[0][0] - 1]) + '/', False
            return ' · '.join(f"/{ipa(vars_[i - 1])}/ ({lab})" for i, lab in spec), True
        if vars_:
            return FUNC.get(k) or '/' + ipa(vars_[0]) + '/', False
        parts = re.split(r'[ \-]', w)
        if len(parts) > 1:
            ps = [self.word(p) for p in parts]
            if all(ps):
                return '/' + ' '.join(ps) + '/', False
        return '', False
