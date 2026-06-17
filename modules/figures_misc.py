# ============================================================
# Cell 11 — modules/figures_misc.py
# ============================================================

src = '''\
import io
import numpy as np
import pandas as pd
import matplotlib.colors as mcolors
import plotly.graph_objects as go
import plotly.express as px

from modules.io_utils import clean_name, is_valid_df
from modules.detect import detect_mlst, detect_locus
from modules.colors import (
    ensure_enough_colors, generate_unique_colors,
    RING_PALETTES, SUNBURST_TEXT_OPTIONS,
)


def to_hex(c):
    if not c or not isinstance(c, str):
        return "#999999"
    c = c.strip()
    if c.startswith("#"):
        if len(c) == 4:
            return f"#{c[1]*2}{c[2]*2}{c[3]*2}"
        return c[:7]
    try:
        return mcolors.to_hex(c)
    except Exception:
        return "#999999"


def draw_hm_p(gdf, leaf_order=None, title="Heatmap"):
    if gdf is None:
        return None
    gene_cols = list(gdf.columns[1:])
    if not gene_cols:
        return None
    df = gdf.set_index(gdf.columns[0])[gene_cols].copy()
    df.index = [clean_name(str(i)) for i in df.index]
    df = df.apply(pd.to_numeric, errors="coerce").fillna(0).astype(int)
    if leaf_order:
        vl = [clean_name(str(l)) for l in leaf_order]
        vl = [l for l in vl if l in df.index]
        if vl:
            df = df.loc[vl]
    fig = go.Figure(go.Heatmap(
        z=df.values, x=gene_cols, y=df.index.tolist(),
        colorscale=[[0, "#f5f5f5"], [1, "#e74c3c"]],
        showscale=True, xgap=2, ygap=1,
    ))
    fig.update_layout(
        title=title, plot_bgcolor="white", paper_bgcolor="white",
        height=max(400, len(df) * 12 + 100),
        yaxis=dict(autorange="reversed", tickfont=dict(size=7)),
        xaxis=dict(tickangle=45, tickfont=dict(size=8)),
    )
    return fig


def draw_prev(gene_rings, n_total, title="Prevalence"):
    if not gene_rings:
        return None
    data = []
    for gene, vals in gene_rings.items():
        seen = set(); count = 0
        for k, v in vals.items():
            ck = clean_name(k)
            if ck not in seen and v >= 1:
                count += 1; seen.add(ck)
        data.append({
            "Gene": gene, "N": count,
            "%": round(100 * count / n_total, 1) if n_total > 0 else 0,
        })
    df     = pd.DataFrame(data).sort_values("N", ascending=False)
    colors = [
        "#e74c3c" if "vana" in g.lower()
        else "#3498db" if "vanb" in g.lower()
        else "#27ae60"
        for g in df["Gene"]
    ]
    fig = go.Figure(go.Bar(
        x=df["Gene"], y=df["%"],
        marker_color=colors, text=df["N"], textposition="outside",
    ))
    fig.update_layout(
        title=title, plot_bgcolor="white", paper_bgcolor="white",
        height=400, xaxis=dict(tickangle=45),
        yaxis=dict(title="%", range=[0, max(df["%"].max() * 1.2, 10)]),
    )
    return fig


def draw_pie(mdf, top_n=15):
    if mdf is None:
        return None
    mc = detect_mlst(mdf)
    if mc is None:
        return None
    v  = mdf[mc].astype(str).replace({"-": "Unknown", "nan": "Unknown", "": "Unknown"})
    v  = v[v != "Unknown"]
    vc = v.value_counts().head(top_n)
    if vc.empty:
        return None
    uc  = ensure_enough_colors([to_hex(c) for c in px.colors.qualitative.Set2], len(vc))
    fig = px.pie(
        values=vc.values,
        names=[f"ST-{x}" for x in vc.index],
        title=f"Top {top_n} MLST",
        color_discrete_sequence=uc,
    )
    fig.update_layout(paper_bgcolor="white", height=450)
    return fig


def draw_sunburst_custom(
    mdf, levels, level_color_cfg=None,
    legend_pos="right", title="Sunburst",
    height=650, text_info="label+percent entry",
):
    if mdf is None or not levels:
        return None, "No data", {}
    vl = [c for c in levels if c in mdf.columns]
    if not vl:
        return None, "Columns not found", {}
    df = mdf[vl].dropna().copy()
    for c in vl:
        df[c] = df[c].astype(str).apply(
            lambda x: x.split(":")[0].strip() if ":" in x else x.strip()
        )
        df = df[~df[c].isin(["-", "Unknown", "nan", "None", ""])]
    if len(df) < 2:
        return None, f"Only {len(df)} rows", {}
    if len(df) > 5000:
        df = df.sample(5000, random_state=42)

    fig = px.sunburst(df, path=vl, title=title)
    alc = {}

    if level_color_cfg:
        for lvl in vl:
            cfg  = level_color_cfg.get(lvl, {"mode": "palette", "palette": "Auto150 (150)"})
            vals = sorted(df[lvl].unique())
            lm   = {}
            if cfg.get("mode") == "solid":
                for v in vals:
                    lm[v] = cfg.get("color", "#3498db")
            else:
                pn = cfg.get("palette", "Auto150 (150)")
                ph = RING_PALETTES.get(pn, generate_unique_colors(150))
                uc = ensure_enough_colors(ph, len(vals))
                for i, v in enumerate(vals):
                    lm[v] = uc[i]
            alc[lvl] = lm
        sd = fig.data[0]
        if hasattr(sd, "ids") and sd.ids is not None and len(sd.ids) > 0:
            nc = []
            for i in range(len(sd.labels)):
                lb = str(sd.labels[i]) if sd.labels[i] is not None else ""
                iv = str(sd.ids[i])    if sd.ids[i]    is not None else ""
                if not lb or lb in ["(?)", "total"]:
                    nc.append("rgba(255,255,255,0)"); continue
                dp2  = iv.count("/")
                li   = min(dp2, len(vl) - 1)
                nc.append(alc.get(vl[li], {}).get(lb, "#cccccc"))
            fig.update_traces(marker=dict(colors=nc))
    else:
        cb  = vl[0]
        uv  = sorted(df[cb].unique())
        uc  = generate_unique_colors(len(uv))
        eff = {v: uc[i] for i, v in enumerate(uv)}
        fig = px.sunburst(df, path=vl, color=cb,
                          color_discrete_map=eff, title=title)
        alc[cb] = eff

    if text_info and text_info != "none":
        fig.update_traces(textinfo=text_info)
    else:
        fig.update_traces(textinfo="none")
    fig.update_traces(marker_line=dict(width=1, color="#333"))

    leg_cfgs = {
        "right": dict(orientation="v", x=1.02,  y=0.5,
                      xanchor="left",  yanchor="middle"),
        "left":  dict(orientation="v", x=-0.15, y=0.5,
                      xanchor="right", yanchor="middle"),
        "none":  None,
    }
    if legend_pos != "none":
        for lvl in alc:
            pfx = (
                "ST-"
                if lvl.lower().strip() in ["mlst", "st", "sequence_type"]
                else ""
            )
            for val, col in alc[lvl].items():
                cnt = int((df[lvl] == val).sum()) if lvl in df.columns else 0
                fig.add_trace(go.Scatter(
                    x=[None], y=[None], mode="markers",
                    marker=dict(size=12, color=col,
                                line=dict(width=1, color="#333")),
                    name=f"{pfx}{val} (n={cnt})",
                    legendgroup=lvl, showlegend=True,
                ))
        if legend_pos in leg_cfgs and leg_cfgs[legend_pos]:
            fig.update_layout(showlegend=True, legend=leg_cfgs[legend_pos])
    else:
        fig.update_layout(showlegend=False)

    fig.update_layout(
        paper_bgcolor="white", plot_bgcolor="white", height=height,
        title=dict(text=title, font=dict(size=15, color="#1a5276")),
        margin=dict(l=30, r=30, t=60, b=30),
    )
    level_info = {
        "levels":       vl,
        "level_colors": alc,
        "level_counts": {
            l: df[l].value_counts().to_dict()
            for l in vl if l in df.columns
        },
    }
    return fig, f"OK — {len(df)} rows", level_info
'''

with open("/content/modules/figures_misc.py", "w") as fh:
    fh.write(src)

print("modules/figures_misc.py written") 
