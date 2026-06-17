# VREfm v3.3 — Vancomycin-Resistant Enterococcus faecium Visualization

Interactive genomic epidemiology dashboard built with Streamlit.  
Runs entirely in **Google Colab** via a Cloudflare tunnel — no local install needed.
https://colab.research.google.com/drive/1SOpNu0UopZmwaPcbysN1SQIOUIPGBYzS?usp=sharing

## Features

| Tab | Description |
|-----|-------------|
| Circular | Phylogenetic circular tree with gene/MLST/country rings |
| Phylo | Phylogram, Cladogram, Circular, Radial layouts |
| Network | Spring, Kamada-Kawai, Circular, Spectral layouts |
| Heatmap | Gene presence/absence heatmap |
| Stats | Prevalence bar chart, MLST pie chart |
| Sunburst | Hierarchical sunburst (Country > MLST > …) |
| Geo | 9 geographic map types |
| Diagnostic | Match statistics between tree, genes and metadata |
| Export | Download figures (PNG 300/600 DPI, SVG, HTML, JSON, PDF) |

## Geographic Maps

- Choropleth
- Bubble Map (size = N isolates, color = dominant ST)
- Connection Map (shared MLST links between countries)
- MLST Distribution (one dot per isolate)
- Pie Map 2D / 3D Globe
- **Diversity Map** (Shannon diversity index)
- **Dominance Map** (clonal dominance visualization)
- Sankey (Country → MLST flow)

## Input Files

| File | Format |
|------|--------|
| Phylogenetic tree | Newick |
| Gene presence/absence | CSV / TSV / XLSX |
| Metadata | CSV / TSV / XLSX |

Metadata must contain columns auto-detected or manually assigned for:
- **Country** (`country`, `geo_loc_name`, `geographic_location`, …)
- **MLST** (`mlst`, `st`, `sequence_type`, …)
- **Locus/Accession** (`locus`, `accession`, …)

## Quick Start (Google Colab)

1. Open `launch_colab.ipynb` in Google Colab
2. Run **Cell 1** (install) then all subsequent cells in order
3. Copy the `trycloudflare.com` URL from **Cell 14**
4. Open the URL in your browser

## Repository Structure

```
VREfm/
├── README.md
├── requirements.txt
├── .gitignore
├── launch_colab.ipynb
└── modules/
    ├── __init__.py
    ├── app.py               ← Streamlit main script
    ├── colors.py            ← Palettes and color utilities
    ├── io_utils.py          ← File readers and caching
    ├── detect.py            ← Auto-detection of metadata columns
    ├── tree_utils.py        ← Tree manipulation
    ├── rings.py             ← Circular ring construction
    ├── geo_data.py          ← Country coordinates
    ├── figures_tree.py      ← Phylogenetic figures
    ├── figures_misc.py      ← Heatmap, stats, sunburst
    ├── figures_geo.py       ← All geographic maps
    └── export_ui.py         ← Export buttons and UI helpers
```

## License

MIT
