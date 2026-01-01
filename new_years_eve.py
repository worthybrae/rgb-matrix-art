import math
import random
import time
import board
import displayio
import framebufferio
import rgbmatrix
import wifi
import socketpool
import ssl
import adafruit_requests

displayio.release_displays()

matrix = rgbmatrix.RGBMatrix(
    width=64, height=64, bit_depth=3,
    rgb_pins=[board.MTX_R1, board.MTX_G1, board.MTX_B1,
              board.MTX_R2, board.MTX_G2, board.MTX_B2],
    addr_pins=[board.MTX_ADDRA, board.MTX_ADDRB, board.MTX_ADDRC,
               board.MTX_ADDRD, board.MTX_ADDRE],
    clock_pin=board.MTX_CLK, latch_pin=board.MTX_LAT, output_enable_pin=board.MTX_OE)
display = framebufferio.FramebufferDisplay(matrix, auto_refresh=True)

g = displayio.Group()
display.root_group = g

pal = displayio.Palette(16)
pal[0] = 0x000000
pal[1] = 0xFF0000
pal[2] = 0xFF6600
pal[3] = 0xFFFF00
pal[4] = 0x00FF00
pal[5] = 0x00FFFF
pal[6] = 0x0066FF
pal[7] = 0xFF00FF
pal[8] = 0xFFFFFF
pal[9] = 0x888888
pal[10] = 0x111111
pal[11] = 0xFFCC99
pal[12] = 0x880000
pal[13] = 0x884400
pal[14] = 0x008800
pal[15] = 0x444444

bmp = displayio.Bitmap(64, 64, 16)
g.append(displayio.TileGrid(bmp, pixel_shader=pal))

# Setup WiFi requests
pool = socketpool.SocketPool(wifi.radio)
requests = adafruit_requests.Session(pool, ssl.create_default_context())

TIME_URL = "http://worldtimeapi.org/api/timezone/America/New_York"
cached_secs = 0
last_fetch = 0
fetch_interval = 60

def fetch_time():
    global cached_secs, last_fetch
    try:
        r = requests.get(TIME_URL)
        data = r.json()
        r.close()
        dt = data["datetime"]
        # Parse "2025-12-31T16:38:45.154394-05:00"
        t_part = dt.split("T")[1].split("-")[0].split("+")[0]
        h, m, s = t_part.split(":")
        cur_secs = int(h) * 3600 + int(m) * 60 + int(float(s))
        cached_secs = 86400 - cur_secs if cur_secs > 0 else 0
        last_fetch = time.monotonic()
    except:
        pass

def secs_to_mid():
    global cached_secs
    elapsed = time.monotonic() - last_fetch
    remaining = cached_secs - int(elapsed)
    return max(0, remaining)

FLOOR_Y = 48
colors = [1, 2, 3, 4, 5, 6, 7]
dim_map = {1:12, 2:13, 3:3, 4:14, 5:5, 6:15, 7:7}

tile_cur = [[random.choice(colors) for _ in range(8)] for _ in range(2)]
tile_tgt = [[random.choice(colors) for _ in range(8)] for _ in range(2)]
tile_prg = [[0 for _ in range(8)] for _ in range(2)]

def tile_col(ty, tx):
    p = tile_prg[ty][tx]
    if p < 5:
        return tile_cur[ty][tx]
    elif p < 10:
        return dim_map.get(tile_cur[ty][tx], tile_cur[ty][tx])
    elif p < 15:
        return dim_map.get(tile_tgt[ty][tx], tile_tgt[ty][tx])
    return tile_tgt[ty][tx]

def draw_floor():
    for ty in range(2):
        for tx in range(8):
            c = tile_col(ty, tx)
            for py in range(8):
                for px in range(8):
                    x, y = tx * 8 + px, FLOOR_Y + ty * 8 + py
                    bmp[x, y] = 10 if px == 0 or py == 0 else c

def upd_tiles():
    for ty in range(2):
        for tx in range(8):
            if tile_prg[ty][tx] > 0:
                tile_prg[ty][tx] += 1
                if tile_prg[ty][tx] >= 20:
                    tile_cur[ty][tx] = tile_tgt[ty][tx]
                    tile_prg[ty][tx] = 0

def new_tile():
    tx, ty = random.randint(0, 7), random.randint(0, 1)
    if tile_prg[ty][tx] == 0:
        tile_tgt[ty][tx] = random.choice(colors)
        if tile_tgt[ty][tx] != tile_cur[ty][tx]:
            tile_prg[ty][tx] = 1

sparkles = []

def draw_ball(f):
    cx, cy, r = 10, 10, 6
    for dy in range(-r, r+1):
        for dx in range(-r, r+1):
            if dx*dx + dy*dy <= r*r:
                a = math.atan2(dy, dx) + f * 0.08
                bmp[cx+dx, cy+dy] = 8 if int(a * 4) % 2 else 9
    for y in range(4):
        bmp[cx, y] = 15
    if f % 3 == 0 and len(sparkles) < 12:
        a = random.uniform(0, 6.28)
        sparkles.append([cx + math.cos(a)*r, cy + math.sin(a)*r,
                        math.cos(a)*1.5, math.sin(a)*1.2,
                        random.choice(colors), 15])

def upd_sparkles():
    for s in sparkles[:]:
        ox, oy = int(s[0]), int(s[1])
        if 0 <= ox < 64 and 0 <= oy < FLOOR_Y:
            bmp[ox, oy] = 0
        s[0] += s[2]
        s[1] += s[3]
        s[5] -= 1
        if s[5] <= 0 or s[0] < 0 or s[0] >= 64 or s[1] >= FLOOR_Y:
            sparkles.remove(s)
        else:
            nx, ny = int(s[0]), int(s[1])
            if 0 <= nx < 64 and 0 <= ny < FLOOR_Y:
                bmp[nx, ny] = s[4]

DIG = {
    '0': 0b111101101101111, '1': 0b010110010010111,
    '2': 0b111001111100111, '3': 0b111001111001111,
    '4': 0b101101111001001, '5': 0b111100111001111,
    '6': 0b111100111101111, '7': 0b111001001001001,
    '8': 0b111101111101111, '9': 0b111101111001111, ':': 0b00100010
}

def draw_dig(ch, x, y, c):
    bits = DIG.get(ch, 0)
    w = 1 if ch == ':' else 3
    for i in range(5):
        for j in range(w):
            px, py = x + j, y + i
            if 0 <= px < 64 and 0 <= py < 64:
                on = bits & (1 << (14 - i * w - j if w == 3 else 4 - i))
                bmp[px, py] = c if on else bmp[px, py]

def clear_time():
    for y in range(3, 10):
        for x in range(30, 64):
            bmp[x, y] = 0

def draw_time(secs, c):
    h, m, s = secs // 3600, (secs % 3600) // 60, secs % 60
    t = f"{h}:{m:02d}:{s:02d}"
    x = 32
    for ch in t:
        draw_dig(ch, x, 4, c)
        x += 2 if ch == ':' else 4

def clear_dancer(bx):
    for dy in range(20):
        for dx in range(-4, 7):
            px, py = bx + dx, FLOOR_Y - 18 + dy
            if 0 <= px < 64 and 0 <= py < FLOOR_Y:
                bmp[px, py] = 0

def draw_dancer(bx, f, c):
    fy = FLOOR_Y - 1
    hy = fy - 17
    for dy in range(3):
        for dx in range(3):
            bmp[bx+dx, hy+dy] = 11
    sway = 1 if f % 4 < 2 else -1
    by = hy + 3
    for dy in range(6):
        for dx in range(3):
            bmp[bx+dx+sway*(dy//3), by+dy] = c
    ay = by + 1
    if f == 0:
        for i in range(4):
            bmp[bx-1-i, ay-2-i] = c
            bmp[bx+3+i, ay-2-i] = c
    elif f == 1:
        for i in range(4):
            bmp[bx-1-i, ay] = c
            bmp[bx+3+i, ay] = c
    elif f == 2:
        for i in range(4):
            bmp[bx-1-i, ay-2-i] = c
            bmp[bx+3+i, ay+i] = c
    elif f == 3:
        for i in range(4):
            bmp[bx-1-i, ay-i] = c
            bmp[bx+3+i, ay-i] = c
    elif f == 4:
        for i in range(4):
            bmp[bx-1-i, ay+i] = c
            bmp[bx+3+i, ay-2-i] = c
    else:
        for i in range(4):
            bmp[bx-1-i, ay-1-(i%2)] = c
            bmp[bx+3+i, ay-1-((i+1)%2)] = c
    ly = by + 6
    ll = fy - ly
    if f % 6 < 2:
        for i in range(ll):
            bmp[bx-1, ly+i] = c
            bmp[bx+3, ly+i] = c
    elif f % 6 < 4:
        for i in range(ll):
            off = i // 2
            bmp[bx+off, ly+i] = c
            bmp[bx+2-off, ly+i] = c
    else:
        for i in range(ll):
            bmp[bx, ly+i] = c
        for i in range(ll-2):
            bmp[bx+3+i//2, ly+i] = c

def celebrate(f):
    clear_time()
    for ch, px in zip("2025", [32, 38, 44, 50]):
        draw_dig(ch, px, 4, colors[f // 6 % 7])
    for _ in range(8):
        bmp[random.randint(0, 63), random.randint(0, 18)] = random.choice(colors)

dancers = [(8, 1), (24, 6), (40, 7), (54, 4)]
dance_f = [0, 3, 1, 4]
frame, celeb = 0, False
last_s, col_i = -1, 0

for y in range(64):
    for x in range(64):
        bmp[x, y] = 0

# Initial time fetch
fetch_time()

draw_floor()
for i, (dx, dc) in enumerate(dancers):
    draw_dancer(dx, dance_f[i], dc)

while True:
    # Refresh time from API every 60 seconds
    if time.monotonic() - last_fetch > fetch_interval:
        fetch_time()

    secs = secs_to_mid()
    if secs == 0:
        celeb = True

    draw_ball(frame)
    upd_sparkles()

    upd_tiles()
    if frame % 12 == 0:
        new_tile()
    draw_floor()

    if frame % 6 == 0:
        for i in range(4):
            clear_dancer(dancers[i][0])
            dance_f[i] = (dance_f[i] + 1) % 6
        for i, (dx, dc) in enumerate(dancers):
            draw_dancer(dx, dance_f[i], dc)

    if secs != last_s:
        last_s = secs
        col_i = (col_i + 1) % 7
        if celeb:
            celebrate(frame)
        else:
            clear_time()
            draw_time(secs, colors[col_i])

    frame += 1
    time.sleep(0.033)
