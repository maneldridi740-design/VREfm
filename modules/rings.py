# ============================================================
# Cell 7 — modules/rings.py
# ============================================================

src = '''\
from collections import defaultdict, Counter
from modules.io_utils import clean_name, robust_match, is_valid_df
from modules.detect import detect_locus, detect_country, detect_mlst
from modules.colors import (
    ensure_enough_colors, generate_unique_colors, ABSENT_COL
)


def proc_genes(gdf, lnames):
    if gdf is None:
        return {}
    gene_cols   = list(gdf.columns[1:])
    genome_ids  = gdf.iloc[:, 0].astype(str).tolist()
    genome_ids_c = [clean_name(g) for g in genome_ids]
    result = {}
    for col in gene_cols:
        vals = {}
        for lf in lnames:
            idx = robust_match(lf, genome_ids, genome_ids_c)
            if idx is not None:
                try:
                    v = int(float(gdf.iloc[idx][col]))
                except Exception:
                    v = 0
                vals[str(lf)]            = v
                vals[clean_name(str(lf))] = v
        result[col] = vals
    return result


def match_stats(lnames, gdf, mdf):
    s = {"total": len(lnames), "g_ok": 0, "m_ok": 0}
    if is_valid_df(gdf):
        gi  = gdf.iloc[:, 0].astype(str).tolist()
        gic = [clean_name(g) for g in gi]
        for lf in lnames:
            if robust_match(lf, gi, gic) is not None:
                s["g_ok"] += 1
    if is_valid_df(mdf):
        lc = detect_locus(mdf)
        if lc:
            mi  = mdf[lc].astype(str).tolist()
            mic = [clean_name(m) for m in mi]
            for lf in lnames:
                if robust_match(lf, mi, mic) is not None:
                    s["m_ok"] += 1
    return s


def build_van_ring(gene_rings, prefix, pal_colors):
    cols = [c for c in gene_rings if c.lower().startswith(prefix.lower())]
    if not cols:
        return None
    all_keys = set()
    for c in cols:
        all_keys.update(gene_rings[c].keys())
    combined = {}
    for k in all_keys:
        present = [c for c in cols if gene_rings[c].get(k, 0) >= 1]
        combined[k] = "+".join(present) if present else "Absent"
    unique_vals = sorted(set(combined.values()))
    palette = {}
    pi = 0
    for v in unique_vals:
        if v == "Absent":
            palette[v] = ABSENT_COL
        else:
            palette[v] = pal_colors[pi % len(pal_colors)]
            pi += 1
    label = prefix.upper()
    if len(cols) > 1:
        label += f" ({len(cols)} var)"
    return {
        "label":   label,
        "values":  combined,
        "palette": palette,
        "counts":  dict(Counter(combined.values())),
    }


def _meta_ring(lnames, mdf, col_fn, label, pal_list=None, clean_val=True):
    if mdf is None:
        return None
    target_col = col_fn(mdf)
    lc         = detect_locus(mdf)
    if target_col is None or lc is None:
        return None
    l2v = {}
    for _, row in mdf.iterrows():
        lo  = str(row[lc]).strip()
        val = str(row[target_col]).strip()
        if val in ["-", "nan", "", "None"]:
            val = "Unknown"
        if clean_val and ":" in val:
            val = val.split(":")[0].strip()
        l2v[lo]             = val
        l2v[clean_name(lo)] = val
    mi  = list(l2v.keys())
    mic = [clean_name(m) for m in mi]
    vals = {}
    for lf in lnames:
        idx = robust_match(lf, mi, mic)
        if idx is not None:
            vals[str(lf)]             = l2v[mi[idx]]
            vals[clean_name(str(lf))] = l2v[mi[idx]]
    if not vals:
        return None
    unique_vals = sorted(set(vals.values()), key=lambda x: (x == "Unknown", x))
    n  = len(unique_vals)
    uc = ensure_enough_colors(pal_list, n) if pal_list else generate_unique_colors(n)
    palette = {}
    for i, v in enumerate(unique_vals):
        palette[v] = "#ccc" if v == "Unknown" else uc[i]
    seen = set()
    ring_counts = defaultdict(int)
    for lf in lnames:
        v2 = vals.get(str(lf), vals.get(clean_name(str(lf)), None))
        if v2 is not None and lf not in seen:
            ring_counts[v2] += 1
            seen.add(lf)
    return {
        "label":   label,
        "values":  vals,
        "palette": palette,
        "counts":  dict(ring_counts),
    }


def mlst_ring(lnames, mdf, pal=None):
    return _meta_ring(lnames, mdf, detect_mlst, "MLST", pal, False)


def country_ring(lnames, mdf, pal=None):
    return _meta_ring(lnames, mdf, detect_country, "Country", pal, True)
'''

with open("/content/modules/rings.py", "w") as fh:
    fh.write(src)

print("modules/rings.py written")
