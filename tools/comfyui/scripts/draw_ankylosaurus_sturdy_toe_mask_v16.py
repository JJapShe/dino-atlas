from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter


ROOT = Path(__file__).resolve().parents[3]
ASSETS = ROOT / "assets" / "dinosaurs"
SOURCE = ASSETS / "ankylosaurus-magniventris-broadskull-i2i-v14.png"
MASK = ASSETS / "ankylosaurus-sturdy-toes-i2i-mask-v16.png"


def main():
    image = Image.open(SOURCE).convert("RGB")
    mask = Image.new("L", image.size, 0)
    draw = ImageDraw.Draw(mask)

    # Tight foot/toe regions on the current v14 side-profile source.
    regions = [
        (285, 675, 500, 815),   # front near foot and toe tips
        (590, 660, 770, 825),   # front far foot
        (770, 635, 955, 790),   # rear far foot under body
        (1075, 635, 1265, 810), # rear near foot and toe tips
    ]
    for box in regions:
        draw.ellipse(box, fill=255)

    mask = mask.filter(ImageFilter.GaussianBlur(radius=3))
    MASK.parent.mkdir(parents=True, exist_ok=True)
    Image.merge("RGB", (mask, mask, mask)).save(MASK)
    print(MASK)


if __name__ == "__main__":
    main()
