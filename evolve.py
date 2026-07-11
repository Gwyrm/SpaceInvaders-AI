"""Neuroévolution WARM-START depuis l'agent BC : optimise la récompense de jeu
(survie + kills − morts − tirs gaspillés sur ses propres bunkers). Partant d'une
politique déjà compétente, elle ne peut que s'améliorer (élitisme). Sauvegarde
`best.npz` uniquement si l'évolué domine le BC.
"""
import sys
import time
import numpy as np

from env import SpaceInvaders
from agent import MLP

HERE = "/Users/pierre/Projets/SpaceInvaders-AI"


def rollout(vec, seed, max_steps=2000):
    env = SpaceInvaders(max_steps=max_steps)
    f = env.reset(seed=seed)
    net = MLP(params=vec)
    tot = 0.0
    while not env.done:
        f, r, d, i = env.step(net.act(f)); tot += r
    cells = sum(int(b.sum()) for b in env.bunkers)
    return tot, i["score"], env.wave, cells


def fitness(vec, seeds, max_steps):
    return float(np.mean([rollout(vec, s, max_steps)[0] for s in seeds]))


def evolve(gens=22, pop=40, elite=6, seeds_per=3, sigma0=0.35, max_steps=2000, seed=0):
    rng = np.random.default_rng(seed)
    base = MLP.load(f"{HERE}/best.npz").to_vector()
    n = len(base)
    P = [base.copy()] + [base + rng.normal(0, sigma0, n) for _ in range(pop - 1)]   # warm-start
    for g in range(gens):
        seeds = [int(rng.integers(1_000_000_000)) for _ in range(seeds_per)]
        fits = np.array([fitness(v, seeds, max_steps) for v in P])
        order = np.argsort(fits)[::-1]
        P = [P[i] for i in order]
        if g % 4 == 0 or g == gens - 1:
            print(f"gen {g:2d}  best {fits[order[0]]:7.1f}  mean {fits.mean():7.1f}", flush=True)
        sigma = sigma0 * (1 - g / gens) + 0.03
        newP = [P[i].copy() for i in range(elite)]
        half = max(2, pop // 2)
        while len(newP) < pop:
            a, b = P[int(rng.integers(half))], P[int(rng.integers(half))]
            child = np.where(rng.random(n) < 0.5, a, b) + rng.normal(0, sigma, n) * (rng.random(n) < 0.5)
            newP.append(child)
        P = newP
    return P


def summarize(vec, seeds):
    r = [rollout(vec, s, 3000) for s in seeds]
    return (np.mean([x[1] for x in r]), np.mean([x[2] for x in r]), np.mean([x[3] for x in r]))


if __name__ == "__main__":
    gens = int(sys.argv[1]) if len(sys.argv) > 1 else 22
    t0 = time.time()
    base_vec = MLP.load(f"{HERE}/best.npz").to_vector()
    P = evolve(gens=gens)
    rng = np.random.default_rng(999)
    seeds = [int(rng.integers(1_000_000_000)) for _ in range(15)]
    cand = P[:8]
    best = cand[int(np.argmax([fitness(v, seeds, 2500) for v in cand]))]
    bs, bw, bc = summarize(base_vec, seeds)
    es, ew, ec = summarize(best, seeds)
    print(f"\nBC     : score {bs:5.0f}  vagues {bw:.1f}  bunkers {bc:.0f}/108")
    print(f"ÉVOLUÉ : score {es:5.0f}  vagues {ew:.1f}  bunkers {ec:.0f}/108")
    better = (es + ew * 100 + ec * 2) >= (bs + bw * 100 + bc * 2)   # score + vagues + bunkers
    if better:
        MLP(params=best).save(f"{HERE}/best.npz"); print("→ best.npz MIS À JOUR (évolué ≥ BC)")
    else:
        print("→ on GARDE le BC (l'évolué ne domine pas)")
    print(f"{gens} gén · {time.time()-t0:.0f}s", flush=True)
