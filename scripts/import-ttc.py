"""Reproduce the TTC factual enrichment from pinned catalogue data, offline.

Only the 30 new Dark Arts paints receive GERInFact numeric hex values.
Existing colours are preserved. See reports/two-thin-coats.
"""
import copy
import hashlib
import json
import pathlib
import re
import subprocess

ROOT = pathlib.Path(__file__).resolve().parent.parent
BASE = '6bf3e7ebaa8d6b6e591c79f769844b4594f13138'
SOURCES = ROOT / 'data/sources'
REPORT = ROOT / 'reports/two-thin-coats'
SWATCHES = ROOT / 'data/upstream/gerinfact-235dc3f'
COLOUR_SOURCE = 'gerinfact-ttc-235dc3f'
ALIASES = {
    'Death Metal': 'Doom Metal',
    'Elder Robe': 'Eldar Robe',
    'Matt Varnish': 'Satin Varnish',
    "Ritz O'Tin": 'Bitz O’ Tin',
    'Septric Green': 'Septic Green',
    'Von Evile Pimple': 'Von Evile Purple',
    'Batle Axe Brass': 'Battle Axe Brass',
    'Helion Red Wash': 'Hellion Red Wash',
    'Keleton Legion': 'Skeleton Legion',
    'Merald Green': 'Emerald Green',
    'RC Flesh Wash': 'Orc Flesh Wash',
    "Sorceror's Cloak": 'Sorcerer’s Cloak',
    'Ur Cloak': 'Fur Cloak',
}


def normalise(name):
    return re.sub('[^a-z0-9]', '', name.lower())


def baseline():
    files = subprocess.check_output(
        ['git', 'ls-tree', '-r', '--name-only', BASE, '--', 'paints'],
        cwd=ROOT, text=True).splitlines()
    return {f: json.loads(subprocess.check_output(
        ['git', 'show', f'{BASE}:{f}'], cwd=ROOT, text=True))
        for f in files if f.endswith('.json')}


def read_swatches():
    metadata = json.loads((SWATCHES / 'SOURCE.json').read_text())
    raw = (SWATCHES / metadata['derived_file']).read_bytes()
    if hashlib.sha256(raw).hexdigest() != metadata['derived_sha256']:
        raise ValueError('GERInFact numeric snapshot failed its integrity check')
    rows = json.loads(raw)
    assert len(rows) == len({r['name'] for r in rows}) == 210
    assert all(re.fullmatch('#[0-9A-F]{6}', r['hex']) for r in rows)
    return rows


def build():
    products = json.loads((SOURCES / 'ttc-manufacturer-products.json').read_text())
    additions = json.loads((SOURCES / 'ttc-additions.json').read_text())
    swatches = {p['name']: p for p in read_swatches()}
    by_name = {normalise(p['name']): p for p in products}
    assert len(by_name) == len(products) == 180
    output, changes, used = {}, [], set()
    for file, paints in baseline().items():
        if not file.startswith('paints/duncan-rhodes/'):
            continue
        updated = []
        for old in paints:
            product = by_name[normalise(ALIASES.get(old['name'], old['name']))]
            assert product['code'] not in used, old['name']
            used.add(product['code'])
            paint = copy.deepcopy(old)
            paint.update(brand='Two Thin Coats', name=product['name'], code=product['code'])
            barcode = dict(ean=product['ean'], source='published', source_url=product['source_url'])
            if barcode not in paint['barcodes']:
                paint['barcodes'].append(barcode)
            updated.append(paint)
            changes.append(dict(before=old, after=paint, source_url=product['source_url'],
                                match='explicit alias' if old['name'] in ALIASES else 'normalised exact name'))
        output[file.replace('/duncan-rhodes/', '/two-thin-coats/')] = updated
    assert len(used) == 180
    assert len(additions) == 39
    for fact in additions:
        paint = dict(brand='Two Thin Coats', range=fact['range'], code=None,
                     name=fact['name'], type=fact['type'], barcodes=[], status='current')
        if fact['range'] == 'Dark Arts':
            paint['colour'] = dict(hex=swatches[fact['name']]['hex'], gradient=None, source=COLOUR_SOURCE)
        slug = fact['range'].lower().replace(' ', '-')
        output.setdefault(f'paints/two-thin-coats/{slug}.json', []).append(paint)
    for paints in output.values():
        paints.sort(key=lambda p: (p['code'] or '', p['name']))
    return output, changes


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n')


def main():
    output, changes = build()
    # Refuse to overwrite unrelated edits or extra records in the affected directories.
    old_files = {f: p for f, p in baseline().items() if f.startswith('paints/duncan-rhodes/')}
    for directory, expected in [('duncan-rhodes', old_files), ('two-thin-coats', output)]:
        for path in (ROOT / 'paints' / directory).glob('*.json'):
            relative = str(path.relative_to(ROOT))
            if relative not in expected or json.loads(path.read_text()) != expected[relative]:
                raise SystemExit(f'Refusing to overwrite unexpected changes: {relative}')
    for file, paints in output.items():
        write_json(ROOT / file, paints)
    for file in old_files:
        (ROOT / file).unlink(missing_ok=True)
    write_json(REPORT / 'existing-record-changes.json', changes)
    write_json(REPORT / 'summary.json', dict(
        baseline=BASE, renamed_and_enriched=180, explicit_name_aliases=len(ALIASES),
        added=39, total_ttc=219, existing_colours_changed=0, added_colours=30,
        added_skus=180, added_barcodes=180))


if __name__ == '__main__':
    main()
