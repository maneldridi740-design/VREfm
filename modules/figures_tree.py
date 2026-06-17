# ============================================================
# Cell 10 — modules/figures_tree.py
# ============================================================

src = '''\
import math
import numpy as np
import networkx as nx
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import plotly.graph_objects as go
import plotly.express as px
from collections import defaultdict

from modules.io_utils import clean_name
from modules.detect import detect_locus
from modules.colors import ABSENT_COL, ensure_enough_colors, generate_unique_colors
from modules.tree_utils import polar_coords, _root_tree, get_leaves


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


def _cmap(mdf, col):
    pal = (
        px.colors.qualitative.Set2
        + px.colors.qualitative.Bold
        + px.colors.qualitative.D3
        + px.colors.qualitative.Alphabet
    )
    cm, v2c = {}, {}
    if mdf is None or col is None or col not in mdf.columns:
        return cm, v2c
    lc = detect_locus(mdf)
    if lc is None:
        return cm, v2c
    uv = list(mdf[col].dropna().unique())
    uc = ensure_enough_colors([to_hex(c) for c in pal], len(uv))
    v2c = {v: uc[i] for i, v in enumerate(uv)}
    for _, row in mdf.iterrows():
        cm[clean_name(str(row[lc]))] = v2c.get(row[col], "#999")
    return cm, v2c


def _arc_segments(theta, r_in, r_out, dtheta, n_pts=4):
    t1, t2 = theta - dtheta / 2, theta + dtheta / 2
    xs, ys = [], []
    for t in np.linspace(t1, t2, n_pts):
        xs.append(r_in  * np.cos(t))
        ys.append(r_in  * np.sin(t))
    for t in np.linspace(t2, t1, n_pts):
        xs.append(r_out * np.cos(t))
        ys.append(r_out * np.sin(t))
    xs.append(r_in * np.cos(t1))
    ys.append(r_in * np.sin(t1))
    xs.append(None)
    ys.append(None)
    return xs, ys


def draw_circ_plotly(
    tree, rings, title="", show_labels=True,
    ring_thick=0.04, ring_gap=0.07,
    show_absent=False, rect_border=0.3,
):
    if tree is None:
        return go.Figure().add_annotation(
            text="No tree", x=0.5, y=0.5,
            xref="paper", yref="paper", showarrow=False,
        )
    depth, angle, leaves = polar_coords(tree)
    if not depth:
        return go.Figure()
    max_d   = max(depth.values()) or 1.0
    n_lv    = len(leaves)
    p2c     = lambda th, r: (r * np.cos(th), r * np.sin(th))
    traces  = []
    ex, ey  = [], []

    def _edges(cl):
        tp = angle.get(id(cl), 0)
        rp = depth.get(id(cl), 0)
        for ch in cl.clades:
            tc  = angle.get(id(ch), 0)
            rc  = depth.get(id(ch), 0)
            t1, t2 = min(tp, tc), max(tp, tc)
            npt = 5 if n_lv > 500 else 15 if n_lv > 200 else 30
            ta  = (
                np.linspace(t2, t1 + 2 * np.pi, npt)
                if t2 - t1 > np.pi
                else np.linspace(t1, t2, npt)
            )
            for t in ta:
                x, y = p2c(t, rp)
                ex.append(x); ey.append(y)
            ex.append(None); ey.append(None)
            x1, y1 = p2c(tc, rp)
            x2, y2 = p2c(tc, rc)
            ex.extend([x1, x2, None])
            ey.extend([y1, y2, None])
            _edges(ch)

    _edges(tree.root)
    lw = 0.5 if n_lv > 500 else 0.7
    traces.append(go.Scatter(
        x=ex, y=ey, mode="lines",
        line=dict(width=lw, color="#555"),
        hoverinfo="none", showlegend=False,
    ))

    dtheta  = 2 * np.pi / max(n_lv, 1) * 0.88
    arc_pts = 2 if n_lv > 500 else 3 if n_lv > 200 else 6

    for ri, ring in enumerate(rings):
        if ring is None:
            continue
        r_in  = max_d * (1.04 + ring_gap  * ri)
        r_out = r_in + max_d * ring_thick
        rv, rp, rl = ring["values"], ring["palette"], ring["label"]
        vg = defaultdict(list)
        for lf in leaves:
            ln  = str(lf.name) if lf.name else ""
            cn  = clean_name(ln)
            th  = angle.get(id(lf), 0)
            val = rv.get(ln, rv.get(cn, None))
            vg["Absent" if val is None else val].append((th, cn))
        for val, items in vg.items():
            col = rp.get(val, ABSENT_COL)
            if val == "Absent" and not show_absent:
                continue
            axs, ays = [], []
            for th, cn in items:
                rxs, rys = _arc_segments(th, r_in, r_out, dtheta, arc_pts)
                axs.extend(rxs); ays.extend(rys)
            nc = ring["counts"].get(val, 0)
            traces.append(go.Scatter(
                x=axs, y=ays, mode="lines",
                fill="toself", fillcolor=col,
                line=dict(width=rect_border, color="rgba(50,50,50,0.4)"),
                name=f"{rl}: {val} ({nc})",
                legendgroup=f"{rl}_{val}", showlegend=True,
                hoverinfo="text",
                hovertext=f"{rl}: {val} (n={nc})",
            ))
        hx, hy, ht = [], [], []
        rm = (r_in + r_out) / 2
        for lf in leaves:
            ln  = str(lf.name) if lf.name else ""
            cn  = clean_name(ln)
            th  = angle.get(id(lf), 0)
            val = rv.get(ln, rv.get(cn, None))
            val = "Absent" if val is None else val
            hx.append(rm * np.cos(th))
            hy.append(rm * np.sin(th))
            ht.append(f"<b>{cn}</b><br>{rl}: {val}")
        sz = max(2, min(8, 800 // max(n_lv, 1)))
        traces.append(go.Scatter(
            x=hx, y=hy, mode="markers",
            marker=dict(size=sz, color="rgba(0,0,0,0)"),
            hovertext=ht, hoverinfo="text", showlegend=False,
        ))

    lx  = [p2c(angle.get(id(l), 0), depth.get(id(l), 0))[0] for l in leaves]
    ly  = [p2c(angle.get(id(l), 0), depth.get(id(l), 0))[1] for l in leaves]
    ln2 = [clean_name(str(l.name)) for l in leaves]
    st2 = show_labels and n_lv <= 200
    msz = 2 if n_lv > 500 else 3
    traces.append(go.Scatter(
        x=lx, y=ly,
        mode="markers+text" if st2 else "markers",
        marker=dict(size=msz, color="#333"),
        text=ln2 if st2 else None,
        textposition="top center",
        textfont=dict(size=5),
        hovertext=[f"<b>{n}</b>" for n in ln2],
        hoverinfo="text", showlegend=False,
    ))

    fig = go.Figure(traces)
    fig.update_layout(
        title=dict(text=f"{title} (n={n_lv})",
                   font=dict(size=15, color="#1a5276")),
        plot_bgcolor="white", paper_bgcolor="white",
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False,
                   scaleanchor="y", scaleratio=1),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        height=800, legend=dict(font=dict(size=8)),
        margin=dict(l=20, r=20, t=60, b=20),
    )
    return fig


def draw_circ_mpl(
    tree, rings, title="", show_labels=False,
    font_size=5, figsize=(14, 14), ring_width=0.03,
):
    if tree is None:
        fig, ax = plt.subplots(figsize=(6, 6))
        ax.text(0.5, 0.5, "No tree", ha="center")
        ax.set_axis_off()
        return fig
    depth, angle, leaves = polar_coords(tree)
    if not depth:
        fig, ax = plt.subplots(figsize=(6, 6))
        ax.text(0.5, 0.5, "Empty", ha="center")
        ax.set_axis_off()
        return fig
    max_d = max(depth.values()) or 1.0
    fig   = plt.figure(figsize=figsize)
    ax    = fig.add_subplot(111, projection="polar")
    ax.set_theta_direction(-1)
    ax.set_theta_offset(np.pi / 2)
    ax.set_axis_off()

    def _draw(cl):
        tp = angle.get(id(cl), 0)
        rp = depth.get(id(cl), 0)
        for ch in cl.clades:
            tc, rc = angle.get(id(ch), 0), depth.get(id(ch), 0)
            t1, t2 = min(tp, tc), max(tp, tc)
            ta = (
                np.linspace(t2, t1 + 2 * np.pi, 50)
                if t2 - t1 > np.pi
                else np.linspace(t1, t2, 50)
            )
            ax.plot(ta, np.full_like(ta, rp), color="#444", lw=0.5, alpha=0.8)
            ax.plot([tc, tc], [rp, rc],        color="#444", lw=0.5, alpha=0.8)
            _draw(ch)

    _draw(tree.root)
    n_lv   = len(leaves)
    dtheta = 2 * np.pi / max(n_lv, 1) * 0.88

    for ri, ring in enumerate(rings):
        if ring is None:
            continue
        rr = max_d * (1.05 + ring_width * 2.5 * ri)
        rv, rp = ring["values"], ring["palette"]
        for lf in leaves:
            ln  = str(lf.name) if lf.name else ""
            cn  = clean_name(ln)
            th  = angle.get(id(lf), 0)
            val = rv.get(ln, rv.get(cn, None))
            col = rp.get(val, ABSENT_COL) if val is not None else ABSENT_COL
            ts  = np.linspace(th - dtheta / 2, th + dtheta / 2, 12)
            ax.fill_between(
                ts,
                rr - ring_width * max_d * 0.9,
                rr + ring_width * max_d * 0.9,
                color=col, alpha=0.9, lw=0.15, edgecolor="#333",
            )
    ax.set_title(title, fontsize=13, fontweight="bold",
                 pad=20, color="#1a5276")
    return fig


def draw_rect(G, xp, yp, mdf=None, ccol=None, title="", show_labels=True):
    T, r = _root_tree(G)
    if r is None:
        return go.Figure()
    leaf   = get_leaves(G)
    cm, v2c = _cmap(mdf, ccol)
    ex, ey = [], []
    for u, v in T.edges():
        if u in xp and v in xp:
            ex += [xp[u], xp[u], xp[v], None]
            ey += [yp[u], yp[v], yp[v], None]
    traces = [go.Scatter(
        x=ex, y=ey, mode="lines",
        line=dict(width=1.3, color="#555"),
        hoverinfo="none", showlegend=False,
    )]
    lv = [n for n in leaf if n in xp]
    traces.append(go.Scatter(
        x=[xp[n] for n in lv],
        y=[yp[n] for n in lv],
        mode="markers+text" if show_labels else "markers",
        marker=dict(
            size=8,
            color=[cm.get(clean_name(str(n)), "#27ae60") for n in lv],
            line=dict(width=1, color="#333"),
        ),
        text=[f" {clean_name(n)}" for n in lv] if show_labels else None,
        textposition="middle right",
        textfont=dict(size=7),
        hoverinfo="text", showlegend=False,
    ))
    for val, col in v2c.items():
        traces.append(go.Scatter(
            x=[None], y=[None], mode="markers",
            marker=dict(size=10, color=col),
            name=str(val),
        ))
    fig = go.Figure(traces)
    fig.update_layout(
        title=dict(text=title),
        plot_bgcolor="white", paper_bgcolor="white",
        showlegend=bool(v2c),
        xaxis=dict(title="Distance", showgrid=True, gridcolor="#eee"),
        yaxis=dict(showticklabels=False, showgrid=False),
        height=max(500, len(lv) * 16 + 100),
    )
    return fig


def draw_net(G, pos, mdf=None, ccol=None, show_labels=True, title=""):
    leaf    = get_leaves(G)
    cm, v2c = _cmap(mdf, ccol)
    ex, ey  = [], []
    for u, v in G.edges():
        if u in pos and v in pos:
            ex += [pos[u][0], pos[v][0], None]
            ey += [pos[u][1], pos[v][1], None]
    traces = [go.Scatter(
        x=ex, y=ey, mode="lines",
        line=dict(width=1, color="#aaa"),
        hoverinfo="none", showlegend=False,
    )]
    vis = [n for n in leaf if n in pos]
    traces.append(go.Scatter(
        x=[pos[n][0] for n in vis],
        y=[pos[n][1] for n in vis],
        mode="markers+text" if show_labels else "markers",
        marker=dict(
            size=12,
            color=[cm.get(clean_name(str(n)), "#27ae60") for n in vis],
            line=dict(width=1, color="#333"),
        ),
        text=[clean_name(n) for n in vis] if show_labels else None,
        textposition="top center",
        textfont=dict(size=6),
        hoverinfo="text", name="Leaves",
    ))
    for val, col in v2c.items():
        traces.append(go.Scatter(
            x=[None], y=[None], mode="markers",
            marker=dict(size=10, color=col),
            name=str(val),
        ))
    fig = go.Figure(traces)
    fig.update_layout(
        title=dict(text=title),
        showlegend=bool(v2c),
        plot_bgcolor="white", paper_bgcolor="white",
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        height=700,
    )
    return fig
'''

with open("/content/modules/figures_tree.py", "w") as fh:
    fh.write(src)

print("modules/figures_tree.py written")
