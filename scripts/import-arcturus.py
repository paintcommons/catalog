"""One-time, offline, additive Arcturus import. Run from any directory with Python 3.

The pinned baseline makes reports reproducible after committing. Existing paint objects
are never changed. Ambiguous identities and conflicting upstream codes are withheld.
"""
import collections
import hashlib
import json
import math
import pathlib
import re
import subprocess
import sys
import unicodedata

ROOT = pathlib.Path(__file__).resolve().parent.parent
BASE = 'cc6ddee'
REVISION = '22791a682e1d155da388f4f856cd7196cd9f2677'
SOURCE = 'arcturus-miniature-paints-22791a6'
VENDOR = ROOT / 'data/upstream/arcturus-22791a6'
REPORT = ROOT / 'reports/arcturus-import'
BRANDS = {'AK': 'AK Interactive', 'AKRC': 'AK Interactive', 'Army_Painter': 'The Army Painter',
          'Citadel_Colour': 'Citadel', 'CoatDArmes': "Coat d'Arms", 'Creature': 'Monument Hobbies',
          'Duncan': 'Duncan Rhodes', 'FolkArt': 'FolkArt', 'GreenStuffWorld': 'Green Stuff World',
          'KimeraKolors': 'Kimera Kolors', 'Mig': 'AMMO by Mig Jimenez', 'Monument': 'Monument Hobbies',
          'MrHobby': 'Mr Hobby', 'MrPaint': 'Mr Paint', 'Scale75': 'Scale75',
          'TomColor': 'Tom Color', 'TurboDork': 'Turbo Dork', 'AppleBarrel': 'Apple Barrel',
          'MissionModels': 'Mission Models'}

def norm(value):
    return re.sub(r'[^a-z0-9]', '', unicodedata.normalize('NFKD', value or '').lower())

def slug(value):
    value = unicodedata.normalize('NFKD', value or '').encode('ascii', 'ignore').decode().lower()
    return re.sub(r'[^a-z0-9]+', '-', value.replace('&', ' and ')).strip('-') or 'general'

def family(brand, value):
    """Only known range aliases; never conflate brush, air, or product generations."""
    value = value or ''
    if brand == 'Citadel':
        return norm(value)
    if brand == 'Vallejo':
        if value in ('Game Color Wash', 'Game Wash'): return 'gamewash'
        if value in ('Game Color Ink', 'Game Ink'): return 'gameink'
        # Current catalogue separates finishes; older upstream groups them together.
        value = re.sub(r' (Metallic|Fluo|Fluorescent|Varnish|Weathering)$', '', value)
    if brand == 'The Army Painter':
        value = {'Warpaints': 'Warpaints (original)', 'Speedpaint Set 2.0': 'Speedpaint 2.0',
                 'Speedpaint Set': 'Speedpaint (original)'}.get(value, value)
        value = re.sub(r' (Metallic|Effects|Wash)$', '', value) if 'Fanatic' in value or '(original)' in value else value
    if brand == 'Monument Hobbies':
        value = value.replace('Monument ', '').replace('ProAcryl', 'Pro Acryl')
        value = {'Pro Acrylic Paints': 'Pro Acryl', 'Pro Signature Series': 'Pro Acryl Signature Series'}.get(value, value)
        value = value.replace('Pro Acryl Transparent', 'Pro Acryl')
    return norm(value)

def codekey(brand, code):
    if not code: return None
    # Display formatting differs, but product codes retain their original spelling in records.
    key = norm(code)
    if brand == 'Monument Hobbies': key = re.sub(r'^mpa', '', key)
    if brand == 'Reaper' and key.isdigit(): key = str(int(key))
    return brand, key

def oklab(hex_value):
    rgb = [int(hex_value[i:i+2], 16) / 255 for i in (1, 3, 5)]
    r, g, b = [v / 12.92 if v <= .04045 else ((v+.055)/1.055)**2.4 for v in rgb]
    l = (.4122214708*r+.5363325363*g+.0514459929*b)**(1/3)
    m = (.2119034982*r+.6806995451*g+.1073969566*b)**(1/3)
    s = (.0883024619*r+.2817188376*g+.6299787005*b)**(1/3)
    return (.2104542553*l+.793617785*m-.0040720468*s,
            1.9779984951*l-2.428592205*m+.4505937099*s,
            .0259040371*l+.7827717662*m-.808675766*s)

def distance(a, b):
    return math.dist(oklab(a), oklab(b))

def read_upstream():
    rows = []
    manifest = json.loads((VENDOR / 'SOURCE.json').read_text())
    if manifest['revision'] != REVISION: raise ValueError('Unexpected source revision')
    for file in sorted(VENDOR.glob('*.md')):
        data = file.read_bytes()
        blob = hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
        if manifest['git_blob_sha1'].get(file.name) != blob: raise ValueError(f'Upstream snapshot changed: {file}')
        headers = None
        for line_no, line in enumerate(file.read_text().splitlines(), 1):
            if not line.startswith('|'): continue
            cells = [c.strip() for c in line.strip().split('|')[1:-1]]
            if cells[0] == 'Name': headers = cells; continue
            if not headers or not re.search(r'`#[a-fA-F0-9]{6}`', line): continue
            if len(cells) != len(headers): raise ValueError(f'{file}:{line_no}: malformed row')
            raw = dict(zip(headers, cells))
            hex_value = re.search(r'`(#[a-fA-F0-9]{6})`', raw['Hex'])[1].upper()
            if hex_value != '#' + ''.join(f'{int(raw[c]):02X}' for c in ('R', 'G', 'B')):
                raise ValueError(f'{file}:{line_no}: RGB and hex disagree')
            code = raw.get('Code')
            if code in (None, '', 'null', 'None'): code = None
            brand = BRANDS.get(file.stem, file.stem)
            range_name = raw['Set'] or None
            if brand == 'Monument Hobbies':
                range_name = (range_name or '').replace('Monument ', '').replace('ProAcryl', 'Pro Acryl') or None
            if brand == 'The Army Painter':
                range_name = {'Warpaints': 'Warpaints (original)', 'Speedpaint Set 2.0': 'Speedpaint 2.0',
                              'Speedpaint Set': 'Speedpaint (original)'}.get(range_name, range_name)
            rows.append({'brand': brand, 'range': range_name, 'code': code, 'name': raw['Name'],
                         'hex': hex_value, 'file': file.name, 'line': line_no,
                         'url': f'https://github.com/Arcturus5404/miniature-paints/blob/{REVISION}/paints/{file.name}#L{line_no}'})
    return rows

def paint_type(row):
    # Upstream has no general-purpose paint-type field. Avoid inventing chemistry.
    text = (row['range'] or '').lower()
    for token, kind in [('primer', 'primer'), ('varnish', 'varnish'), ('wash', 'wash'),
                        ('ink', 'ink'), ('speedpaint', 'speedpaint'), ('xpress', 'speedpaint'),
                        ('metallic', 'metallic'), ('metal color', 'metallic'),
                        ('medium', 'medium'), ('effect', 'effect')]:
        if token in text: return kind
    if 'acrylic' in text or '3rd gen' in text or row['brand'] in ('Citadel', 'Monument Hobbies'):
        if text == 'shade': return 'wash'
        if text == 'contrast': return 'speedpaint'
        return 'acrylic'
    return 'other'

def run():
    git = lambda *args: subprocess.check_output(['git', *args], cwd=ROOT, text=True)
    baseline = {}
    for file in git('ls-tree', '-r', '--name-only', BASE, '--', 'paints').splitlines():
        if file.endswith('.json'): baseline[file] = json.loads(git('show', f'{BASE}:{file}'))
    existing = [p for values in baseline.values() for p in values]
    by_code = collections.defaultdict(list)
    by_name = collections.defaultdict(list)
    for p in existing:
        if p['code']: by_code[codekey(p['brand'], p['code'])].append(p)
        by_name[(p['brand'], norm(p['name']))].append(p)
    rows = read_upstream()
    grouped = collections.defaultdict(list)
    for r in rows:
        key = codekey(r['brand'], r['code']) or (r['brand'], family(r['brand'], r['range']), norm(r['name']))
        grouped[key].append(r)
    additions = []; decisions = []; comparisons = []; held = []; seen = {}
    for r in rows:
        record = {**r}
        if not r['name'].strip():
            decisions.append({**record, 'decision': 'withheld-empty-name'}); held.append(decisions[-1]); continue
        matches = by_code.get(codekey(r['brand'], r['code']), []) if r['code'] else []
        basis = 'code'
        if not matches:
            matches = [p for p in by_name[(r['brand'], norm(r['name']))]
                       if family(p['brand'], p['range']) == family(r['brand'], r['range'])]
            basis = 'name-and-range'
        # Turbo Dork's upstream table has no finish/shift subdivision. A unique exact name
        # in the existing manufacturer catalogue is safer than inventing a duplicate range.
        if not matches and r['brand'] == 'Turbo Dork':
            matches = by_name[(r['brand'], norm(r['name']))]; basis = 'unique-name-existing-brand'
        if matches:
            decisions.append({**record, 'decision': 'preserved-existing', 'match_basis': basis,
                              'existing_ids': [p['id'] for p in matches]})
            for p in matches:
                if p.get('colour'):
                    delta = distance(p['colour']['hex'], r['hex'])
                    comparisons.append({**record, 'existing_id': p['id'], 'existing_name': p['name'],
                                        'existing_range': p['range'], 'existing_hex': p['colour']['hex'],
                                        'existing_colour_source': p['colour']['source'], 'match_basis': basis,
                                        'name_disagrees': norm(p['name']) != norm(r['name']),
                                        'oklab_distance': round(delta, 6), 'substantial': delta >= .08})
            continue
        # Uncertain same-name matches in a differently labelled range need review, not a guess.
        same_name = by_name[(r['brand'], norm(r['name']))]
        distinct_product_range = (r['brand'] == 'Citadel' and (r['range'] == 'Spray' or 'discontinued' in (r['range'] or ''))) or (r['brand'] == 'The Army Painter' and r['range'] in ('Warpaints Air', 'Speedpaint (original)', 'Warpaints Fanatic'))
        if same_name and not r['code'] and not distinct_product_range:
            decisions.append({**record, 'decision': 'withheld-ambiguous-existing-range',
                              'existing_ids': [p['id'] for p in same_name]}); held.append(decisions[-1]); continue
        key = codekey(r['brand'], r['code']) or (r['brand'], family(r['brand'], r['range']), norm(r['name']))
        peers = grouped[key]
        if len({(norm(p['name']), p['hex']) for p in peers}) > 1:
            decisions.append({**record, 'decision': 'withheld-conflicting-upstream-identity'}); held.append(decisions[-1]); continue
        if key in seen:
            decisions.append({**record, 'decision': 'duplicate-upstream', 'canonical_url': seen[key]}); continue
        seen[key] = r['url']
        p = {k: r[k] for k in ('brand', 'range', 'code', 'name')}
        p.update(type=paint_type(r), barcodes=[], colour={'hex': r['hex'], 'gradient': None, 'source': SOURCE}, status='discontinued' if 'discontinued' in (r['range'] or '').lower() else 'current')
        path = f"paints/{slug(p['brand'])}/{slug(p['range'])}.json"
        additions.append((path, p))
        decisions.append({**record, 'decision': 'added', 'catalogue_file': path,
                          'type_basis': 'explicit range wording where available; otherwise other',
                          'availability_note': 'Discontinued when explicitly stated upstream; otherwise current is the contribution default, not a manufacturer verification.'})
    # Preserve schema uniqueness when upstream assigns two codes to the same name/range.
    collisions = collections.Counter((p['brand'], p['range'], p['name'].lower()) for _, p in additions)
    conflicting = {(p['brand'], p['range'], p['name'].lower()) for _, p in additions
                   if collisions[(p['brand'], p['range'], p['name'].lower())] > 1}
    for d in decisions:
        if d['decision'] == 'added' and (d['brand'], d['range'], d['name'].lower()) in conflicting:
            d['decision'] = 'withheld-conflicting-upstream-name'; held.append(d)
    additions = [(path, p) for path, p in additions if (p['brand'], p['range'], p['name'].lower()) not in conflicting]
    files = {k: list(v) for k, v in baseline.items()}
    for path, p in additions: files.setdefault(path, []).append(p)
    # Refuse to replace unrelated work or alter a baseline record.
    previous = json.loads((REPORT / 'decisions.json').read_text()) if (REPORT / 'decisions.json').exists() else []
    prior_keys = {(d['brand'], d['range'], d['code'], d['name']) for d in previous if d['decision'] == 'added'}
    obsolete = []
    for path in ROOT.joinpath('paints').glob('*/*.json'):
        rel = str(path.relative_to(ROOT)); current = json.loads(path.read_text())
        expected = files.get(rel)
        if any(p not in (expected or []) and (p.get('id') or (p['brand'], p['range'], p['code'], p['name']) not in prior_keys) for p in current):
            raise ValueError(f'Refusing to overwrite unrelated changes in {rel}')
        if expected is None: obsolete.append(path)
    for path in obsolete: path.unlink()
    for path, values in files.items():
        target = ROOT / path
        if values == baseline.get(path):
            target.write_text(git('show', f'{BASE}:{path}')); continue
        target.parent.mkdir(parents=True, exist_ok=True)
        # Existing objects are preserved exactly; only their array order may change.
        values.sort(key=lambda p: (p['code'] is None, p['code'] or '', p['name']))
        target.write_text(json.dumps(values, ensure_ascii=False, indent=2) + '\n')
    REPORT.mkdir(parents=True, exist_ok=True)
    comparisons.sort(key=lambda p: -p['oklab_distance'])
    summary = {'upstream_revision': REVISION, 'baseline_revision': git('rev-parse', BASE).strip(),
               'baseline_records': len(existing), 'upstream_hobby_rows': len(rows), 'added': len(additions),
               'total_records': len(existing)+len(additions), 'preserved_existing_records': len(existing),
               'decisions': dict(collections.Counter(r['decision'] for r in decisions)),
               'added_by_brand': dict(sorted(collections.Counter(p['brand'] for _, p in additions).items())),
               'colour_comparisons': len(comparisons), 'substantial_colour_disagreements': sum(c['substantial'] for c in comparisons),
               'substantial_threshold': {'metric': 'Euclidean OKLab, sRGB D65, scale 0–1', 'minimum': .08},
               'snapshot_sha256': {f.name: hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted(VENDOR.iterdir())}}
    outputs = [('summary', summary), ('decisions', decisions)]
    if '--review-reports' in sys.argv:
        outputs += [('withheld', held), ('colour-comparisons', comparisons),
                    ('colour-disagreements', [c for c in comparisons if c['substantial']])]
    for name, data in outputs:
        (REPORT / (name+'.json')).write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps(summary, indent=2))

if __name__ == '__main__': run()
