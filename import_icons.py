#!/usr/bin/env python3
"""Подмена иконок настоящими из Simple Icons.

Использование:
    python import_icons.py ПУТЬ/К/simple-icons/icons   # папка с *.svg из Simple Icons
    python build.py

Скрипт сопоставляет id бейджей из badges.json с файлами Simple Icons
(по имени и по таблице ALIASES), копирует найденные в icons/ и печатает,
чего не нашлось: для таких бейджей остаются текущие иконки.
"""
import json, re, shutil, sys
from pathlib import Path

ROOT = Path(__file__).parent

# id бейджа -> возможные имена в Simple Icons (без .svg)
ALIASES = {
    "nodejs": ["nodedotjs"], "nextjs": ["nextdotjs"], "nuxt": ["nuxtdotjs", "nuxt"],
    "vue": ["vuedotjs"], "threejs": ["threedotjs"], "express": ["express"],
    "tailwind": ["tailwindcss"], "unreal": ["unrealengine"], "itch": ["itchdotio"],
    "epic-games": ["epicgames"], "gamejolt": ["gamejolt"], "android-studio": ["androidstudio"],
    "aftereffects": ["adobeaftereffects"], "premiere": ["adobepremierepro"],
    "photoshop": ["adobephotoshop"], "illustrator": ["adobeillustrator"],
    "davinci": ["davinciresolve"], "fl-studio": ["flstudio"], "obs": ["obsstudio"],
    "chatgpt": ["openai"], "copilot": ["githubcopilot"], "gemini": ["googlegemini"],
    "mistral": ["mistralai"], "stable-diffusion": ["stabilityai"], "love": ["love2d"],
    "babylonjs": ["babylondotjs"], "raspberry-pi": ["raspberrypi"], "arch": ["archlinux"],
    "macos": ["apple", "macos"], "ios": ["ios"], "wsl": ["windowsterminal"],
    "rest-api": [], "websockets": [], "jquery": ["jquery"], "bun": ["bun"],
}

def norm(s):
    return re.sub(r"[^a-z0-9]", "", s.lower())

def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    src = Path(sys.argv[1])
    files = {norm(p.stem): p for p in src.glob("*.svg")}
    if not files:
        sys.exit(f"В {src} нет SVG-файлов")
    cfg = json.loads((ROOT / "badges.json").read_text(encoding="utf-8"))
    (ROOT / "icons").mkdir(exist_ok=True)
    done, missing = [], []
    for cat in cfg["categories"]:
        for it in cat["items"]:
            bid = it["id"]
            names = [bid] + ALIASES.get(bid, [])
            hit = next((files[norm(n)] for n in names if norm(n) in files), None)
            if hit:
                shutil.copyfile(hit, ROOT / "icons" / f"{bid}.svg")
                done.append(bid)
            else:
                missing.append(bid)
    print(f"Заменено настоящими: {len(done)}")
    print(f"Не нашлось ({len(missing)}), остаются как были: {', '.join(missing)}")

if __name__ == "__main__":
    main()
