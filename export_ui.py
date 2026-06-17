# ============================================================
# Cell 9 — modules/export_ui.py
# ============================================================

src = '''\
import io
import re
import streamlit as st


def safe_key(s):
    return re.sub(r"[^a-zA-Z0-9_]", "_", str(s))[:50]


def show_palette_preview(palette, max_show=16):
    html = "".join(
        f"<span style=\'display:inline-block;width:14px;height:14px;"
        f"background:{c};border-radius:2px;margin:1px;"
        f"border:1px solid #ddd\'></span>"
        for c in palette[:max_show]
    )
    n = len(palette)
    if n > max_show:
        html += f" <b>+{n - max_show}</b>"
    html += f" <span style=\\"color:#888\\">({n})</span>"
    st.markdown(html, unsafe_allow_html=True)


def btn(key, label="Generate"):
    if key not in st.session_state:
        st.session_state[key] = False
    c1, c2 = st.columns([1, 5])
    with c1:
        st.markdown(\'<div class="gbtn">\', unsafe_allow_html=True)
        if st.button(label, key=f"_b_{key}"):
            st.session_state[key] = not st.session_state[key]
        st.markdown("</div>", unsafe_allow_html=True)
    with c2:
        if st.session_state[key]:
            st.success("Active")
        else:
            st.info("Click to generate")
    return st.session_state[key]


def export_plotly(fig, prefix="fig", height=800):
    if fig is None:
        return
    st.markdown(\'<div class="ebox">\', unsafe_allow_html=True)
    st.markdown("#### Export")
    dpi = st.radio(
        "Resolution", ["300 DPI", "600 DPI"],
        index=0, key=f"dpi_{prefix}", horizontal=True,
    )
    cfg = {
        "300 DPI": {"scale": 4, "w": 1400},
        "600 DPI": {"scale": 8, "w": 1400},
    }[dpi]
    d1, d2, d3, d4 = st.columns(4)
    with d1:
        st.download_button(
            "HTML", fig.to_html(include_plotlyjs="cdn"),
            f"{prefix}.html", "text/html",
            use_container_width=True,
        )
    with d2:
        try:
            buf = io.BytesIO()
            fig.write_image(
                buf, format="png",
                scale=cfg["scale"], width=cfg["w"], height=height,
            )
            st.download_button(
                f"PNG {dpi}", buf.getvalue(),
                f"{prefix}.png", "image/png",
                use_container_width=True,
            )
        except Exception as ex:
            st.warning(f"PNG: {ex}")
    with d3:
        try:
            buf2 = io.BytesIO()
            fig.write_image(buf2, format="svg", width=cfg["w"], height=height)
            st.download_button(
                "SVG", buf2.getvalue(),
                f"{prefix}.svg", "image/svg+xml",
                use_container_width=True,
            )
        except Exception:
            pass
    with d4:
        st.download_button(
            "JSON", fig.to_json(),
            f"{prefix}.json", "application/json",
            use_container_width=True,
        )
    st.markdown("</div>", unsafe_allow_html=True)


def export_mpl(fig_mpl, prefix="fig"):
    if fig_mpl is None:
        return
    st.markdown(\'<div class="ebox">\', unsafe_allow_html=True)
    st.markdown("#### Export")
    dpi = st.radio(
        "Resolution", ["300 DPI", "600 DPI"],
        index=0, key=f"dpi_{prefix}", horizontal=True,
    )
    dv = 300 if "300" in dpi else 600
    d1, d2, d3 = st.columns(3)
    with d1:
        buf = io.BytesIO()
        fig_mpl.savefig(
            buf, format="png", dpi=dv,
            bbox_inches="tight", facecolor="white",
        )
        st.download_button(
            f"PNG {dpi}", buf.getvalue(),
            f"{prefix}.png", "image/png",
            use_container_width=True,
        )
    with d2:
        buf2 = io.BytesIO()
        fig_mpl.savefig(
            buf2, format="svg", bbox_inches="tight", facecolor="white"
        )
        st.download_button(
            "SVG", buf2.getvalue(),
            f"{prefix}.svg", "image/svg+xml",
            use_container_width=True,
        )
    with d3:
        buf3 = io.BytesIO()
        fig_mpl.savefig(
            buf3, format="pdf", bbox_inches="tight", facecolor="white"
        )
        st.download_button(
            "PDF", buf3.getvalue(),
            f"{prefix}.pdf", "application/pdf",
            use_container_width=True,
        )
    st.markdown("</div>", unsafe_allow_html=True)


def apply_color_overrides(rings, prefix="circ"):
    for ring in rings:
        if ring is None:
            continue
        sk_label = safe_key(ring["label"])
        for val in list(ring["palette"].keys()):
            k = f"cco_{prefix}_{sk_label}_{safe_key(val)}"
            if k in st.session_state:
                ring["palette"][val] = st.session_state[k]


def show_color_editors(rings, prefix="circ", max_default=24):
    if not rings:
        return
    st.markdown("### Edit colors")
    if st.button("Reset colors", key=f"reset_{prefix}_colors"):
        keys_del = [k for k in st.session_state
                    if k.startswith(f"cco_{prefix}_")]
        for k in keys_del:
            del st.session_state[k]
        st.rerun()
    for ring in rings:
        if ring is None:
            continue
        sk_label = safe_key(ring["label"])
        sorted_vals = sorted(
            [v for v in ring["palette"].keys() if v != "Absent"],
            key=lambda v: ring["counts"].get(v, 0),
            reverse=True,
        )
        n_vals = len(sorted_vals)
        with st.expander(f"{ring[\'label\']} — {n_vals} categories",
                         expanded=False):
            show_all = True
            if n_vals > max_default:
                st.caption(f"Top {max_default} shown")
                show_all = st.checkbox(
                    f"Show all {n_vals}",
                    key=f"showall_{prefix}_{sk_label}",
                )
            display_vals = sorted_vals if show_all else sorted_vals[:max_default]
            for row_start in range(0, len(display_vals), 6):
                cols = st.columns(6)
                for j, val in enumerate(display_vals[row_start: row_start + 6]):
                    with cols[j]:
                        cnt     = ring["counts"].get(val, 0)
                        k       = f"cco_{prefix}_{sk_label}_{safe_key(val)}"
                        current = ring["palette"].get(val, "#999999")
                        st.color_picker(f"{val} ({cnt})", value=current, key=k)


def apply_sunburst_overrides(alc, prefix="sb"):
    for lvl in alc:
        sk_lvl = safe_key(lvl)
        for val in list(alc[lvl].keys()):
            k = f"cco_{prefix}_{sk_lvl}_{safe_key(val)}"
            if k in st.session_state:
                alc[lvl][val] = st.session_state[k]


def show_sunburst_color_editors(alc, level_counts, prefix="sb", max_default=24):
    if not alc:
        return
    st.markdown("### Edit Sunburst colors")
    if st.button("Reset", key=f"reset_{prefix}_colors"):
        keys_del = [k for k in st.session_state
                    if k.startswith(f"cco_{prefix}_")]
        for k in keys_del:
            del st.session_state[k]
        st.rerun()
    for lvl, cm in alc.items():
        sk_lvl = safe_key(lvl)
        cc2 = level_counts.get(lvl, {})
        sorted_vals = sorted(
            cm.keys(), key=lambda v: cc2.get(v, 0), reverse=True
        )
        n_vals = len(sorted_vals)
        pfx = (
            "ST-"
            if lvl.lower().strip() in ["mlst", "st", "sequence_type"]
            else ""
        )
        with st.expander(f"{lvl} — {n_vals} values", expanded=False):
            show_all = True
            if n_vals > max_default:
                st.caption(f"Top {max_default} shown")
                show_all = st.checkbox(
                    f"Show all {n_vals}",
                    key=f"showall_{prefix}_{sk_lvl}",
                )
            display_vals = sorted_vals if show_all else sorted_vals[:max_default]
            for row_start in range(0, len(display_vals), 6):
                cols = st.columns(6)
                for j, val in enumerate(display_vals[row_start: row_start + 6]):
                    with cols[j]:
                        cnt     = cc2.get(val, 0)
                        k       = f"cco_{prefix}_{sk_lvl}_{safe_key(val)}"
                        current = cm.get(val, "#999999")
                        st.color_picker(
                            f"{pfx}{val} ({cnt})", value=current, key=k
                        )
'''

with open("/content/modules/export_ui.py", "w") as fh:
    fh.write(src)

print("modules/export_ui.py written")
