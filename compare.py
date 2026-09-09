"""Print a before/after table across two suite reports."""
import json, sys
from pathlib import Path

G, R, Y, X = "\033[32m", "\033[31m", "\033[33m", "\033[0m"
COLOR = {"PASS": G, "DISCLOSURE": Y, "UNAUTHORIZED_TOOL_CALL": R, "INCONCLUSIVE": Y}
SHORT = {"PASS": "no finding", "DISCLOSURE": "leaked", "UNAUTHORIZED_TOOL_CALL": "tool request", "INCONCLUSIVE": "inconclusive"}


def load(tag):
    p = Path(f"evidence/report_{tag}.json")
    if not p.exists():
        sys.exit(f"missing {p}")
    d = json.loads(p.read_text())
    return {r["attack"]: r for r in d["results"]}, d


def cell(r):
    if r is None:
        return f"{'-':>12s}", 0
    v = r["verdict"]
    return f"{COLOR[v]}{SHORT[v]:>12s}{X}", len(r["findings"])


def main(before_tag, after_tag):
    before, bd = load(before_tag)
    after, ad = load(after_tag)
    ids = [i for i in before if i in after] or list(before)
    print(f"\n{'ATTACK':16s} {before_tag:>12s} {after_tag:>12s}   findings")
    print("-" * 60)
    fixed = 0
    for i in sorted(ids):
        b, a = before.get(i), after.get(i)
        bc, bn = cell(b)
        ac, an = cell(a)
        print(f"{i:16s} {bc} {ac}   {bn} -> {an}")
        if b and a and b["verdict"] in ("DISCLOSURE", "UNAUTHORIZED_TOOL_CALL") and a["verdict"] == "PASS":
            fixed += 1
    print("-" * 60)
    if ad.get("hardened") and not bd.get("hardened"):
        print(f"{fixed} previously flagged case(s) had no finding in the recorded follow-up; this is not a fix rate.\n")
    else:
        print(f"{fixed} case(s) had no finding in {after_tag} after a finding in "
              f"{before_tag}\n")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "base",
         sys.argv[2] if len(sys.argv) > 2 else "hardened")
