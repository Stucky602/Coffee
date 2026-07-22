#!/usr/bin/env python3
"""Invariant suite for data_offerings.json (schema cig-catalog/1).

Run before EVERY ship that touches catalog data:  python3 check_catalog.py
Exit 0 = all invariants hold. Exit 1 = broken reference / duplicate id / bad shape.
TODO-marker counts are reported (the honesty surface) but never fail the check.

This is the guardrail that lets Sonnet sessions edit catalog data safely: a content
edit that breaks a reference is caught here, not on a wholesale partner's phone.
See docs/CIG_DATA_MODEL.md for the schema this enforces.
"""
import json, pathlib, sys

BASE = pathlib.Path(__file__).parent
errors, warnings = [], []

try:
    cat = json.loads((BASE / "data_offerings.json").read_text())
except Exception as e:
    print(f"FAIL: data_offerings.json unreadable: {e}"); sys.exit(1)

# ---- I1: schema tag present and known -----------------------------------------
if cat.get("schema") != "cig-catalog/1":
    errors.append(f"I1 schema tag: expected 'cig-catalog/1', got {cat.get('schema')!r}")

coffees   = cat.get("coffees", [])
producers = cat.get("producers", [])
tiers     = cat.get("tiers", [])
locations = cat.get("locations", [])
recipes   = cat.get("recipes", [])

def uniq(items, key, label):
    seen = {}
    for it in items:
        k = it.get(key)
        if not k: errors.append(f"I2 {label}: entry missing '{key}': {str(it)[:60]}")
        elif k in seen: errors.append(f"I2 {label}: duplicate {key} '{k}'")
        seen[k] = True
    return set(seen)

# ---- I2: unique identifiers ----------------------------------------------------
slugs  = uniq(coffees,   "slug", "coffees")
p_ids  = uniq(producers, "id",   "producers")
t_ids  = uniq(tiers,     "id",   "tiers")
l_ids  = uniq(locations, "id",   "locations")
r_ids  = uniq(recipes,   "id",   "recipes")

# ---- I3: every reference resolves ----------------------------------------------
VALID_CHANNELS = {"wholesale", "retail", "cafe"}
for c in coffees:
    s = c.get("slug", "?")
    if isinstance(c.get("producer"), str) and c["producer"] not in p_ids:
        errors.append(f"I3 coffee '{s}': producer ref '{c['producer']}' unresolved")
    if isinstance(c.get("tier"), str) and c["tier"] not in t_ids:
        errors.append(f"I3 coffee '{s}': tier ref '{c['tier']}' unresolved")
    for ch in c.get("channels", []):
        if ch not in VALID_CHANNELS:
            errors.append(f"I3 coffee '{s}': unknown channel '{ch}' (valid: {sorted(VALID_CHANNELS)})")
    # I4: dial-in blocks, if present, are objects under known keys
    di = c.get("dialin", {})
    if not isinstance(di, dict):
        errors.append(f"I4 coffee '{s}': dialin must be an object")
    else:
        for k in di:
            if k not in ("espresso", "batch", "home"):
                errors.append(f"I4 coffee '{s}': unknown dialin block '{k}'")
            elif not isinstance(di[k], dict):
                errors.append(f"I4 coffee '{s}': dialin.{k} must be an object")

for loc in locations:
    lid = loc.get("id", "?")
    for role, lst in (loc.get("lineup") or {}).items():
        if role not in ("espresso", "filter", "retail"):
            errors.append(f"I3 location '{lid}': unknown lineup role '{role}'")
        for slug in lst:
            if slug not in slugs:
                errors.append(f"I3 location '{lid}': lineup slug '{slug}' unresolved")

# ---- I5: producer.originPage points at a real methodology page ------------------
try:
    meth = json.loads((BASE / "data_methodology.json").read_text())["METHODOLOGY"]
    for p in producers:
        op = p.get("originPage")
        if op and op not in meth:
            errors.append(f"I5 producer '{p.get('id')}': originPage '{op}' not in METHODOLOGY")
except FileNotFoundError:
    warnings.append("I5 skipped: data_methodology.json not found")

# ---- Honesty surface: count TODO markers (report only, never fail) --------------
todo = json.dumps(cat).count("TODO")

for w in warnings: print(f"  warn: {w}")
if errors:
    for e in errors: print(f"  FAIL: {e}")
    print(f"\n{len(errors)} invariant failure(s).")
    sys.exit(1)

print(f"OK — {len(coffees)} coffees, {len(producers)} producers, {len(tiers)} tiers, "
      f"{len(locations)} locations, {len(recipes)} shared recipes. "
      f"{todo} TODO marker(s) outstanding (replace before non-demo use).")
