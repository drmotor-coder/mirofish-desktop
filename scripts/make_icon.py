#!/usr/bin/env python3
"""
Генерирует иконку MiroFish: фиолетовый градиент + стилизованная рыба-граф.
Создаёт assets/icon.png (512) и assets/icon.ico (мультиразмер).
"""
import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
ASSETS.mkdir(exist_ok=True)

S = 512
img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
draw = ImageDraw.Draw(img)

# --- фон: скруглённый квадрат с диагональным градиентом #667eea -> #764ba2 ---
c1 = (102, 126, 234)
c2 = (118, 75, 162)
grad = Image.new("RGB", (S, S), c1)
gd = grad.load()
for y in range(S):
    for x in range(S):
        t = (x + y) / (2 * S)
        gd[x, y] = (
            int(c1[0] + (c2[0] - c1[0]) * t),
            int(c1[1] + (c2[1] - c1[1]) * t),
            int(c1[2] + (c2[2] - c1[2]) * t),
        )
mask = Image.new("L", (S, S), 0)
ImageDraw.Draw(mask).rounded_rectangle([0, 0, S - 1, S - 1], radius=110, fill=255)
img.paste(grad, (0, 0), mask)
draw = ImageDraw.Draw(img)

# --- рыба-граф: узлы по контуру рыбы + рёбра ---
cx, cy = 256, 262
# точки тела рыбы (эллипс) + хвост
body = []
for a in range(0, 360, 45):
    r = math.radians(a)
    body.append((cx + 150 * math.cos(r), cy + 95 * math.sin(r)))
tail = [(cx + 165, cy - 70), (cx + 235, cy - 110), (cx + 235, cy + 110), (cx + 165, cy + 70)]

white = (255, 255, 255, 235)
faint = (255, 255, 255, 90)

# рёбра тела
for i in range(len(body)):
    draw.line([body[i], body[(i + 1) % len(body)]], fill=faint, width=5)
# несколько «предсказательных» связей через центр
for p in body:
    draw.line([(cx - 40, cy), p], fill=faint, width=3)
# хвост
draw.line([tail[0], tail[1]], fill=faint, width=5)
draw.line([tail[1], tail[2]], fill=faint, width=5)
draw.line([tail[2], tail[3]], fill=faint, width=5)

# узлы
for p in body + tail:
    draw.ellipse([p[0] - 13, p[1] - 13, p[0] + 13, p[1] + 13], fill=white)
# центральный узел покрупнее
draw.ellipse([cx - 40 - 17, cy - 17, cx - 40 + 17, cy + 17], fill=white)
# глаз
draw.ellipse([cx - 95, cy - 40, cx - 70, cy - 15], fill=(118, 75, 162, 255))

# лёгкое свечение
glow = img.filter(ImageFilter.GaussianBlur(6))
img = Image.alpha_composite(glow, img)

png_path = ASSETS / "icon.png"
img.save(png_path)

# ICO мультиразмер
ico_path = ASSETS / "icon.ico"
img.save(ico_path, sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])

print(f"OK: {png_path}")
print(f"OK: {ico_path}")
