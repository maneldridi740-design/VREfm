# VREfm v3.3  
### Vancomycin-Resistant *Enterococcus faecium* Visualization Platform

Interactive genomic epidemiology dashboard built with **Streamlit**.  
Runs entirely in **Google Colab via a secure Cloudflare tunnel** — no local installation required.

---

## 🚀 Launch in Google Colab

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1SOpNu0UopZmwaPcbysN1SQIOUIPGBYzS?usp=sharing)

---

## ✨ Features

| Tab | Description |
|------|------------|
| **Circular** | Phylogenetic circular tree with gene / MLST / country rings |
| **Phylo** | Phylogram, Cladogram, Circular, Radial layouts |
| **Network** | Spring, Kamada-Kawai, Circular, Spectral layouts |
| **Heatmap** | Gene presence/absence heatmap |
| **Stats** | Prevalence bar chart, MLST pie chart |
| **Sunburst** | Hierarchical sunburst (Country > MLST > …) |
| **Geo** | 9 advanced geographic visualization maps |
| **Diagnostic** | Match statistics between tree, genes and metadata |
| **Export** | Download figures (PNG 300/600 DPI, SVG, HTML, JSON, PDF) |

---

## 🌍 Geographic Maps

- Choropleth
- Bubble Map (size = N isolates, color = dominant ST)
- Connection Map (shared MLST links between countries)
- MLST Distribution (one dot per isolate)
- Pie Map 2D / 3D Globe
- **Diversity Map** (Shannon diversity index)
- **Dominance Map** (clonal dominance visualization)
- Sankey (Country → MLST flow)

---

## 📂 Input Files

| File | Format |
|------|--------|
| Phylogenetic tree | Newick |
| Gene presence/absence | CSV / TSV / XLSX |
| Metadata | CSV / TSV / XLSX |

Metadata must contain columns (auto-detected or manually assigned):

- **Country** (`country`, `geo_loc_name`, `geographic_location`, …)
- **MLST** (`mlst`, `st`, `sequence_type`, …)
- **Locus / Accession** (`locus`, `accession`, …)

---

## ⚡ Quick Start

1. Click the **Open in Colab** badge above  
2. Run **Cell 1 (installation)**  
3. Run all subsequent cells  
4. Copy the generated `trycloudflare.com` URL  
5. Open it in your browser  

---

## 📁 Repository Structure

```
VREfm/
├── README.md
├── requirements.txt
├── .gitignore
├── launch_colab.ipynb
└── modules/
    ├── __init__.py
    ├── app.py
    ├── colors.py
    ├── io_utils.py
    ├── detect.py
    ├── tree_utils.py
    ├── rings.py
    ├── geo_data.py
    ├── figures_tree.py
    ├── figures_misc.py
    ├── figures_geo.py
    └── export_ui.py
```

---

## 🔬 Scientific Scope

VREfm provides an integrated visualization environment for:

- MLST distribution analysis  
- Clonal dominance detection  
- Geographic dissemination patterns  
- Gene prevalence mapping  
- Phylogenetic contextualization  

Designed for **genomic epidemiology research** and antimicrobial resistance surveillance.

---

## 📜 License

MIT License
