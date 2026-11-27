#!/usr/bin/env python3
"""Скачивает настоящие иконки Simple Icons в icons/ (нужен интернет).

    python download_icons.py                 # только то, чего ещё нет настоящим
    python download_icons.py react vue       # только указанные id (качаются заново)
    python download_icons.py --force         # скачать всё заново
    python build.py

Что пропускается:
  - иконки, которые уже настоящие (файл Simple Icons с тегом <title>);
  - бренды, которых раньше не нашлось в Simple Icons (список в icons_missing.txt).
Старые иконки перед заменой копируются в icons_backup/.
"""
import json, shutil, sys, urllib.error, urllib.request
from pathlib import Path

from import_icons import ALIASES

ROOT = Path(__file__).parent
BASE = "https://cdn.jsdelivr.net/npm/simple-icons@latest/icons/{}.svg"

def fetch(slug):
    try:
        req = urllib.request.Request(BASE.format(slug), headers={"User-Agent": "badges-catalog"})
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
        raise

def is_real(path):
    """Настоящая иконка Simple Icons: в файле есть <title>, у нарисованных вручную его нет."""
    return path.exists() and "<title>" in path.read_text(encoding="utf-8", errors="ignore")

def main():
    args = sys.argv[1:]
    force = "--force" in args
    only = [a for a in args if not a.startswith("--")]

    cfg = json.loads((ROOT / "badges.json").read_text(encoding="utf-8"))
    ids = [it["id"] for c in cfg["categories"] for it in c["items"]]
    if only:
        ids = [i for i in ids if i in only]

    icons, backup = ROOT / "icons", ROOT / "icons_backup"
    missing_file = ROOT / "icons_missing.txt"
    icons.mkdir(exist_ok=True)
    backup.mkdir(exist_ok=True)
    known_missing = set()
    if missing_file.exists() and not force:
        known_missing = set(missing_file.read_text(encoding="utf-8").split())

    ok, miss, skipped = [], [], 0
    for bid in ids:
        old = icons / f"{bid}.svg"
        if not force and not only and (is_real(old) or bid in known_missing):
            skipped += 1
            continue
        slugs = list(dict.fromkeys(ALIASES.get(bid, []) + [bid.replace("-", ""), bid]))
        svg = next((s for s in (fetch(x) for x in slugs) if s), None)
        if svg is None:
            miss.append(bid)
            continue
        if old.exists() and not (backup / old.name).exists():
            shutil.copyfile(old, backup / old.name)
        old.write_text(svg, encoding="utf-8")
        ok.append(bid)
        print("ok  ", bid)

    if miss or force or only:
        # запоминаем, чего нет в Simple Icons, чтобы не искать это при каждом запуске
        keep = (known_missing | set(miss)) - set(ok)
        missing_file.write_text("\n".join(sorted(keep)) + ("\n" if keep else ""), encoding="utf-8")
    print(f"\nСкачано настоящих: {len(ok)}, пропущено (уже есть): {skipped}")
    if miss:
        print(f"Нет в Simple Icons ({len(miss)}), остались прежние: {', '.join(miss)}")

if __name__ == "__main__":
    main()
