#!/usr/bin/env python3
"""Del en samlet Power BI-temafil op i src/.

Brug:  python scripts/split.py sti/til/temafil.json

- src/theme.json            alt på topniveau undtagen visualStyles
- src/visualStyles/<n>.json  én fil pr. visualtype ("*" gemmes som _default.json)

Filer i src/visualStyles, som IKKE findes i inputfilen (fx DAPSPC), bliver
liggende. Filer, der findes i inputfilen, overskrives - brug git diff til at se
hvad der er ændret.
"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
VS = SRC / "visualStyles"
DEFAULT_NAME = "_default"  # "*" er ikke et gyldigt filnavn på Windows


def write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(data, indent=2, ensure_ascii=False) + "\n"
    path.write_text(text, encoding="utf-8", newline="\n")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("theme", type=Path, help="samlet temafil (.json)")
    args = ap.parse_args()

    data = json.loads(args.theme.read_text(encoding="utf-8-sig"))
    styles = data.pop("visualStyles", None)
    if not isinstance(styles, dict):
        print("Fejl: filen har ingen visualStyles", file=sys.stderr)
        return 1

    write_json(SRC / "theme.json", data)

    written = set()
    for name, style in styles.items():
        fname = DEFAULT_NAME if name == "*" else name
        write_json(VS / f"{fname}.json", style)
        written.add(fname)

    kept = sorted(p.stem for p in VS.glob("*.json") if p.stem not in written)
    print(f"Skrev src/theme.json og {len(written)} visualtyper")
    if kept:
        print("Uændret (findes ikke i inputfilen): " + ", ".join(kept))
    return 0


if __name__ == "__main__":
    sys.exit(main())
