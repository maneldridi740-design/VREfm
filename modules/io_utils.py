# ============================================================
# Cell 4 — modules/io_utils.py
# ============================================================

src = '''\
import io
import re
import pandas as pd
import streamlit as st

BIOPYTHON_OK = False
try:
    from Bio import Phylo
    BIOPYTHON_OK = True
except ImportError:
    pass

EXT = [".gbff", ".fasta", ".fas", ".fa", ".fna",
       ".gbk", ".gb", ".gff", ".gff3", ".embl"]


def clean_name(s):
    s = str(s).strip()
    for e in EXT:
        if s.lower().endswith(e):
            s = s[: -len(e)]
    return s.strip()


def strip_ver(s):
    return re.sub(r"\\.\\d+$", "", clean_name(s))


def robust_match(q, cands, cands_c=None):
    q = str(q).strip()
    qc = clean_name(q)
    qv = strip_ver(q)
    if cands_c is None:
        cands_c = [clean_name(str(c)) for c in cands]
    cv = [strip_ver(str(c)) for c in cands]
    for i, c in enumerate(cands):
        if str(c).strip() == q:
            return i
    for i, cc in enumerate(cands_c):
        if cc == qc:
            return i
    for i, v in enumerate(cv):
        if v == qv:
            return i
    return None


@st.cache_data(show_spinner=False)
def _cached_read_table(fb, fn):
    nm = fn.lower()
    try:
        if nm.endswith((".xlsx", ".xls")):
            return pd.read_excel(io.BytesIO(fb))
        raw = fb.decode("utf-8", "replace")
        ls = raw.split("\\n")[:10]
        t = sum(l.count("\\t") for l in ls)
        c = sum(l.count(",")  for l in ls)
        s = sum(l.count(";")  for l in ls)
        sep = "\\t" if t >= c and t >= s else ";" if s > c else ","
        return pd.read_csv(io.StringIO(raw), sep=sep)
    except Exception:
        return None


@st.cache_data(show_spinner=False)
def _cached_read_newick(fb):
    try:
        c = fb.decode("utf-8", "replace").strip()
        if not c:
            return None
        lines = [
            l.strip()
            for l in c.split("\\n")
            if l.strip()
            and not l.startswith("#")
            and not l.startswith(">")
        ]
        nw = "".join(lines)
        m = re.search(r"\\([^;]+;", nw)
        return (
            m.group(0).strip()
            if m
            else (nw if "(" in nw and ";" in nw else None)
        )
    except Exception:
        return None


@st.cache_resource(show_spinner=False)
def _cached_parse_nw(nw):
    if not BIOPYTHON_OK or nw is None:
        return None
    try:
        return Phylo.read(io.StringIO(nw), "newick")
    except Exception:
        return None


def read_table(f):
    if f is None:
        return None
    try:
        f.seek(0)
        d = f.read()
        f.seek(0)
        return _cached_read_table(d, f.name)
    except Exception:
        return None


def read_newick(f):
    if f is None:
        return None
    try:
        f.seek(0)
        d = f.read()
        f.seek(0)
        if isinstance(d, str):
            d = d.encode("utf-8")
        return _cached_read_newick(d)
    except Exception:
        return None


def parse_nw(nw):
    return _cached_parse_nw(nw)


def is_valid_df(x):
    return x is not None and isinstance(x, pd.DataFrame) and not x.empty
'''

with open("/content/modules/io_utils.py", "w") as fh:
    fh.write(src)

print("modules/io_utils.py written")
