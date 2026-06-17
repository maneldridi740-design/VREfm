# ============================================================
# Cell 13 — modules/app.py  (Streamlit main entry point)
# ============================================================

src = '''\
import sys
sys.path.insert(0, "/content")

import math
import warnings
warnings.filterwarnings("ignore")

import streamlit as st
import pandas as pd
import numpy as np
import networkx as nx
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px

from modules.colors import (
    generate_unique_colors, ensure_enough_colors,
    VANA_PALETTES, VANB_PALETTES, RING_PALETTES,
    ABSENT_COL, SUNBURST_TEXT_OPTIONS,
)
from modules.io_utils import (
    read_table, read_newick, parse_nw, is_valid_df,
    clean_name, EXT,
)
from modules.detect import (
    detect_locus, detect_country, detect_mlst,
    get_countries, get_mlsts, loci_for_filter,
)
from modules.tree_utils import (
    bio_to_nx, get_leaves, polar_coords,
    rect_lay, clado_lay, circ_lay, radial_lay,
    filter_tree, limit_tree, prepare_tree,
)
from modules.rings import (
    proc_genes, match_stats, build_van_ring,
    mlst_ring, country_ring,
)
from modules.geo_data import COUNTRY_COORDS
from modules.figures_tree import (
    draw_circ_plotly, draw_circ_mpl, draw_rect, draw_net,
)
from modules.figures_misc import (
    draw_hm_p, draw_prev, draw_pie, draw_sunburst_custom,
)
from modules.figures_geo import (
    draw_geo, draw_bubble_map, draw_connection_map,
    draw_mlst_flow_map, draw_pie_map, draw_sankey,
    draw_diversity_map, draw_dominance_map,
)
from modules.export_ui import (
    safe_key, btn, export_plotly, export_mpl,
    show_palette_preview,
    apply_color_overrides, show_color_editors,
    apply_sunburst_overrides, show_sunburst_color_editors,
)

# ── Page config ──────────────────────────────────────────────
st.set_page_config(
    page_title="VREfm v3.3",
    page_icon="\\U0001f9ec",
    layout="wide",
)

st.markdown("""
<style>
.main { background: #f8f9fa }
section[data-testid="stSidebar"] { background: #eef1f5 }
.hdr {
    background: linear-gradient(135deg,#1a5276,#27ae60 60%,#2980b9);
    padding: 1.2rem 2rem; border-radius: 12px;
    margin-bottom: 1rem; text-align: center
}
.hdr h1 { color:#fff; margin:0; font-size:1.8rem }
.hdr p  { color:#d5f5e3; margin:.2rem 0 0; font-size:.85rem }
.gbtn button {
    background:#27ae60!important; color:white!important;
    border-radius:8px!important; font-weight:bold!important;
    padding:.4rem 1.5rem!important; border:none!important
}
.gbtn button:hover { background:#1e8449!important }
.ebox {
    background:#f0f7f0; border:1px solid #c3e6cb;
    border-radius:8px; padding:.8rem; margin-top:.8rem
}
</style>
""", unsafe_allow_html=True)

st.markdown(
    \'<div class="hdr"><h1>VREfm v3.3</h1>\'
    "<p>Color Picker · Smart Geo · 200 MLST</p></div>",
    unsafe_allow_html=True,
)

# ── Sidebar ──────────────────────────────────────────────────
FTT = ["newick", "nwk", "tree", "txt", "fa", "fas", "fasta"]
FTD = ["csv", "tsv", "xlsx", "xls", "txt"]

with st.sidebar:
    st.markdown("## Files")
    nf_c = st.file_uploader("Tree — Chromosome", type=FTT, key="nc")
    nf_p = st.file_uploader("Tree — Plasmid",    type=FTT, key="np2")
    gf_c = st.file_uploader("Genes — Chromosome",type=FTD, key="gc2")
    gf_p = st.file_uploader("Genes — Plasmid",   type=FTD, key="gp2")
    mf   = st.file_uploader("Metadata",           type=FTD, key="mf2")
    st.markdown("---")
    mode = st.selectbox("Mode", ["1 Chromosome", "2 Plasmid", "3 Combined"])
    st.markdown("---")
    vpa     = st.selectbox("VanA palette", list(VANA_PALETTES.keys()), key="vpa")
    vpb     = st.selectbox("VanB palette", list(VANB_PALETTES.keys()), key="vpb")
    va_cols = VANA_PALETTES[vpa]
    vb_cols = VANB_PALETTES[vpb]
    st.markdown("---")
    st.markdown("### Ring settings")
    show_lbl      = st.checkbox("Labels", False)
    lbl_sz        = st.slider("Font size", 3, 12, 5)
    fig_sz        = st.slider("Figure size", 8, 24, 14)
    ring_w        = st.slider("Ring width (mpl)", 0.01, 0.08, 0.03, 0.005)
    ring_thick_p  = st.slider("Ring thickness",   0.02, 0.12, 0.04, 0.005)
    ring_gap_p    = st.slider("Ring gap",          0.04, 0.15, 0.07, 0.005)
    rect_border_p = st.slider("Border width",       0.0,  2.0,  0.3, 0.1)
    show_absent   = st.checkbox("Show absent", False)
    use_plotly    = st.checkbox("Plotly engine", True)
    s_va = st.checkbox("VanA ring",    True)
    s_vb = st.checkbox("VanB ring",    True)
    s_ml = st.checkbox("MLST ring",    True)
    s_co = st.checkbox("Country ring", True)

# ── File loading ─────────────────────────────────────────────
tree_c = tree_p = None
if nf_c:
    nw = read_newick(nf_c)
    tree_c = parse_nw(nw) if nw else None
    if tree_c:
        st.sidebar.success(f"Chr: {tree_c.count_terminals()} leaves")

if nf_p:
    nw = read_newick(nf_p)
    tree_p = parse_nw(nw) if nw else None
    if tree_p:
        st.sidebar.success(f"Pla: {tree_p.count_terminals()} leaves")

gdf_c = read_table(gf_c) if gf_c else None
gdf_p = read_table(gf_p) if gf_p else None
if is_valid_df(gdf_c): st.sidebar.success("Genes — Chr loaded")
if is_valid_df(gdf_p): st.sidebar.success("Genes — Pla loaded")

meta_df = read_table(mf) if mf else None
if is_valid_df(meta_df):
    st.sidebar.success(f"Metadata: {meta_df.shape[0]} rows")

with st.sidebar:
    st.markdown("---")
    st.markdown("### Filters")
    f_countries = f_mlsts = None
    if is_valid_df(meta_df):
        ac = get_countries(meta_df)
        if ac:
            f_countries = st.multiselect("Countries", ac, default=[], key="fc")
        am = get_mlsts(meta_df)
        if am:
            f_mlsts = st.multiselect("MLST", am, default=[], key="fm")
    f_nmax = st.number_input("Max leaves (0 = all)", 0, 10000, 0, 50, key="fn")


def get_active():
    if "Chromosome" in mode:
        bt = tree_c if tree_c is not None else tree_p
        gd = gdf_c  if is_valid_df(gdf_c)  else gdf_p
    elif "Plasmid" in mode:
        bt = tree_p if tree_p is not None else tree_c
        gd = gdf_p  if is_valid_df(gdf_p)  else gdf_c
    else:
        bt = tree_c if tree_c is not None else tree_p
        gd = gdf_c  if is_valid_df(gdf_c)  else gdf_p
    return bt, gd if is_valid_df(gd) else None


bio_tree, gene_df = get_active()

filtered_loci = None
if is_valid_df(meta_df):
    hfc = f_countries and len(f_countries) > 0
    hfm = f_mlsts     and len(f_mlsts)     > 0
    if hfc or hfm:
        filtered_loci = loci_for_filter(
            meta_df,
            f_countries if hfc else None,
            f_mlsts     if hfm else None,
        )

# ── Tabs ─────────────────────────────────────────────────────
tabs = st.tabs([
    "Circular", "Phylo", "Network", "Heatmap",
    "Stats", "Sunburst", "Geo", "Diagnostic", "Export", "Guide",
])

# ────────────────────────────────────────────────────────────
# TAB 0 — Circular
# ────────────────────────────────────────────────────────────
with tabs[0]:
    st.subheader("Circular Tree")
    if bio_tree is None:
        st.info("Upload a Newick tree file to get started.")
    else:
        st.caption(f"Loaded tree: {bio_tree.count_terminals()} leaves")
        st.markdown("### Ring palettes")
        pal_names = list(RING_PALETTES.keys())
        pc1, pc2  = st.columns(2)
        with pc1:
            mlst_pal_name = st.selectbox(
                "MLST palette", pal_names,
                index=pal_names.index("Auto150 (150)")
                      if "Auto150 (150)" in pal_names else 0,
                key="circ_mlst_pal",
            )
            show_palette_preview(RING_PALETTES[mlst_pal_name])
        with pc2:
            country_pal_name = st.selectbox(
                "Country palette", pal_names,
                index=pal_names.index("Bold (12)")
                      if "Bold (12)" in pal_names else 0,
                key="circ_country_pal",
            )
            show_palette_preview(RING_PALETTES[country_pal_name])
        if is_valid_df(meta_df):
            mc = detect_mlst(meta_df)
            if mc:
                nm = (
                    meta_df[mc].dropna().astype(str)
                    .replace({"-": "", "nan": ""}).replace("", "_x_")
                )
                nm   = nm[nm != "_x_"].nunique()
                np2  = len(RING_PALETTES[mlst_pal_name])
                if nm > np2:
                    st.warning(f"{nm} MLST types > {np2} palette colors")
                else:
                    st.success(f"{nm} MLST types ≤ {np2} palette colors")
        st.markdown("---")
        if "circ_rings" not in st.session_state:
            st.session_state["circ_rings"] = []
        if btn("circ_main", "Generate circular tree"):
            with st.spinner("Preparing tree..."):
                at, no, nf2 = prepare_tree(bio_tree, filtered_loci, f_nmax)
            lvs    = at.get_terminals()
            lnames = [str(l.name) for l in lvs]
            c1, c2 = st.columns(2)
            with c1: st.metric("Original leaves", no)
            with c2: st.metric("Displayed leaves", nf2)
            with st.spinner("Drawing..."):
                gr = proc_genes(gene_df, lnames) if is_valid_df(gene_df) else {}
                rings = []
                if s_va and gr:
                    r = build_van_ring(gr, "vanA", va_cols)
                    if r: rings.append(r)
                if s_vb and gr:
                    r = build_van_ring(gr, "vanB", vb_cols)
                    if r: rings.append(r)
                if s_ml and is_valid_df(meta_df):
                    r = mlst_ring(lnames, meta_df, RING_PALETTES[mlst_pal_name])
                    if r: rings.append(r)
                if s_co and is_valid_df(meta_df):
                    r = country_ring(lnames, meta_df, RING_PALETTES[country_pal_name])
                    if r: rings.append(r)
                st.session_state["circ_rings"] = rings
                st.session_state["circ_tree"]  = at
                apply_color_overrides(rings, "circ")
                ml = mode.split(" ", 1)[1] if " " in mode else mode
                if use_plotly:
                    fig = draw_circ_plotly(
                        at, rings, f"Circular — {ml}", show_lbl,
                        ring_thick=ring_thick_p, ring_gap=ring_gap_p,
                        show_absent=show_absent, rect_border=rect_border_p,
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    export_plotly(fig, "circular", 800)
                else:
                    fig = draw_circ_mpl(
                        at, rings, f"Circular — {ml}", show_lbl,
                        lbl_sz, (fig_sz, fig_sz), ring_w,
                    )
                    st.pyplot(fig, use_container_width=True)
                    export_mpl(fig, "circular_mpl")
        if st.session_state.get("circ_rings"):
            st.markdown("---")
            show_color_editors(st.session_state["circ_rings"], "circ")
            if st.button("Apply new colors", key="circ_reapply"):
                rings = st.session_state["circ_rings"]
                apply_color_overrides(rings, "circ")
                at = st.session_state.get("circ_tree", bio_tree)
                if at is not None:
                    ml = mode.split(" ", 1)[1] if " " in mode else mode
                    if use_plotly:
                        fig = draw_circ_plotly(
                            at, rings, f"Circular — {ml} (updated)", show_lbl,
                            ring_thick=ring_thick_p, ring_gap=ring_gap_p,
                            show_absent=show_absent, rect_border=rect_border_p,
                        )
                        st.plotly_chart(fig, use_container_width=True)
                        export_plotly(fig, "circular_updated", 800)
                    else:
                        fig = draw_circ_mpl(
                            at, rings, f"Circular — {ml} (updated)", show_lbl,
                            lbl_sz, (fig_sz, fig_sz), ring_w,
                        )
                        st.pyplot(fig, use_container_width=True)
                        export_mpl(fig, "circular_mpl_updated")

# ────────────────────────────────────────────────────────────
# TAB 1 — Phylo
# ────────────────────────────────────────────────────────────
with tabs[1]:
    st.subheader("Phylograms")
    if bio_tree is None:
        st.info("Load a tree file first.")
    else:
        sty = st.selectbox(
            "Style", ["Phylogram", "Cladogram", "Circular", "Radial"],
            key="phsty",
        )
        ccol = None
        if is_valid_df(meta_df):
            sel = st.selectbox(
                "Color leaves by", ["None"] + list(meta_df.columns), key="pc"
            )
            if sel != "None":
                ccol = sel
        if btn("phylo_fig", f"Generate {sty}"):
            with st.spinner(f"Drawing {sty}..."):
                at1, _, _ = prepare_tree(bio_tree, filtered_loci, f_nmax)
                G = bio_to_nx(at1)
                comps = list(nx.connected_components(G))
                if len(comps) > 1:
                    G = G.subgraph(max(comps, key=len)).copy()
                if not nx.is_tree(G) and G.number_of_nodes() > 0:
                    G = nx.minimum_spanning_tree(G)
                fig = None
                if sty == "Phylogram":
                    xp, yp = rect_lay(G, branch_scale=True)
                    if xp:
                        fig = draw_rect(G, xp, yp, meta_df, ccol,
                                        "Phylogram", show_lbl)
                elif sty == "Cladogram":
                    xp, yp = clado_lay(G)
                    if xp:
                        fig = draw_rect(G, xp, yp, meta_df, ccol,
                                        "Cladogram", show_lbl)
                elif sty == "Circular":
                    xc, yc = circ_lay(G)
                    if xc:
                        pos = {n: (xc[n], yc[n]) for n in xc}
                        fig = draw_net(G, pos, meta_df, ccol,
                                       show_lbl, "Circular")
                        fig.update_layout(
                            xaxis=dict(scaleanchor="y", scaleratio=1)
                        )
                elif sty == "Radial":
                    xr, yr = radial_lay(G)
                    if xr:
                        pos = {n: (xr[n], yr[n]) for n in xr}
                        fig = draw_net(G, pos, meta_df, ccol,
                                       show_lbl, "Radial")
                        fig.update_layout(
                            xaxis=dict(scaleanchor="y", scaleratio=1)
                        )
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
                    export_plotly(fig, f"phylo_{sty.lower()}", 700)

# ────────────────────────────────────────────────────────────
# TAB 2 — Network
# ────────────────────────────────────────────────────────────
with tabs[2]:
    st.subheader("Network")
    if bio_tree is None:
        st.info("Load a tree file first.")
    else:
        lay = st.selectbox(
            "Layout",
            ["spring", "kamada_kawai", "circular", "spectral"],
            key="nl",
        )
        cc2 = None
        if is_valid_df(meta_df):
            s2 = st.selectbox(
                "Color by", ["None"] + list(meta_df.columns), key="nc3"
            )
            if s2 != "None":
                cc2 = s2
        if btn("net_fig", "Generate network"):
            at2, _, _ = prepare_tree(bio_tree, filtered_loci, f_nmax)
            G  = bio_to_nx(at2)
            nn = max(G.number_of_nodes(), 1)
            try:
                if lay == "spring":
                    pos = nx.spring_layout(G, k=3 / math.sqrt(nn),
                                           iterations=80, seed=42)
                elif lay == "kamada_kawai":
                    pos = nx.kamada_kawai_layout(G)
                elif lay == "circular":
                    pos = nx.circular_layout(G)
                else:
                    pos = nx.spectral_layout(G)
            except Exception:
                pos = nx.spring_layout(G, seed=42)
            fig = draw_net(G, pos, meta_df, cc2, show_lbl, f"Network — {lay}")
            st.plotly_chart(fig, use_container_width=True)
            export_plotly(fig, f"net_{lay}", 700)

# ────────────────────────────────────────────────────────────
# TAB 3 — Heatmap
# ────────────────────────────────────────────────────────────
with tabs[3]:
    st.subheader("Gene Heatmap")
    ds = {}
    if is_valid_df(gdf_c): ds["Chromosome"] = gdf_c
    if is_valid_df(gdf_p): ds["Plasmid"]    = gdf_p
    if not ds:
        st.info("Upload gene presence/absence data.")
    else:
        sd = (
            st.selectbox("Dataset", list(ds.keys()), key="hd")
            if len(ds) > 1 else list(ds.keys())[0]
        )
        if btn("hm_fig", "Generate heatmap"):
            at3, _, _ = prepare_tree(bio_tree, filtered_loci, f_nmax)
            lo = (
                [str(l.name) for l in at3.get_terminals()]
                if at3 else None
            )
            fig = draw_hm_p(ds[sd], lo, f"Heatmap — {sd}")
            if fig:
                st.plotly_chart(fig, use_container_width=True)
                export_plotly(fig, "heatmap", 500)

# ────────────────────────────────────────────────────────────
# TAB 4 — Stats
# ────────────────────────────────────────────────────────────
with tabs[4]:
    st.subheader("Statistics")
    if btn("stat_prev", "Gene prevalence"):
        at4, _, _ = prepare_tree(bio_tree, filtered_loci, f_nmax)
        if at4 and is_valid_df(gene_df):
            ln3 = [str(l.name) for l in at4.get_terminals()]
            gr3 = proc_genes(gene_df, ln3)
            fig = draw_prev(gr3, len(ln3))
            if fig:
                st.plotly_chart(fig, use_container_width=True)
                export_plotly(fig, "prevalence", 400)
    if btn("stat_pie", "MLST pie chart"):
        fig = draw_pie(meta_df)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
            export_plotly(fig, "mlst_pie", 450)

# ────────────────────────────────────────────────────────────
# TAB 5 — Sunburst
# ────────────────────────────────────────────────────────────
with tabs[5]:
    st.subheader("Sunburst Chart")
    if not is_valid_df(meta_df):
        st.info("Upload metadata to use this tab.")
    else:
        all_cols = list(meta_df.columns)
        cc_det   = detect_country(meta_df)
        mc_det   = detect_mlst(meta_df)
        st.markdown("### 1. Hierarchy levels")
        lc1, lc2, lc3, lc4 = st.columns(4)
        with lc1:
            i1   = all_cols.index(cc_det) + 1 if cc_det and cc_det in all_cols else 0
            lvl1 = st.selectbox("Level 1", ["None"] + all_cols, index=i1, key="sb_l1")
        with lc2:
            i2   = all_cols.index(mc_det) + 1 if mc_det and mc_det in all_cols else 0
            lvl2 = st.selectbox("Level 2", ["None"] + all_cols, index=i2, key="sb_l2")
        with lc3:
            lvl3 = st.selectbox("Level 3", ["None"] + all_cols, index=0, key="sb_l3")
        with lc4:
            lvl4 = st.selectbox("Level 4", ["None"] + all_cols, index=0, key="sb_l4")
        seen_lv    = set()
        level_cols = []
        for lv in [lvl1, lvl2, lvl3, lvl4]:
            if lv != "None" and lv not in seen_lv:
                level_cols.append(lv)
                seen_lv.add(lv)
        if not level_cols:
            st.warning("Select at least one level.")
        else:
            st.info(f"Hierarchy: {' > '.join(level_cols)}")
            st.markdown("---")
            st.markdown("### 2. Color settings per level")
            pal_names    = list(RING_PALETTES.keys())
            sb_level_cfg = {}
            default_pals = [
                "Auto150 (150)", "Alphabet (26)",
                "Dark24 (24)",   "Bold (12)",
            ]
            for idx, col in enumerate(level_cols):
                n_unique = (
                    meta_df[col].dropna().astype(str)
                    .apply(lambda x: x.split(":")[0].strip()
                           if ":" in x else x.strip())
                    .replace({"-": "", "nan": "", "None": "", "Unknown": ""})
                    .replace("", "__drop__")
                )
                n_unique = n_unique[n_unique != "__drop__"].nunique()
                with st.expander(
                    f"Level {idx+1}: {col} ({n_unique} categories)",
                    expanded=(idx == 0),
                ):
                    lm = st.radio(
                        "Color mode", ["Palette", "Solid color"],
                        key=f"sb_lm_{idx}", horizontal=True,
                    )
                    if "Palette" in lm:
                        dp = default_pals[idx % len(default_pals)]
                        if n_unique > 150:
                            dp = "Auto200 (200)"
                        elif n_unique > 50:
                            dp = "Auto150 (150)"
                        elif n_unique > 20:
                            dp = "Auto50 (50)"
                        di   = pal_names.index(dp) if dp in pal_names else 0
                        lpal = st.selectbox(
                            "Palette", pal_names, index=di, key=f"sb_lp_{idx}"
                        )
                        show_palette_preview(RING_PALETTES[lpal])
                        n_pal = len(RING_PALETTES[lpal])
                        if n_unique > n_pal:
                            st.warning(f"{n_unique} > {n_pal} — auto-extension applied")
                        else:
                            st.success(f"{n_unique} ≤ {n_pal} ✓")
                        sb_level_cfg[col] = {"mode": "palette", "palette": lpal}
                    else:
                        default_colors = [
                            "#3498db", "#27ae60", "#e67e22", "#9b59b6",
                            "#e74c3c", "#1abc9c", "#f39c12", "#2c3e50",
                        ]
                        lcolor = st.color_picker(
                            "Color",
                            default_colors[idx % len(default_colors)],
                            key=f"sb_lc_{idx}",
                        )
                        sb_level_cfg[col] = {"mode": "solid", "color": lcolor}
            st.markdown("---")
            st.markdown("### 3. Text display")
            text_opt_names  = list(SUNBURST_TEXT_OPTIONS.keys())
            sb_text_choice  = st.selectbox(
                "Segment labels", text_opt_names, index=0, key="sb_text_opt"
            )
            sb_text_info    = SUNBURST_TEXT_OPTIONS[sb_text_choice]
            st.markdown("---")
            oc1, oc2 = st.columns(2)
            with oc1:
                sb_leg = st.selectbox("Legend position",
                                      ["right", "left", "none"], key="sb_leg")
            with oc2:
                sb_height = st.slider("Chart height", 400, 1000, 650, 50,
                                      key="sb_hh")
            if "sb_alc" not in st.session_state:
                st.session_state["sb_alc"] = {}
            if "sb_lc" not in st.session_state:
                st.session_state["sb_lc"]  = {}
            st.markdown("---")
            if btn("sunburst_gen", "Generate Sunburst"):
                try:
                    fig, msg, li = draw_sunburst_custom(
                        mdf=meta_df, levels=level_cols,
                        level_color_cfg=sb_level_cfg,
                        legend_pos=sb_leg,
                        title=f"Sunburst — {' > '.join(level_cols)}",
                        height=sb_height, text_info=sb_text_info,
                    )
                    st.caption(msg)
                    if fig is not None:
                        st.session_state["sb_alc"] = li.get("level_colors", {})
                        st.session_state["sb_lc"]  = li.get("level_counts",  {})
                        apply_sunburst_overrides(st.session_state["sb_alc"], "sb")
                        alc = st.session_state["sb_alc"]
                        vl  = li.get("levels", level_cols)
                        sd  = fig.data[0]
                        if (alc and hasattr(sd, "ids")
                                and sd.ids is not None and len(sd.ids) > 0):
                            nc = []
                            for i in range(len(sd.labels)):
                                lb  = str(sd.labels[i]) if sd.labels[i] is not None else ""
                                iv  = str(sd.ids[i])    if sd.ids[i]    is not None else ""
                                if not lb or lb in ["(?)", "total"]:
                                    nc.append("rgba(255,255,255,0)"); continue
                                dp2  = iv.count("/")
                                idx2 = min(dp2, len(vl) - 1)
                                nc.append(alc.get(vl[idx2], {}).get(lb, "#cccccc"))
                            fig.update_traces(
                                marker=dict(colors=nc),
                                selector=dict(type="sunburst"),
                            )
                        st.plotly_chart(fig, use_container_width=True)
                        export_plotly(fig, "sunburst", sb_height)
                        st.session_state["sb_fig"]    = fig
                        st.session_state["sb_vl"]     = vl
                        st.session_state["sb_height"] = sb_height
                    else:
                        st.warning(msg)
                except Exception as e:
                    st.error(f"Error: {e}")
                    st.exception(e)
            if st.session_state.get("sb_alc"):
                st.markdown("---")
                show_sunburst_color_editors(
                    st.session_state["sb_alc"],
                    st.session_state.get("sb_lc", {}), "sb",
                )
                if st.button("Apply new colors", key="sb_reapply"):
                    apply_sunburst_overrides(st.session_state["sb_alc"], "sb")
                    fig = st.session_state.get("sb_fig")
                    alc = st.session_state["sb_alc"]
                    vl  = st.session_state.get("sb_vl", level_cols)
                    if fig is not None and alc:
                        sd = fig.data[0]
                        if (hasattr(sd, "ids")
                                and sd.ids is not None and len(sd.ids) > 0):
                            nc = []
                            for i in range(len(sd.labels)):
                                lb  = str(sd.labels[i]) if sd.labels[i] is not None else ""
                                iv  = str(sd.ids[i])    if sd.ids[i]    is not None else ""
                                if not lb or lb in ["(?)", "total"]:
                                    nc.append("rgba(255,255,255,0)"); continue
                                dp2  = iv.count("/")
                                idx2 = min(dp2, len(vl) - 1)
                                nc.append(alc.get(vl[idx2], {}).get(lb, "#cccccc"))
                            fig.update_traces(
                                marker=dict(colors=nc),
                                selector=dict(type="sunburst"),
                            )
                        st.plotly_chart(fig, use_container_width=True)
                        export_plotly(
                            fig, "sunburst_updated",
                            st.session_state.get("sb_height", 650),
                        )

# ────────────────────────────────────────────────────────────
# TAB 6 — Geo
# ────────────────────────────────────────────────────────────
with tabs[6]:
    st.subheader("Geographic Maps")
    if not is_valid_df(meta_df):
        st.info("Upload metadata to use geographic maps.")
    else:
        st.markdown("### Column mapping")
        all_meta_cols = ["(auto-detect)"] + list(meta_df.columns)
        gc1, gc2 = st.columns(2)
        with gc1:
            manual_country = st.selectbox(
                "Country column", all_meta_cols, index=0, key="geo_cc_manual"
            )
        with gc2:
            manual_mlst = st.selectbox(
                "MLST column", all_meta_cols, index=0, key="geo_mc_manual"
            )
        auto_cc = detect_country(meta_df)
        auto_mc = detect_mlst(meta_df)
        eff_cc  = manual_country if manual_country != "(auto-detect)" else auto_cc
        eff_mc  = manual_mlst   if manual_mlst   != "(auto-detect)" else auto_mc
        dc1, dc2 = st.columns(2)
        with dc1:
            if eff_cc:
                sv = meta_df[eff_cc].dropna().astype(str).head(3).tolist()
                st.success(f"Country column: **{eff_cc}**")
                st.caption(f"Samples: {', '.join(sv)}")
            else:
                st.error("Country column not found — select manually above.")
                st.caption(f"Available: {', '.join(meta_df.columns[:10])}")
        with dc2:
            if eff_mc:
                sv = meta_df[eff_mc].dropna().astype(str).head(3).tolist()
                st.success(f"MLST column: **{eff_mc}**")
                st.caption(f"Samples: {', '.join(sv)}")
            else:
                st.warning("MLST column not found — some maps require it.")
                st.caption(f"Available: {', '.join(meta_df.columns[:10])}")
        _orig_meta = meta_df.copy()
        if manual_country != "(auto-detect)" and manual_country in meta_df.columns:
            if manual_country != "country":
                _orig_meta["country"] = meta_df[manual_country]
        if manual_mlst != "(auto-detect)" and manual_mlst in meta_df.columns:
            if "mlst" not in [c.lower() for c in _orig_meta.columns]:
                _orig_meta["mlst"] = meta_df[manual_mlst]
        if eff_cc:
            raw = (
                meta_df[eff_cc].dropna().astype(str)
                .apply(lambda x: x.split(":")[0].strip()).unique()
            )
            recognized     = [c for c in raw if c in COUNTRY_COORDS]
            not_recognized = [
                c for c in raw
                if c not in COUNTRY_COORDS
                and c not in ["", "nan", "-", "Unknown", "None"]
            ]
            with st.expander(
                f"Country recognition: {len(recognized)} / {len(raw)}"
            ):
                if recognized:
                    st.success(
                        f"Recognized ({len(recognized)}): "
                        f"{', '.join(sorted(recognized)[:20])}"
                    )
                if not_recognized:
                    st.warning(
                        f"Not recognized ({len(not_recognized)}): "
                        f"{', '.join(sorted(not_recognized)[:20])}"
                    )
                    st.caption(
                        "These will not appear on coordinate-based maps."
                    )
        st.markdown("---")
        geo_mode = st.radio(
            "Map type",
            [
                "Choropleth", "Bubble Map", "Connection Map",
                "MLST Distribution", "Pie Map 2D", "Pie Map 3D",
                "Diversity Map", "Dominance Map", "Sankey",
            ],
            horizontal=True, key="geo_mode",
        )
        use_df = _orig_meta

        if "Choropleth" in geo_mode:
            st.markdown("##### Choropleth — isolate count per country")
            if btn("geo_fig", "Generate Choropleth"):
                fig = draw_geo(use_df)
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
                    export_plotly(fig, "geo_choropleth", 450)
                else:
                    st.error("No countries matched the ISO lookup table.")

        elif "Bubble" in geo_mode:
            st.markdown("##### Bubble Map — size = N isolates, color = dominant ST")
            if btn("geo_bubble", "Generate Bubble Map"):
                fig = draw_bubble_map(use_df)
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
                    export_plotly(fig, "geo_bubble", 550)
                else:
                    st.error("No countries found in coordinate database.")

        elif "Connection" in geo_mode:
            st.markdown("##### Connection Map — links between countries sharing STs")
            if btn("geo_conn", "Generate Connection Map"):
                fig = draw_connection_map(use_df)
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
                    export_plotly(fig, "geo_connection", 600)
                else:
                    st.error("Need ≥ 2 countries with MLST data.")

        elif "MLST Distribution" in geo_mode:
            st.markdown("##### MLST Distribution — each dot = 1 isolate")
            if btn("geo_mlst", "Generate MLST Distribution"):
                fig = draw_mlst_flow_map(use_df)
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
                    export_plotly(fig, "geo_mlst_dist", 600)
                else:
                    st.error("Country and MLST columns are required.")

        elif "Pie Map 2D" in geo_mode:
            st.markdown("##### Pie Map 2D — MLST distribution per country")
            pm1, pm2, pm3 = st.columns(3)
            with pm1:
                pie_text_mode = st.radio(
                    "Segment labels",
                    ["pct+val", "pct", "val", "none"],
                    format_func=lambda x: {
                        "pct+val": "Value + %", "pct": "% only",
                        "val": "Value only", "none": "None",
                    }[x],
                    key="pie2d_txt", horizontal=True,
                )
            with pm2:
                pie_r   = st.slider("Pie size", 1.0, 8.0, 3.0, 0.5, key="pie2d_r")
            with pm3:
                pie_top = st.slider("Top N STs", 5, 25, 10, 1, key="pie2d_top")
            pie_min_lbl = st.slider("Min % to show label", 5, 50, 12, 1,
                                    key="pie2d_minlbl")
            if btn("geo_pie2d", "Generate Pie Map 2D"):
                fig = draw_pie_map(
                    use_df, show_mode=pie_text_mode,
                    pie_radius=pie_r, top_n_st=pie_top,
                    projection="natural earth",
                    show_labels=(pie_text_mode != "none"),
                    min_pct_label=pie_min_lbl,
                )
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
                    export_plotly(fig, "geo_pie2d", 600)
                else:
                    st.error("Country and MLST columns with recognized countries required.")

        elif "Pie Map 3D" in geo_mode:
            st.markdown("##### Pie Map 3D — interactive globe with MLST pies")
            gm1, gm2, gm3 = st.columns(3)
            with gm1:
                pie3d_text = st.radio(
                    "Segment labels",
                    ["pct+val", "pct", "val", "none"],
                    format_func=lambda x: {
                        "pct+val": "Value + %", "pct": "% only",
                        "val": "Value only", "none": "None",
                    }[x],
                    key="pie3d_txt", horizontal=True,
                )
            with gm2:
                pie3d_r   = st.slider("Pie size", 1.0, 8.0, 3.5, 0.5, key="pie3d_r")
            with gm3:
                pie3d_top = st.slider("Top N STs", 5, 25, 10, 1, key="pie3d_top")
            rot1, rot2 = st.columns(2)
            with rot1:
                rot_lon = st.slider("Longitude rotation", -180, 180, 10, 5,
                                    key="pie3d_rlon")
            with rot2:
                rot_lat = st.slider("Latitude rotation", -90, 90, 30, 5,
                                    key="pie3d_rlat")
            pie3d_minlbl = st.slider("Min % to show label", 5, 50, 15, 1,
                                     key="pie3d_minlbl")
            if btn("geo_pie3d", "Generate Pie Map 3D"):
                fig = draw_pie_map(
                    use_df, show_mode=pie3d_text,
                    pie_radius=pie3d_r, top_n_st=pie3d_top,
                    projection="orthographic",
                    rot_lon=rot_lon, rot_lat=rot_lat,
                    show_labels=(pie3d_text != "none"),
                    min_pct_label=pie3d_minlbl,
                )
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
                    export_plotly(fig, "geo_pie3d_globe", 750)
                else:
                    st.error("Country and MLST columns with recognized countries required.")

        elif "Diversity Map" in geo_mode:
            st.markdown("##### Diversity Map — clonal diversity per country")
            st.caption(
                "Size = number of isolates | "
                "Color = Shannon diversity index (MLST)"
            )
            if btn("geo_diversity", "Generate Diversity Map"):
                fig = draw_diversity_map(use_df)
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
                    export_plotly(fig, "geo_diversity", 620)
                else:
                    st.error("Country and MLST columns with recognized countries required.")

        elif "Dominance Map" in geo_mode:
            st.markdown("##### Dominance Map — clonal dominance per country")
            st.caption(
                "Grey halo = total isolates | "
                "Colored inner disk = dominant ST strength"
            )
            dom_top = st.slider("Top N STs", 5, 25, 10, 1, key="dom_top")
            if btn("geo_dominance", "Generate Dominance Map"):
                fig = draw_dominance_map(use_df, top_n_st=dom_top)
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
                    export_plotly(fig, "geo_dominance", 620)
                else:
                    st.error("Country and MLST columns with recognized countries required.")

        elif "Sankey" in geo_mode:
            st.markdown("##### Sankey — flow from Country to MLST")
            if btn("sankey_fig", "Generate Sankey"):
                fig = draw_sankey(use_df)
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
                    export_plotly(fig, "sankey", 500)
                else:
                    st.error("Country and MLST columns with valid data required.")

# ────────────────────────────────────────────────────────────
# TAB 7 — Diagnostic
# ────────────────────────────────────────────────────────────
with tabs[7]:
    st.subheader("Diagnostic")
    if btn("diag_fig", "Run diagnostic"):
        if bio_tree:
            at9, no, nf9 = prepare_tree(bio_tree, filtered_loci, f_nmax)
            ln9 = [str(l.name) for l in at9.get_terminals()]
            s9  = match_stats(ln9, gene_df, meta_df)
            c1, c2, c3 = st.columns(3)
            with c1: st.metric("Original leaves", no)
            with c2: st.metric("Displayed leaves", nf9)
            with c3: st.metric("Gene matches",
                                f"{s9[\'g_ok\']} / {nf9}")
        else:
            st.warning("No tree loaded.")
    if is_valid_df(meta_df):
        with st.expander("Metadata preview"):
            st.dataframe(meta_df.head(20), use_container_width=True)

# ────────────────────────────────────────────────────────────
# TAB 8 — Export
# ────────────────────────────────────────────────────────────
with tabs[8]:
    st.subheader("Export Data")
    if is_valid_df(gdf_c):
        st.download_button(
            "Download Genes — Chr",
            gdf_c.to_csv(index=False),
            "genes_chr.csv", "text/csv",
        )
    if is_valid_df(gdf_p):
        st.download_button(
            "Download Genes — Pla",
            gdf_p.to_csv(index=False),
            "genes_pla.csv", "text/csv",
        )
    if is_valid_df(meta_df):
        st.download_button(
            "Download Metadata",
            meta_df.to_csv(index=False),
            "metadata.csv", "text/csv",
        )

# ────────────────────────────────────────────────────────────
# TAB 9 — Guide
# ────────────────────────────────────────────────────────────
with tabs[9]:
    st.subheader("User Guide — VREfm v3.3")
    st.markdown("""
### New in v3.3

#### Color Picker
- **Circular Tree**: after generation, color pickers appear for each ring category
- **Sunburst**: individual color picker for every category value
- **Apply** button redraws the figure with updated colors
- **Reset** button restores the default palette

#### Geographic Maps (9 types)

| Map | Description |
|-----|-------------|
| Choropleth | Classic country coloring by isolate count |
| Bubble Map | Size = N isolates, Color = dominant ST |
| Connection Map | Lines between countries sharing MLST types |
| MLST Distribution | One dot per isolate, Top 12 STs colored |
| Pie Map 2D | MLST pie charts per country (flat map) |
| Pie Map 3D | MLST pie charts per country (interactive globe) |
| Diversity Map | Size = N isolates, Color = Shannon H index |
| Dominance Map | Grey halo = total, colored disk = dominant ST |
| Sankey | Flow diagram: Country → MLST |

#### Sunburst
- Up to 200 colors via Auto palettes
- Text options: label, percentage, value, or none
- Per-category color picker after generation

#### Export formats
PNG (300 / 600 DPI), SVG, HTML, JSON, PDF

#### Supported input files
| File | Format |
|------|--------|
| Phylogenetic tree | Newick (.nwk, .tree, .txt, .fa…) |
| Gene presence/absence | CSV, TSV, XLSX |
| Metadata | CSV, TSV, XLSX |
    """)

st.markdown(
    "<div style=\'text-align:center;color:#999;font-size:.7rem;"
    "margin-top:2rem\'>VREfm v3.3 — Modular Edition</div>",
    unsafe_allow_html=True,
)
'''

with open("/content/modules/app.py", "w") as fh:
    fh.write(src)

print("modules/app.py written")
