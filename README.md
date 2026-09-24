# VREfm v4.0  
### Vancomycin-Resistant *Enterococcus faecium* Genomic Visualization Platform

Interactive genomic epidemiology and phylogenetics platform built with **Streamlit**.  
Runs entirely in **Google Colab via a secure Cloudflare tunnel** — no local installation required.

---

## 🚀 Launch in Google Colab

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1SOpNu0UopZmwaPcbysN1SQIOUIPGBYzS?usp=sharing)

---

## ✨ Features

| Tab | Capabilities & Methodologies |
|------|-----------------------------|
| **Tree Builder (New)** | **Automated Phylogenetic Inference**: Build trees on the fly using **Neighbor-Joining (NJ)** or **UPGMA** from SNP distance matrices or gene profiles (Jaccard metric). Direct Newick export. |
| **Circular** | Circular phylogram with multi-layered metadata rings (Gene presence/absence, MLST, Country). |
| **Phylo** | Rectangular Phylogram, Cladogram, Radial, and **Interactive Tanglegram** (Chromosome vs. Plasmid tree reconciliation to track horizontal gene transfer). Root preservation & Midpoint rooting. |
| **Network** | Topology networks with Spring, Kamada-Kawai, Circular, and Spectral layouts. |
| **Heatmap** | High-performance gene presence/absence clustered matrix ($O(1)$ fast lookup). |
| **Stats & Biostats** | **Inferential Statistics**: Fisher's Exact Test, Chi-square ($\chi^2$), Odds Ratios (95% CI) for MLST vs. resistance genes (*vanA*/*vanB*), Simpson ($1-D$) & Shannon diversity indices. |
| **Sunburst** | Hierarchical lineage exploration (Country > MLST > Resistance Profile). |
| **Geo** | **9 Geographic & Spatial Epidemiology Maps**: Choropleth, Bubble Map, Connection Map (shared lineages), Clonal Dominance, 2D/3D Diversity Globe, and Sankey flow. |
| **Diagnostic** | Strict cross-integrity validation between tree leaves, gene profiles, and metadata records. |
| **Export** | Publication-ready figure exports (PNG 300/600 DPI, vector SVG, interactive HTML, PDF). |

---

## 📂 Input Data

| Data Type | Accepted Formats | Description |
|-----------|------------------|-------------|
| **Phylogenetic Tree** *(Optional)* | `.nwk`, `.tree`, `.txt` | Precomputed Newick tree, **OR** infer directly inside the app. |
| **Distance Matrix** *(Optional)* | `.csv`, `.tsv` | Pairwise SNP/Hamming distance matrix for automated NJ/UPGMA tree building. |
| **Gene Presence / Absence** | `.csv`, `.tsv`, `.xlsx` | Binary (0/1) or categorical matrix for Chromosome and/or Plasmid loci. |
| **Metadata** | `.csv`, `.tsv`, `.xlsx` | Epidemiological data (Country, MLST, Isolation source, Year, etc.). |

### Automatic Metadata Detection
The app automatically detects key columns based on aliases:
- **Country**: `country`, `geo_loc_name`, `geographic_location`, `region`, ...
- **MLST / Lineage**: `mlst`, `st`, `sequence_type`, `clonal_complex`, ...
- **Sample ID**: `locus`, `isolate`, `accession`, `genome_id`, `id`, ...

---

## 🧬 Comparative Genomics: Chromosome vs. Plasmid

VREfm enables joint analysis of chromosomal backbones and plasmidomes:
- **Matrix Merging**: Automatic reconciliation of chromosomal and plasmid markers.
- **Tanglegram Visualization**: Compare incongruences between core-genome evolution and mobile genetic elements (e.g., *vanA* transposon *Tn1546* dissemination).

---

## ⚡ Quick Start

1. Click the **Open in Colab** badge above.
2. Run **Cell 1** (Installs dependencies and writes validated modules).
3. Run the **Streamlit & Cloudflare tunnel** cell.
4. Click on the generated `trycloudflare.com` public URL.
5. Upload your files or load the built-in demo dataset to explore!

---

## 📁 Repository Structure

```
VREfm/
├── README.md
├── requirements.txt
├── .gitignore
├── launch_colab.ipynb
└── modules/
    ├── __init__.py           # Package initialization & exports
    ├── app.py                # Main Streamlit dashboard & tab routing
    ├── colors.py             # Harmonized color palettes & ring styles
    ├── io_utils.py           # Parsers, tree inference (NJ/UPGMA) & validators
    ├── detect.py             # Heuristic column detection & locus filters
    ├── tree_utils.py         # DiGraph topology, rooting & sampling
    ├── rings.py              # Polar coordinate layout for circular trees
    ├── geo_data.py           # Country centroid coordinates & ISO codes
    ├── figures_tree.py       # Plotly tree engines, radial & tanglegrams
    ├── figures_misc.py       # Heatmaps, networks, and inferential stats
    ├── figures_geo.py        # 9 spatial epidemiology maps & globes
    └── export_ui.py          # High-resolution rendering & vector exports
```

---

## 🔬 Scientific & Epidemiological Scope

VREfm is engineered for antimicrobial resistance (AMR) surveillance and hospital genomic epidemiology:

- **Clonal Complex Surveillance**: Tracking hospital-adapted high-risk clones (notably CC17: ST80, ST117, ST78, ST203).
- **Horizontal Gene Transfer (HGT)**: Distinguishing clonal expansion from plasmid-mediated resistance transmission.
- **Statistical Rigor**: Quantitative evaluation of genetic associations with hypothesis testing (Fisher / $\chi^2$).
- **Epidemiological Caution**: Geographic link lines represent shared ecological ST distributions and do not imply direct transmission chains without cgMLST/SNP validation.

---

## 📜 License

**MIT License**. 
