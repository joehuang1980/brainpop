from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets" / "cards"

JOBS = [
    {
        "src": ROOT / "螢幕擷取畫面 2026-07-08 110846 (1).png",
        "labels": ["shy-guy", "boo"],
    },
    {
        "src": ROOT / "螢幕擷取畫面 2026-07-08 110846.png",
        "labels": ["mario", "luigi", "princess-peach", "bowser", "yoshi", "toad"],
    },
    {
        "src": ROOT / "螢幕擷取畫面 2026-07-08 110905.png",
        "labels": ["goomba"],
    },
    {
        "src": ROOT / "螢幕擷取畫面 2026-07-08 110920.png",
        "labels": ["fire-flower"],
    },
]


def _foreground_bbox(img: Image.Image, threshold: int = 22):
    """Find non-background bbox by comparing pixels against sampled corner color."""
    rgb = img.convert("RGB")
    width, height = rgb.size
    bg = rgb.getpixel((0, 0))

    min_x = width
    min_y = height
    max_x = -1
    max_y = -1

    pixels = rgb.load()
    for y in range(height):
        for x in range(width):
            r, g, b = pixels[x, y]
            dr = abs(r - bg[0])
            dg = abs(g - bg[1])
            db = abs(b - bg[2])
            if dr + dg + db > threshold:
                if x < min_x:
                    min_x = x
                if y < min_y:
                    min_y = y
                if x > max_x:
                    max_x = x
                if y > max_y:
                    max_y = y

    if max_x < min_x or max_y < min_y:
        return None
    return min_x, min_y, max_x + 1, max_y + 1


def _expand_bbox(bbox, width: int, height: int, padding_ratio: float = 0.08):
    x1, y1, x2, y2 = bbox
    pad_x = int((x2 - x1) * padding_ratio)
    pad_y = int((y2 - y1) * padding_ratio)
    x1 = max(0, x1 - pad_x)
    y1 = max(0, y1 - pad_y)
    x2 = min(width, x2 + pad_x)
    y2 = min(height, y2 + pad_y)
    return x1, y1, x2, y2


def slice_job(src: Path, labels: list[str]):
    im = Image.open(src).convert("RGBA")
    width, height = im.size
    count = len(labels)
    tile_w = width / count

    for idx, label in enumerate(labels):
        left = int(round(idx * tile_w))
        right = int(round((idx + 1) * tile_w))

        tile = im.crop((left, 0, right, height))

        # Keep top area only to avoid name text below character.
        icon_top = int(height * 0.06)
        icon_bottom = int(height * 0.78)
        icon_region = tile.crop((0, icon_top, tile.width, icon_bottom))

        bbox = _foreground_bbox(icon_region)
        if bbox is None:
            cropped = icon_region
        else:
            bbox = _expand_bbox(bbox, icon_region.width, icon_region.height)
            cropped = icon_region.crop(bbox)

        out = ASSETS / f"{label}.png"
        cropped.save(out)
        print(f"saved {out.relative_to(ROOT)} {cropped.size[0]}x{cropped.size[1]}")


def main():
    ASSETS.mkdir(parents=True, exist_ok=True)
    for job in JOBS:
        slice_job(job["src"], job["labels"])


if __name__ == "__main__":
    main()
