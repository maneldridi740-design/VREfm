# ============================================================
# Cell 6 — modules/tree_utils.py
# ============================================================

src = '''\
import copy
import math
import numpy as np
import networkx as nx


def bio_to_nx(tree):
    if tree is None:
        return nx.Graph()
    G = nx.Graph()
    ct = [0]

    def _walk(cl, parent=None):
        nm = str(cl.name).strip() if cl.name else None
        if not nm or nm == "None":
            ct[0] += 1
            nm = f"_i{ct[0]}"
        base = nm
        while nm in G.nodes:
            ct[0] += 1
            nm = f"{base}_d{ct[0]}"
        G.add_node(nm)
        if parent is not None:
            wt = float(cl.branch_length) if cl.branch_length else 0.001
            G.add_edge(parent, nm, weight=round(max(1e-4, abs(wt)), 6))
        for ch in cl.clades:
            _walk(ch, nm)

    _walk(tree.root)
    return G


def get_leaves(G):
    return [n for n in G.nodes if not str(n).startswith("_i")]


def _root_tree(G, r=None):
    if G.number_of_nodes() == 0:
        return nx.DiGraph(), None
    if r is None:
        internal = [n for n in G.nodes if str(n).startswith("_i")]
        r = (
            max(internal, key=lambda n: G.degree(n))
            if internal
            else max(G.nodes, key=lambda n: G.degree(n))
        )
    T = nx.bfs_tree(G, r)
    for u, v in T.edges():
        T[u][v]["weight"] = G[u][v].get("weight", 1) if G.has_edge(u, v) else 1
    return T, r


def polar_coords(tree):
    if tree is None:
        return {}, {}, []
    depth = {}

    def _depth(cl, cur):
        depth[id(cl)] = cur
        for ch in cl.clades:
            _depth(ch, cur + (ch.branch_length or 0.001))

    _depth(tree.root, 0.0)
    leaves = tree.get_terminals()
    n = max(len(leaves), 1)
    leaf_angle = {id(l): 2 * np.pi * i / n for i, l in enumerate(leaves)}
    angle = {}

    def _angle(cl):
        if cl.is_terminal():
            angle[id(cl)] = leaf_angle.get(id(cl), 0.0)
            return angle[id(cl)]
        ca = [_angle(ch) for ch in cl.clades]
        angle[id(cl)] = float(np.mean(ca))
        return angle[id(cl)]

    _angle(tree.root)
    return depth, angle, leaves


def rect_lay(G, r=None, branch_scale=True):
    T, r = _root_tree(G, r)
    if r is None:
        return {}, {}
    counter = [0]
    xp, yp = {}, {}

    def dfs(nd, dep):
        children = list(T.successors(nd))
        xp[nd] = dep
        if not children:
            yp[nd] = counter[0]
            counter[0] += 1
        else:
            for ch in children:
                w = T[nd][ch].get("weight", 1) if branch_scale else 1
                dfs(ch, dep + w)
            yp[nd] = np.mean([yp[ch] for ch in children])

    dfs(r, 0)
    return xp, yp


def clado_lay(G, r=None):
    T, r = _root_tree(G, r)
    if r is None:
        return {}, {}
    dm = nx.single_source_shortest_path_length(T, r)
    md = max(dm.values()) if dm else 1
    counter = [0]
    xp, yp = {}, {}

    def dfs(nd, dep):
        children = list(T.successors(nd))
        if not children:
            xp[nd] = md
            yp[nd] = counter[0]
            counter[0] += 1
        else:
            xp[nd] = dep
            for ch in children:
                dfs(ch, dep + 1)
            yp[nd] = np.mean([yp[ch] for ch in children])

    dfs(r, 0)
    return xp, yp


def circ_lay(G, r=None):
    xr, yr = rect_lay(G, r, True)
    if not xr:
        return {}, {}
    mx = max(xr.values()) or 1
    my = max(yr.values()) or 1
    xc, yc = {}, {}
    for nd in xr:
        rr = xr[nd] / mx
        th = yr[nd] / my * 2 * np.pi
        xc[nd] = rr * np.cos(th)
        yc[nd] = rr * np.sin(th)
    return xc, yc


def radial_lay(G, r=None):
    T, r = _root_tree(G, r)
    if r is None:
        return {}, {}
    leaf_count = {}

    def _lc(nd):
        children = list(T.successors(nd))
        if not children:
            leaf_count[nd] = 1
        else:
            leaf_count[nd] = sum(_lc(ch) for ch in children)
        return leaf_count[nd]

    _lc(r)
    xp, yp = {}, {}

    def lay(nd, a0, a1, rr):
        xp[nd] = rr * math.cos((a0 + a1) / 2)
        yp[nd] = rr * math.sin((a0 + a1) / 2)
        children = list(T.successors(nd))
        cur = a0
        for ch in children:
            w = T[nd][ch].get("weight", 1)
            span = (a1 - a0) * leaf_count[ch] / max(leaf_count[nd], 1)
            lay(ch, cur, cur + span, rr + w)
            cur += span

    lay(r, 0, 2 * np.pi, 0)
    return xp, yp


def filter_tree(tree, keep):
    if tree is None or not keep:
        return tree
    from modules.io_utils import clean_name
    t2 = copy.deepcopy(tree)
    kc = {clean_name(str(n)) for n in keep}
    for lf in [l for l in t2.get_terminals()
               if clean_name(str(l.name)) not in kc]:
        try:
            t2.prune(lf)
        except Exception:
            pass
    return t2 if t2.count_terminals() > 0 else tree


def limit_tree(tree, max_n):
    if tree is None:
        return tree
    max_n = int(max_n)
    if max_n <= 0:
        return tree
    t2 = copy.deepcopy(tree)
    terms = t2.get_terminals()
    if len(terms) <= max_n:
        return t2
    for lf in terms[max_n:]:
        try:
            t2.prune(lf)
        except Exception:
            pass
    return t2 if t2.count_terminals() > 0 else tree


def prepare_tree(tree, fl, mx):
    if tree is None:
        return None, 0, 0
    original = tree.count_terminals()
    active = tree
    if fl and len(fl) > 0:
        active = filter_tree(tree, fl)
    active = limit_tree(active, mx)
    return active, original, active.count_terminals()
'''

with open("/content/modules/tree_utils.py", "w") as fh:
    fh.write(src)

print("modules/tree_utils.py written")
