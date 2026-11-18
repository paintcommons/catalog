"""Prepare stop-based Arcturus review; never bulk-replace existing hex values.

Defaults to a dry run. --apply refuses paint records edited outside the pinned
baseline or this generator's previous proposals. No image sampling is performed.
"""
import collections
import copy
import html
import importlib.util
import json
import math
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
CLEAN = '12a3154807c3708ca169e2cd095528f504776404'
OUT = ROOT / 'reports/arcturus-review'
spec = importlib.util.spec_from_file_location('arcturus', ROOT / 'scripts/import-arcturus.py')
imp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(imp)


def baseline():
    git = lambda *args: subprocess.check_output(['git', *args], cwd=ROOT, text=True)
    return {f: json.loads(git('show', f'{CLEAN}:{f}'))
            for f in git('ls-tree', '-r', '--name-only', CLEAN, '--', 'paints').splitlines() if f.endswith('.json')}


def to_gradient_distance(value, gradient):
    point = imp.oklab(value)
    stops = [imp.oklab(x) for x in gradient]
    result = float('inf')
    for a, b in zip(stops, stops[1:]):
        vector = [y-x for x,y in zip(a,b)]
        norm = sum(x*x for x in vector)
        t = max(0, min(1, sum((p-x)*d for p,x,d in zip(point,a,vector))/norm)) if norm else 0
        result = min(result, math.dist(point, [x+t*d for x,d in zip(a,vector)]))
    return result


def prepare():
    files = baseline()
    by_id = {p['id']:p for rows in files.values() for p in rows if p.get('id')}
    observations = json.loads((imp.REPORT / 'colour-disagreements.json').read_text())
    grouped = collections.defaultdict(list)
    for row in observations: grouped[row['existing_id']].append(row)
    proposals = []
    for pid, alternatives in sorted(grouped.items()):
        ranked = sorted(alternatives, key=lambda c:(c['name_disagrees'], c['match_basis']!='code', c['file']=='Creature.md', c['file'], c['line']))
        row = ranked[0]
        before = copy.deepcopy(by_id[pid]); after = copy.deepcopy(before)
        colour = before['colour']; gradient = colour['gradient']
        kind = before['type']; text = f"{before['range']} {before['name']}".lower()
        near = None
        if colour['source'] == 'manual-override':
            disposition = 'preserve-manual-override'
        elif row['name_disagrees']:
            disposition = 'hold-identity-review'
        elif kind in ('speedpaint', 'wash') or re.search(r'\bwash(es)?\b|\bglaze', text):
            if gradient is not None:
                disposition = 'hold-existing-transparent-stops'
            elif imp.oklab(row['hex'])[0] < imp.oklab(colour['hex'])[0]:
                after['colour'] = dict(hex=colour['hex'], gradient=[row['hex'],colour['hex'],None], source=imp.SOURCE)
                disposition = 'propose-pooled-stop'
            else:
                disposition = 'hold-lighter-transparent-observation'
        elif kind == 'metallic' or before['brand']=='Turbo Dork':
            if gradient:
                near = to_gradient_distance(row['hex'], gradient)
                disposition = 'preserve-near-existing-gradient' if near <= .04 else 'hold-outside-existing-gradient'
            else:
                disposition = 'needs-approved-image-gradient-sampling'
        else:
            disposition = 'hold-flat-range-spot-check'
        applies = after != before
        proposals.append(dict(id=pid, status='pending-review' if applies else 'preserved-for-review',
                              before=before, after=after, selected_source=row, alternatives=ranked[1:],
                              disposition=disposition, apply=applies,
                              gradient_distance=round(near,6) if near is not None else None,
                              requires_colour_override=applies,
                              stop_provenance=[dict(role='pooled candidate',hex=row['hex'],source=imp.SOURCE,url=row['url']),
                                               dict(role='retained true colour',hex=colour['hex'],source=colour['source']),
                                               dict(role='thinned',hex=None,source=None)] if applies else None))
    return files, proposals


def render(proposals):
    esc = html.escape
    rows=[]
    def sample(colour, gradient=None):
        colours=[c for c in (gradient or [colour]) if c]
        css=colours[0] if len(colours)==1 else 'linear-gradient(90deg,'+','.join(colours)+')'
        return f'<span class="swatch" style="background:{css}"></span><code>'+esc(colour)+'</code>'
    for row in sorted(proposals,key=lambda r:(not r['apply'],-r['selected_source']['oklab_distance'])):
        before, after, source = row['before'],row['after'],row['selected_source']
        detail='Pooled → true colour → unknown thinned. Main hex retained. Needs colour-override after review.' if row['apply'] else 'Existing catalogue record remains unchanged.'
        if row['gradient_distance'] is not None:detail+=f" Distance to existing OKLab stop polyline: {row['gradient_distance']:.3f} (near-path threshold 0.04)."
        rows.append(f'<tr data-action="{esc(row["disposition"])}"><td><strong>{esc(before["brand"])} — {esc(before["name"])}</strong><br>{esc(before["range"] or "")} · {esc(before["code"] or "")}</td><td>{sample(before["colour"]["hex"],before["colour"]["gradient"])}<small>{esc(before["colour"]["source"])}</small></td><td>{sample(source["hex"])}<a href="{esc(source["url"])}">Pinned Arcturus row</a></td><td>{sample(after["colour"]["hex"],after["colour"]["gradient"])}<small>{esc(str(after["colour"]["gradient"]))}</small></td><td><strong>{esc(row["disposition"])}</strong><br>{esc(detail)}<br>Current ↔ Arcturus: {source["oklab_distance"]:.3f}</td></tr>')
    options=''.join(f'<option value="{esc(x)}">{esc(x)}</option>' for x in sorted({r['disposition'] for r in proposals}))
    return '<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Arcturus tonal and colour review</title><style>body{font:16px/1.5 system-ui;margin:28px;color:#17202a;background:#f7f8fa}table{width:100%;border-collapse:collapse;background:white}td,th{padding:14px;border-bottom:1px solid #ccd3dc;text-align:left;vertical-align:top}th{position:sticky;top:0;background:#e8edf3}.swatch{display:block;width:150px;height:64px;border:1px solid #777;margin:4px 0}small{display:block;color:#536070}input,select{padding:10px;margin:12px;font:inherit}a{color:#075aaa}code{font-size:14px}</style><h1>Arcturus tonal and colour review</h1><p>Pending joint review. All existing main hex values and manual overrides are preserved. Only matching-name darker transparent observations propose pooled stops; unknown thinned positions remain null. Metallics and flat colours remain unchanged pending the listed evidence checks. Numeric source: Rick Fleuren / Miniature Painter Pro, MIT; full notice and record provenance travel with the catalogue. Distances are Euclidean OKLab (0–1), not CIEDE2000. No upstream observation is presumed better.</p><p>Identity conflicts moved to <a href="../arcturus-import/conflict-review.html">the import review</a>. New sources rank 40, below manufacturer charts; stop proposals need colour-override only after review. Missing stops shown here are unknown, not extracted whites.</p><label>Search<input id="search" type="search" placeholder="Brand, range, paint or hex"></label><label>Action<select id="action"><option value="">All dispositions</option>'+options+'</select></label><span id="count"></span><table><thead><tr><th>Paint / range</th><th>Current</th><th>Arcturus observation</th><th>Proposed / preserved</th><th>Disposition</th></tr></thead><tbody>'+''.join(rows)+'</tbody></table><script>const rows=[...document.querySelectorAll("tbody tr")],search=document.getElementById("search"),action=document.getElementById("action");function render(){let n=0;for(const r of rows){r.hidden=!(r.textContent.toLowerCase().includes(search.value.toLowerCase())&&(!action.value||r.dataset.action===action.value));if(!r.hidden)n++;}document.getElementById("count").textContent=n+" paints";}search.oninput=action.onchange=render;render();</script></html>'


def main():
    files, proposals = prepare()
    summary = dict(status='draft-not-approved',review_base_commit=CLEAN, compared_paints=len(proposals),
                   source_observations=sum(1+len(r["alternatives"]) for r in proposals), pooled_stop_proposals=sum(r['apply'] for r in proposals),
                   main_hex_replacements=0, conflict_additions=0,
                   dispositions=dict(collections.Counter(r['disposition'] for r in proposals)),
                   gradient_near_path_threshold=.04)
    print(json.dumps(summary,indent=2))
    if '--apply' not in sys.argv:return
    previous_path=OUT/'colour-proposals.json'
    previous={r['id']:r['after'] for r in json.loads(previous_path.read_text())} if previous_path.exists() else {}
    current={str(p.relative_to(ROOT)):json.loads(p.read_text()) for p in (ROOT/'paints').glob('*/*.json')}
    originals=copy.deepcopy(files)
    updates={r['id']:r for r in proposals if r['apply']}
    for file, paints in files.items():
        for i,paint in enumerate(paints):
            row=updates.get(paint.get('id'))
            if row:paints[i]=row['after']
    for file, paints in current.items():
        expected=files.get(file)
        if expected is None:raise ValueError('Unexpected file '+file)
        for paint in paints:
            if paint not in originals[file] and paint not in expected and paint!=previous.get(paint.get('id')):
                raise ValueError('Refusing to overwrite review edits in '+file)
    for file, paints in files.items():
        if paints!=originals[file]:imp_path=ROOT/file;imp_path.write_text(json.dumps(paints,indent=2,ensure_ascii=False)+'\n')
    OUT.mkdir(parents=True,exist_ok=True)
    for name,data in [('summary',summary),('colour-proposals',proposals)]:
        (OUT/(name+'.json')).write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n')
    per_range=collections.defaultdict(list)
    for row in proposals:per_range[f"{row['before']['brand']} / {row['before']['range']}"].append(row)
    (OUT/'per-range-review.json').write_text(json.dumps(per_range,indent=2,ensure_ascii=False)+'\n')
    (OUT/'colour-review.html').write_text(render(proposals))


if __name__=='__main__':main()
