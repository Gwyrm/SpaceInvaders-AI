"""Montage final — « Space Invaders : voir l'intérieur du modèle ».

Assemble : le VRAI agent + son réseau, calés sur les beats de la voix off ; le jeu
progresse (lent d'abord, puis accéléré) jusqu'à l'INVASION à haute vitesse (le
climax) ; captions burnées (audio-sync) ; musique duckée + whoosh ; export TikTok
+ YouTube Shorts. Look verrouillé (arcade CRT × instrument).
"""
import os, math
os.environ["SDL_VIDEODRIVER"] = "dummy"
import sys
sys.path.insert(0, "/Users/pierre/Projets/tiktok-ia-playbook")
sys.path.insert(0, "/Users/pierre/Projets/SpaceInvaders-AI")
import numpy as np
import pygame
pygame.init(); pygame.font.init()
from studio import theme, scene, motion, overlays, captions, music
from studio.overlays import blurred
from studio.montage import Montage
from studio.export import TIKTOK, YOUTUBE_SHORTS
import env as E
from agent import MLP
from voiceover_tts import SEGMENTS

FPS = 30
VOICE = "/Users/pierre/Projets/SpaceInvaders-AI/runs/voice"
OUT = "/Users/pierre/Projets/tiktok-ia-playbook/runs"

def mono(sz):
    p = pygame.font.match_font("menlo,monaco,couriernew,dejavusansmono")
    return pygame.font.Font(p, sz) if p else pygame.font.Font(None, sz)
f_hud, f_out, f_lbl, f_pct, f_cap = mono(40), mono(44), mono(20), mono(30), mono(37)
f_go = mono(92)

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

seam = pygame.Surface((1080, 4), pygame.SRCALPHA)
_xs = np.linspace(-1, 1, 1080); _al = (np.clip(1 - (_xs / 0.9) ** 2, 0, 1) * 150).astype(np.uint8)
pygame.surfarray.pixels3d(seam)[:] = np.array(CYAN)[None, None, :]
pygame.surfarray.pixels_alpha(seam)[:] = _al[:, None]
seam_glow = blurred(pygame.transform.smoothscale(seam, (1080, 16)), 4)

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

def caption(surf, text, cy=988):
    if not text: return
    fnt = f_cap; maxw = 1080 - 96
    words = text.split(); lines, cur = [], ""            # retour à la ligne (≤ 2 lignes)
    for w in words:
        cand = (cur + " " + w).strip()
        if not cur or fnt.size(cand)[0] <= maxw:
            cur = cand
        else:
            lines.append(cur); cur = w
    if cur: lines.append(cur)
    lines = lines[:2]
    rends = [fnt.render(l, True, (238, 244, 250)) for l in lines]
    lh = rends[0].get_height() + 3
    bh = lh * len(rends) + 12
    bw = max(r.get_width() for r in rends) + 40
    by = int(cy - bh / 2)
    pill = pygame.Surface((bw, bh), pygame.SRCALPHA)
    overlays.round_rect(pill, (0, 0, bw, bh), (6, 9, 14, 205), radius=12)
    surf.blit(pill, (540 - bw // 2, by))
    y = by + 6
    for r in rends:
        surf.blit(r, (540 - r.get_width() // 2, y)); y += lh

def draw_frame(surf, env, net, cap_text, dead=False):
    feats = env.features(); acts = net.layer_acts(feats); choice = int(np.argmax(acts[-1]))
    scene.backdrop(surf)
    overlays.round_rect(surf, (GX, GY, GW, GH), (9, 12, 18), radius=24)
    pygame.draw.rect(surf, (24, 30, 42), (GX, GY, GW, GH), width=2, border_radius=24)
    glow = pygame.Surface((1080, 1920), pygame.SRCALPHA)
    cx_env, cy_env = env._cols_x(), env._rows_y()
    for r, c in zip(*np.where(env.alive)):
        bmp, col = ROW_SPR[r]
        draw_sprite(glow, bmp, mx(cx_env[c]), my(cy_env[r]), 6, col)
    if env.laser is not None:
        pygame.draw.rect(glow, (225, 248, 255), (int(mx(env.laser[0])) - 4, int(my(env.laser[1])), 8, 34))
    for b in env.bombs:
        bx, by = mx(b[0]), my(b[1])
        pygame.draw.lines(glow, theme.RED, False, [(bx, by), (bx - 10, by + 22), (bx + 10, by + 44), (bx, by + 66)], 5)
    surf.blit(blurred(glow, 8), (0, 0), special_flags=pygame.BLEND_RGB_ADD)
    surf.blit(glow, (0, 0))
    cw, ch = int(E.CELL * SX) + 1, int(E.CELL * SY) + 1
    for i, cells in enumerate(env.bunkers):
        x0 = env.shield_x[i] - cells.shape[1] * E.CELL / 2.0
        for r in range(cells.shape[0]):
            for c in range(cells.shape[1]):
                if cells[r, c]:
                    pygame.draw.rect(surf, (74, 182, 112),
                                     (int(mx(x0 + c * E.CELL)), int(my(env.shield_ytop + r * E.CELL)), cw, ch))
    ccx, ccy = mx(env.cannon_x), my(E.CANNON_Y)
    pygame.draw.rect(surf, CYAN, (int(ccx) - 42, int(ccy), 84, 24), border_radius=6)
    pygame.draw.rect(surf, CYAN, (int(ccx) - 12, int(ccy) - 20, 24, 22), border_radius=4)
    pygame.draw.rect(surf, (210, 244, 255), (int(ccx) - 4, int(ccy) - 28, 8, 12))
    pygame.draw.line(surf, (70, 165, 108), (GX + 40, GY + GH - 30), (GX + GW - 40, GY + GH - 30), 3)
    scene.crt(surf, (GX, GY, GW, GH), gap=3, line_alpha=48, vignette=110, radius=24)
    glow_text(surf, f_hud, f"SCORE {int(env.score):05d}", theme.GREEN, GX + 44, GY + 30)
    for i in range(max(0, env.lives)):
        lx = GX + GW - 56 - i * 46
        pygame.draw.polygon(surf, CYAN, [(lx - 16, GY + 54), (lx + 16, GY + 54), (lx, GY + 34)])
    surf.blit(seam_glow, (0, SEAM_Y - 6), special_flags=pygame.BLEND_RGB_ADD)
    surf.blit(seam, (0, SEAM_Y))
    motion.neural_net(surf, [10, 9, 9, 4], acts, net.W, box=(90, 1090, 900, 640),
                      in_labels=["cible G", "cible D", "bloqué", "bombe G", "bombe D", "canon", "abri", "menace", "vies", "vitesse"],
                      out_labels=["GAUCHE", "DROITE", "TIR", "RIEN"], choice=choice,
                      label_font=f_lbl, out_font=f_out, pct_font=f_pct,
                      focus=theme.GOLD, focus_p=0.5 + 0.32 * math.sin(env.steps / 5))
    if dead:                                              # défaite lisible
        veil = pygame.Surface((GW, GH), pygame.SRCALPHA); veil.fill((6, 8, 12, 150))
        surf.blit(veil, (GX, GY))
        go = f_go.render("GAME OVER", True, (252, 98, 85))
        glow_text(surf, f_go, "GAME OVER", (252, 98, 85),
                  GX + GW // 2 - go.get_width() // 2, GY + GH // 2 - 46)
    caption(surf, cap_text)

# ---------------------------------------------------------------- montage
def main():
    order = [n for n, _ in SEGMENTS]
    m = Montage(voice_dir=VOICE, fps=FPS)
    seg_frames = {n: m.seg(n) for n in order}
    total_frames = sum(seg_frames.values())
    net = MLP.load("/Users/pierre/Projets/SpaceInvaders-AI/best.npz")

    SEED = 13                                             # vague 5 puis INVASION à vitesse max (endgame skillé)
    probe = E.SpaceInvaders(max_steps=100000); probe.reset(seed=SEED)
    n_steps = 0
    while not probe.done:
        probe.step(net.act(probe.features())); n_steps += 1

    # captions par beat (audio-sync approx via by_words)
    cap_sched = {}
    import re
    for n, txt in SEGMENTS:
        sents = [s.strip() for s in re.split(r"(?<=[.!?])\s+", txt) if s.strip()]
        cap_sched[n] = captions.by_words(sents, seg_frames[n] / FPS)

    # TEMPS RÉEL : 1 pas de jeu par frame → seuls les ALIENS accélèrent à l'écran
    # (laser et bombes gardent leur vitesse constante). Rendu = état + décision, puis pas.
    # ENDGAME : elle survit longtemps → on montre les ~total_frames DERNIERS pas (finit sur la mort)
    start = max(0, n_steps - total_frames)
    env = E.SpaceInvaders(max_steps=200000); env.reset(seed=SEED)
    for _ in range(start):                                # avance rapide (silencieux) jusqu'au endgame
        if not env.done:
            env.step(net.act(env.features()))
    for n in order:
        for f in range(seg_frames[n]):
            cap = captions.current(cap_sched[n], f / FPS)
            draw_frame(m.surf, env, net, cap, dead=env.done)
            m.save(m.surf, shake=6 if (env.done or env.cur_speed() > 0.85) else 0)
            if not env.done:
                env.step(net.act(env.features()))

    audio = m.assemble_audio(order, music_make=music.make, music_gain=2.3,
                             sfx=[(0.12, "whoosh")])
    meta = dict(
        title="Space Invaders : le jeu truqué qu'une IA ne peut pas gagner",
        hook="Ce jeu est truqué pour que tu perdes 👀 elle joue, ou elle calcule ? 👇",
        description="Une IA joue à Space Invaders — un jeu conçu pour être imbattable. "
                    "On voit son réseau de neurones décider en direct. #shorts #ia #ai",
        hashtags=["ia", "intelligenceartificielle", "spaceinvaders", "ai", "jeuvideo", "neurones"],
    )
    m.export([TIKTOK, YOUTUBE_SHORTS], audio, OUT, name="space_invaders", metadata=meta)
    print(f"partie={n_steps} pas · vidéo={total_frames} frames (temps réel)")
    m.close()

if __name__ == "__main__":
    main()
