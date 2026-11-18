"""Reference-only numeric comparisons with the official Wave 1–3 PDF graphics.

Requires pypdf and Pillow. PDFs remain outside the repository. These samples
describe chart artwork, not measured paint or manufacturer-specified RGB stops.
"""
import argparse
import hashlib
import importlib.util
import json
import math
import pathlib
import statistics

ROOT = pathlib.Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location('review', ROOT / 'scripts/propose-ttc-review.py')
review = importlib.util.module_from_spec(spec)
spec.loader.exec_module(review)

# Positions measured on full-page renders scaled to 2200 pixels wide. All
# three charts place 60 paints in a 6-column/10-row grid. Wave 2 prints its
# glazes before its washes despite the reversed SKU order. Sample interiors
# only; Wave 1/2 also exclude their central badges.
CHARTS = [
    dict(wave=1, file='wave1-conversion.pdf', x0=90, dx=350, y0=303.5, dy=109.3, radius=45,
         badge=True, url='https://www.duncanrhodes.com/wp-content/uploads/2023/08/Conversion-Chart-Wave-1_2023_01.pdf'),
    dict(wave=2, file='wave2-conversion.pdf', x0=100, dx=350, y0=307, dy=109, radius=45,
         badge=True, url='https://www.duncanrhodes.com/wp-content/uploads/2023/08/Conversion-Chart-Wave-2_2023_01.pdf'),
    dict(wave=3, file='wave3.pdf', x0=67.8, dx=362.75, y0=317.2, dy=111.2, radius=46.4,
         badge=False, url='https://www.duncanrhodes.com/wp-content/uploads/2025/10/Wave-3-Colour-Chart_2024.pdf'),
]


def hex_value(rgb):
    return '#' + ''.join(f'{round(v):02X}' for v in rgb)


def sample(image, cx, cy, radius, badge, limit=.85):
    values = []
    for y in range(math.floor(cy-radius), math.ceil(cy+radius)+1):
        for x in range(math.floor(cx-radius), math.ceil(cx+radius)+1):
            dx, dy = (x-cx)/radius, (y-cy)/radius
            if dx*dx + dy*dy > limit**2:
                continue
            if badge and abs(dx) < .30 and abs(dy) < .45:
                continue
            values.append((image.getpixel((x, y)), math.hypot(dx, dy)))
    return values


def main():
    from pypdf import PdfReader
    from PIL import Image
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--evidence-dir', type=pathlib.Path, required=True)
    args = parser.parse_args()
    comparisons = review.compare()
    output, sources = [], []
    for chart in CHARTS:
        path = args.evidence_dir / chart['file']
        reader = PdfReader(path)
        assert len(reader.pages) == len(reader.pages[0].images) == 1
        image = reader.pages[0].images[0].image.convert('RGBA')
        image = Image.alpha_composite(Image.new('RGBA', image.size, 'white'), image).convert('RGB')
        scale = image.width / 2200
        sources.append(dict(**chart, sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                            page=1, embedded_image_pixels=list(image.size)))
        rows = sorted((r for r in comparisons if r['before']['range'] == f'Wave {chart["wave"]}'),
                      key=lambda r:r['before']['code'])
        if chart['wave'] == 2:
            by_code = {r['before']['code']: r for r in rows}
            order = list(range(10061, 10112)) + list(range(10115, 10121)) + list(range(10112, 10115))
            rows = [by_code[str(code)] for code in order]
        assert len(rows) == 60
        for index, row in enumerate(rows):
            cx = (chart['x0'] + (index % 6) * chart['dx']) * scale
            cy = (chart['y0'] + (index // 6) * chart['dy']) * scale
            radius = chart['radius'] * scale
            samples = sample(image, cx, cy, radius, chart['badge'])
            median = hex_value([statistics.median(v[0][c] for v in samples) for c in range(3)])
            ordered = sorted(samples, key=lambda v:review.arcturus.oklab(hex_value(v[0]))[0])
            stops = [hex_value(ordered[round(q*(len(ordered)-1))][0]) for q in (.1, .5, .9)]
            before, alternative = row['before']['colour']['hex'], row['gerinfact_colour']['hex']
            entry = dict(code=row['before']['code'], name=row['before']['name'], wave=chart['wave'],
                         chart_url=chart['url'], chart_sha256=sources[-1]['sha256'],
                         grid_row=index//6+1, grid_column=index%6+1,
                         native_sample_centre=[round(cx, 3), round(cy, 3)], native_radius=round(radius, 3),
                         samples=len(samples), reference_median=median,
                         reference_lightness_quantiles=stops,
                         current_hex=before, gerinfact_hex=alternative,
                         current_to_reference=round(review.arcturus.distance(before, median), 6),
                         gerinfact_to_reference=round(review.arcturus.distance(alternative, median), 6))
            if entry['code'] == '10044':
                # The rim is excluded from the representative interior median,
                # but inspect it separately to test the two-tone interpretation.
                full = sample(image, cx, cy, radius, chart['badge'], limit=.97)
                nearest = {}
                for label, value in [('current', before), ('gerinfact', alternative)]:
                    pixel, radial = min(full, key=lambda v:review.arcturus.distance(value, hex_value(v[0])))
                    nearest[label] = dict(hex=hex_value(pixel), distance=round(review.arcturus.distance(value, hex_value(pixel)), 6),
                                          normalised_radius=round(radial, 4))
                entry['nearest_chart_pixels'] = nearest
            output.append(entry)
    metadata = dict(purpose='Reference comparisons only; no catalogue swatches are populated from PDFs.',
                    attribution='Trans Atlantis Games and Duncan Rhodes Painting Academy, official Two Thin Coats conversion/comparison charts.',
                    method='Decode the single embedded raster at native resolution; composite alpha on white. Use circular interiors r ≤ 0.85; Wave 1/2 exclude the central badge rectangle |x| < 0.30r, |y| < 0.45r. Report per-channel median RGB and actual pixels at the 10th, 50th and 90th OKLab-lightness percentiles. Compare each numeric candidate with the median using Euclidean OKLab on a 0–1 scale, not CIEDE2000. Dragon’s Gold additionally checks nearest pixels out to r ≤ 0.97.',
                    limitations='Reference graphic samples depend on ROI and PDF image decoding; metallic gradients are not a single paint measurement. Quantile colours are not manufacturer-specified gradient stops. No chart artwork is redistributed and no artwork licence is asserted.',
                    charts=sources, comparisons=output)
    review.ttc.write_json(review.OUT / 'ttc-chart-references.json', metadata)
    print(json.dumps(next(r for r in output if r['code']=='10044'), indent=2))


if __name__ == '__main__':
    main()
