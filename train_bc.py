"""Behavior cloning : entraîne le MLP [7,9,9,4] à IMITER une bonne stratégie
scriptée (traquer la colonne la plus proche, tirer aligné, esquiver, pré-viser).

Donne un agent qui BOUGE et vise pour de vrai (viz dynamique), réseau aux
activations authentiques. Rétro-propagation numpy + pondération des classes.
"""
import numpy as np

from env import SpaceInvaders, CANNON_Y
from agent import MLP

HERE = "/Users/pierre/Projets/SpaceInvaders-AI"


def expert(env):
    """Stratégie maligne : viser l'alien le + proche à TIR DÉGAGÉ (préserve les
    bunkers) ; s'abriter derrière un bunker quand une bombe menace, sinon esquiver."""
    axs, ays, rr, cc = env.alive_centers()
    if len(axs) == 0:
        return 3
    # esquive ANTICIPÉE : fuir la bombe la + imminente (la + basse) si non abritée
    threats = [b for b in env.bombs
               if abs(b[0] - env.cannon_x) < 52 and b[1] > CANNON_Y - 340
               and not env._shot_blocked_at(env.cannon_x)]
    if threats:
        b = max(threats, key=lambda b: b[1])
        return 1 if b[0] < env.cannon_x else 0
    clear = [x for x in axs if not env._shot_blocked_at(x)]
    pool = clear if clear else list(axs)
    target = min(pool, key=lambda x: abs(x - env.cannon_x))
    if abs(env.cannon_x - target) > 18:                   # zone morte > pas (13) → pas d'oscillation
        return 1 if env.cannon_x < target else 0
    return 2


def collect(n_episodes=40, max_steps=1500, seed=0):
    rng = np.random.default_rng(seed)
    X, Y = [], []
    for _ in range(n_episodes):
        env = SpaceInvaders(max_steps=max_steps)
        f = env.reset(seed=int(rng.integers(1_000_000)))
        while not env.done:
            a = expert(env)
            X.append(f.copy()); Y.append(a)
            f, _, _, _ = env.step(a)
    return np.array(X), np.array(Y)


def _softmax(z):
    z = z - z.max(1, keepdims=True); e = np.exp(z)
    return e / e.sum(1, keepdims=True)


def train_bc(iters=5000, lr=0.05, seed=0):
    X, Y = collect(seed=seed)
    n = X.shape[0]
    Yh = np.eye(4)[Y]
    freq = np.bincount(Y, minlength=4) / n
    w = 1.0 / (freq + 0.05); w /= w.mean()
    wy = w[Y][:, None]                                    # léger rééquilibrage des classes
    rng = np.random.default_rng(seed)
    W0 = rng.normal(0, .4, (10, 9)); b0 = np.zeros(9)
    W1 = rng.normal(0, .4, (9, 9)); b1 = np.zeros(9)
    W2 = rng.normal(0, .4, (9, 4)); b2 = np.zeros(4)
    p = None
    for _ in range(iters):
        a1 = np.tanh(X @ W0 + b0)
        a2 = np.tanh(a1 @ W1 + b1)
        p = _softmax(a2 @ W2 + b2)
        dz3 = (p - Yh) * wy / n
        dW2 = a2.T @ dz3; db2 = dz3.sum(0)
        dz2 = (dz3 @ W2.T) * (1 - a2 ** 2)
        dW1 = a1.T @ dz2; db1 = dz2.sum(0)
        dz1 = (dz2 @ W1.T) * (1 - a1 ** 2)
        dW0 = X.T @ dz1; db0 = dz1.sum(0)
        for P, dP in [(W0, dW0), (b0, db0), (W1, dW1), (b1, db1), (W2, dW2), (b2, db2)]:
            P -= lr * dP
    acc = (p.argmax(1) == Y).mean()
    vec = np.concatenate([W0.ravel(), b0, W1.ravel(), b1, W2.ravel(), b2])
    return vec, acc


if __name__ == "__main__":
    import time
    from collections import Counter
    t0 = time.time()
    vec, acc = train_bc()
    MLP(params=vec).save(f"{HERE}/best.npz")
    net = MLP.load(f"{HERE}/best.npz")
    lbl = ["GAUCHE", "DROITE", "TIR", "RIEN"]
    scores, waves, dist = [], [], Counter()
    for s in range(10):
        env = SpaceInvaders(max_steps=3000); f = env.reset(seed=s)
        while not env.done:
            a = net.act(f); dist[a] += 1; f, _, _, _ = env.step(a)
        scores.append(env.score); waves.append(env.wave)
    tot = sum(dist.values())
    print(f"BC acc={acc:.2f} | score~{np.mean(scores):.0f} vagues~{np.mean(waves):.1f} | "
          f"{ {lbl[k]: f'{100*dist[k]/tot:.0f}%' for k in range(4)} } | {time.time()-t0:.0f}s")
