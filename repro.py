"""Show which findings reproduce across runs of the same target.

Scoring is deterministic, the calls are not. A single run tells you a failure
is reachable; it cannot tell you how often. This lines runs up side by side so
a stable weakness is distinguishable from a lucky one.

    python repro.py base base2 demoaudio
"""
import json, sys
from pathlib import Path
from report import validate_report

MARK = {"PASS": ("no finding", "\033[32m"),
        "DISCLOSURE": ("leaked", "\033[33m"),
        "UNAUTHORIZED_TOOL_CALL": ("tool requested", "\033[31m"),
        "INCONCLUSIVE": ("inconclusive", "\033[33m")}
RESET = "\033[0m"


def load(tag):
    p = Path(f"evidence/report_{tag}.json")
    if not p.exists():
        return None
    try:
        d = json.loads(p.read_text())
    except (OSError, UnicodeError, ValueError):
        return None
    if validate_report(d, require_case_ids=True):
        return None
    return {r["attack"]: r for r in d["results"]}


def main(tags):
    runs = [(t, load(t)) for t in tags]
    missing = [t for t, r in runs if r is None]
    if missing:
        print(f"no usable report for: {', '.join(missing)}; comparison is inconclusive")
        return 1
    runs = [(t, r) for t, r in runs if r]

    attacks = sorted({a for _, r in runs for a in r})
    if not attacks:
        print("No recorded cases to compare; comparison is inconclusive.")
        return 1
    w = max(len(a) for a in attacks) + 2
    head = "ATTACK".ljust(w) + "".join(t[:13].rjust(15) for t, _ in runs)
    print(head)
    print("-" * len(head))

    stable, flaky, clean = [], [], []
    for a in attacks:
        cells, verdicts = "", []
        for _, r in runs:
            got = r.get(a)
            if not got:
                cells += "".rjust(15)
                continue
            verdict = got.get("verdict", "INCONCLUSIVE")
            if not isinstance(verdict, str):
                verdict = "INCONCLUSIVE"
            label, colour = MARK.get(verdict, MARK["INCONCLUSIVE"])
            n = len(got["findings"])
            txt = f"{label}" + (f" ({n})" if n else "")
            cells += f"{colour}{txt.rjust(15)}{RESET}"
            verdicts.append(verdict)
        print(a.ljust(w) + cells)
        if any(v not in ("PASS", "DISCLOSURE", "UNAUTHORIZED_TOOL_CALL") for v in verdicts):
            print(f"  {a}: incomplete evidence; no cross-run conclusion.")
            continue
        broke = [v for v in verdicts if v != "PASS"]
        if len(verdicts) < 2:
            continue
        if len(broke) == len(verdicts):
            stable.append(a)
        elif broke:
            flaky.append(a)
        else:
            clean.append(a)

    print("-" * len(head))
    if stable:
        print(f"reproduced every run:  {', '.join(stable)}")
    if flaky:
        print(f"broke intermittently:  {', '.join(flaky)}")
    if clean:
        print(f"no finding in compared samples: {', '.join(clean)}")
    if flaky:
        print("\nAn intermittent break is still a break. It is reachable, and a "
              "run where it held is not evidence that it was fixed.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:] or ["base", "base2", "demoaudio"]))
