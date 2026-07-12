"""Rendu du VRAI agent entraîné jouant à Space Invaders + son réseau réel qui
s'allume (activations authentiques via MLP.layer_acts). Look studio (arcade CRT ×
instrument). Sortie : tiktok-ia-playbook/runs/agent_real.mp4.
"""
import os, math, tempfile, subprocess, shutil
os.environ["SDL_VIDEODRIVER"] = "dummy"
import sys
sys.path.insert(0, "/Users/pierre/Projets/tiktok-ia-playbook")
sys.path.insert(0, "/Users/pierre/Projets/SpaceInvaders-AI")
import numpy as np
import pygame
pygame.init(); pygame.font.init()
from studio import theme, scene, motion, overlays
from studio.overlays import blurred
import env as E
from agent import MLP

W, H = 1080, 1920
FPS, SECS = 30, 8.0

def mono(sz):
    p = pygame.font.match_font("menlo,monaco,couriernew,dejavusansmono")
    return pygame.font.Font(p, sz) if p else pygame.font.Font(None, sz)
f_hud, f_out, f_lbl, f_pct = mono(40), mono(44), mono(20), mono(30)

LIME, TEAL, MAG, AMB = (163, 230, 53), (92, 208, 179), (232, 121, 201), (240, 172, 95)
CYAN = theme.BLUE
SQUID = ["...XX...", "..XXXX..", ".XXXXXX.", "XX.XX.XX", "XXXXXXXX", "..X..X..", ".X.XX.X.", "X.X..X.X"]
CRAB = ["..X.....X..", "...X...X...", "..XXXXXXX..", ".XX.XXX.XX.", "XXXXXXXXXXX", "X.XXXXXXX.X", "X.X.....X.X", "...XX.XX..."]
OCTO = ["....XXXX....", ".XXXXXXXXXX.", "XXXXXXXXXXXX", "XXX..XX..XXX", "XXXXXXXXXXXX", "...XX..XX...", "..XX.XX.XX..", ".XX..XX..XX."]
ROW_SPR = [(SQUID, LIME), (CRAB, TEAL), (CRAB, MAG), (OCTO, AMB)]

GX, GY, GW, GH = 40, 54, 1000, 880
SX, SY = GW / E.W, GH / E.H
SEAM_Y = GY + GH + 26
def mx(ex): return GX + ex * SX
def my(ey): return GY + ey * SY

def draw_sprite(dst, bmp, cx, cy, px, color):
    w, h = len(bmp[0]) * px, len(bmp) * px
    x0, y0 = int(cx - w / 2), int(cy - h / 2)
    for r, row in enumerate(bmp):
        for c, ch in enumerate(row):
            if ch == "X":
                pygame.draw.rect(dst, color, (x0 + c * px, y0 + r * px, px, px))

def glow_text(surf, font, txt, color, x, y, blur=3):
    t = font.render(txt, True, color); pad = blur * 4
    s = pygame.Surface((t.get_width() + 2 * pad, t.get_height() + 2 * pad), pygame.SRCALPHA)
    s.blit(t, (pad, pad)); s = blurred(s, blur)
    s.fill((110, 110, 110, 255), special_flags=pygame.BLEND_RGB_MULT)
    surf.blit(s, (x - pad, y - pad), special_flags=pygame.BLEND_RGB_ADD)
    surf.blit(t, (x, y))

seam = pygame.Surface((W, 4), pygame.SRCALPHA)
xs = np.linspace(-1, 1, W); al = (np.clip(1 - (xs / 0.9) ** 2, 0, 1) * 150).astype(np.uint8)
pygame.surfarray.pixels3d(seam)[:] = np.array(CYAN)[None, None, :]
pygame.surfarray.pixels_alpha(seam)[:] = al[:, None]
seam_glow = blurred(pygame.transform.smoothscale(seam, (W, 16)), 4)

OUT = ["GAUCHE", "DROITE", "TIR", "RIEN"]
env = E.SpaceInvaders(max_steps=100000)
net = MLP.load("/Users/pierre/Projets/SpaceInvaders-AI/best.npz")
env.reset(seed=7)

tmp = tempfile.mkdtemp(prefix="agent_"); N = int(FPS * SECS)
for f in range(N):
    feats = env.features()
    acts = net.layer_acts(feats)
    choice = int(np.argmax(acts[-1]))

    surf = pygame.Surface((W, H)); scene.backdrop(surf)
    overlays.round_rect(surf, (GX, GY, GW, GH), (9, 12, 18), radius=24)
    pygame.draw.rect(surf, (24, 30, 42), (GX, GY, GW, GH), width=2, border_radius=24)

    glow = pygame.Surface((W, H), pygame.SRCALPHA)
    cx_env = env._cols_x(); cy_env = env._rows_y()
    rr, cc = np.where(env.alive)
    for r, c in zip(rr, cc):
        bmp, col = ROW_SPR[r]
        draw_sprite(glow, bmp, mx(cx_env[c]), my(cy_env[r]), 6, col)
    if env.laser is not None:
        pygame.draw.rect(glow, (225, 248, 255), (int(mx(env.laser[0])) - 4, int(my(env.laser[1])), 8, 34))
    for b in env.bombs:
        bx, by = mx(b[0]), my(b[1])
        pygame.draw.lines(glow, theme.RED, False,
                          [(bx, by), (bx - 10, by + 22), (bx + 10, by + 44), (bx, by + 66)], 5)
    surf.blit(blurred(glow, 8), (0, 0), special_flags=pygame.BLEND_RGB_ADD)
    surf.blit(glow, (0, 0))

    # bunkers destructibles (cellules)
    cw, ch = int(E.CELL * SX) + 1, int(E.CELL * SY) + 1
    for i, cells in enumerate(env.bunkers):
        x0 = env.shield_x[i] - cells.shape[1] * E.CELL / 2.0
        for r in range(cells.shape[0]):
            for c in range(cells.shape[1]):
                if cells[r, c]:
                    pygame.draw.rect(surf, (74, 182, 112),
                                     (int(mx(x0 + c * E.CELL)), int(my(env.shield_ytop + r * E.CELL)), cw, ch))
    # canon
    ccx, ccy = mx(env.cannon_x), my(E.CANNON_Y)
    pygame.draw.rect(surf, CYAN, (int(ccx) - 42, int(ccy), 84, 24), border_radius=6)
    pygame.draw.rect(surf, CYAN, (int(ccx) - 12, int(ccy) - 20, 24, 22), border_radius=4)
    pygame.draw.rect(surf, (210, 244, 255), (int(ccx) - 4, int(ccy) - 28, 8, 12))
    pygame.draw.line(surf, (70, 165, 108), (GX + 40, GY + GH - 30), (GX + GW - 40, GY + GH - 30), 3)

    scene.crt(surf, (GX, GY, GW, GH), gap=3, line_alpha=48, vignette=110, radius=24)
    glow_text(surf, f_hud, f"SCORE {int(env.score):05d}", theme.GREEN, GX + 44, GY + 30)
    for i in range(env.lives):
        lx = GX + GW - 56 - i * 46
        pygame.draw.polygon(surf, CYAN, [(lx - 16, GY + 54), (lx + 16, GY + 54), (lx, GY + 34)])

    surf.blit(seam_glow, (0, SEAM_Y - 6), special_flags=pygame.BLEND_RGB_ADD)
    surf.blit(seam, (0, SEAM_Y))

    motion.neural_net(surf, [10, 9, 9, 4], acts, net.W, box=(90, 1080, 900, 640),
                      in_labels=["cible G", "cible D", "bloqué", "bombe G", "bombe D", "canon", "abri", "menace", "vies", "vitesse"],
                      out_labels=OUT, choice=choice, label_font=f_lbl, out_font=f_out,
                      pct_font=f_pct, focus=theme.GOLD, focus_p=0.5 + 0.32 * math.sin(f / 5))

    pygame.image.save(surf, f"{tmp}/f{f:04d}.png")
    env.step(choice)
    if env.done:
        env.reset(seed=7 + f)

out = "/Users/pierre/Projets/SpaceInvaders-AI/runs/agent_real.mp4"
subprocess.run(["ffmpeg", "-y", "-framerate", str(FPS), "-i", f"{tmp}/f%04d.png",
                "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", out],
               check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
shutil.copy(f"{tmp}/f0120.png", "/Users/pierre/Projets/SpaceInvaders-AI/runs/agent_real_frame.png")
print("SAVED", out)
