# ============================================================
# Cell 12 — modules/figures_geo.py
# ============================================================

src = '''\
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from collections import defaultdict

from modules.detect import detect_country, detect_mlst
from modules.colors import generate_unique_colors, ensure_enough_colors
from modules.geo_data import COUNTRY_COORDS


def _clean_geo_mlst_df(mdf):
    if mdf is None:
        return None, None, None
    cc = detect_country(mdf)
    mc = detect_mlst(mdf)
    if cc is None or mc is None:
        return None, cc, mc
    df = mdf[[cc, mc]].dropna().copy()
    df[cc] = df[cc].astype(str).apply(lambda x: x.split(":")[0].strip())
    df[mc] = df[mc].astype(str).str.strip()
    bad    = {"-", "nan", "", "Unknown", "None", "ST-", "ST-nan", "ST--"}
    df     = df[~df[mc].isin(bad)]
    return (df, cc, mc) if len(df) >= 2 else (None, cc, mc)


# ── ISO lookup ───────────────────────────────────────────────
_ISO = {
    "France": "FRA", "Germany": "DEU", "China": "CHN",
    "Australia": "AUS", "Brazil": "BRA", "Canada": "CAN",
    "USA": "USA", "United States": "USA",
    "United States of America": "USA",
    "Japan": "JPN", "India": "IND",
    "UK": "GBR", "United Kingdom": "GBR",
    "Belgium": "BEL", "Spain": "ESP", "Italy": "ITA",
    "Netherlands": "NLD", "Sweden": "SWE", "Denmark": "DNK",
    "Norway": "NOR", "Finland": "FIN", "Switzerland": "CHE",
    "Austria": "AUT", "Poland": "POL", "Portugal": "PRT",
    "Ireland": "IRL", "Greece": "GRC", "Turkey": "TUR",
    "Russia": "RUS", "South Korea": "KOR", "Korea": "KOR",
    "Republic of Korea": "KOR",
    "Taiwan": "TWN", "Thailand": "THA", "Vietnam": "VNM",
    "Viet Nam": "VNM", "Malaysia": "MYS", "Singapore": "SGP",
    "Indonesia": "IDN", "Mexico": "MEX", "Argentina": "ARG",
    "Chile": "CHL", "Colombia": "COL", "Peru": "PER",
    "Egypt": "EGY", "South Africa": "ZAF", "Nigeria": "NGA",
    "Kenya": "KEN", "Morocco": "MAR", "Tunisia": "TUN",
    "Israel": "ISR", "Saudi Arabia": "SAU", "UAE": "ARE",
    "Iran": "IRN", "Pakistan": "PAK", "Bangladesh": "BGD",
    "Czech Republic": "CZE", "Czechia": "CZE",
    "Hungary": "HUN", "Romania": "ROU", "Bulgaria": "BGR",
    "Croatia": "HRV", "Serbia": "SRB", "Slovakia": "SVK",
    "Slovenia": "SVN", "Estonia": "EST", "Latvia": "LVA",
    "Lithuania": "LTU", "Luxembourg": "LUX", "Iceland": "ISL",
    "New Zealand": "NZL", "Cuba": "CUB", "Ecuador": "ECU",
    "Venezuela": "VEN", "Uruguay": "URY", "Paraguay": "PRY",
    "Bolivia": "BOL", "Panama": "PAN", "Costa Rica": "CRI",
}


def draw_geo(mdf):
    if mdf is None:
        return None
    cc = detect_country(mdf)
    if cc is None:
        return None
    df     = mdf.copy()
    df[cc] = df[cc].astype(str).apply(lambda x: x.split(":")[0].strip())
    counts = df[cc].value_counts().reset_index()
    counts.columns = ["Country", "Count"]
    counts["ISO"]  = counts["Country"].map(_ISO)
    counts         = counts.dropna(subset=["ISO"])
    if counts.empty:
        return None
    fig = px.choropleth(
        counts, locations="ISO", color="Count",
        hover_name="Country",
        color_continuous_scale="YlOrRd",
        title="Choropleth — Isolates per Country",
    )
    fig.update_layout(
        paper_bgcolor="white", height=450,
        geo=dict(showframe=False, showcoastlines=True),
    )
    return fig


def draw_bubble_map(mdf):
    if mdf is None:
        return None
    cc = detect_country(mdf)
    mc = detect_mlst(mdf)
    if cc is None:
        return None
    df = mdf.copy()
    df["_country"] = df[cc].astype(str).apply(lambda x: x.split(":")[0].strip())
    agg = []
    for country, grp in df.groupby("_country"):
        coord = COUNTRY_COORDS.get(country)
        if coord is None:
            continue
        n = len(grp); dom_st = "Unknown"; st_dist = ""
        if mc and mc in grp.columns:
            sts = grp[mc].astype(str).replace(
                {"-": "Unknown", "nan": "Unknown", "": "Unknown"}
            )
            sts = sts[sts != "Unknown"]
            if len(sts) > 0:
                vc     = sts.value_counts()
                dom_st = str(vc.index[0])
                st_dist = "<br>".join(
                    [f"  ST-{s}: {c}" for s, c in vc.head(5).items()]
                )
        agg.append({
            "Country": country, "lat": coord[0], "lon": coord[1],
            "Count": n, "Dominant_ST": f"ST-{dom_st}",
            "hover": (
                f"<b>{country}</b><br>N = {n}<br>"
                f"Dominant: ST-{dom_st}<br>{st_dist}"
            ),
        })
    if not agg:
        return None
    adf  = pd.DataFrame(agg)
    dst  = sorted(adf["Dominant_ST"].unique())
    uc   = generate_unique_colors(len(dst))
    cmap = {s: uc[i] for i, s in enumerate(dst)}
    fig  = go.Figure()
    for st_val in dst:
        sub = adf[adf["Dominant_ST"] == st_val]
        fig.add_trace(go.Scattergeo(
            lat=sub["lat"], lon=sub["lon"],
            marker=dict(
                size=np.clip(sub["Count"].values ** 0.5 * 8, 8, 80),
                color=cmap[st_val],
                line=dict(width=1, color="#333"),
                opacity=0.8, sizemode="diameter",
            ),
            text=sub["hover"], hoverinfo="text",
            name=st_val, legendgroup=st_val,
        ))
    fig.update_layout(
        title=dict(text="Bubble Map — Size=N, Color=Dominant ST",
                   font=dict(size=14, color="#1a5276")),
        geo=dict(projection_type="natural earth",
                 showland=True, landcolor="#f0f0f0",
                 showocean=True, oceancolor="#e8f4f8",
                 showcoastlines=True, coastlinecolor="#999",
                 showcountries=True, countrycolor="#ccc",
                 showframe=False),
        paper_bgcolor="white", height=550,
        legend=dict(title="Dominant ST", font=dict(size=9)),
    )
    return fig


def draw_connection_map(mdf):
    if mdf is None:
        return None
    cc = detect_country(mdf)
    mc = detect_mlst(mdf)
    if cc is None or mc is None:
        return None
    df     = mdf[[cc, mc]].dropna().copy()
    df[cc] = df[cc].astype(str).apply(lambda x: x.split(":")[0].strip())
    df[mc] = df[mc].astype(str)
    df     = df[~df[mc].isin(["-", "nan", "", "Unknown", "None"])]
    if len(df) < 2:
        return None
    c_sts, c_cnt = {}, {}
    for country, grp in df.groupby(cc):
        if country not in COUNTRY_COORDS:
            continue
        sts = set(grp[mc].unique())
        if sts:
            c_sts[country] = sts
            c_cnt[country] = len(grp)
    if len(c_sts) < 2:
        return None
    countries   = list(c_sts.keys())
    connections = []
    for i in range(len(countries)):
        for j in range(i + 1, len(countries)):
            c1, c2  = countries[i], countries[j]
            shared  = c_sts[c1] & c_sts[c2]
            if shared:
                connections.append({
                    "from": c1, "to": c2,
                    "n_shared": len(shared),
                    "shared_sts": sorted(shared),
                })
    if not connections:
        return None
    connections.sort(key=lambda x: x["n_shared"])
    max_shared = max(c["n_shared"] for c in connections)
    fig = go.Figure()
    for conn in connections:
        p1    = COUNTRY_COORDS[conn["from"]]
        p2    = COUNTRY_COORDS[conn["to"]]
        inten = conn["n_shared"] / max(max_shared, 1)
        width = 1 + inten * 5
        alpha = 0.3 + inten * 0.5
        top   = ", ".join([f"ST-{s}" for s in conn["shared_sts"][:5]])
        extra = (
            f"  +{len(conn['shared_sts'])-5} more"
            if len(conn["shared_sts"]) > 5 else ""
        )
        n_pts = 20
        lats  = np.linspace(p1[0], p2[0], n_pts)
        lons  = np.linspace(p1[1], p2[1], n_pts)
        curve = min(abs(p1[0] - p2[0]) + abs(p1[1] - p2[1]), 30) * 0.15
        for k in range(n_pts):
            lats[k] += np.sin(np.pi * k / (n_pts - 1)) * curve
        fig.add_trace(go.Scattergeo(
            lat=lats, lon=lons, mode="lines",
            line=dict(width=width, color=f"rgba(231,76,60,{alpha})"),
            hoverinfo="text",
            hovertext=(
                f"<b>{conn['from']} — {conn['to']}</b><br>"
                f"Shared STs: {conn['n_shared']}<br>{top}{extra}"
            ),
            showlegend=False,
        ))
    for country in c_sts:
        coord = COUNTRY_COORDS[country]
        n     = c_cnt.get(country, 0)
        n_sts = len(c_sts[country])
        top3  = sorted(c_sts[country])[:3]
        fig.add_trace(go.Scattergeo(
            lat=[coord[0]], lon=[coord[1]],
            mode="markers+text",
            marker=dict(
                size=np.clip(n ** 0.4 * 6, 8, 40),
                color="#2980b9",
                line=dict(width=2, color="white"),
                opacity=0.9,
            ),
            text=[country], textposition="top center",
            textfont=dict(size=8, color="#1a5276"),
            hoverinfo="text",
            hovertext=(
                f"<b>{country}</b><br>N isolates: {n}<br>"
                f"N STs: {n_sts}<br>"
                f"Top: {', '.join(f'ST-{s}' for s in top3)}"
            ),
            showlegend=False,
        ))
    n_conn      = len(connections)
    total_shared = sum(c["n_shared"] for c in connections)
    fig.update_layout(
        title=dict(
            text=f"Connection Map — {n_conn} links, {total_shared} shared STs",
            font=dict(size=14, color="#1a5276"),
        ),
        geo=dict(
            projection_type="natural earth",
            showland=True, landcolor="#fafafa",
            showocean=True, oceancolor="#e8f4f8",
            showcoastlines=True, coastlinecolor="#bbb",
            showcountries=True, countrycolor="#ddd",
            showframe=False,
        ),
        paper_bgcolor="white", height=600,
        annotations=[dict(
            text="Line width = N shared STs | Node size = N isolates",
            xref="paper", yref="paper", x=0.5, y=-0.05,
            showarrow=False, font=dict(size=10, color="#888"),
        )],
    )
    return fig


def draw_mlst_flow_map(mdf):
    if mdf is None:
        return None
    cc = detect_country(mdf)
    mc = detect_mlst(mdf)
    if cc is None or mc is None:
        return None
    df     = mdf[[cc, mc]].dropna().copy()
    df[cc] = df[cc].astype(str).apply(lambda x: x.split(":")[0].strip())
    df[mc] = "ST-" + df[mc].astype(str)
    df     = df[~df[mc].isin(["ST-", "ST-nan", "ST--", "ST-Unknown", "ST-None"])]
    if len(df) < 2:
        return None
    top_sts   = df[mc].value_counts().head(12).index.tolist()
    df["_grp"] = df[mc].apply(lambda x: x if x in top_sts else "Other")
    valid     = df[df[cc].isin(COUNTRY_COORDS.keys())]
    if valid.empty:
        return None
    all_sts  = sorted(df["_grp"].unique(), key=lambda x: (x == "Other", x))
    uc       = generate_unique_colors(len(all_sts))
    st_colors = {s: uc[i] for i, s in enumerate(all_sts)}
    if "Other" in st_colors:
        st_colors["Other"] = "#cccccc"
    np.random.seed(42)
    fig = go.Figure()
    for st_val in all_sts:
        sub = valid[valid["_grp"] == st_val]
        lats, lons, hovers = [], [], []
        for _, row in sub.iterrows():
            coord = COUNTRY_COORDS.get(row[cc])
            if coord:
                lats.append(coord[0] + np.random.uniform(-1.5, 1.5))
                lons.append(coord[1] + np.random.uniform(-1.5, 1.5))
                hovers.append(f"{row[cc]}: {row[mc]}")
        if lats:
            fig.add_trace(go.Scattergeo(
                lat=lats, lon=lons, mode="markers",
                marker=dict(size=6, color=st_colors[st_val],
                            opacity=0.7, line=dict(width=0.5, color="white")),
                name=f"{st_val} ({len(lats)})",
                hoverinfo="text", hovertext=hovers,
            ))
    fig.update_layout(
        title=dict(text="MLST Distribution Map — Each dot = 1 isolate",
                   font=dict(size=14, color="#1a5276")),
        geo=dict(projection_type="natural earth",
                 showland=True, landcolor="#f8f8f8",
                 showocean=True, oceancolor="#e8f4f8",
                 showcoastlines=True, coastlinecolor="#999",
                 showcountries=True, countrycolor="#ddd",
                 showframe=False),
        paper_bgcolor="white", height=600,
        legend=dict(title="MLST", font=dict(size=9), itemsizing="constant"),
    )
    return fig


def _pie_wedge_geo(lat0, lon0, radius, a_start, a_end, n_pts=20):
    cos_lat = max(abs(np.cos(np.radians(lat0))), 0.15)
    lats = [lat0]; lons = [lon0]
    for a in np.linspace(a_start, a_end, max(n_pts, 3)):
        lats.append(lat0 + radius * np.sin(a))
        lons.append(lon0 + radius * np.cos(a) / cos_lat)
    lats.append(lat0); lons.append(lon0)
    return lats, lons


def draw_pie_map(
    mdf, show_mode="pct+val", pie_radius=3.0, top_n_st=10,
    projection="natural earth", rot_lon=0, rot_lat=0,
    show_labels=True, min_pct_label=12,
):
    if mdf is None:
        return None
    cc = detect_country(mdf)
    mc = detect_mlst(mdf)
    if cc is None or mc is None:
        return None
    df     = mdf[[cc, mc]].dropna().copy()
    df[cc] = df[cc].astype(str).apply(lambda x: x.split(":")[0].strip())
    df[mc] = df[mc].astype(str)
    df     = df[~df[mc].isin(["-", "nan", "", "Unknown", "None"])]
    if len(df) < 2:
        return None
    gsc     = df[mc].value_counts()
    top_sts = gsc.head(top_n_st).index.tolist()
    uc      = generate_unique_colors(len(top_sts) + 1)
    st_col  = {s: uc[i] for i, s in enumerate(top_sts)}
    st_col["Other"] = "#cccccc"
    fig   = go.Figure()
    added = set()
    c_grp = df.groupby(cc)
    max_c = c_grp.size().max() if len(c_grp) > 0 else 1
    n_ctr = 0
    for country, grp in c_grp:
        coord = COUNTRY_COORDS.get(country)
        if coord is None:
            continue
        n_ctr += 1
        lat0, lon0 = coord
        n_tot  = len(grp)
        scale  = (n_tot / max(max_c, 1)) ** 0.25
        r      = max(1.0, min(pie_radius * (0.5 + 0.5 * scale), pie_radius * 2.0))
        vc     = grp[mc].value_counts()
        st_data = []; other = 0
        for st_val, cnt in vc.items():
            if st_val in top_sts:
                st_data.append((st_val, cnt))
            else:
                other += cnt
        if other > 0:
            st_data.append(("Other", other))
        st_data.sort(key=lambda x: -x[1])
        ang = -np.pi / 2
        cos_lat = max(abs(np.cos(np.radians(lat0))), 0.15)
        for st_val, cnt in st_data:
            pct   = cnt / max(n_tot, 1)
            sweep = pct * 2 * np.pi
            if sweep < 0.02:
                ang += sweep; continue
            lats, lons = _pie_wedge_geo(lat0, lon0, r, ang, ang + sweep,
                                        max(4, int(sweep * 12)))
            col      = st_col.get(st_val, "#cccccc")
            st_label = f"ST-{st_val}" if st_val != "Other" else "Other"
            show_leg = st_label not in added
            if show_leg:
                added.add(st_label)
            if show_mode == "pct":
                info = f"{pct*100:.1f}%"
            elif show_mode == "val":
                info = f"n={cnt}"
            elif show_mode == "pct+val":
                info = f"n={cnt} ({pct*100:.1f}%)"
            else:
                info = ""
            fig.add_trace(go.Scattergeo(
                lat=lats, lon=lons, mode="lines",
                fill="toself", fillcolor=col,
                line=dict(width=0.8, color="white"),
                name=(
                    f"{st_label} (n={gsc.get(st_val, cnt)})"
                    if show_leg else ""
                ),
                legendgroup=st_label, showlegend=show_leg,
                hoverinfo="text",
                hovertext=(
                    f"<b>{country}</b><br>{st_label}: {info}"
                    f"<br>Total: {n_tot}"
                ),
            ))
            if show_labels and pct * 100 >= min_pct_label and show_mode != "none":
                mid_a   = ang + sweep / 2
                txt_r   = r * 0.5
                txt_lat = lat0 + txt_r * np.sin(mid_a)
                txt_lon = lon0 + txt_r * np.cos(mid_a) / cos_lat
                seg_txt = f"{pct*100:.0f}%" if show_mode == "pct" else str(cnt)
                fig.add_trace(go.Scattergeo(
                    lat=[txt_lat], lon=[txt_lon], mode="text",
                    text=[seg_txt],
                    textfont=dict(size=max(5, min(8, int(r))),
                                  color="white", family="Arial Black"),
                    showlegend=False, hoverinfo="none",
                ))
            ang += sweep
        fig.add_trace(go.Scattergeo(
            lat=[lat0 - r - 1.0], lon=[lon0], mode="text",
            text=[country], textfont=dict(size=7, color="#1a5276"),
            showlegend=False, hoverinfo="none",
        ))
    is_globe = projection == "orthographic"
    geo_cfg  = dict(
        projection_type=projection,
        showland=True, landcolor="#f5f5f0",
        showocean=True, oceancolor="#dceefb",
        showcoastlines=True, coastlinecolor="#aaa",
        showcountries=True, countrycolor="#ccc",
        showframe=False, resolution=50,
    )
    if is_globe:
        geo_cfg["projection_rotation"] = dict(lon=rot_lon, lat=rot_lat)
    fig.update_layout(
        title=dict(
            text=(
                f"Pie Map ({'3D Globe' if is_globe else '2D Map'}) — "
                f"{n_ctr} countries, Top {top_n_st} STs"
            ),
            font=dict(size=14, color="#1a5276"),
        ),
        geo=geo_cfg,
        paper_bgcolor="white",
        height=750 if is_globe else 600,
        legend=dict(title="MLST", font=dict(size=9), itemsizing="constant"),
        margin=dict(l=10, r=10, t=50, b=10),
    )
    return fig


def draw_sankey(mdf):
    if mdf is None:
        return None
    cc = detect_country(mdf)
    mc = detect_mlst(mdf)
    if cc is None or mc is None:
        return None
    df     = mdf[[cc, mc]].dropna().copy()
    df[cc] = df[cc].astype(str).apply(lambda x: x.split(":")[0].strip())
    df[mc] = df[mc].astype(str)
    df     = df[~df[mc].isin(["-", "nan", "", "Unknown"])]
    if len(df) < 2:
        return None
    cs     = sorted(df[cc].unique())
    ms     = sorted(df[mc].unique())
    labels = list(cs) + [f"ST-{m}" for m in ms]
    ci     = {c: i for i, c in enumerate(cs)}
    mi     = {m: i + len(cs) for i, m in enumerate(ms)}
    links  = defaultdict(int)
    for _, row in df.iterrows():
        links[(ci[row[cc]], mi[row[mc]])] += 1
    s, t, v = [], [], []
    for (a, b), val in links.items():
        s.append(a); t.append(b); v.append(val)
    import matplotlib.colors as _mc
    def _hex(c):
        try:
            c = c.strip()
            return c[:7] if c.startswith("#") else _mc.to_hex(c)
        except Exception:
            return "#999999"
    pal = px.colors.qualitative.Set2 + px.colors.qualitative.Bold
    uc  = ensure_enough_colors([_hex(c) for c in pal], len(labels))
    fig = go.Figure(go.Sankey(
        node=dict(pad=15, thickness=20, label=labels, color=uc),
        link=dict(source=s, target=t, value=v),
    ))
    fig.update_layout(
        title="Country to MLST",
        paper_bgcolor="white", height=500,
    )
    return fig


def draw_diversity_map(mdf):
    df, cc, mc = _clean_geo_mlst_df(mdf)
    if df is None:
        return None
    rows = []
    for country, grp in df.groupby(cc):
        coord = COUNTRY_COORDS.get(country)
        if coord is None:
            continue
        vc       = grp[mc].value_counts()
        n        = len(grp)
        richness = int(len(vc))
        p        = vc.values / max(n, 1)
        shannon  = float(-(p * np.log2(p)).sum()) if len(p) > 0 else 0.0
        evenness = float(shannon / np.log2(richness)) if richness > 1 else 0.0
        dominant = str(vc.index[0]) if len(vc) > 0 else "NA"
        dom_pct  = float(100 * vc.iloc[0] / max(n, 1)) if len(vc) > 0 else 0.0
        top_lines = "<br>".join(
            [f"ST-{st}: {cnt}" for st, cnt in vc.head(5).items()]
        )
        rows.append({
            "country": country,
            "lat": coord[0], "lon": coord[1],
            "count": n, "richness": richness,
            "shannon": shannon, "evenness": evenness,
            "dominant": dominant, "dom_pct": dom_pct,
            "hover": (
                f"<b>{country}</b><br>"
                f"Total isolates: {n}<br>"
                f"Distinct MLSTs: {richness}<br>"
                f"Shannon H: {shannon:.2f}<br>"
                f"Evenness: {evenness:.2f}<br>"
                f"Dominant ST: ST-{dominant} ({dom_pct:.1f}%)<br><br>"
                f"{top_lines}"
            ),
        })
    if not rows:
        return None
    adf     = pd.DataFrame(rows)
    max_cnt = max(adf["count"].max(), 1)
    sizes   = np.clip((adf["count"] / max_cnt) ** 0.5 * 38, 8, 42)
    cmax    = max(float(adf["shannon"].max()), 0.01)
    fig     = go.Figure()
    fig.add_trace(go.Scattergeo(
        lat=adf["lat"], lon=adf["lon"], mode="markers",
        marker=dict(
            size=sizes, color=adf["shannon"],
            colorscale="Viridis", cmin=0, cmax=cmax,
            colorbar=dict(title="Shannon H"),
            opacity=0.9, line=dict(width=1.1, color="white"),
        ),
        hoverinfo="text", hovertext=adf["hover"],
        name="Countries",
    ))
    fig.update_layout(
        title=dict(
            text="Diversity Map — Size = N isolates, Color = MLST diversity (Shannon H)",
            font=dict(size=14, color="#1a5276"),
        ),
        geo=dict(
            projection_type="natural earth",
            showland=True, landcolor="#f7f7f2",
            showocean=True, oceancolor="#dcecf8",
            showcoastlines=True, coastlinecolor="#9aa3aa",
            showcountries=True, countrycolor="#cfd8dc",
            showframe=False,
            lonaxis=dict(range=[-180, 180]),
            lataxis=dict(range=[-60, 85]),
        ),
        paper_bgcolor="white", height=620,
        margin=dict(l=10, r=10, t=55, b=10),
        annotations=[dict(
            text="Color = clonal diversity | Size = number of isolates",
            x=0.5, y=0.02, xref="paper", yref="paper",
            showarrow=False, font=dict(size=10, color="#666"),
        )],
    )
    return fig


def draw_dominance_map(mdf, top_n_st=10):
    df, cc, mc = _clean_geo_mlst_df(mdf)
    if df is None:
        return None
    gsc     = df[mc].value_counts()
    top_sts = gsc.head(top_n_st).index.tolist()
    colors  = generate_unique_colors(len(top_sts) + 1)
    st_col  = {st: colors[i] for i, st in enumerate(top_sts)}
    st_col["Other"] = "#bdbdbd"
    rows = []
    for country, grp in df.groupby(cc):
        coord = COUNTRY_COORDS.get(country)
        if coord is None:
            continue
        vc       = grp[mc].value_counts()
        n        = len(grp)
        if len(vc) == 0:
            continue
        dom_raw  = str(vc.index[0])
        dom_plot = dom_raw if dom_raw in top_sts else "Other"
        dom_frac = float(vc.iloc[0] / max(n, 1))
        richness = int(len(vc))
        top_lines = "<br>".join(
            [f"ST-{st}: {cnt}" for st, cnt in vc.head(5).items()]
        )
        rows.append({
            "country": country,
            "lat": coord[0], "lon": coord[1],
            "count": n, "richness": richness,
            "dom_raw": dom_raw, "dom_plot": dom_plot,
            "dom_frac": dom_frac, "dom_pct": 100 * dom_frac,
            "hover": (
                f"<b>{country}</b><br>"
                f"Total isolates: {n}<br>"
                f"Distinct MLSTs: {richness}<br>"
                f"Dominant ST: ST-{dom_raw}<br>"
                f"Dominance: {100*dom_frac:.1f}%<br><br>"
                f"{top_lines}"
            ),
        })
    if not rows:
        return None
    adf     = pd.DataFrame(rows)
    max_cnt = max(adf["count"].max(), 1)
    adf["outer"] = np.clip((adf["count"] / max_cnt) ** 0.5 * 44, 10, 46)
    adf["inner"] = np.clip(
        adf["outer"] * (0.22 + 0.78 * adf["dom_frac"]), 5, 44
    )
    fig = go.Figure()
    fig.add_trace(go.Scattergeo(
        lat=adf["lat"], lon=adf["lon"], mode="markers",
        marker=dict(
            size=adf["outer"],
            color="rgba(160,160,160,0.28)",
            line=dict(width=0.8, color="rgba(90,90,90,0.55)"),
        ),
        hoverinfo="skip", showlegend=True,
        name="Halo — total isolates",
    ))
    levels = [st for st in top_sts if st in adf["dom_plot"].unique()]
    if "Other" in adf["dom_plot"].unique():
        levels += ["Other"]
    for st in levels:
        sub = adf[adf["dom_plot"] == st]
        if sub.empty:
            continue
        fig.add_trace(go.Scattergeo(
            lat=sub["lat"], lon=sub["lon"], mode="markers",
            marker=dict(
                size=sub["inner"],
                color=st_col.get(st, "#bdbdbd"),
                opacity=0.9, line=dict(width=1.0, color="white"),
            ),
            hoverinfo="text", hovertext=sub["hover"],
            name=f"ST-{st}" if st != "Other" else "Other",
        ))
    fig.update_layout(
        title=dict(
            text=(
                f"Dominance Map — Grey halo = total isolates, "
                f"inner color = dominant ST (Top {top_n_st})"
            ),
            font=dict(size=14, color="#1a5276"),
        ),
        geo=dict(
            projection_type="natural earth",
            showland=True, landcolor="#f7f7f2",
            showocean=True, oceancolor="#dcecf8",
            showcoastlines=True, coastlinecolor="#9aa3aa",
            showcountries=True, countrycolor="#cfd8dc",
            showframe=False,
            lonaxis=dict(range=[-180, 180]),
            lataxis=dict(range=[-60, 85]),
        ),
        paper_bgcolor="white", height=620,
        margin=dict(l=10, r=10, t=55, b=10),
        legend=dict(title="Dominant MLST", font=dict(size=9),
                    itemsizing="constant"),
        annotations=[dict(
            text="Larger colored disk = stronger single-ST dominance",
            x=0.5, y=0.02, xref="paper", yref="paper",
            showarrow=False, font=dict(size=10, color="#666"),
        )],
    )
    return fig
'''

with open("/content/modules/figures_geo.py", "w") as fh:
    fh.write(src)

print("modules/figures_geo.py written")
