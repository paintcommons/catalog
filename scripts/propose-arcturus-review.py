"""Prepare review candidates against the clean import. Dry run unless --apply.

These deterministic proposals are NOT accepted corrections. Review and edit them
before merging. Refuses to overwrite a catalogue already edited during review.
"""
import collections
import copy
import importlib.util
import json
import pathlib
import struct
import subprocess
import sys
import zlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
CLEAN = 'ddcd495b55ef3e1611a9886affcfa47eaad5092c'
OUT = ROOT / 'reports/arcturus-review'
spec = importlib.util.spec_from_file_location('arcturus', ROOT / 'scripts/import-arcturus.py')
imp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(imp)


def png(path, colours):
    """Draw numeric data as swatches; no third-party artwork or imaging library."""
    width, height = 240, 44
    values = [bytes.fromhex(c.removeprefix('#')) for c in colours]
    pixels = bytearray()
    for y in range(height):
        pixels.append(0)
        for x in range(width):
            border = x < 1 or x >= width-1 or y < 1 or y >= height-1
            centre = len(values) == 2 and 118 <= x < 122
            pixels.extend(b'\x88\x88\x88' if border or centre else values[min(len(values)-1, x*len(values)//width)])
    def chunk(name, data):
        return struct.pack('!I', len(data))+name+data+struct.pack('!I', zlib.crc32(name+data) & 0xffffffff)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR', struct.pack('!2I5B', width, height, 8, 2, 0, 0, 0))
                     +chunk(b'IDAT', zlib.compress(bytes(pixels)))+chunk(b'IEND', b''))


def prepare():
    git = lambda *args: subprocess.check_output(['git', *args], cwd=ROOT, text=True)
    files = {f: json.loads(git('show', f'{CLEAN}:{f}')) for f in git('ls-tree', '-r', '--name-only', CLEAN, '--', 'paints').splitlines() if f.endswith('.json')}
    original = copy.deepcopy(files)
    flagged = json.loads((imp.REPORT / 'colour-disagreements.json').read_text())
    withheld = json.loads((imp.REPORT / 'withheld.json').read_text())
    by_id = {p['id']: p for values in files.values() for p in values if p.get('id')}
    candidates = collections.defaultdict(list)
    for c in flagged: candidates[c['existing_id']].append(c)
    replacements = []
    for pid, observations in sorted(candidates.items()):
        # Prefer matching names, then code matches, then the named Monument table
        # over its misfiled Creature duplicate. All alternatives remain in the ledger.
        ranked = sorted(observations, key=lambda c: (c['name_disagrees'], c['match_basis'] != 'code',
                                                     c['file'] == 'Creature.md', c['file'], c['line']))
        c = ranked[0]
        p = by_id[pid]
        before = copy.deepcopy(p)
        p['colour'] = {'hex': c['hex'], 'gradient': None, 'source': imp.SOURCE}
        replacements.append({'status': 'pending-review', 'id': pid, 'before': before, 'after': copy.deepcopy(p),
                             'selected_source': c, 'alternatives': ranked[1:],
                             'selection_reason': 'Provisional: matching name, code match, named manufacturer table, then source order. Not a colour-quality finding.'})
    paints = [p for values in files.values() for p in values]
    names = {(p['brand'], p['range'], p['name'].lower()): p for p in paints}
    codes = {imp.codekey(p['brand'], p['code']): p for p in paints if p['code']}
    decisions = []; added = []
    for c in sorted(withheld, key=lambda c: (c['file'], c['line'])):
        entry = {'status': 'pending-review', 'source': c}
        if not c['name'].strip():
            entry.update(proposal='unresolved', reason='Upstream name is empty; no product name invented.')
        else:
            key = (c['brand'], c['range'], c['name'].lower())
            collision = codes.get(imp.codekey(c['brand'], c['code'])) if c['code'] else None
            collision = collision or names.get(key)
            if collision:
                entry.update(proposal='alternative-to-selected-candidate', selected_record=copy.deepcopy(collision),
                             reason='Provisional first-source-row selection preserves unique code and name constraints; review both alternatives.')
            else:
                p = {k: c[k] for k in ('brand', 'range', 'code', 'name')}
                p.update(type=imp.paint_type(c), barcodes=[], colour={'hex': c['hex'], 'gradient': None, 'source': imp.SOURCE},
                         status='discontinued' if 'discontinued' in (c['range'] or '') else 'current')
                path = f"paints/{imp.slug(p['brand'])}/{imp.slug(p['range'])}.json"
                files.setdefault(path, []).append(p)
                names[key] = p
                if p['code']: codes[imp.codekey(p['brand'], p['code'])] = p
                entry.update(proposal='add-candidate', catalogue_file=path, after=copy.deepcopy(p),
                             reason='Provisional first source row for this unique code/name. Range identity or conflicting upstream variants require human review.')
                added.append(entry)
        decisions.append(entry)
    summary = {'status': 'draft-not-approved', 'clean_import_commit': CLEAN, 'colour_replacements': len(replacements),
               'flagged_observations': len(flagged), 'conflict_source_rows': len(withheld), 'candidate_additions': len(added),
               'conflict_dispositions': dict(collections.Counter(d['proposal'] for d in decisions)),
               'proposed_total_records': sum(len(v) for v in files.values()),
               'warning': 'Proposals for joint review; upstream is not presumed better than manufacturer values. No existing non-colour fields are changed.'}
    print(json.dumps(summary, indent=2))
    if '--apply' not in sys.argv: return
    current_files = {str(p.relative_to(ROOT)): json.loads(p.read_text()) for p in (ROOT / 'paints').glob('*/*.json')}
    if current_files != original: raise ValueError('Catalogue differs from the clean base. Refusing to overwrite review edits.')
    for path, values in files.items():
        if values == original.get(path): continue
        target = ROOT / path; target.parent.mkdir(parents=True, exist_ok=True)
        values.sort(key=lambda p: (p['code'] is None, p['code'] or '', p['name']))
        target.write_text(json.dumps(values, ensure_ascii=False, indent=2)+'\n')
    OUT.mkdir(parents=True, exist_ok=True)
    for name, data in [('summary', summary), ('colour-proposals', replacements), ('conflict-proposals', decisions)]:
        (OUT / (name+'.json')).write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n')
    def esc(v): return str(v or '').replace('|', '\\|').replace('\n', ' ')
    md = '# Proposed colour replacements — pending review\n\nLeft: current manufacturer/catalogue colour. Right: proposed Arcturus colour. All replacements are provisional; neither source is assumed correct. Hex comparison uses Euclidean OKLab ≥ 0.08 (0–1 scale), not CIEDE2000. Some colours have multiple upstream observations; all are retained in [colour-proposals.json](colour-proposals.json). Gradients would be cleared because Arcturus supplies no replacement gradient.\n\n| Paint | Current → proposed | Hex values | Distance | Source / identity note |\n| --- | --- | --- | ---: | --- |\n'
    for i, proposal in enumerate(sorted(replacements, key=lambda p: -p['selected_source']['oklab_distance']), 1):
        b, a, c = proposal['before'], proposal['after'], proposal['selected_source']
        img = f'swatches/colour-{i:03}.png'; png(OUT / img, [b['colour']['hex'], a['colour']['hex']])
        md += f"| {esc(b['brand'])} — {esc(b['name'])} ({esc(b['range'])}) | ![Current then proposed]({img}) | `{b['colour']['hex']}` → `{a['colour']['hex']}` | {c['oklab_distance']:.3f} | [Arcturus row]({c['url']}); {esc(b['colour']['source'])}" + ('; **name differs: review identity**' if c['name_disagrees'] else '') + ' |\n'
    (OUT / 'colour-review.md').write_text(md)
    md = '# Proposed conflict resolutions — pending review\n\nFirst-source-row choices below are placeholders for joint review, not verified product identity decisions. Compare each swatch and source row before approving. Alternatives do not create duplicate codes/names. A missing-name row remains unresolved.\n\n| Source paint / range / code | Upstream swatch | Proposal | Selected colour, if competing | Source |\n| --- | --- | --- | --- | --- |\n'
    for i, d in enumerate(decisions, 1):
        c = d['source']; selected = d.get('selected_record', {}).get('colour', {}).get('hex')
        img = f'swatches/conflict-{i:03}.png'; png(OUT / img, [c['hex']] if not selected else [c['hex'], selected])
        md += f"| {esc(c['brand'])} — {esc(c['name'])} / {esc(c['range'])} / {esc(c['code'])} | ![Upstream then selected alternative if present]({img}) `{c['hex']}` | {d['proposal']} | {selected or '—'} | [Row]({c['url']}) |\n"
    (OUT / 'conflict-review.md').write_text(md)
    (OUT / 'README.md').write_text(f'''# Draft Arcturus replacements and conflict resolutions

Stacked on the clean import commit `{CLEAN}`. **Not approved for merging.**

- Proposes {len(replacements)} existing colour replacements from 392 substantial disagreement observations. Existing names, IDs, codes, barcodes and status are unchanged.
- Proposes {len(added)} candidate additions from the 127 withheld source rows; competing alternatives remain in the review ledger, and the empty-name row remains unresolved.
- [Colour review with rendered swatches](colour-review.md): current colour on the left, proposed colour on the right.
- [Conflict review with rendered swatches](conflict-review.md): each upstream candidate and any selected competing colour.
- Full before/after records and alternative source observations: `colour-proposals.json`, `conflict-proposals.json`.

Selections are deterministic starting points, not endorsements of Arcturus over manufacturer swatches. Reviewers should edit or reject individual changes. This PR clears gradients only on the proposed colour replacements because upstream publishes a single hex. All original colours and gradients are retained in the before/after ledger.

Validate with `node scripts/validate.mjs --base {CLEAN}` and `PYTHONDONTWRITEBYTECODE=1 python3 scripts/import-arcturus.test.py`. The one-time proposal script defaults to a dry run; `--apply` refuses any tree already changed from its clean baseline. Do not rerun the clean importer over accepted review edits.
''')


if __name__ == '__main__': prepare()
