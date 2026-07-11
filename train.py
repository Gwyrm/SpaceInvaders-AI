"""Neuroévolution (GA) de l'agent MLP pour Space Invaders (comme Flappy/Petri).

Maximise la récompense de jeu (kills + survie + vagues − morts). Fitness moyennée
sur plusieurs seeds (anti-chance), sélection finale robuste sur 20 seeds parmi les
élites. Sauvegarde le meilleur dans best.npz. Usage : python train.py [generations].
"""
import sys
import time
import numpy as np

from env import SpaceInvaders
from agent import MLP

HERE = "/Users/pierre/Projets/SpaceInvaders-AI"


def rollout(vec, seed, max_steps=1600):
    """Joue une partie ; renvoie (fitness, score, vagues)."""
    env = SpaceInvaders(max_steps=max_steps)
    f = env.reset(seed=seed)
    net = MLP(params=vec)
    tot = 0.0
    while not env.done:
        f, r, done, info = env.step(net.act(f))
        tot += r
    return tot, info["score"], env.wave


def play_random(seed, max_steps=1600):
    env = SpaceInvaders(max_steps=max_steps)
    env.reset(seed=seed)
    rr = np.random.default_rng(seed)
    while not env.done:
        _, _, _, info = env.step(int(rr.integers(4)))
    return info["score"]


def fitness(vec, seeds, max_steps):
    return float(np.mean([rollout(vec, s, max_steps)[0] for s in seeds]))


def train(pop=56, gens=40, elite=6, seeds_per=3, max_steps=1600, sigma0=0.6, seed=0):
    rng = np.random.default_rng(seed)
    n = MLP.n_params()
    P = [rng.normal(0, 0.5, n) for _ in range(pop)]
    for g in range(gens):
        seeds = [int(rng.integers(1_000_000_000)) for _ in range(seeds_per)]
        fits = np.array([fitness(v, seeds, max_steps) for v in P])
        order = np.argsort(fits)[::-1]
        P = [P[i] for i in order]                       # trié : meilleurs en tête
        if g % 5 == 0 or g == gens - 1:
            print(f"gen {g:2d}  best {fits[order[0]]:8.1f}  mean {fits.mean():8.1f}", flush=True)
        sigma = sigma0 * (1 - g / gens) + 0.05
        newP = [P[i].copy() for i in range(elite)]      # élites conservées
        half = max(2, pop // 2)
        while len(newP) < pop:
            a, b = P[int(rng.integers(half))], P[int(rng.integers(half))]
            child = np.where(rng.random(n) < 0.5, a, b)
            child = child + rng.normal(0, sigma, n) * (rng.random(n) < 0.5)
            newP.append(child)
        P = newP
    return P                                            # population finale (élites en tête)


if __name__ == "__main__":
    gens = int(sys.argv[1]) if len(sys.argv) > 1 else 40
    t0 = time.time()
    P = train(gens=gens)

    # sélection finale ROBUSTE : les 10 meilleurs re-évalués sur 20 seeds
    rng = np.random.default_rng(999)
    sel_seeds = [int(rng.integers(1_000_000_000)) for _ in range(20)]
    cand = P[:10]
    cand_fit = [fitness(v, sel_seeds, 1600) for v in cand]
    best = cand[int(np.argmax(cand_fit))]
    MLP(params=best).save(f"{HERE}/best.npz")

    # rapport : entraîné vs aléatoire (mêmes seeds de test)
    test = [int(rng.integers(1_000_000_000)) for _ in range(20)]
    tr = [rollout(best, s) for s in test]
    tr_score = np.mean([x[1] for x in tr]); tr_wave = np.mean([x[2] for x in tr])
    rnd = np.mean([play_random(s) for s in test])
    print(f"\n=== ENTRAÎNÉ score {tr_score:.0f} (vagues~{tr_wave:.1f})  |  "
          f"ALÉATOIRE score {rnd:.0f}  →  x{tr_score/max(1,rnd):.1f} ===")
    print(f"best.npz sauvé · {gens} gén · {time.time()-t0:.0f}s", flush=True)
