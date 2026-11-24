#!/usr/bin/env python3
"""Saml src/ til én Power BI-temafil og valider den.

Brug:
  python scripts/build.py                   -> dist/theme.json
  python scripts/build.py --out dist/x.json
  python scripts/build.py --check           (valider uden at skrive fil)
  python scripts/build.py --compare orig.json   (semantisk sammenligning med en eksisterende temafil)
"""
import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
VS = SRC / "visualStyles"
DEFAULT_NAME = "_default"

HEX = re.compile(r"^#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})$")


def load(path: Path):
    def no_dupes(pairs):
        keys = [k for k, _ in pairs]
        dupes = sorted({k for k in keys if keys.count(k) > 1})
        if dupes:
            raise ValueError(f"{path.relative_to(ROOT)}: dubleret nøgle {dupes}")
        return dict(pairs)

    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=no_dupes)


def assemble() -> dict:
    theme = load(SRC / "theme.json")
    files = sorted(VS.glob("*.json"), key=lambda p: (p.stem != DEFAULT_NAME, p.stem.lower()))
    theme["visualStyles"] = {("*" if p.stem == DEFAULT_NAME else p.stem): load(p) for p in files}
    return theme


def validate(theme: dict) -> list[str]:
    errors: list[str] = []
    if not theme.get("name"):
        errors.append("'name' mangler")
    if not theme.get("dataColors"):
        errors.append("'dataColors' mangler eller er tom")

    tokens = {k for k, v in theme.items() if isinstance(v, str) and HEX.match(v)}

    def walk(o, path):
        if isinstance(o, dict):
            solid = o.get("solid")
            if isinstance(solid, dict) and isinstance(solid.get("color"), str):
                c = solid["color"]
                if not HEX.match(c) and c not in tokens:
                    errors.append(f"{path}: ukendt farve '{c}'")
            for k, v in o.items():
                walk(v, f"{path}/{k}")
        elif isinstance(o, list):
            for i, v in enumerate(o):
                walk(v, f"{path}[{i}]")
        elif isinstance(o, str) and o.startswith("#") and not HEX.match(o):
            errors.append(f"{path}: ugyldig hex-farve '{o}'")

    walk(theme, "")
    for i, c in enumerate(theme.get("dataColors", [])):
        if not HEX.match(c):
            errors.append(f"dataColors[{i}]: ugyldig hex-farve '{c}'")
    return errors


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", type=Path, default=ROOT / "dist" / "theme.json")
    ap.add_argument("--check", action="store_true", help="valider uden at skrive")
    ap.add_argument("--compare", type=Path, help="sammenlign semantisk med eksisterende temafil")
    args = ap.parse_args()

    try:
        theme = assemble()
    except ValueError as e:
        print(f"Fejl: {e}", file=sys.stderr)
        return 1

    errors = validate(theme)
    if errors:
        print("Validering fejlede:", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 1

    if args.compare:
        other = json.loads(args.compare.read_text(encoding="utf-8-sig"))
        if other != theme:
            a, b = set(other.get("visualStyles", {})), set(theme["visualStyles"])
            print("Afviger fra sammenligningsfilen.", file=sys.stderr)
            if a ^ b:
                print(f"  kun i den ene: {sorted(a ^ b)}", file=sys.stderr)
            return 1
        print("Identisk (semantisk) med sammenligningsfilen")

    if not args.check:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        text = json.dumps(theme, indent=2, ensure_ascii=False) + "\n"
        args.out.write_text(text, encoding="utf-8", newline="\n")
        print(f"Skrev {args.out.relative_to(ROOT)} ({len(text.encode('utf-8')) / 1024:.0f} KB, "
              f"{len(theme['visualStyles'])} visualtyper)")
    else:
        print(f"OK ({len(theme['visualStyles'])} visualtyper)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
