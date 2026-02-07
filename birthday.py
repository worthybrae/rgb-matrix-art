import math
import random
import time

import board
import displayio
import framebufferio
import rgbmatrix

displayio.release_displays()

matrix = rgbmatrix.RGBMatrix(
    width=64,
    height=64,
    bit_depth=3,
    rgb_pins=[
        board.MTX_R1,
        board.MTX_G1,
        board.MTX_B1,
        board.MTX_R2,
        board.MTX_G2,
        board.MTX_B2,
    ],
    addr_pins=[
        board.MTX_ADDRA,
        board.MTX_ADDRB,
        board.MTX_ADDRC,
        board.MTX_ADDRD,
        board.MTX_ADDRE,
    ],
    clock_pin=board.MTX_CLK,
    latch_pin=board.MTX_LAT,
    output_enable_pin=board.MTX_OE,
)
display = framebufferio.FramebufferDisplay(matrix, auto_refresh=True)

main_group = displayio.Group()
display.root_group = main_group

palette = displayio.Palette(8)
palette[0] = 0x000000
palette[1] = 0xFF0050
palette[2] = 0xFF3377
palette[3] = 0xFF77AA
palette[4] = 0xFFAACC
palette[5] = 0xFFDD44
palette[6] = 0xFF69B4
palette[7] = 0xFFFFFF

bmp = displayio.Bitmap(64, 64, 8)
grid = displayio.TileGrid(bmp, pixel_shader=palette)
main_group.append(grid)

# Big symmetric heart (2x larger)
H_ART = [
    "    ********          ********    ",
    "  ************      ************  ",
    " **************    ************** ",
    "****************  ****************",
    "**********************************",
    "**********************************",
    "**********************************",
    "**********************************",
    "**********************************",
    "**********************************",
    " ******************************** ",
    "  ******************************  ",
    "   ****************************   ",
    "    **************************    ",
    "     ************************     ",
    "      **********************      ",
    "       ********************       ",
    "        ******************        ",
    "         ****************         ",
    "          **************          ",
    "           ************           ",
    "            **********            ",
    "             ********             ",
    "              ******              ",
    "               ****               ",
    "                **                ",
]

HEART = []
hox = 15
hoy = 19
for ry, row in enumerate(H_ART):
    for rx, ch in enumerate(row):
        if ch == '*':
            HEART.append((hox + rx, hoy + ry))

# Bubble text
TEXT = []

# HAPPY
for y in range(14, 23):
    for x in range(4, 7): TEXT.append((x, y))
    for x in range(11, 14): TEXT.append((x, y))
for x in range(4, 14):
    TEXT.append((x, 17))
    TEXT.append((x, 18))

for y in range(16, 23):
    for x in range(16, 19): TEXT.append((x, y))
    for x in range(23, 26): TEXT.append((x, y))
for x in range(16, 26):
    TEXT.append((x, 14))
    TEXT.append((x, 15))
    TEXT.append((x, 18))
    TEXT.append((x, 19))

for y in range(14, 23):
    for x in range(28, 31): TEXT.append((x, y))
for x in range(28, 36):
    TEXT.append((x, 14))
    TEXT.append((x, 15))
    TEXT.append((x, 18))
    TEXT.append((x, 19))
TEXT.append((34, 16))
TEXT.append((35, 16))
TEXT.append((34, 17))
TEXT.append((35, 17))

for y in range(14, 23):
    for x in range(38, 41): TEXT.append((x, y))
for x in range(38, 46):
    TEXT.append((x, 14))
    TEXT.append((x, 15))
    TEXT.append((x, 18))
    TEXT.append((x, 19))
TEXT.append((44, 16))
TEXT.append((45, 16))
TEXT.append((44, 17))
TEXT.append((45, 17))

for x in range(48, 51): TEXT.append((x, 14)); TEXT.append((x, 15))
for x in range(55, 58): TEXT.append((x, 14)); TEXT.append((x, 15))
for x in range(50, 56): TEXT.append((x, 16)); TEXT.append((x, 17))
for y in range(18, 23):
    for x in range(52, 55): TEXT.append((x, y))

# BDAY
for y in range(26, 35):
    for x in range(8, 11): TEXT.append((x, y))
for x in range(8, 16):
    TEXT.append((x, 26))
    TEXT.append((x, 27))
    TEXT.append((x, 29))
    TEXT.append((x, 30))
    TEXT.append((x, 33))
    TEXT.append((x, 34))
TEXT.append((14, 28))
TEXT.append((15, 28))
TEXT.append((14, 31))
TEXT.append((15, 31))
TEXT.append((14, 32))
TEXT.append((15, 32))

for y in range(26, 35):
    for x in range(19, 22): TEXT.append((x, y))
for x in range(19, 26):
    TEXT.append((x, 26))
    TEXT.append((x, 27))
    TEXT.append((x, 33))
    TEXT.append((x, 34))
for y in range(28, 33):
    TEXT.append((26, y))
    TEXT.append((27, y))

for y in range(28, 35):
    for x in range(30, 33): TEXT.append((x, y))
    for x in range(37, 40): TEXT.append((x, y))
for x in range(30, 40):
    TEXT.append((x, 26))
    TEXT.append((x, 27))
    TEXT.append((x, 30))
    TEXT.append((x, 31))

for x in range(42, 45): TEXT.append((x, 26)); TEXT.append((x, 27))
for x in range(49, 52): TEXT.append((x, 26)); TEXT.append((x, 27))
for x in range(44, 50): TEXT.append((x, 28)); TEXT.append((x, 29))
for y in range(30, 35):
    for x in range(46, 49): TEXT.append((x, y))

# MIA
for y in range(38, 47):
    for x in range(14, 17): TEXT.append((x, y))
    for x in range(23, 26): TEXT.append((x, y))
for x in range(14, 26):
    TEXT.append((x, 38))
    TEXT.append((x, 39))
TEXT.append((18, 40))
TEXT.append((19, 40))
TEXT.append((20, 40))
TEXT.append((21, 40))
TEXT.append((19, 41))
TEXT.append((20, 41))

for y in range(38, 47):
    for x in range(29, 32): TEXT.append((x, y))

for y in range(40, 47):
    for x in range(35, 38): TEXT.append((x, y))
    for x in range(43, 46): TEXT.append((x, y))
for x in range(35, 46):
    TEXT.append((x, 38))
    TEXT.append((x, 39))
    TEXT.append((x, 42))
    TEXT.append((x, 43))

HEART = list(set(HEART))
TEXT = list(set(TEXT))

while len(HEART) < len(TEXT):
    HEART.append(HEART[len(HEART) % 50])
while len(TEXT) < len(HEART):
    TEXT.append(TEXT[len(TEXT) % 50])

NUM = len(HEART)

HCX = 32
HCY = 32

hbx = [HEART[i][0] - HCX for i in range(NUM)]
hby = [HEART[i][1] - HCY for i in range(NUM)]

px = [0.0] * NUM
py = [0.0] * NUM
vx = [0.0] * NUM
vy = [0.0] * NUM
tx = [TEXT[i][0] for i in range(NUM)]
ty = [TEXT[i][1] for i in range(NUM)]

state = 0
timer = 0
drawn = False

# Calculate distance from center for each heart pixel
hdist = []
for i in range(NUM):
    d = math.sqrt(hbx[i]*hbx[i] + hby[i]*hby[i])
    hdist.append(d)
max_dist = max(hdist)
radius = 0.0

# Track which heart pixels have been drawn (to prevent flashing)
heart_drawn = [False] * NUM
bmp.fill(0)  # Clear once at start

while True:
    if state == 0:  # Heart growing from center outward
        radius += 0.08  # Slower growth

        # Only draw NEW pixels as they become visible (no flashing)
        for i in range(NUM):
            if hdist[i] <= radius and not heart_drawn[i]:
                x, y = HEART[i][0], HEART[i][1]
                px[i] = float(x)
                py[i] = float(y)
                if 0 <= x < 64 and 0 <= y < 64:
                    bmp[x, y] = 1 + (i % 6)  # Multi-color like confetti
                heart_drawn[i] = True

        if radius >= max_dist + 1:
            state = 1
            timer = 0
            radius = 0.0
            for i in range(NUM):
                dx = px[i] - HCX
                dy = py[i] - HCY
                d = math.sqrt(dx*dx + dy*dy) + 1
                spd = 2 + random.random() * 3
                vx[i] = dx/d * spd + random.random() - 0.5
                vy[i] = dy/d * spd + random.random() - 0.5

    elif state == 1:  # Explode
        bmp.fill(0)
        for i in range(NUM):
            vy[i] += 0.02
            vx[i] *= 0.97
            vy[i] *= 0.97
            px[i] += vx[i]
            py[i] += vy[i]
            if px[i] < 0: px[i] += 64
            if px[i] >= 64: px[i] -= 64
            if py[i] < 0: py[i] += 64
            if py[i] >= 64: py[i] -= 64
            x, y = int(px[i]), int(py[i])
            if 0 <= x < 64 and 0 <= y < 64:
                bmp[x, y] = 1 + (i % 6)

        timer += 1
        if timer >= 25:  # Less confetti time
            state = 2
            timer = 0

    elif state == 2:  # Fast formation - particles zip to text
        bmp.fill(0)

        # Easing that starts moderate and accelerates
        e = 0.10 + timer * 0.012

        for i in range(NUM):
            # Move toward target
            dx = tx[i] - px[i]
            dy = ty[i] - py[i]
            px[i] += dx * e
            py[i] += dy * e

            x, y = int(px[i]), int(py[i])
            if 0 <= x < 64 and 0 <= y < 64:
                bmp[x, y] = 1 + (i % 6)  # Multi-color throughout

        timer += 1
        if timer >= 26:  # 25% faster (was 35)
            # Draw final text now to prevent flicker on transition
            bmp.fill(0)
            for idx, (x, y) in enumerate(TEXT):
                if 0 <= x < 64 and 0 <= y < 64:
                    bmp[x, y] = 1 + (idx % 6)  # Multi-color like confetti
            for i in range(NUM):
                px[i] = float(tx[i])
                py[i] = float(ty[i])
            state = 3
            timer = 0
            drawn = True  # Already drew text, skip redraw in state 3

    elif state == 3:  # Hold text solid
        if not drawn:
            bmp.fill(0)
            for idx, (x, y) in enumerate(TEXT):
                if 0 <= x < 64 and 0 <= y < 64:
                    bmp[x, y] = 1 + (idx % 6)  # Multi-color like confetti
            for i in range(NUM):
                px[i] = float(tx[i])
                py[i] = float(ty[i])
            drawn = True

        timer += 1
        if timer >= 300:  # Longer on text
            state = 4
            timer = 0
            drawn = False
            for i in range(NUM):
                vx[i] = random.random() * 0.6 - 0.3
                vy[i] = -random.random() * 0.5

    elif state == 4:  # Fall off screen
        bmp.fill(0)
        all_off = True
        for i in range(NUM):
            vy[i] += 0.15  # Faster fall
            px[i] += vx[i]
            py[i] += vy[i]
            if px[i] < 0: px[i] += 64
            if px[i] >= 64: px[i] -= 64
            x, y = int(px[i]), int(py[i])
            if 0 <= x < 64 and 0 <= y < 64:
                bmp[x, y] = 1 + (i % 6)
                all_off = False

        if all_off:
            state = 5
            timer = 0
            bmp.fill(0)  # Clear screen

    elif state == 5:  # Blank pause
        timer += 1
        if timer >= 30:  # ~1 second pause
            state = 0
            timer = 0
            radius = 0.0
            for i in range(NUM):
                heart_drawn[i] = False

    time.sleep(0.033)
