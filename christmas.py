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

# Color palette
palette = displayio.Palette(16)
palette[0] = 0x0A0A28  # Dark night sky
palette[1] = 0xFF0099  # Bright hot pink (for presents)
palette[2] = 0xFFFFFF  # Bright white snow
palette[3] = 0xCCDDFF  # Light blue snow
palette[4] = 0x88AADD  # Fading snow
palette[5] = 0x446688  # Almost melted
palette[6] = 0x006622  # Dark green (tree)
palette[7] = 0x008833  # Medium green
palette[8] = 0x00AA44  # Light green
palette[9] = 0x553311  # Brown trunk
palette[10] = 0xFFFF00  # Bright yellow
palette[11] = 0xFFEE88  # Moon glow
palette[12] = 0xFF0000  # Bright red
palette[13] = 0xFF6600  # Bright orange
palette[14] = 0x0A3010  # Dark green ground
palette[15] = 0xDD00FF  # Bright purple (for presents)

# Main bitmap
bmp = displayio.Bitmap(64, 64, 16)
grid = displayio.TileGrid(bmp, pixel_shader=palette)
main_group.append(grid)

# Ground level
GROUND_Y = 54


# Draw static background once
def init_background():
    # Sky - solid dark blue
    for y in range(GROUND_Y):
        for x in range(64):
            bmp[x, y] = 0

    # Ground - dark green with white snow speckles
    for y in range(GROUND_Y, 64):
        for x in range(64):
            # Random white speckles for snow on grass
            if random.random() < 0.15:
                bmp[x, y] = 2  # White snow
            else:
                bmp[x, y] = 14  # Dark green

    # Crescent moon
    mx, my = 54, 8
    for dy in range(-5, 6):
        for dx in range(-5, 6):
            d1 = math.sqrt(dx * dx + dy * dy)  # Main moon circle
            d2 = math.sqrt((dx + 3) ** 2 + dy * dy)  # Offset circle to cut out
            if d1 < 5 and d2 > 4:
                if d1 < 4:
                    bmp[mx + dx, my + dy] = 10  # Bright yellow
                else:
                    bmp[mx + dx, my + dy] = 11  # Glow


# Draw a tree - wide at bottom, narrow at top
def draw_tree(tx, size, colors):
    # Trunk
    trunk_h = size // 4
    trunk_w = 1 if size < 12 else 2
    for y in range(GROUND_Y - trunk_h, GROUND_Y):
        for dx in range(trunk_w):
            if 0 <= tx + dx < 64:
                bmp[tx + dx, y] = 9

    # Foliage - triangle shape (wide at bottom, narrow at top)
    layers = size // 3
    tree_top = GROUND_Y - trunk_h - 1

    for layer in range(layers):
        # Bottom layers are widest, top layers are narrowest
        width = layers - layer  # Decreases as we go up
        if size > 12:
            width += 1

        y_pos = tree_top - layer * 2

        for dy in range(2):
            for dx in range(-width, width + 1):
                px = tx + dx
                py = y_pos - dy
                if 0 <= px < 64 and 0 <= py < 64:
                    shade = colors[(abs(dx) + dy + layer) % len(colors)]
                    bmp[px, py] = shade

    # Star on top
    star_y = tree_top - layers * 2
    if 0 <= star_y < 64:
        bmp[tx, star_y] = 10


init_background()

# Draw trees at various positions
trees = [
    (8, 15, [6, 7, 8]),
    (20, 10, [6, 7]),
    (32, 18, [6, 7, 8, 7]),
    (45, 12, [6, 7, 8]),
    (56, 9, [6, 7]),
]

for tx, size, colors in trees:
    draw_tree(tx, size, colors)

# Store background for quick restore
bg_data = []
for y in range(64):
    row = []
    for x in range(64):
        row.append(bmp[x, y])
    bg_data.append(row)

# Santa on sleigh - snowman shape (big body, small head)
SANTA_W, SANTA_H = 14, 11
santa_pixels = []

# 9=brown (sleigh), c=12 (red), 2=white, a=10 (gold)
santa_art = [
    "00000002200000",
    "0000002cc20000",
    "0000002cc20000",
    "00000022220000",
    "0000cccccccc00",
    "000cccccccccc0",
    "000cccccccccc0",
    "0000cccccccc00",
    "09999999999990",
    "99999999999999",
    "09000000000090",
]

char_map = {"0": 0, "2": 2, "9": 9, "a": 10, "c": 12}

# Parse santa art into pixel list [(dx, dy, color), ...]
for y, row in enumerate(santa_art):
    for x, ch in enumerate(row):
        if ch != "0":  # Skip transparent
            santa_pixels.append((x, y, char_map[ch]))

# Santa state
santa_x = -30.0
santa_y = 15
santa_active = False
santa_cooldown = 250  # Frames between appearances
santa_prev_positions = []  # Track positions to clear

# Present colors: pink, red, yellow, orange, purple
# 1=pink, 12=red, 10=yellow, 13=orange, 15=purple
present_palette_colors = [1, 12, 10, 13, 15]


# Presents that Santa drops
class Present:
    def __init__(self):
        self.active = False
        self.x = 0
        self.y = 0
        self.prev_y = 0
        self.vy = 0
        self.color = 12
        self.lifetime = 0
        self.on_ground = False

    def drop(self, x, y):
        self.x = int(x)
        self.y = y
        self.prev_y = y
        self.vy = random.uniform(1.0, 2.0)
        self.color = random.choice(present_palette_colors)
        self.lifetime = random.randint(150, 450)  # 5-15 seconds at 30fps
        self.land_y = GROUND_Y + random.randint(0, 5)  # Land within the green ground
        self.active = True
        self.on_ground = False

    def update(self):
        if not self.active:
            return

        if not self.on_ground:
            # Clear previous position before moving
            self.clear_at(int(self.prev_y))
            self.prev_y = self.y
            self.y += self.vy
            if self.y >= self.land_y:
                self.y = self.land_y
                self.on_ground = True
        else:
            self.lifetime -= 1
            if self.lifetime <= 0:
                self.clear_at(int(self.y))
                self.active = False

    def draw(self):
        if not self.active:
            return
        iy = int(self.y)
        for dy in range(4):
            for dx in range(4):
                px, py = self.x + dx, iy + dy
                if 0 <= px < 64 and 0 <= py < 64:
                    bmp[px, py] = self.color

    def clear_at(self, y_pos):
        for dy in range(4):
            for dx in range(4):
                px, py = self.x + dx, y_pos + dy
                if 0 <= px < 64 and 0 <= py < 64:
                    bmp[px, py] = bg_data[py][px]

    def clear(self):
        self.clear_at(int(self.y))


presents = [Present() for _ in range(10)]
present_drop_timer = 0


# Snowflake class with melting
class Snowflake:
    def __init__(self):
        self.reset(start_random=True)

    def reset(self, start_random=False):
        self.x = random.uniform(0, 63)
        self.y = random.uniform(-20, 0) if not start_random else random.uniform(-20, 50)
        self.vy = random.uniform(0.4, 0.9)
        self.vx = 0
        self.landed = False
        self.melt_timer = 0
        self.brightness = 2
        self.needs_redraw = True
        self.prev_x = -1
        self.prev_y = -1

    def update(self, wind):
        if self.landed:
            # Melting phase - only update occasionally
            self.melt_timer += 1
            if self.melt_timer > 15:
                self.melt_timer = 0
                self.brightness += 1
                self.needs_redraw = True
                if self.brightness > 5:
                    # Clear and reset
                    self.clear()
                    self.reset()
        else:
            # Falling phase - always needs redraw
            self.needs_redraw = True

            # Store previous position for clearing
            self.prev_x = int(self.x) % 64
            self.prev_y = int(self.y)

            self.vx = self.vx * 0.9 + wind * 0.1
            self.x += self.vx
            self.y += self.vy

            # Wrap horizontally
            if self.x < 0:
                self.x += 64
            elif self.x >= 64:
                self.x -= 64

            # Check if landed
            ix, iy = int(self.x), int(self.y)
            if iy >= GROUND_Y - 1:
                self.landed = True
                self.y = GROUND_Y - 1
            elif 0 <= ix < 64 and 0 <= iy < 64:
                bg_color = bg_data[iy][ix]
                if bg_color in [6, 7, 8, 9]:
                    self.landed = True

    def draw(self):
        if not self.needs_redraw:
            return
        ix, iy = int(self.x) % 64, int(self.y)
        if 0 <= iy < 64 and 0 <= ix < 64:
            bmp[ix, iy] = self.brightness
        if self.landed:
            self.needs_redraw = False

    def clear_previous(self):
        # Only clear if we were falling (not landed)
        if not self.landed and self.prev_y >= 0:
            if 0 <= self.prev_y < 64 and 0 <= self.prev_x < 64:
                bmp[self.prev_x, self.prev_y] = bg_data[self.prev_y][self.prev_x]

    def clear(self):
        ix, iy = int(self.x) % 64, int(self.y)
        if 0 <= iy < 64 and 0 <= ix < 64:
            bmp[ix, iy] = bg_data[iy][ix]


snowflakes = [Snowflake() for _ in range(60)]

# Stars
stars = [(random.randint(0, 50), random.randint(0, 25)) for _ in range(12)]

# Animation
frame = 0
wind = 0
wind_target = 0

while True:
    # Update wind
    if frame % 120 == 0:
        wind_target = random.uniform(-0.8, 0.8)
    wind = wind * 0.98 + wind_target * 0.02

    # Clear previous positions of falling snow only
    for s in snowflakes:
        s.clear_previous()

    # Clear previous Santa positions
    for px, py in santa_prev_positions:
        if 0 <= px < 64 and 0 <= py < 64:
            bmp[px, py] = bg_data[py][px]
    santa_prev_positions.clear()

    # Update Santa
    if santa_active:
        santa_x += 0.7
        # Gentle bob
        santa_y = 12 + int(1.5 * math.sin(frame * 0.12))

        # Draw Santa
        for dx, dy, color in santa_pixels:
            px = int(santa_x) + dx
            py = santa_y + dy
            if 0 <= px < 64 and 0 <= py < 64:
                # Don't draw over trees
                if bg_data[py][px] not in [6, 7, 8, 9]:
                    bmp[px, py] = color
                    santa_prev_positions.append((px, py))

        # Drop presents periodically
        present_drop_timer += 1
        if present_drop_timer > 25 and 0 < santa_x < 55:
            present_drop_timer = 0
            for p in presents:
                if not p.active:
                    p.drop(santa_x + 8, santa_y + SANTA_H)
                    break

        # Check if Santa has left the screen
        if santa_x > 75:
            santa_active = False
            santa_cooldown = random.randint(200, 400)
    else:
        # Countdown to next appearance
        santa_cooldown -= 1
        if santa_cooldown <= 0:
            santa_active = True
            santa_x = -SANTA_W
            santa_y = random.randint(8, 18)

    # Update and draw presents
    for p in presents:
        p.update()
        if p.active:
            p.draw()

    # Twinkle stars
    for sx, sy in stars:
        if bg_data[sy][sx] == 0:
            if random.random() > 0.7:
                bmp[sx, sy] = 10 if random.random() > 0.5 else 11
            else:
                bmp[sx, sy] = 0

    # Update and draw snow
    for s in snowflakes:
        s.update(wind)
        s.draw()

    frame += 1
    time.sleep(0.03)
