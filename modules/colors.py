# ============================================================
# Cell 3 — modules/colors.py
# ============================================================

src = '''\
import colorsys


def generate_unique_colors(n):
    if n <= 0:
        return []
    if n == 1:
        return ["#e74c3c"]
    base30 = [
        "#e6194b", "#3cb44b", "#ffe119", "#4363d8", "#f58231",
        "#911eb4", "#42d4f4", "#f032e6", "#bfef45", "#fabed4",
        "#469990", "#dcbeff", "#9a6324", "#fffac8", "#800000",
        "#aaffc3", "#808000", "#ffd8b1", "#000075", "#a9a9a9",
        "#e6beff", "#1abc9c", "#e74c3c", "#8e44ad", "#2ecc71",
        "#3498db", "#e67e22", "#1a5276", "#d35400", "#c0392b",
    ]
    if n <= 30:
        return base30[:n]
    colors = list(base30)
    golden = 0.618033988749895
    for i in range(30, n):
        h = (i * golden) % 1.0
        phase = i % 5
        if phase == 0:
            s, l = 0.85, 0.45
        elif phase == 1:
            s, l = 0.70, 0.58
        elif phase == 2:
            s, l = 0.95, 0.35
        elif phase == 3:
            s, l = 0.60, 0.65
        else:
            s, l = 0.80, 0.42
        r, g, b = colorsys.hls_to_rgb(h, l, s)
        colors.append(f"#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}")
    return colors[:n]


def ensure_enough_colors(palette, n):
    if n <= len(palette):
        return palette[:n]
    return generate_unique_colors(n)


VANA_PALETTES = {
    "Red": [
        "#e74c3c", "#c0392b", "#a93226", "#922b21", "#7b241c",
        "#641e16", "#f1948a", "#ec7063", "#cb4335", "#b03a2e",
    ],
    "Orange": [
        "#e67e22", "#d35400", "#f39c12", "#dc7633", "#ca6f1e",
        "#b9770e", "#f0b27a", "#eb984e", "#e59866", "#d68910",
    ],
    "Purple": [
        "#8e44ad", "#7d3c98", "#6c3483", "#5b2c6f", "#4a235a",
        "#a569bd", "#bb8fce", "#d2b4de", "#9b59b6", "#884ea0",
    ],
}

VANB_PALETTES = {
    "Blue": [
        "#3498db", "#2980b9", "#2471a3", "#1f618d", "#1a5276",
        "#154360", "#85c1e9", "#5dade2", "#2e86c1", "#2874a6",
    ],
    "Cyan": [
        "#1abc9c", "#16a085", "#148f77", "#117a65", "#0e6655",
        "#0b5345", "#76d7c4", "#48c9b0", "#17a589", "#138d75",
    ],
    "Green": [
        "#27ae60", "#229954", "#1e8449", "#196f3d", "#145a32",
        "#0e6251", "#82e0aa", "#58d68d", "#28b463", "#239b56",
    ],
}

RING_PALETTES = {
    "Tab20 (20)": [
        "#1f77b4", "#aec7e8", "#ff7f0e", "#ffbb78", "#2ca02c",
        "#98df8a", "#d62728", "#ff9896", "#9467bd", "#c5b0d5",
        "#8c564b", "#c49c94", "#e377c2", "#f7b6d2", "#7f7f7f",
        "#c7c7c7", "#bcbd22", "#dbdb8d", "#17becf", "#9edae5",
    ],
    "Alphabet (26)": [
        "#AA0DFE", "#3283FE", "#85660D", "#782AB6", "#565656",
        "#1C8356", "#16FF32", "#F7E1A0", "#E2E2E2", "#1CBE4F",
        "#C4451C", "#DEA0FD", "#FE00FA", "#325A9B", "#FEAF16",
        "#F8A19F", "#90AD1C", "#F6222E", "#1CFFCE", "#2ED9FF",
        "#B10DA1", "#C075A6", "#FC1CBF", "#B00068", "#FBE426",
        "#FA0087",
    ],
    "Dark24 (24)": [
        "#2E91E5", "#E15F99", "#1CA71C", "#FB0D0D", "#DA16FF",
        "#222A2A", "#B68100", "#750D86", "#EB663B", "#511CFB",
        "#00A08B", "#FB00D1", "#FC0080", "#B2828D", "#6C7C32",
        "#778AAE", "#862A16", "#A777F1", "#620042", "#1616A7",
        "#DA60CA", "#6C4516", "#0D2A63", "#AF0038",
    ],
    "Mega30 (30)": [
        "#e6194b", "#3cb44b", "#ffe119", "#4363d8", "#f58231",
        "#911eb4", "#42d4f4", "#f032e6", "#bfef45", "#fabed4",
        "#469990", "#dcbeff", "#9a6324", "#fffac8", "#800000",
        "#aaffc3", "#808000", "#ffd8b1", "#000075", "#a9a9a9",
        "#e6beff", "#1abc9c", "#e74c3c", "#8e44ad", "#2ecc71",
        "#3498db", "#e67e22", "#1a5276", "#d35400", "#c0392b",
    ],
    "Set2 (8)": [
        "#66c2a5", "#fc8d62", "#8da0cb", "#e78ac3",
        "#a6d854", "#ffd92f", "#e5c494", "#b3b3b3",
    ],
    "Bold (12)": [
        "#7f3c8d", "#11a579", "#3969ac", "#f2b701", "#e73f74",
        "#80ba5a", "#e68310", "#008695", "#cf1c90", "#f97b72",
        "#4b4b8f", "#a5aa99",
    ],
    "Vivid (12)": [
        "#e58606", "#5d69b1", "#52bca3", "#99c945", "#cc61b0",
        "#24796c", "#daa51b", "#2f8ac4", "#764e9f", "#ed645a",
        "#a5aa99", "#2b8cbe",
    ],
    "D3 (10)": [
        "#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd",
        "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf",
    ],
    "Rainbow (20)": [
        "#FF0000", "#FF4500", "#FF7F00", "#FFB300", "#FFFF00",
        "#7FFF00", "#00FF00", "#00FF7F", "#00FFFF", "#007FFF",
        "#0000FF", "#4B0082", "#8B00FF", "#9400D3", "#FF1493",
        "#FF69B4", "#00CED1", "#FFD700", "#32CD32", "#DC143C",
    ],
    "Spectral (8)": [
        "#d53e4f", "#f46d43", "#fdae61", "#fee08b",
        "#e6f598", "#abdda4", "#66c2a5", "#3288bd",
    ],
    "Auto50 (50)":   [],
    "Auto100 (100)": [],
    "Auto150 (150)": [],
    "Auto200 (200)": [],
}


def _init_auto_palettes():
    RING_PALETTES["Auto50 (50)"]   = generate_unique_colors(50)
    RING_PALETTES["Auto100 (100)"] = generate_unique_colors(100)
    RING_PALETTES["Auto150 (150)"] = generate_unique_colors(150)
    RING_PALETTES["Auto200 (200)"] = generate_unique_colors(200)


_init_auto_palettes()

ABSENT_COL = "#f0f0f0"

SUNBURST_TEXT_OPTIONS = {
    "Label + Percentage":  "label+percent entry",
    "Label only":          "label",
    "Percentage only":     "percent entry",
    "Label + Value":       "label+value",
    "Value only":          "value",
    "Label + pct parent":  "label+percent parent",
    "None":                "none",
}
'''

with open("/content/modules/colors.py", "w") as fh:
    fh.write(src)

print("modules/colors.py written")
