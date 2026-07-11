"""SpaceInvaders — jeu headless (numpy) pour entraîner/visualiser un petit agent.

Features interprétables (7) + mécanique d'ACCÉLÉRATION : la formation va plus vite
quand il reste moins d'aliens (move_interval ∝ alive/total). Actions : 0 GAUCHE,
1 DROITE, 2 TIR, 3 RIEN. Déterministe pour un seed donné.
"""
import numpy as np

ROWS, COLS = 4, 8
N_ALIENS = ROWS * COLS
W, H = 1000.0, 800.0
DX, DY = 70.0, 58.0
STEP_X, STEP_Y = 14.0, 26.0
BASE_INT = 18
CANNON_Y = H - 40.0
CANNON_SPD = 13.0
LASER_SPD = 40.0
BOMB_SPD = 9.0
BOMB_INT = 44                    # bombes moins fréquentes → esquivables (jeu jouable)
MARGIN = 60.0
POINTS = [40, 30, 20, 10]        # points par rangée (haut → bas)

# Bunker destructible (forme arche classique) : chaque "X" = une cellule.
BUNKER = ["..XXXX..", ".XXXXXX.", "XXXXXXXX", "XXXXXXXX", "XXX..XXX", "XX....XX"]
CELL = 12.0


class SpaceInvaders:
    def __init__(self, max_steps=1500):
        self.max_steps = max_steps
        self.reset()

    def reset(self, seed=None):
        self.rng = np.random.default_rng(seed)
        self.alive = np.ones((ROWS, COLS), dtype=bool)
        self.fx, self.fy = 150.0, 100.0        # centre de l'alien (row0,col0)
        self.dir = 1
        self.move_t = 0
        self.cannon_x = W / 2
        self.laser = None                       # [x, y] ou None
        self.bombs = []                         # liste de [x, y]
        self.bomb_t = 0
        self.shield_x = np.array([W * 0.26, W * 0.5, W * 0.74])
        self.shield_ytop = H - 210.0
        self.bunkers = [np.array([[ch == "X" for ch in row] for row in BUNKER]) for _ in range(3)]
        self._cells0 = sum(int(b.sum()) for b in self.bunkers)
        self.lives = 3
        self.wave = 0
        self.score = 0.0
        self.steps = 0
        self.prev_dist = None
        self.done = False
        return self.features()

    # ---------------- géométrie ----------------
    def _cols_x(self):
        return self.fx + np.arange(COLS) * DX
    def _rows_y(self):
        return self.fy + np.arange(ROWS) * DY

    def alive_centers(self):
        cx, cy = self._cols_x(), self._rows_y()
        rr, cc = np.where(self.alive)
        return cx[cc], cy[rr], rr, cc

    def move_interval(self):
        base = BASE_INT / (1.0 + 0.12 * self.wave)          # + rapide à chaque vague
        return max(1, int(round(base * int(self.alive.sum()) / N_ALIENS)))

    def cur_speed(self):
        return float(np.clip(1.0 - self.move_interval() / BASE_INT, 0, 1))

    # ---------------- observation ----------------
    def features(self):
        axs, ays, rr, cc = self.alive_centers()
        if len(axs):                                        # cible = alien le + proche à TIR DÉGAGÉ
            clear = [x for x in axs if not self._shot_blocked_at(x)]
            pool = np.asarray(clear) if clear else axs
            target = float(pool[int(np.argmin(np.abs(pool - self.cannon_x)))])
            off = (target - self.cannon_x) / W
            menace = float(np.clip((ays.max() - 274.0) / 446.0, 0, 1))   # 0=aliens en haut, 1=invasion
        else:
            off, menace = 0.0, 0.0
        cg = float(np.clip(-off * 3.0, 0, 1))               # cible à gauche
        cd = float(np.clip(off * 3.0, 0, 1))                # cible à droite
        bloque = 1.0 if self._shot_blocked_at(self.cannon_x) else 0.0   # mon tir touche un bunker ?
        bg = bd = 0.0                                       # TIRS ENNEMIS : menace imminente à G / à D
        for b in self.bombs:
            dx = b[0] - self.cannon_x
            if abs(dx) < 75:                                # dans le couloir du canon
                imm = float(np.clip(b[1] / CANNON_Y, 0, 1))   # bombe basse = imminente
                if dx <= 0: bg = max(bg, imm)
                if dx >= 0: bd = max(bd, imm)
        return np.array([cg, cd, bloque, bg, bd, self.cannon_x / W,
                         sum(int(b.sum()) for b in self.bunkers) / self._cells0,
                         menace, self.lives / 3.0, self.cur_speed()], dtype=np.float64)

    # ---------------- dynamique ----------------
    def _shot_blocked_at(self, x):
        """Un tir vertical en x heurterait-il une cellule de bunker intacte ?"""
        for i, cells in enumerate(self.bunkers):
            x0 = self.shield_x[i] - cells.shape[1] * CELL / 2.0
            col = int((x - x0) // CELL)
            if 0 <= col < cells.shape[1] and cells[:, col].any():
                return True
        return False

    def _hit_bunker(self, x, y, blast=0):
        """Collision projectile/bunker : creuse la (les) cellule(s) touchée(s).
        Renvoie True si un bunker est touché → le projectile est stoppé."""
        for i, cells in enumerate(self.bunkers):
            x0 = self.shield_x[i] - cells.shape[1] * CELL / 2.0
            col = int((x - x0) // CELL)
            row = int((y - self.shield_ytop) // CELL)
            if 0 <= row < cells.shape[0] and 0 <= col < cells.shape[1] and cells[row, col]:
                for dr in range(-blast, blast + 1):
                    for dc in range(-blast, blast + 1):
                        r, c = row + dr, col + dc
                        if 0 <= r < cells.shape[0] and 0 <= c < cells.shape[1]:
                            cells[r, c] = False
                return True
        return False

    def step(self, action):
        if self.done:
            return self.features(), 0.0, True, {"score": self.score}
        self.steps += 1
        reward = 0.02                                   # bonus de survie

        # canon
        if action == 0: self.cannon_x -= CANNON_SPD
        elif action == 1: self.cannon_x += CANNON_SPD
        self.cannon_x = float(np.clip(self.cannon_x, 40, W - 40))

        # récompense de VISÉE : se rapprocher de l'alien vivant le plus proche
        axs0, _, _, _ = self.alive_centers()
        if len(axs0):
            d = float(np.min(np.abs(axs0 - self.cannon_x)))
            if self.prev_dist is not None:
                reward += 0.03 * (self.prev_dist - d) / DX
            self.prev_dist = d

        if action == 2 and self.laser is None:
            self.laser = [self.cannon_x, CANNON_Y - 24]
        elif action == 2:
            reward -= 0.08                              # tir gaspillé (laser déjà en vol)

        # laser — collision CONTINUE le long du trajet (pas de tunneling)
        if self.laser is not None:
            lx = self.laser[0]
            y_from = self.laser[1]
            y_to = y_from - LASER_SPD
            self.laser[1] = y_to
            axs, ays, rr, cc = self.alive_centers()
            yy = y_from
            while yy >= y_to:
                if yy < 0:
                    self.laser = None; break
                if self._hit_bunker(lx, yy):             # 1ʳᵉ cellule intacte → stoppé + creusée
                    self.laser = None; reward -= 1.5; break   # tir gaspillé sur son propre bunker
                if len(axs):
                    hit = (np.abs(axs - lx) < 20) & (np.abs(ays - yy) < 20)
                    if hit.any():
                        idx = np.where(hit)[0]
                        j = int(idx[np.argmax(ays[idx])])
                        self.alive[int(rr[j]), int(cc[j])] = False
                        self.score += POINTS[int(rr[j])]; reward += POINTS[int(rr[j])]
                        self.laser = None; break
                yy -= 8.0

        # formation
        self.move_t += 1
        if self.move_t >= self.move_interval():
            self.move_t = 0
            axs, ays, rr, cc = self.alive_centers()
            if len(axs):
                if axs.min() + self.dir * STEP_X < MARGIN or axs.max() + self.dir * STEP_X > W - MARGIN:
                    self.fy += STEP_Y; self.dir *= -1
                else:
                    self.fx += self.dir * STEP_X

        axs, ays, rr, cc = self.alive_centers()
        if len(ays) and ays.max() >= CANNON_Y - 40:      # invasion
            self.done = True
            return self.features(), reward - 50, True, {"score": self.score}

        # bombes
        self.bomb_t += 1
        if self.bomb_t >= BOMB_INT and len(axs):
            self.bomb_t = 0
            c = int(self.rng.choice(np.unique(cc)))
            m = cc == c
            j = np.where(m)[0][np.argmax(ays[m])]
            self.bombs.append([float(axs[j]), float(ays[j]) + 10])
        nb = []
        for b in self.bombs:
            b[1] += BOMB_SPD
            if b[1] > H:
                continue
            if self._hit_bunker(b[0], b[1], blast=0):     # bombe grignote 1 cellule → bunkers durables
                continue
            if abs(b[0] - self.cannon_x) < 42 and b[1] > CANNON_Y - 30:   # hitbox = largeur du canon
                self.lives -= 1; reward -= 20
                if self.lives <= 0:
                    self.done = True
                continue
            nb.append(b)
        self.bombs = nb

        if self.alive.sum() == 0:                         # vague nettoyée → suivante, + rapide
            self.wave += 1
            self.score += 100; reward += 100
            self.alive[:] = True
            self.fx, self.fy, self.dir, self.move_t = 150.0, 100.0, 1, 0
            self.bombs = []
            # les bunkers restent creusés d'une vague à l'autre (réaliste, + dur)
        if self.steps >= self.max_steps:
            self.done = True
        return self.features(), reward, self.done, {"score": self.score, "wave": self.wave}
