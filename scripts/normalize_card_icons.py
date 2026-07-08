from collections import Counter, deque
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets" / "cards"

ICON_NAMES = [
    "goomba",
    "shy-guy",
    "boo",
    "toad",
    "yoshi",
    "mario",
    "luigi",
    "princess-peach",
    "bowser",
    "fire-flower",
]

CANVAS = 512
FILL_RATIO = 0.76
BG_DIST_THRESHOLD = 16


def _is_near_white(r: int, g: int, b: int) -> bool:
    return r >= 248 and g >= 248 and b >= 248


def _find_background_color(img: Image.Image) -> tuple[int, int, int]:
    rgb = img.convert("RGB")
    w, h = rgb.size
    p = rgb.load()

    border = Counter()
    for y in range(h):
        for x in range(w):
            if x < 8 or y < 8 or x >= w - 8 or y >= h - 8:
                r, g, b = p[x, y]
                if not _is_near_white(r, g, b):
                    border[(r, g, b)] += 1

    if border:
        return border.most_common(1)[0][0]

    # Fallback for rare cases.
    r, g, b = rgb.getpixel((w // 2, 0))
    return r, g, b


def _fg_mask(img: Image.Image, bg: tuple[int, int, int]) -> list[list[bool]]:
    rgb = img.convert("RGB")
    w, h = rgb.size
    p = rgb.load()

    fg = [[False] * w for _ in range(h)]
    for y in range(h):
        row = fg[y]
        for x in range(w):
            r, g, b = p[x, y]
            if _is_near_white(r, g, b):
                continue
            dist = abs(r - bg[0]) + abs(g - bg[1]) + abs(b - bg[2])
            if dist > BG_DIST_THRESHOLD:
                row[x] = True
    return fg


def _remove_border_connected(mask: list[list[bool]]) -> None:
    h = len(mask)
    w = len(mask[0]) if h else 0
    q = deque()

    for x in range(w):
        if mask[0][x]:
            q.append((x, 0))
        if mask[h - 1][x]:
            q.append((x, h - 1))
    for y in range(h):
        if mask[y][0]:
            q.append((0, y))
        if mask[y][w - 1]:
            q.append((w - 1, y))

    while q:
        x, y = q.popleft()
        if x < 0 or y < 0 or x >= w or y >= h or not mask[y][x]:
            continue
        mask[y][x] = False
        q.append((x + 1, y))
        q.append((x - 1, y))
        q.append((x, y + 1))
        q.append((x, y - 1))


def _largest_component_bbox(mask: list[list[bool]]) -> tuple[int, int, int, int] | None:
    h = len(mask)
    w = len(mask[0]) if h else 0
    seen = [[False] * w for _ in range(h)]
    best_area = 0
    best_bbox = None

    for y in range(h):
        for x in range(w):
            if not mask[y][x] or seen[y][x]:
                continue

            q = deque([(x, y)])
            seen[y][x] = True
            area = 0
            min_x = max_x = x
            min_y = max_y = y

            while q:
                cx, cy = q.popleft()
                area += 1
                if cx < min_x:
                    min_x = cx
                if cy < min_y:
                    min_y = cy
                if cx > max_x:
                    max_x = cx
                if cy > max_y:
                    max_y = cy

                for nx, ny in ((cx + 1, cy), (cx - 1, cy), (cx, cy + 1), (cx, cy - 1)):
                    if 0 <= nx < w and 0 <= ny < h and mask[ny][nx] and not seen[ny][nx]:
                        seen[ny][nx] = True
                        q.append((nx, ny))

            if area > best_area:
                best_area = area
                best_bbox = (min_x, min_y, max_x + 1, max_y + 1)

    return best_bbox


def _expand_bbox(bbox: tuple[int, int, int, int], w: int, h: int) -> tuple[int, int, int, int]:
    x1, y1, x2, y2 = bbox
    pad_x = int((x2 - x1) * 0.08)
    pad_y = int((y2 - y1) * 0.08)
    return max(0, x1 - pad_x), max(0, y1 - pad_y), min(w, x2 + pad_x), min(h, y2 + pad_y)


def normalize_icon(path: Path) -> tuple[int, int]:
    im = Image.open(path).convert("RGBA")
    w, h = im.size

    bg = _find_background_color(im)
    mask = _fg_mask(im, bg)
    _remove_border_connected(mask)
    bbox = _largest_component_bbox(mask)

    if bbox is None:
        # Keep unchanged if detection fails.
        return w, h

    bbox = _expand_bbox(bbox, w, h)
    cropped = im.crop(bbox)

    cw, ch = cropped.size
    scale = (CANVAS * FILL_RATIO) / max(cw, ch)
    nw = max(1, int(round(cw * scale)))
    nh = max(1, int(round(ch * scale)))
    resized = cropped.resize((nw, nh), Image.Resampling.LANCZOS)

    out = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
    ox = (CANVAS - nw) // 2
    oy = (CANVAS - nh) // 2
    out.paste(resized, (ox, oy), resized)
    out.save(path)
    return nw, nh


def main() -> None:
    for name in ICON_NAMES:
        path = ASSETS / f"{name}.png"
        if not path.exists():
            print(f"skip missing {path}")
            continue
        nw, nh = normalize_icon(path)
        print(f"normalized {path.relative_to(ROOT)} content={nw}x{nh} canvas={CANVAS}x{CANVAS}")


if __name__ == "__main__":
    main()
