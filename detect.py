# ============================================================
# Cell 5 — modules/detect.py
# ============================================================

src = '''\
import pandas as pd


def detect_locus(df):
    if df is None:
        return None
    for c in df.columns:
        if c.lower().strip() in [
            "locus", "accession", "accession-locus", "accession_locus"
        ]:
            return c
    return None


def detect_country(df):
    if df is None:
        return None
    canonical = {
        "country", "pays", "geo_location", "geo_loc_name",
        "geographic_location", "collection_country",
        "isolation_country", "location",
        "geo_loc_name_country",
        "geo_loc_name_country_territory",
        "origin", "source_country",
    }
    for c in df.columns:
        cl = c.lower().strip().replace(" ", "_").replace("-", "_")
        if cl in canonical:
            return c
    for c in df.columns:
        cl = c.lower()
        if any(k in cl for k in ("country", "geo_loc", "geographic", "pays")):
            return c
    return None


def detect_mlst(df):
    if df is None:
        return None
    canonical = {
        "mlst", "st", "sequence_type", "sequence_type_mlst",
        "mlst_st", "st_type", "typing", "mlst_type", "pubmlst",
    }
    for c in df.columns:
        cl = c.lower().strip().replace(" ", "_").replace("-", "_")
        if cl in canonical:
            return c
    for c in df.columns:
        cl = c.lower()
        if "mlst" in cl or "sequence_type" in cl or cl.strip() == "st":
            return c
    return None


def get_countries(mdf):
    if mdf is None:
        return []
    cc = detect_country(mdf)
    if cc is None:
        return []
    return sorted(
        mdf[cc].dropna().astype(str)
        .apply(lambda x: x.split(":")[0].strip())
        .unique()
    )


def get_mlsts(mdf):
    if mdf is None:
        return []
    mc = detect_mlst(mdf)
    if mc is None:
        return []
    return sorted([
        str(v) for v in mdf[mc].dropna().unique()
        if str(v) not in ["-", "nan", "Unknown"]
    ])


def loci_for_filter(mdf, countries, mlsts):
    if mdf is None:
        return None
    lc = detect_locus(mdf)
    cc = detect_country(mdf)
    mc = detect_mlst(mdf)
    if lc is None:
        return None
    mask = pd.Series(True, index=mdf.index)
    if countries and cc:
        mask = mask & (
            mdf[cc].astype(str)
            .apply(lambda x: x.split(":")[0].strip())
            .isin(countries)
        )
    if mlsts and mc:
        mask = mask & mdf[mc].astype(str).isin(mlsts)
    return mdf.loc[mask, lc].astype(str).tolist()
'''

with open("/content/modules/detect.py", "w") as fh:
    fh.write(src)

print("modules/detect.py written")
