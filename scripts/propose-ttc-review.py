"""Compare GERInFact's numeric values with the TTC import; changes remain proposals.

Run with --apply to write the review files and proposed catalogue replacements.
Refuses to overwrite TTC records edited away from the baseline or prior proposals.
"""
import copy
import html
import importlib.util
import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
BASE = 'df41f4fd93363ae9ce7cf80a31d6defc621e1397'
OUT = ROOT / 'reports/arcturus-review'
SOURCE_URL = 'https://github.com/GERInFact/ttc_citadel/blob/235dc3f5fda248a2499d68098cbc000e232f413a/colors.json'


def module(name, file):
    spec = importlib.util.spec_from_file_location(name, ROOT / 'scripts' / file)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


ttc = module('ttc', 'import-ttc.py')
arcturus = module('arcturus', 'import-arcturus.py')
# Explicit source spelling matches; never use fuzzy matching silently.
ALIASES = {
    'Emperor Red': 'Emporer Red',
    'Emperor’s Purple': "Emporer's Purple",
    'Bitz O’ Tin': "Bits O' Tin",
    'Ray Gun Glow': 'Ray Gun Blue',
    'Sorcerer’s Cloak': "Sorceror's Cloak",
}


def compare():
    swatches = {ttc.normalise(r['name']): r for r in ttc.read_swatches()}
    rows = []
    for wave in range(1, 4):
        file = f'paints/two-thin-coats/wave-{wave}.json'
        raw = subprocess.check_output(['git', 'show', f'{BASE}:{file}'], cwd=ROOT, text=True)
        for before in json.loads(raw):
            name = ALIASES.get(before['name'], before['name'])
            source = swatches[ttc.normalise(name)]
            delta = arcturus.distance(before['colour']['hex'], source['hex'])
            different = before['colour']['hex'] != source['hex']
            after = copy.deepcopy(before)
            if different:
                after['colour'] = dict(hex=source['hex'], gradient=None, source=ttc.COLOUR_SOURCE)
            identity = before['name'] == 'Ray Gun Glow'
            rows.append(dict(status='pending-review' if different else 'unchanged',
                             catalogue_file=file, before=before, after=after,
                             source_name=source['name'], source_index=source['source_index'],
                             source_url=SOURCE_URL, oklab_distance=round(delta, 6),
                             substantial=delta >= .08, colour_differs=different,
                             match='explicit alias' if before['name'] in ALIASES else 'normalised exact name',
                             identity_review=identity,
                             note='Possible source-name mismatch: Ray Gun Blue versus Ray Gun Glow; verify identity before accepting.' if identity else
                                  'Explicit spelling alias; review the source name.' if before['name'] in ALIASES else
                                  'Numeric comparison only; source is not presumed more accurate.'))
    assert len(rows) == 180
    return rows


def render(rows):
    esc = html.escape
    body = []
    for row in sorted(rows, key=lambda r: (-r['oklab_distance'], r['before']['code'])):
        before, after = row['before'], row['after']
        flag = 'SUBSTANTIAL' if row['substantial'] else 'minor difference' if row['colour_differs'] else 'same hex'
        swatch = lambda colour: f'<span class="swatch" style="background:{colour}"></span><code>{colour}</code>'
        body.append(f'<tr data-substantial="{str(row["substantial"]).lower()}" data-identity="{str(row["identity_review"]).lower()}">'
                    f'<td><strong>{esc(before["name"])}</strong><br>{esc(before["range"])} · {esc(before["code"])}</td>'
                    f'<td>{swatch(before["colour"]["hex"])}<small>{esc(before["colour"]["source"])}</small></td>'
                    f'<td>{swatch(after["colour"]["hex"])}<small>{esc(row["source_name"])}</small></td>'
                    f'<td>{row["oklab_distance"]:.3f}<br><strong>{flag}</strong></td>'
                    f'<td>{esc(row["note"])}<br><a href="{SOURCE_URL}" target="_blank" rel="noopener noreferrer">GERInFact source · array index {row["source_index"]}</a></td></tr>')
    return '''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Two Thin Coats — colour comparison review</title><style>
body{font:16px/1.5 system-ui,sans-serif;margin:32px;color:#17202a;background:#f7f8fa}h1{margin-bottom:8px}p{max-width:1000px}
input,select{font:inherit;padding:10px;margin:8px 12px 18px 0}table{border-collapse:collapse;width:100%;background:white}th,td{text-align:left;padding:16px;border-bottom:1px solid #ccd3dc;vertical-align:top}th{position:sticky;top:0;background:#e8edf3}td:nth-child(2),td:nth-child(3){min-width:170px}.swatch{display:block;width:160px;height:64px;border:1px solid #6a7380;border-radius:4px;margin-bottom:6px}small{display:block;color:#536070;max-width:230px}a{color:#075aaa}code{font-size:15px}tr[data-identity=true]{background:#fff3dc}label{display:inline-block}@media(max-width:900px){body{margin:12px}table{display:block;overflow-x:auto}}
</style><h1>Two Thin Coats — GERInFact colour comparison</h1>
<p><strong>Pending review.</strong> Existing colours are preserved in the TTC import PR. This draft proposes replacing only differing values. Neither source is assumed more accurate. All 180 existing paints are shown: 167 differing values (23 substantial at Euclidean OKLab ≥ 0.08), 13 identical. Five names use explicit aliases; Ray Gun Blue / Ray Gun Glow needs identity review. Distances use a 0–1 OKLab scale, not CIEDE2000. No images are loaded.</p>
<p>Attribution: <a href="https://gerinfact.github.io/ttc_citadel/">GERInFact — TTC–Citadel Converter</a>. Numeric values from pinned revision <a href="'''+SOURCE_URL+'''">235dc3f</a>. No explicit upstream licence found; numeric factual reuse directed by the maintainer. No artwork or open-licence grant is asserted. Current source labels and complete before/after records are retained in the JSON ledger.</p>
<label>Search <input id="search" type="search" placeholder="Paint, range, SKU or hex"></label><label>Show <select id="filter"><option value="all">All comparisons</option><option value="substantial">Substantial differences</option><option value="identity">Identity review</option></select></label><span id="count"></span>
<table><thead><tr><th>Paint</th><th>Current · preserved in TTC PR</th><th>GERInFact · proposed</th><th>OKLab distance</th><th>Evidence / identity</th></tr></thead><tbody>'''+''.join(body)+'''</tbody></table><script>
const rows=[...document.querySelectorAll('tbody tr')],search=document.getElementById('search'),filter=document.getElementById('filter');
function render(){let count=0;for(const row of rows){const matches=row.textContent.toLowerCase().includes(search.value.toLowerCase())&&(filter.value==='all'||row.dataset[filter.value]==='true');row.hidden=!matches;if(matches)count++;}document.getElementById('count').textContent=count+(count===1?' comparison':' comparisons');}search.oninput=filter.onchange=render;render();
</script></html>'''


def main():
    rows = compare()
    changed = [r for r in rows if r['colour_differs']]
    summary = dict(review_base_commit=BASE, compared=len(rows), proposed_replacements=len(changed),
                   substantial_differences=sum(r['substantial'] for r in rows),
                   unchanged_hex=sum(not r['colour_differs'] for r in rows), explicit_aliases=len(ALIASES),
                   identity_reviews=sum(r['identity_review'] for r in rows), existing_colours_changed_in_import=0)
    print(json.dumps(summary, indent=2))
    if '--apply' not in sys.argv:
        return
    files = {}
    for row in rows:
        file = row['catalogue_file']
        files.setdefault(file, json.loads((ROOT / file).read_text()))
        index = next(i for i, p in enumerate(files[file]) if p['code'] == row['before']['code'])
        if files[file][index] not in (row['before'], row['after']):
            raise ValueError(f'Refusing to overwrite review edits: {file} {row["before"]["name"]}')
        files[file][index] = row['after']
    for file, paints in files.items():
        ttc.write_json(ROOT / file, paints)
    ttc.write_json(OUT / 'ttc-colour-comparisons.json', rows)
    ttc.write_json(OUT / 'ttc-colour-summary.json', summary)
    (OUT / 'ttc-colour-review.html').write_text(render(rows))


if __name__ == '__main__':
    main()
